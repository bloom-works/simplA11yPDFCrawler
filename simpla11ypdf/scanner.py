import os

import pikepdf
from pikepdf import Pdf

from simpla11ypdf.constants import OUTPUT_FIELDS
from simpla11ypdf.checks.document import (
    check_bookmarks,
    check_empty_text,
    check_language,
    check_metadata_and_title,
    check_protection,
    check_tagging,
)
from simpla11ypdf.checks.alt_text import check_nested_alt_text, check_hides_annotation
from simpla11ypdf.checks.annotations import check_annotations
from simpla11ypdf.checks.figures import check_figures
from simpla11ypdf.checks.forms import check_forms, check_form_fields
from simpla11ypdf.checks.headings import check_headings
from simpla11ypdf.checks.lists import check_lists
from simpla11ypdf.checks.tables import check_tables
from simpla11ypdf.checks.tagged_content import check_tagged_content
from simpla11ypdf.image_detection import detect_image_objects
from simpla11ypdf.figure_content import (
    collect_empty_alt_figure_mcids,
    detect_image_backed_mcids,
)
from simpla11ypdf.structure import load_structure_items


def init_result(file_name: str, site: str = None):
    """Create a blank scan result dictionary for a single PDF file.

    Initialises all keys from ``OUTPUT_FIELDS`` to ``None``, then sets known
    defaults: ``Site`` and ``File`` (basename only), an empty ``_log``
    string, ``Accessible=True`` (presumption of conformity),
    ``Exempt=False``, and ``TotallyInaccessible=False``.

    Args:
        file_name: Path to the PDF file. Only the basename is stored in the
                   result.
        site: Optional site identifier string to associate with this result.

    Returns:
        A dict keyed by every field in ``OUTPUT_FIELDS`` plus ``_log``, ready
        to be populated by the individual check functions.
    """
    result = {}
    for field in OUTPUT_FIELDS:
        result[field] = None
    result["Site"] = site
    result["File"] = os.path.basename(file_name)
    result["_log"] = ""
    result["Accessible"] = True  # presumption of conformity :)
    result["Exempt"] = False
    result["TotallyInaccessible"] = False
    return result


def finalize_result(result):
    """Set the TotallyInaccessible flag based on critical test outcomes.

    A document is considered totally inaccessible when it both fails tagging
    and contains no text (i.e. a scanned, untagged image), or when it fails
    the protection check (screen readers are blocked by encryption).

    Args:
        result: A fully populated scan result dict (all checks already run).

    Returns:
        None. Mutates ``result``, setting ``TotallyInaccessible`` to ``True``
        when the above conditions are met.
    """
    if result["TaggedTest"] == "Fail" and result["EmptyTextTest"] == "Fail":
        result["TotallyInaccessible"] = True

    if result["ProtectedTest"] == "Fail":
        result["TotallyInaccessible"] = True


def format_structure_debug(pdf, limit: int = 50) -> str:
    structure_items = load_structure_items(pdf)

    lines = [
        f"Tagged PDF: {'yes' if structure_items else 'no'}",
        f"First {limit} structure items:",
    ]

    lines.extend(str(item) for item in structure_items[:limit])

    return "\n".join(lines)


def check_file(file_name: str, site: str = None, debug: bool = False):
    """Run all accessibility checks on a single PDF file.

    Opens the PDF with pikepdf, records the PDF version and page count, then
    runs every check in sequence: metadata/title, tagging, protection,
    language, forms, bookmarks, and empty-text. Pike errors (corrupted files,
    password-protected files that cannot be opened, unexpected value errors)
    are caught and recorded in the result rather than raised. Calls
    :func:`finalize_result` before returning.

    Args:
        file_name: Path to the PDF file to analyse.
        site: Optional site identifier string passed through to
              :func:`init_result`.
        debug: Reserved for future use; currently has no effect.

    Returns:
        A fully populated result dict (see ``OUTPUT_FIELDS``) with all
        accessibility test outcomes. On a pikepdf error, ``BrokenFile`` is
        set to ``True``, ``Accessible`` to ``None``, and the error message
        appended to ``_log``.
    """
    result = init_result(file_name, site)

    try:
        pdf = Pdf.open(file_name)
        result["PDFVersion"] = pdf.pdf_version
        result["Pages"] = len(pdf.pages)

        check_metadata_and_title(pdf, result)
        check_tagging(pdf, result)

        structure_items = []
        if result.get("StructTreeRootPresent") is True:
            structure_items = load_structure_items(pdf)

        image_info = detect_image_objects(pdf)

        target_mcids_by_page = collect_empty_alt_figure_mcids(structure_items)
        image_backed_mcids = detect_image_backed_mcids(
            pdf,
            target_mcids_by_page=target_mcids_by_page,
        )

        check_tagged_content(pdf, result)
        check_protection(pdf, result)
        check_language(pdf, result)
        check_forms(pdf, result)
        check_bookmarks(pdf, result)
        check_empty_text(pdf, result)

        check_figures(
            structure_items,
            result,
            image_info=image_info,
            image_backed_mcids=image_backed_mcids,
        )
        check_nested_alt_text(structure_items, result)
        check_hides_annotation(structure_items, result)
        check_headings(structure_items, result)
        check_lists(structure_items, result)
        check_tables(structure_items, result)
        check_form_fields(pdf, structure_items, result)
        check_annotations(pdf, structure_items, result)

    except pikepdf.PasswordError as err:
        result["BrokenFile"] = True
        result["Accessible"] = None
        result["_log"] += "Password protected file: {0}".format(err)
    except pikepdf.PdfError as err:
        result["BrokenFile"] = True
        result["Accessible"] = None
        result["_log"] += "PdfError: {0}".format(err)
    except ValueError as err:
        result["BrokenFile"] = True
        result["Accessible"] = None
        result["_log"] += "ValueError: {0}".format(err)

    finalize_result(result)
    return result
