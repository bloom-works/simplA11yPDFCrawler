from simpla11ypdf.models import StructureItem

LAYOUT_FIGURE_ANCESTOR_TYPES = {
    "Art",
}


def _has_layout_figure_ancestor(fig: StructureItem) -> bool:
    """
    Return true when a Figure appears inside an Art/TextBox-style layout
    container.

    In tested Acrobat behavior, empty-alt vector Figures inside this kind of
    layout container may pass, while standalone empty-alt Figures fail.
    """
    return fig.parent_type in LAYOUT_FIGURE_ANCESTOR_TYPES or any(
        ancestor_type in LAYOUT_FIGURE_ANCESTOR_TYPES
        for ancestor_type in fig.ancestor_types
    )


def _empty_alt_can_be_treated_as_intentional(
    fig: StructureItem,
    is_image_backed: bool | None,
) -> bool:
    """
    Empty /Alt is only treated as intentional when the Figure is known not to be
    image-backed and appears inside a layout/art container.
    """
    if is_image_backed is not False:
        return False

    return _has_layout_figure_ancestor(fig)


def check_figures(
    structure_items: list[StructureItem],
    result: dict,
    image_info: dict[str, int] | None = None,
    image_backed_mcids: set[tuple[str, int]] | None = None,
) -> None:
    """
    Inspect normalized structure items and report basic figure/alt-text findings.

    Tagged PDF rules:
    - Pass: every Figure has non-empty /Alt, or has explicit empty /Alt in a
    layout/art container where the Figure appears to be intentionally silent
    - Warn: no failing figures, but at least one Figure relies only on /ActualText
    - Fail: at least one Figure has no /Alt and no usable /ActualText, or has
    explicit empty /Alt outside a layout/art container

    Diagnostic counts:
    - FiguresWithAlt: figures with non-empty /Alt
    - FiguresWithEmptyAlt: figures whose /Alt entry exists but has no usable text
    - FiguresWithActualTextOnly: figures with usable /ActualText but no usable /Alt
    - FiguresWithoutAlt: figures with no /Alt entry at all

    Untagged PDF fallback:
    - Fail: image objects are present, but no figure tagging is available
    - NotApplicable: no image objects detected
    """
    if image_info is None:
        image_info = {"ImageObjectsFound": 0, "PagesWithImages": 0}

    result["ImageObjectsFound"] = image_info["ImageObjectsFound"]
    result["PagesWithImages"] = image_info["PagesWithImages"]

    result["FiguresFound"] = 0
    result["FiguresWithAlt"] = 0
    result["FiguresWithEmptyAlt"] = 0
    result["FiguresWithActualTextOnly"] = 0
    result["FiguresWithoutAlt"] = 0
    result["FiguresAltTextIssues"] = ""

    # No structure tree fallback:
    # if the PDF has no structure tree, structure-based figure analysis is not reliable.
    if result.get("StructTreeRootPresent") is not True:
        if image_info["ImageObjectsFound"] > 0:
            result["FiguresAltTextTest"] = "Fail"
            result["Accessible"] = False
            result["_log"] += "untagged-images, "
        else:
            result["FiguresAltTextTest"] = "NotApplicable"
        return

    figures = [item for item in structure_items if item.normalized_type == "Figure"]

    result["FiguresFound"] = len(figures)

    if not figures:
        result["FiguresAltTextTest"] = "Pass"
        return

    failing_issues: list[str] = []
    warning_issues: list[str] = []

    for fig in figures:
        ref = fig.object_ref or "unknown-object"

        has_usable_alt = fig.alt_source == "/Alt"
        has_usable_actual_text = fig.alt_source == "/ActualText"
        has_empty_alt = fig.has_alt_entry and not has_usable_alt

        is_image_backed: bool | None = None
        if image_backed_mcids is not None and fig.page_ref and fig.mcids:
            is_image_backed = any(
                (fig.page_ref, mcid) in image_backed_mcids for mcid in fig.mcids
            )

        if has_usable_alt:
            result["FiguresWithAlt"] += 1

        if has_empty_alt:
            result["FiguresWithEmptyAlt"] += 1

        if not fig.has_alt_entry:
            result["FiguresWithoutAlt"] += 1

        if has_usable_actual_text:
            result["FiguresWithActualTextOnly"] += 1
            warning_issues.append(
                f"{ref}: Figure uses /ActualText but has no non-empty /Alt"
            )

        if not fig.alt:
            if fig.has_alt_entry:
                if _empty_alt_can_be_treated_as_intentional(fig, is_image_backed):
                    # Empty /Alt can be intentional for non-image-backed Figures inside
                    # Art/TextBox-style layout containers. Standalone empty-alt Figures are
                    # reported because Acrobat fails this pattern in tested files.
                    continue

                failing_issues.append(f"{ref}: Figure has empty /Alt")
                continue

            if fig.has_actual_text_entry:
                failing_issues.append(
                    f"{ref}: Figure has no /Alt and empty /ActualText"
                )
            else:
                failing_issues.append(f"{ref}: Figure has no /Alt or /ActualText")

    if failing_issues:
        result["FiguresAltTextIssues"] = " | ".join(failing_issues)
        result["FiguresAltTextTest"] = "Fail"
        result["Accessible"] = False
        result["_log"] += "figures-alt, "
    elif warning_issues:
        result["FiguresAltTextIssues"] = " | ".join(warning_issues)
        result["FiguresAltTextTest"] = "Warn"
        result["_log"] += "figures-actualtext-warn, "
    else:
        result["FiguresAltTextTest"] = "Pass"
