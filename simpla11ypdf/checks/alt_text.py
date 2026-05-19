from simpla11ypdf.models import StructureItem


def _ancestor_items(
    structure_items: list[StructureItem], index: int
) -> list[StructureItem]:
    """
    Return the actual ancestor items for the structure item at index by walking
    backward through the flat depth-ordered structure list.
    """
    item = structure_items[index]
    ancestors: list[StructureItem] = []
    target_depth = item.depth - 1

    for i in range(index - 1, -1, -1):
        candidate = structure_items[i]
        if candidate.depth == target_depth:
            ancestors.append(candidate)
            target_depth -= 1
            if target_depth < 0:
                break

    return ancestors


def check_nested_alt_text(structure_items: list[StructureItem], result: dict) -> None:
    """
    Fail when an alt-bearing structure item is nested inside another alt-bearing
    structure subtree.

    Current behavior:

    NotApplicable:
    - document is not tagged
    - no structure items with alt text are present

    Fail:
    - at least one alt-bearing structure item has an alt-bearing ancestor

    Pass:
    - alt-bearing structure items exist, but none are nested inside another
      alt-bearing structure subtree
    """
    result["NestedAltTextTest"] = "NotApplicable"
    result["NestedAltTextIssues"] = ""

    if result.get("StructTreeRootPresent") is not True:
        return

    alt_indexes = [
        i for i, item in enumerate(structure_items) if item.alt and item.normalized_type
    ]

    if not alt_indexes:
        return

    issues: list[str] = []

    for index in alt_indexes:
        item = structure_items[index]
        ancestors = _ancestor_items(structure_items, index)
        alt_ancestors = [ancestor for ancestor in ancestors if ancestor.alt]

        if alt_ancestors:
            nearest = alt_ancestors[0]
            issues.append(
                f"{item.object_ref or 'unknown-object'}: "
                f"{item.normalized_type} has alt nested inside "
                f"{nearest.normalized_type} with alt"
            )

    result["NestedAltTextIssues"] = " | ".join(issues)

    if issues:
        result["NestedAltTextTest"] = "Fail"
        result["Accessible"] = False
        result["_log"] += "alt-nested-fail, "
    else:
        result["NestedAltTextTest"] = "Pass"


def check_hides_annotation(structure_items: list[StructureItem], result: dict) -> None:
    """
    Warn when form annotations may be hidden by alternate text.

    Adobe flags "Hides annotation" when annotation-bearing structure content is
    inside alternate text. The most common form case is either:

    - a Form structure element has /Alt or /ActualText and an OBJR child
    - a Form structure element has an OBJR child and an ancestor has /Alt or
      /ActualText

    We keep this as Warn rather than Fail because this is still a structural
    approximation, even though Adobe reports it as a failure.
    """
    SUSPICIOUS_TYPES = {
        "Form",
    }

    result["HidesAnnotationTest"] = "NotApplicable"
    result["HidesAnnotationIssues"] = ""

    if result.get("StructTreeRootPresent") is not True:
        return

    issues: list[str] = []

    for index, item in enumerate(structure_items):
        if item.normalized_type not in SUSPICIOUS_TYPES:
            continue

        if not item.has_objr:
            continue

        ref = item.object_ref or "unknown-object"
        objr_count = item.objr_count or 1

        if item.alt:
            source = item.alt_source or "alt text"
            issues.append(
                f"{ref}: {item.normalized_type} has {source} "
                f"and {objr_count} OBJR child"
            )
            continue

        ancestors = _ancestor_items(structure_items, index)
        alt_ancestors = [ancestor for ancestor in ancestors if ancestor.alt]

        if alt_ancestors:
            nearest = alt_ancestors[0]
            nearest_ref = nearest.object_ref or "unknown-object"
            source = nearest.alt_source or "alt text"

            issues.append(
                f"{ref}: {item.normalized_type} has {objr_count} OBJR child "
                f"inside {nearest.normalized_type} {nearest_ref} with {source}"
            )

    if not issues:
        result["HidesAnnotationTest"] = "Pass"
    else:
        result["HidesAnnotationTest"] = "Warn"
        result["HidesAnnotationIssues"] = " | ".join(issues)
        result["_log"] += "alt-hides-annotation-warn, "
