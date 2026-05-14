from __future__ import annotations

from typing import Any

import pikepdf

from scanner.models import StructureItem
from scanner.structure import obj_get, safe_name


def _object_ref(obj: Any) -> str | None:
    try:
        return repr(obj.objgen)
    except Exception:
        return None


def _mcid_from_bdc_operands(operands: list[Any]) -> int | None:
    """
    Extract a direct /MCID value from a BDC property dictionary.

    This intentionally handles only the simple direct-dictionary form for now:
        /Figure << /MCID 3 >> BDC
    """
    if len(operands) < 2:
        return None

    properties = operands[1]
    mcid = obj_get(properties, "/MCID")

    try:
        return int(mcid)
    except Exception:
        return None


def _active_mcid(stack: list[int | None]) -> int | None:
    """
    Return the nearest active MCID in the marked-content stack.
    """
    for mcid in reversed(stack):
        if mcid is not None:
            return mcid

    return None


def _xobject_name_from_operands(operands: list[Any]) -> str | None:
    if not operands:
        return None

    return safe_name(operands[0])


def _image_xobject_names(content: Any) -> set[str]:
    """
    Return XObject names on this content object whose subtype is /Image.

    This lets us avoid resolving the same XObject repeatedly for every Do
    operator in the page content stream.
    """
    image_names: set[str] = set()

    resources = obj_get(content, "/Resources")
    if resources is None:
        return image_names

    xobjects = obj_get(resources, "/XObject")
    if xobjects is None:
        return image_names

    try:
        keys = list(xobjects.keys())
    except Exception:
        return image_names

    for key in keys:
        try:
            xobject = xobjects.get(key)
        except Exception:
            continue

        if safe_name(obj_get(xobject, "/Subtype")) != "/Image":
            continue

        key_text = safe_name(key)
        if key_text:
            image_names.add(key_text)

        image_names.add(str(key))

    return image_names


def collect_empty_alt_figure_mcids(
    structure_items: list[StructureItem],
) -> dict[str, set[int]]:
    """
    Return page_ref -> MCIDs for Figures where image-backed detection matters.

    We only need image-backed detection for Figures with an explicit empty /Alt.

    We do not need it for:
    - Figures with non-empty /Alt, because they already pass
    - Figures with no /Alt, because they fail without image-backed detection
    - Figures with no page_ref or MCIDs, because we cannot match them to content
    """
    targets: dict[str, set[int]] = {}

    for item in structure_items:
        if item.normalized_type != "Figure":
            continue

        # Non-empty /Alt already passes.
        if item.alt_source == "/Alt":
            continue

        # Missing /Alt fails separately; image-backed lookup is not needed.
        if not item.has_alt_entry:
            continue

        # At this point, this is an explicit empty-/Alt Figure.
        if not item.page_ref or not item.mcids:
            continue

        targets.setdefault(item.page_ref, set()).update(item.mcids)

    return targets


def detect_image_backed_mcids(
    pdf,
    *,
    target_mcids_by_page: dict[str, set[int]],
) -> set[tuple[str, int]]:
    """
    Return (page_ref, mcid) pairs whose marked-content block paints an image
    XObject directly in a page content stream.

    This targeted version only scans pages/MCIDs that matter for figure alt-text
    checking, usually explicit empty-/Alt Figure elements.

    This intentionally remains a small implementation:
    - tracks BMC / BDC / EMC nesting
    - recognizes direct BDC property dictionaries with /MCID
    - treats a block as image-backed when it contains a Do operator whose
      XObject resolves to /Subtype /Image
    - does not yet recurse into Form XObjects or handle named property lists
    """
    image_backed_mcids: set[tuple[str, int]] = set()

    if not target_mcids_by_page:
        return image_backed_mcids

    for page in pdf.pages:
        page_ref = _object_ref(page.obj)
        if page_ref is None:
            continue

        target_mcids_for_page = target_mcids_by_page.get(page_ref)
        if not target_mcids_for_page:
            continue

        image_xobject_names = _image_xobject_names(page)

        # If this page has no image XObjects, parsing the content stream cannot
        # produce any image-backed MCID findings.
        if not image_xobject_names:
            continue

        try:
            operations = pikepdf.parse_content_stream(page)
        except Exception:
            continue

        marked_content_stack: list[int | None] = []
        found_target_mcids: set[int] = set()

        for operands, operator in operations:
            operator_name = str(operator)

            if operator_name == "BDC":
                marked_content_stack.append(_mcid_from_bdc_operands(operands))
                continue

            if operator_name == "BMC":
                marked_content_stack.append(None)
                continue

            if operator_name == "EMC":
                if marked_content_stack:
                    marked_content_stack.pop()
                continue

            if operator_name != "Do":
                continue

            mcid = _active_mcid(marked_content_stack)
            if mcid is None:
                continue

            if mcid not in target_mcids_for_page:
                continue

            xobject_name = _xobject_name_from_operands(operands)
            if xobject_name not in image_xobject_names:
                continue

            image_backed_mcids.add((page_ref, mcid))
            found_target_mcids.add(mcid)

            # Once every target MCID on this page has been confirmed as
            # image-backed, there is no reason to keep scanning this page.
            if target_mcids_for_page.issubset(found_target_mcids):
                break

    return image_backed_mcids
