from scanner.models import StructureItem


def check_figures(
    structure_items: list[StructureItem],
    result: dict,
    image_info: dict[str, int] | None = None,
) -> None:
    """
    Inspect normalized structure items and report basic figure/alt-text findings.

    Tagged PDF rules:
    - Pass: every Figure has non-empty /Alt
    - Warn: no Figure is missing usable alternate text, but at least one Figure
      relies on /ActualText instead of non-empty /Alt
    - Fail: at least one Figure has no usable alternate text in either /Alt
      or /ActualText

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

    # Untagged fallback:
    # if the PDF is not tagged, structure-based figure analysis is not reliable.
    if result.get("TaggedTest") != "Pass":
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

        # At this stage, preserve the existing scanner rule:
        # no usable text in either /Alt or /ActualText is still a failure.
        if not fig.alt:
            if fig.has_alt_entry:
                failing_issues.append(
                    f"{ref}: Figure has empty /Alt and no usable /ActualText"
                )
            elif fig.has_actual_text_entry:
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
        result["_log"] += "figures-actualtext, "
    else:
        result["FiguresAltTextTest"] = "Pass"
