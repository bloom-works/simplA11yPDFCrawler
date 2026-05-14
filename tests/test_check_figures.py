from pathlib import Path

from pikepdf import Pdf

from scanner.checks.figures import check_figures
from scanner.checks.document import check_tagging
from scanner.figure_content import (
    collect_empty_alt_figure_mcids,
    detect_image_backed_mcids,
)
from scanner.image_detection import detect_image_objects
from scanner.structure import load_structure_items

FIXTURE_SUBDIR = "figures"


def open_pdf(path: Path) -> Pdf:
    return Pdf.open(str(path))


def build_figure_inputs(pdf: Pdf, result: dict):
    check_tagging(pdf, result)

    structure_items = []
    if pdf.Root.get("/StructTreeRoot") is not None:
        structure_items = load_structure_items(pdf)

    image_info = detect_image_objects(pdf)

    target_mcids_by_page = collect_empty_alt_figure_mcids(structure_items)
    image_backed_mcids = detect_image_backed_mcids(
        pdf,
        target_mcids_by_page=target_mcids_by_page,
    )

    return structure_items, image_info, image_backed_mcids


def test_figures_check_passes_for_tagged_pdf_with_no_figures(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_tagged_no_figures_pass.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"
    assert result["FiguresFound"] == 0
    assert result["FiguresAltTextTest"] == "Pass"
    assert result["FiguresWithAlt"] == 0
    assert result["FiguresWithActualTextOnly"] == 0
    assert result["FiguresWithoutAlt"] == 0
    assert result["FiguresWithEmptyAlt"] == 0
    assert result["FiguresAltTextIssues"] == ""


def test_figures_check_passes_for_tagged_pdf_with_figure_alt_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_tagged_alt_pass.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"
    assert result["FiguresFound"] == 1
    assert result["FiguresWithAlt"] == 1
    assert result["FiguresWithActualTextOnly"] == 0
    assert result["FiguresWithoutAlt"] == 0
    assert result["FiguresAltTextTest"] == "Pass"
    assert result["FiguresWithEmptyAlt"] == 0
    assert result["FiguresAltTextIssues"] == ""


def test_figures_check_warns_for_tagged_pdf_with_actualtext_only(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_tagged_actualtext_warn.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"
    assert result["FiguresFound"] == 1
    assert result["FiguresWithActualTextOnly"] == 1
    assert result["FiguresWithoutAlt"] == 1
    assert result["FiguresAltTextTest"] == "Warn"
    assert result["FiguresWithEmptyAlt"] == 0
    assert "uses /ActualText" in result["FiguresAltTextIssues"]
    assert "figures-empty-alt-warn" in result["_log"]


def test_figures_check_fails_for_tagged_pdf_with_figure_missing_alt_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_tagged_no_alt_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"
    assert result["FiguresFound"] == 1
    assert result["FiguresWithoutAlt"] == 1
    assert result["FiguresAltTextTest"] == "Fail"
    assert result["Accessible"] is False
    assert result["FiguresWithEmptyAlt"] == 0
    assert "no /Alt or /ActualText" in result["FiguresAltTextIssues"]
    assert "figures-alt" in result["_log"]


def test_figures_check_fails_for_image_figure_with_empty_alt_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_tagged_empty_alt_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf,
            result,
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"
    assert result["ImageObjectsFound"] == 1
    assert result["FiguresFound"] == 1
    assert result["FiguresWithAlt"] == 0
    assert result["FiguresWithEmptyAlt"] == 1
    assert result["FiguresWithActualTextOnly"] == 0
    assert result["FiguresWithoutAlt"] == 0

    assert result["FiguresAltTextTest"] == "Warn"
    assert "empty /Alt" in result["FiguresAltTextIssues"]
    assert result["Accessible"] is True
    assert "figures-alt" not in result["_log"]


def test_figures_check_fails_for_untagged_pdf_with_image(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_untagged_images_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Fail"
    assert result["ImageObjectsFound"] == 1
    assert result["FiguresFound"] == 0
    assert result["FiguresAltTextTest"] == "Fail"
    assert result["Accessible"] is False
    assert "untagged-images" in result["_log"]


def test_figures_check_is_not_applicable_for_untagged_pdf_without_image(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_untagged_no_images_na.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Fail"
    assert result["ImageObjectsFound"] == 0
    assert result["FiguresFound"] == 0
    assert result["FiguresAltTextTest"] == "NotApplicable"


def test_figures_check_fails_for_scanned_image_only_pdf(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / "empty_text" / "empty_text_image_only_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf, result
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Fail"
    assert result["ImageObjectsFound"] == 1
    assert result["FiguresFound"] == 0
    assert result["FiguresAltTextTest"] == "Fail"
    assert result["Accessible"] is False
    assert "untagged-images" in result["_log"]


def test_figures_check_passes_for_vector_figures_with_empty_alt_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_vector_empty_alt_pass.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf,
            result,
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"

    # This fixture has image-backed logo Figures with non-empty alt text,
    # plus vector-only Figures with explicit empty /Alt.
    assert result["ImageObjectsFound"] >= 1
    assert result["FiguresFound"] == 8
    assert result["FiguresWithAlt"] == 4
    assert result["FiguresWithEmptyAlt"] == 4
    assert result["FiguresWithActualTextOnly"] == 0
    assert result["FiguresWithoutAlt"] == 0

    # The important Adobe-aligned behavior:
    # empty /Alt is accepted only because these specific Figures are not
    # image-backed.
    assert result["FiguresAltTextTest"] == "Pass"
    assert result["FiguresAltTextIssues"] == ""
    assert result["Accessible"] is True
    assert "figures-alt" not in result["_log"]


def test_figures_check_fails_for_vector_figures_with_missing_alt_text(
    fixtures_dir: Path,
    make_result,
):
    pdf_path = fixtures_dir / FIXTURE_SUBDIR / "figures_vector_missing_alt_fail.pdf"
    result = make_result(pdf_path.name)

    with open_pdf(pdf_path) as pdf:
        structure_items, image_info, image_backed_mcids = build_figure_inputs(
            pdf,
            result,
        )
        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )

    assert result["TaggedTest"] == "Pass"

    # Same document shape as the empty-alt fixture, but the vector Figures
    # no longer have /Alt entries at all.
    assert result["ImageObjectsFound"] >= 1
    assert result["FiguresFound"] == 8
    assert result["FiguresWithAlt"] == 4
    assert result["FiguresWithEmptyAlt"] == 0
    assert result["FiguresWithActualTextOnly"] == 0
    assert result["FiguresWithoutAlt"] == 4

    assert result["FiguresAltTextTest"] == "Fail"
    assert result["Accessible"] is False
    assert "no /Alt or /ActualText" in result["FiguresAltTextIssues"]
    assert "figures-alt" in result["_log"]
