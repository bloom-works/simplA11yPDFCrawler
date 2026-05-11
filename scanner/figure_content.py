from __future__ import annotations

from typing import Any

import pikepdf

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


def _resolve_xobject(content: Any, operands: list[Any]) -> Any | None:
    if not operands:
        return None

    xobject_name = operands[0]
    xobject_name_text = safe_name(xobject_name)

    resources = obj_get(content, "/Resources")
    if resources is None:
        return None

    xobjects = obj_get(resources, "/XObject")
    if xobjects is None:
        return None

    try:
        return xobjects.get(xobject_name)
    except Exception:
        pass

    if xobject_name_text:
        try:
            return xobjects.get(xobject_name_text)
        except Exception:
            pass

    return None


def detect_image_backed_mcids(pdf) -> set[tuple[str, int]]:
    """
    Return (page_ref, mcid) pairs whose marked-content block paints an image
    XObject directly in a page content stream.

    This is intentionally a small first version:
    - tracks BMC / BDC / EMC nesting
    - recognizes direct BDC property dictionaries with /MCID
    - treats a block as image-backed when it contains a Do operator whose
      XObject resolves to /Subtype /Image
    - does not yet recurse into Form XObjects or handle named property lists
    """
    image_backed_mcids: set[tuple[str, int]] = set()

    for page in pdf.pages:
        page_ref = _object_ref(page.obj)
        if page_ref is None:
            continue

        try:
            operations = pikepdf.parse_content_stream(page)
        except Exception:
            continue

        marked_content_stack: list[int | None] = []

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

            xobject = _resolve_xobject(page, operands)
            if safe_name(obj_get(xobject, "/Subtype")) == "/Image":
                image_backed_mcids.add((page_ref, mcid))

    return image_backed_mcids
