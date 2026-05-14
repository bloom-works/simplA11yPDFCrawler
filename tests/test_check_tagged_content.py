from pathlib import Path

from pikepdf import Pdf

from simpla11ypdf.checks.document import check_tagging
from simpla11ypdf.checks.tagged_content import check_tagged_content

FIXTURE_SUBDIR = "tagged_content"


def open_pdf(path: Path) -> Pdf:
    return Pdf.open(str(path))


def test_tagged_content_check_passes_for_tagged_pdf_with_no_unmarked_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagged_content_pass.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_fails_for_google_docs_visible_header_footer(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir
        / FIXTURE_SUBDIR
        / "tagged_content_google_docs_header_footer_fail.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 14
    assert "page=1" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_fails_for_google_docs_empty_header_footer(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir
        / FIXTURE_SUBDIR
        / "tagged_content_google_docs_empty_header_footer_fail.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 2
    assert "page=1" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert "\\x00\\x03" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_passes_for_artifact_header_footer(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir / FIXTURE_SUBDIR / "tagged_content_artifact_header_footer_pass.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_fails_for_header_footer_after_artifacts_removed(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir
        / FIXTURE_SUBDIR
        / "tagged_content_not_artifacts_header_footer_fail.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 2
    assert "page=1" in result["UntaggedContentSummary"]
    assert "source=xobject" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert "HEADER" in result["UntaggedContentSummary"]
    assert "FOOTER" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_fails_for_add_text_content(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagged_content_add_text_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 1
    assert "page=1" in result["UntaggedContentSummary"]
    assert "source=page" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert result["UntaggedContentSummary"] != ""
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_fails_when_pdf_is_not_tagged(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagged_content_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Fail"
    assert result["TaggedContentTest"] == "Fail"
    assert result["Accessible"] is False


def test_tagged_content_check_warns_for_unmarked_whitespace_fixture(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagged_content_whitespace_only_warn.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Warn"

    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""

    assert result["UntaggedWhitespaceContentCount"] == 1
    assert "page=1" in result["UntaggedWhitespaceContentSummary"]
    assert "source=page" in result["UntaggedWhitespaceContentSummary"]
    assert "op=Tj" in result["UntaggedWhitespaceContentSummary"]
    assert "text=' '" in result["UntaggedWhitespaceContentSummary"]

    assert result["Accessible"] is True
    assert "tagged-content-whitespace-warn" in result["_log"]
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_warns_for_marked_whitespace_without_mcid(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir / FIXTURE_SUBDIR / "tagged_content_wcag_pdf2_bookmarks_warn.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)
        check_tagged_content(pdf, result)

    assert result["TaggedTest"] == "Pass"
    assert result["TaggedContentTest"] == "Warn"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedWhitespaceContentCount"] == 5
    assert result["Accessible"] is True
    assert "tagged-content-whitespace-warn" in result["_log"]


#########################################################
################# NO-FIXTURE UNIT TESTS #################
#########################################################


class FakeContent:
    def __init__(self, operations, resources=None, subtype=None):
        self.operations = operations
        self.resources = resources
        self.subtype = subtype

    def get(self, key, default=None):
        if key == "/Resources":
            return self.resources if self.resources is not None else default
        if key == "/Subtype":
            return self.subtype if self.subtype is not None else default
        return default


class FakePdf:
    def __init__(self, pages):
        self.pages = pages


def fake_pdf_with_ops(*page_operations):
    return FakePdf([FakeContent(ops) for ops in page_operations])


def fake_form_xobject(operations):
    return FakeContent(operations, subtype="/Form")


def fake_page_with_xobjects(operations, xobjects):
    return FakeContent(
        operations,
        resources={
            "/XObject": xobjects,
        },
    )


def patch_parse_content_stream(monkeypatch):
    def fake_parse_content_stream(content):
        return content.operations

    monkeypatch.setattr(
        "simpla11ypdf.checks.tagged_content.pikepdf.parse_content_stream",
        fake_parse_content_stream,
    )


def test_tagged_content_check_fails_for_unmarked_text_showing_operator(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            (["Hello"], "Tj"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 1
    assert "page=1" in result["UntaggedContentSummary"]
    assert "source=page" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert "Hello" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_fails_for_text_inside_marked_content_without_mcid(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            (["/P"], "BMC"),
            (["Hello"], "Tj"),
            ([], "EMC"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 1
    assert "text='Hello'" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_passes_for_text_inside_marked_content_with_mcid(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            (["/P", {"/MCID": 0}], "BDC"),
            (["Hello"], "Tj"),
            ([], "EMC"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_passes_for_text_inside_artifact(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            (["/Artifact"], "BMC"),
            (["Decorative header"], "Tj"),
            ([], "EMC"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_warns_for_unmarked_whitespace_text(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            (["   "], "Tj"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Warn"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["UntaggedWhitespaceContentCount"] == 1
    assert (
        "page=1 source=page op=Tj text='   '"
        in result["UntaggedWhitespaceContentSummary"]
    )
    assert result["Accessible"] is True
    assert "tagged-content-whitespace-warn" in result["_log"]
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_fails_for_unmarked_tj_array_text(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    pdf = fake_pdf_with_ops(
        [
            ([["Hel", -120, "lo"]], "TJ"),
        ]
    )
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 1
    assert "page=1" in result["UntaggedContentSummary"]
    assert "source=page" in result["UntaggedContentSummary"]
    assert "op=TJ" in result["UntaggedContentSummary"]
    assert "Hello" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_fails_for_unmarked_text_inside_form_xobject(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    form_xobject = fake_form_xobject(
        [
            (["HEADER"], "Tj"),
        ]
    )

    page = fake_page_with_xobjects(
        [
            (["/Fm0"], "Do"),
        ],
        {
            "/Fm0": form_xobject,
        },
    )

    pdf = FakePdf([page])
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Fail"
    assert result["UntaggedContentCount"] == 1
    assert "page=1" in result["UntaggedContentSummary"]
    assert "source=xobject" in result["UntaggedContentSummary"]
    assert "/Fm0" in result["UntaggedContentSummary"]
    assert "op=Tj" in result["UntaggedContentSummary"]
    assert "HEADER" in result["UntaggedContentSummary"]
    assert result["Accessible"] is False
    assert "tagged-content-fail" in result["_log"]


def test_tagged_content_check_passes_for_form_xobject_inside_artifact(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    form_xobject = fake_form_xobject(
        [
            (["HEADER"], "Tj"),
        ]
    )

    page = fake_page_with_xobjects(
        [
            (["/Artifact"], "BMC"),
            (["/Fm0"], "Do"),
            ([], "EMC"),
        ],
        {
            "/Fm0": form_xobject,
        },
    )

    pdf = FakePdf([page])
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]


def test_tagged_content_check_ignores_non_form_xobject(
    make_result,
    monkeypatch,
):
    patch_parse_content_stream(monkeypatch)

    image_xobject = FakeContent(
        operations=[
            (["This should not be parsed"], "Tj"),
        ],
        subtype="/Image",
    )

    page = fake_page_with_xobjects(
        [
            (["/Im0"], "Do"),
        ],
        {
            "/Im0": image_xobject,
        },
    )

    pdf = FakePdf([page])
    result = make_result("fake.pdf")
    result["TaggedTest"] = "Pass"

    check_tagged_content(pdf, result)

    assert result["TaggedContentTest"] == "Pass"
    assert result["UntaggedContentCount"] == 0
    assert result["UntaggedContentSummary"] == ""
    assert result["Accessible"] is True
    assert "tagged-content-fail" not in result["_log"]
