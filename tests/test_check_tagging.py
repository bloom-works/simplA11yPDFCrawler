from pathlib import Path

from pikepdf import Pdf

from simpla11ypdf.checks.document import check_tagging

FIXTURE_SUBDIR = "tagging"


def open_pdf(path: Path) -> Pdf:
    return Pdf.open(str(path))


def test_tagging_check_passes_for_tagged_pdf(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagging_pass.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)

    assert result["StructTreeRootPresent"] is True
    assert result["MarkedAsTagged"] is True
    assert result["TaggedTest"] == "Pass"
    assert result["Accessible"] is True
    assert "tagged" not in result["_log"]


def test_tagging_check_fails_for_untagged_pdf(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagging_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)

    assert result["StructTreeRootPresent"] is False
    assert result["MarkedAsTagged"] is False
    assert result["TaggedTest"] == "Fail"
    assert result["Accessible"] is False
    assert "tagged" in result["_log"]


def test_tagging_check_fails_when_struct_tree_exists_but_markinfo_missing(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = (
        fixtures_dir / FIXTURE_SUBDIR / "tagging_struct_tree_markinfo_missing.pdf"
    )
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)

    assert result["StructTreeRootPresent"] is True
    assert result["MarkedAsTagged"] is False
    assert result["TaggedTest"] == "Fail"
    assert result["Accessible"] is False
    assert "tagged" in result["_log"]


def test_tagging_check_fails_when_struct_tree_exists_but_marked_false(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagging_struct_tree_marked_false.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)

    assert result["StructTreeRootPresent"] is True
    assert result["MarkedAsTagged"] is False
    assert result["TaggedTest"] == "Fail"
    assert result["Accessible"] is False
    assert "tagged" in result["_log"]


def test_tagging_check_fails_when_marked_true_but_struct_tree_missing(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "tagging_marked_true_no_struct_tree.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        check_tagging(pdf, result)

    assert result["StructTreeRootPresent"] is False
    assert result["MarkedAsTagged"] is True
    assert result["TaggedTest"] == "Fail"
    assert result["Accessible"] is False
    assert "tagged" in result["_log"]
