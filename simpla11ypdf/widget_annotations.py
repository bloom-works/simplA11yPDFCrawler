from __future__ import annotations

from typing import Any

from simpla11ypdf.structure import obj_get, safe_name

WIDGET_SUBTYPE = "/Widget"


def object_key(obj: Any) -> tuple[int, int] | None:
    try:
        return tuple(obj.objgen)
    except Exception:
        return None


def top_level_acroform_widget_keys(pdf) -> set[tuple[int, int]]:
    """
    Return AcroForm /Fields entries that are themselves /Widget annotations.

    These are the widget annotations that should be owned by
    Forms > Tagged form fields, rather than Page Content > Tagged annotations.
    """
    acroform = obj_get(pdf.Root, "/AcroForm")
    fields = obj_get(acroform, "/Fields") if acroform is not None else None

    if fields is None:
        return set()

    keys: set[tuple[int, int]] = set()

    try:
        for field in fields:
            if safe_name(obj_get(field, "/Subtype")) == WIDGET_SUBTYPE:
                key = object_key(field)
                if key is not None:
                    keys.add(key)
    except Exception:
        pass

    return keys


def is_top_level_acroform_widget(
    widget_obj: Any,
    top_level_widget_keys: set[tuple[int, int]],
) -> bool:
    key = object_key(widget_obj)
    return key is not None and key in top_level_widget_keys
