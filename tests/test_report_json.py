from scanner.report import build_json_report


def base_result():
    return {
        "ProtectedTest": "Pass",
        "EmptyTextTest": "Pass",
        "TaggedTest": "Pass",
        "TaggedContentTest": "Pass",
        "UntaggedContentSummary": "",
        "LanguageTest": "Pass",
        "TitleTest": "Pass",
        "BookmarksTest": "Pass",
        "TaggedAnnotationsTest": "NotApplicable",
        "FormFieldCount": 0,
        "TaggedFormFieldsTest": "NotApplicable",
        "FormsTest": "NotApplicable",
        "FiguresAltTextTest": "Pass",
        "NestedAltTextTest": "NotApplicable",
        "HidesAnnotationTest": "NotApplicable",
        "InvalidTRParents": "",
        "InvalidCellParents": "",
        "TablesWithoutHeaders": "",
        "IrregularTables": "",
        "InvalidListItemParents": "",
        "InvalidListChildren": "",
        "MalformedListNodes": "",
        "HeadingsTest": "Pass",
    }


def find_rule(report, category, rule_name):
    return next(
        rule
        for rule in report["Detailed Report"][category]
        if rule["Rule"] == rule_name
    )


def test_report_summary_says_no_problems_when_no_failed_or_warning_rules():
    result = base_result()

    report = build_json_report(result, compatible=True)

    assert report["Summary"]["Failed"] == 0
    assert report["Summary"]["Warning"] == 0
    assert report["Summary"]["Description"] == (
        "The checker found no problems in this document."
    )


def test_report_maps_warn_to_warning_in_normal_report_mode_debug():
    result = {
        **base_result(),
        "HidesAnnotationTest": "Warn",
        "HidesAnnotationIssues": "(40, 0): Form has alt text and OBJR child",
    }

    report = build_json_report(result, debug=True)

    hides_annotation = find_rule(
        report,
        "Alternate Text",
        "Hides annotation",
    )

    assert hides_annotation["Status"] == "Warning"
    assert hides_annotation["Original status"] == "Warn"
    assert hides_annotation["Details"] == "(40, 0): Form has alt text and OBJR child"
    assert "Severity" not in hides_annotation

    assert report["Summary"]["Failed"] == 0
    assert report["Summary"]["Warning"] == 1
    assert report["Summary"]["Description"] == (
        "The checker found warnings which may require manual review."
    )


def test_report_maps_warn_to_failed_with_warning_severity_in_compatible_mode_debug():
    result = {
        **base_result(),
        "HidesAnnotationTest": "Warn",
        "HidesAnnotationIssues": "(40, 0): Form has alt text and OBJR child",
    }

    report = build_json_report(result, compatible=True, debug=True)

    hides_annotation = find_rule(
        report,
        "Alternate Text",
        "Hides annotation",
    )

    assert hides_annotation["Status"] == "Failed"
    assert hides_annotation["Original status"] == "Warn"
    assert hides_annotation["Severity"] == "Warning"
    assert hides_annotation["Details"] == "(40, 0): Form has alt text and OBJR child"

    assert report["Summary"]["Failed"] == 1
    assert report["Summary"]["Warning"] == 0
    assert report["Summary"]["Description"] == (
        "The checker found problems which may prevent the document from "
        "being fully accessible."
    )


def test_report_marks_tagged_content_failed_when_tagged_content_test_fails_debug():
    result = {
        **base_result(),
        "TaggedContentTest": "Fail",
        "UntaggedContentSummary": "page=1 source=page op=Tj text='Hello'",
    }

    report = build_json_report(result, debug=True)

    tagged_content = find_rule(
        report,
        "Page Content",
        "Tagged content",
    )

    assert tagged_content["Status"] == "Failed"
    assert tagged_content["Original status"] == "Fail"
    assert tagged_content["Details"] == "page=1 source=page op=Tj text='Hello'"

    assert report["Summary"]["Failed"] == 1
    assert report["Summary"]["Warning"] == 0


def test_report_marks_tagged_content_failed_when_document_is_not_tagged_debug():
    result = {
        **base_result(),
        "TaggedTest": "Fail",
        "TaggedContentTest": "Fail",
    }

    report = build_json_report(result, debug=True)

    tagged_content = find_rule(
        report,
        "Page Content",
        "Tagged content",
    )

    assert tagged_content["Status"] == "Failed"
    assert tagged_content["Details"] == (
        "Document is not tagged; page content cannot be verified as tagged."
    )
