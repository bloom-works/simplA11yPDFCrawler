import csv
import json
import os

import typer

from pikepdf import Pdf

from scanner.constants import OUTPUT_FIELDS
from scanner.report import build_json_report
from scanner.scanner import check_file, format_structure_debug

DEBUG_ONLY_FIELDS = ["_log", "fonts", "numTxtObjects"]


def non_debug_output_fields() -> list[str]:
    return [field for field in OUTPUT_FIELDS if field not in DEBUG_ONLY_FIELDS]


def debug_output_fields() -> list[str]:
    return OUTPUT_FIELDS + [
        field for field in DEBUG_ONLY_FIELDS if field not in OUTPUT_FIELDS
    ]


def remove_debug_fields(result: dict) -> None:
    for field in DEBUG_ONLY_FIELDS:
        result.pop(field, None)


def print_json(data: dict, pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(data, indent=4))
    else:
        print(json.dumps(data))


app = typer.Typer()


@app.command(name="tocsv")
def to_csv(
    site: str,
    inputfile: str,
    outputfile: str = "./out/pdfCheck.csv",
    debug: bool = False,
):
    result = check_file(inputfile, site, debug=debug)

    if debug:
        out_fields = debug_output_fields()
    else:
        remove_debug_fields(result)
        out_fields = non_debug_output_fields()

    csv_exists = os.path.exists(outputfile)

    with open(outputfile, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        if not csv_exists:
            writer.writeheader()
        writer.writerow(result)


@app.command(name="tojson")
def to_json(
    inputfile: str,
    debug: bool = False,
    pretty: bool = False,
):
    result = check_file(inputfile, debug=debug)

    if not debug:
        remove_debug_fields(result)

    print_json(result, pretty=pretty)


@app.command(name="tojsonreport")
def to_json_report(
    inputfile: str,
    debug: bool = False,
    pretty: bool = False,
    compatible: bool = False,
):
    result = check_file(inputfile, debug=debug)

    report = build_json_report(
        result,
        compatible=compatible,
        debug=debug,
    )

    print_json(report, pretty=pretty)


@app.command(name="structure")
def structure(
    inputfile: str,
    limit: int = 50,
):
    pdf = Pdf.open(inputfile)
    print(format_structure_debug(pdf, limit=limit))


def main() -> None:
    app()
