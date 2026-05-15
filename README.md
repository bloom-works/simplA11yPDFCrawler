# simplA11yPDFCrawler

simplA11yPDFCrawler is a PDF accessibility crawler and scanner supporting the simplified accessibility monitoring method as described in the [commission implementing decision EU 2018/1524](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32018D1524&from=EN). It is used by [SIP (Information and Press Service)](https://sip.gouvernement.lu/en.html) in Luxembourg to monitor the websites of public sector bodies.

The tool can be used in two ways:

1. **Crawler workflow**: crawl a list of websites, download documents, analyze all PDFs, and generate CSV/JSON output.
2. **Single-PDF workflow**: run the PDF checker directly against an individual PDF and return either raw JSON or a structured accessibility report.

The generated files can be used by [simplA11yGenReport](https://github.com/accessibility-luxembourg/simplA11yGenReport) to give an overview of the state of document accessibility on controlled websites.

Most of the [accessibility reports (in french)](https://data.public.lu/fr/datasets/audits-simplifies-de-laccessibilite-numerique-2020-2021/) published by SIP on [data.public.lu](https://data.public.lu) have been generated using [simplA11yGenReport](https://github.com/accessibility-luxembourg/simplA11yGenReport) and data coming from this tool.

## PDF accessibility tests

The checker runs document-level tests, page-content tagging tests, structure-tree tests, annotation tests, form tests, figure/alt-text tests, heading tests, list tests and table tests.

| Category       | Test                    | Description                                                                                                                                                                                                                                                                                               |
| -------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Document       | `EmptyTextTest`         | Checks whether the file appears to contain real text or only images. This can detect scanned/image-only PDFs without OCR.                                                                                                                                                                                 |
| Document       | `TaggedTest`            | Checks whether the document has a PDF structure tree and is marked as tagged.                                                                                                                                                                                                                             |
| Page Content   | `TaggedContentTest`     | Checks whether meaningful page content is associated with document structure by an `/MCID`, or marked as an artifact. Meaningful untagged text and untagged image XObjects fail; whitespace-only untagged text warns. Recursively inspects content inside Form XObjects.                                  |
| Document       | `ProtectedTest`         | Checks whether document permissions block access by assistive technologies.                                                                                                                                                                                                                               |
| Document       | `TitleTest`             | Checks whether the PDF has a title and whether the title is configured to display in the PDF reader title bar.                                                                                                                                                                                            |
| Document       | `LanguageTest`          | Checks whether the PDF has a valid default language.                                                                                                                                                                                                                                                      |
| Document       | `BookmarksTest`         | Checks whether PDFs longer than 20 pages have bookmarks.                                                                                                                                                                                                                                                  |
| Document       | `hasXmp`                | Checks whether XMP metadata is present.                                                                                                                                                                                                                                                                   |
| Document       | `Exempt`                | Estimates whether the document is outside the legal scope based on its creation/modification date.                                                                                                                                                                                                        |
| Forms          | `FormsTest`             | Checks whether interactive form fields have descriptions.                                                                                                                                                                                                                                                 |
| Forms          | `TaggedFormFieldsTest`  | Checks whether each interactive form field widget is connected to the PDF structure tree through `/StructParent`, `/ParentTree` and a matching `/OBJR` reference on a `Form` structure element. Widget page association may be resolved through either the widget `/P` entry or the page `/Annots` array. |
| Forms          | `Form`                  | Detects whether the PDF contains AcroForm fields.                                                                                                                                                                                                                                                         |
| Forms          | `xfa`                   | Detects dynamic XFA forms.                                                                                                                                                                                                                                                                                |
| Annotations    | `TaggedAnnotationsTest` | Checks each link annotation against the structure tree using `/StructParent`, `/ParentTree` and matching `/OBJR` references. This is a structural approximation.                                                                                                                                          |
| Annotations    | annotation inventory    | Counts annotations, link annotations, widget annotations, internal links and external links.                                                                                                                                                                                                              |
| Alternate Text | `FiguresAltTextTest`    | Checks `Figure` structure elements for usable alternate text. Missing `/Alt` fails; empty `/Alt` fails unless the Figure appears to be intentionally silent inside an `Art`/layout container; `/ActualText`-only warns.                                                                                   |
| Alternate Text | `NestedAltTextTest`     | Checks for alternate text nested inside another alt-bearing structure element.                                                                                                                                                                                                                            |
| Alternate Text | `HidesAnnotationTest`   | Warns when a form annotation may be hidden by alternate text on the Form element itself or on an alt-bearing ancestor, such as a Table with `/Alt`.                                                                                                                                                       |
| Images         | image object detection  | Counts image XObjects and pages containing images. Used as a fallback when the PDF is untagged.                                                                                                                                                                                                           |
| Headings       | `HeadingsTest`          | Checks heading structure for skipped levels, plain `H` tags, first heading level and missing headings.                                                                                                                                                                                                    |
| Lists          | `ListsTest`             | Checks PDF list structure, including `L`, `LI`, `Lbl` and `LBody` relationships.                                                                                                                                                                                                                          |
| Tables         | `TablesTest`            | Checks table structure, including `TR`, `TH`, `TD`, headers and table regularity.                                                                                                                                                                                                                         |
| Tables         | row/column regularity   | Warns about uneven row lengths, including basic `RowSpan` and `ColSpan` handling.                                                                                                                                                                                                                         |

### Known limitations

This tool performs automated checks. It does not replace a full manual accessibility audit.

Some issues cannot be reliably verified from automated checks alone, including:

- logical reading order
- color contrast
- full validation of page-content-to-structure associations beyond the automated tagged-content checks, such as confirming that every `/MCID` resolves correctly through the structure tree
- multimedia accessibility
- visual validation of form labels, instructions and tab order; the checker verifies structural widget tagging and field descriptions, but does not replace manual review of form usability
- semantic quality of alternate text; the checker verifies the presence and structure of alternate text, but does not determine whether the text is meaningful or sufficient
- some untagged non-text drawing operations, such as vector paths, fills, strokes and shadings; untagged image XObjects are detected, but other painted graphics still require manual review

## Installation

### Development install

Clone the repository and install the Python package with Poetry:

```bash
git clone https://github.com/bloom-works/simplA11yPDFCrawler.git
cd simplA11yPDFCrawler

poetry install
npm install

mkdir -p crawled_files out
chmod a+x *.sh
```

This installs the `simpla11ypdf` Python package and exposes the `simpla11ypdf` command-line tool.

Check that the CLI is available:

```bash
poetry run simpla11ypdf --help
```

On macOS, the `timeout` command may not be available. Install GNU coreutils if needed:

```bash
brew install coreutils
```

### Install from GitHub

If you want to use the scanner as a package from another project, install it from a Git tag:

```bash
pip install "simpla11ypdf @ git+https://github.com/bloom-works/simplA11yPDFCrawler.git@v2.0.0"
```

Or with Poetry:

```toml
simpla11ypdf = { git = "https://github.com/bloom-works/simplA11yPDFCrawler.git", tag = "v2.0.0" }
```

The package can then be used from Python:

```python
from simpla11ypdf.scanner import check_file
```

## Usage: crawl and analyze websites

To crawl websites, store the list of target sites in `list-sites.txt`, one domain per line.

Example:

```text
test.public.lu
etat.public.lu
projects.accesscomputing.uw.edu
```

Then run the workflow in two steps.

### 1. Crawl documents

```bash
./crawl.sh
```

This crawls all sites listed in `list-sites.txt`. Each site is crawled for a maximum of 4 hours by default (it can be adjusted in `crawl.sh`). The resulting files will be placed in the `crawled_files` folder. This step can be quite long.

### 2. Analyze downloaded PDFs

```bash
./analyse.sh
```

This analyses the files and detects accessibility issues. The resulting files will be placed in the `out` folder.

Everytime you come back to the project and start a terminal, you have to load the virtual environment first with the following command:

```bash
source ./env/bin/activate
```

#### Output files

Running `analyse.sh` creates three files in the `out` folder.

<details>
<summary>
<strong>`out/pdfCheck.csv`</strong>
</summary>

<br>
One row per PDF. This is the main per-file scanner output.

Fields include:

| Field                              | Description                                                                                                                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Site`                             | Site/domain associated with the file.                                                                                                                                                          |
| `File`                             | PDF filename.                                                                                                                                                                                  |
| `Accessible`                       | `False` if the scanner found a failing accessibility issue.                                                                                                                                    |
| `TotallyInaccessible`              | `True` if the PDF fails critical access checks, such as being untagged and image-only, or blocking assistive technology access.                                                                |
| `BrokenFile`                       | `True` if the PDF could not be opened or parsed.                                                                                                                                               |
| `TaggedTest`                       | Whether the PDF is tagged.                                                                                                                                                                     |
| `TaggedContentTest`                | Whether meaningful page content appears to be structurally tagged or artifacted. Fails for meaningful untagged text and untagged image XObjects; warns for whitespace-only untagged text.      |
| `UntaggedContentCount`             | Number of meaningful content operations found outside artifact content and without an active `/MCID`, including text-showing operations and image XObject painting operations.                 |
| `UntaggedContentSummary`           | Summary of meaningful untagged content operations, including page, source, operator and text/image diagnostic snippet.                                                                         |
| `UntaggedWhitespaceContentCount`   | Number of whitespace-only text-showing operations found outside artifact content and without an active `/MCID`, including text inside Form XObjects.                                           |
| `UntaggedWhitespaceContentSummary` | Summary of whitespace-only text-showing operations, including page, source, operator and text snippet.                                                                                         |
| `EmptyTextTest`                    | Whether text content appears to be present.                                                                                                                                                    |
| `ProtectedTest`                    | Whether permissions allow assistive technology access.                                                                                                                                         |
| `TitleTest`                        | Whether the PDF title exists and is shown in the title bar.                                                                                                                                    |
| `LanguageTest`                     | Whether the PDF has a valid document language.                                                                                                                                                 |
| `BookmarksTest`                    | Whether a long PDF has bookmarks.                                                                                                                                                              |
| `Exempt`                           | Whether the document appears to predate the legal deadline.                                                                                                                                    |
| `Date`                             | Best available creation/modification date.                                                                                                                                                     |
| `hasTitle`                         | Whether a title is present.                                                                                                                                                                    |
| `hasDisplayDocTitle`               | Whether the Display Document Title flag is set.                                                                                                                                                |
| `hasLang`                          | Whether a document language is present.                                                                                                                                                        |
| `InvalidLang`                      | Whether the language tag is invalid.                                                                                                                                                           |
| `hasBookmarks`                     | Whether bookmarks are present.                                                                                                                                                                 |
| `hasXmp`                           | Whether XMP metadata is present.                                                                                                                                                               |
| `PDFVersion`                       | PDF version.                                                                                                                                                                                   |
| `Creator`                          | Creator software, if available.                                                                                                                                                                |
| `Producer`                         | Producer software, if available.                                                                                                                                                               |
| `Pages`                            | Page count.                                                                                                                                                                                    |
| `Form`                             | Whether AcroForm fields are present.                                                                                                                                                           |
| `xfa`                              | Whether dynamic XFA appears to be present.                                                                                                                                                     |
| `FormFieldCount`                   | Number of interactive form fields found.                                                                                                                                                       |
| `FormFieldSummary`                 | Debug-style summary of detected fields.                                                                                                                                                        |
| `FormsTest`                        | Whether form fields have descriptions.                                                                                                                                                         |
| `FieldsWithoutDescription`         | Fields missing descriptions.                                                                                                                                                                   |
| `TaggedFormFieldsTest`             | Whether each form field widget is structurally connected through `/StructParent`, `/ParentTree` and a matching `/OBJR` reference on a `Form` structure element.                                |
| `TaggedFormFieldIssues`            | Details for tagged form field failures, including fields with no widget annotation, widgets with no page association, missing `/StructParent` entries, unresolved `/ParentTree` mappings, etc. |
| `AnnotationsFound`                 | Whether annotations were found.                                                                                                                                                                |
| `AnnotationCount`                  | Total number of annotations.                                                                                                                                                                   |
| `AnnotationSubtypeCounts`          | Count of annotation subtypes.                                                                                                                                                                  |
| `LinkAnnotationCount`              | Number of link annotations.                                                                                                                                                                    |
| `WidgetAnnotationCount`            | Number of widget annotations.                                                                                                                                                                  |
| `TaggedAnnotationsTest`            | Whether each link annotation is connected to the structure tree through `/StructParent`, `/ParentTree` and a matching `/OBJR` reference.                                                       |
| `TaggedAnnotationIssues`           | Details for link annotations that are missing `/StructParent`, do not resolve through `/ParentTree`, map to an unexpected structure type, or lack a matching `/OBJR`.                          |
| `AnnotationSummary`                | Debug-style summary of detected annotations, including page, subtype, flags, rectangle, action/destination, widget state and structure parent where available.                                 |
| `LinkStructureCount`               | Number of `Link` structure elements.                                                                                                                                                           |
| `ExternalLinkAnnotationCount`      | Number of external URI link annotations.                                                                                                                                                       |
| `InternalLinkAnnotationCount`      | Number of internal destination link annotations.                                                                                                                                               |
| `AnnotationPagesWithLinks`         | Number of pages containing link annotations.                                                                                                                                                   |
| `HidesAnnotationTest`              | Whether alternate text may hide annotation content. Warns for Form annotations with alternate text directly on the Form element or on an alt-bearing ancestor.                                 |
| `HidesAnnotationIssues`            | Details for hides-annotation warnings, including Form elements with `/OBJR` children inside an ancestor with `/Alt` or `/ActualText`.                                                          |
| `ImageObjectsFound`                | Number of image XObjects found.                                                                                                                                                                |
| `PagesWithImages`                  | Number of pages containing image XObjects.                                                                                                                                                     |
| `FiguresFound`                     | Number of `Figure` structure elements.                                                                                                                                                         |
| `FiguresWithAlt`                   | Number of figures with non-empty `/Alt` text.                                                                                                                                                  |
| `FiguresWithEmptyAlt`              | Number of figures with an `/Alt` entry that is present but empty. Empty `/Alt` generally fails unless the Figure appears to be intentionally silent inside an `Art`/layout container.          |
| `FiguresWithActualTextOnly`        | Number of figures using non-empty `/ActualText` but no non-empty `/Alt`.                                                                                                                       |
| `FiguresWithoutAlt`                | Number of figures with no `/Alt` entry at all.                                                                                                                                                 |
| `FiguresAltTextTest`               | Figure alternate text result. Fails for missing `/Alt`, empty `/Alt` outside an `Art`/layout container, and empty `/ActualText`; warns for `/ActualText`-only cases.                           |
| `FiguresAltTextIssues`             | Details of figure alternate-text findings, such as empty `/Alt`, missing `/Alt`, and `/ActualText`-only cases.                                                                                 |
| `NestedAltTextTest`                | Nested alternate text result.                                                                                                                                                                  |
| `NestedAltTextIssues`              | Details of nested alternate text issues.                                                                                                                                                       |
| `HeadingsTest`                     | Heading hierarchy result.                                                                                                                                                                      |
| `HeadingCount`                     | Number of heading structure elements.                                                                                                                                                          |
| `HeadingSequence`                  | Heading sequence, such as `H1 > H2 > H3`.                                                                                                                                                      |
| `HeadingIssues`                    | Heading hierarchy issues.                                                                                                                                                                      |
| `ListsTest`                        | List structure result.                                                                                                                                                                         |
| `ListCount`                        | Number of list structure elements.                                                                                                                                                             |
| `InvalidListItemParents`           | `LI` elements with invalid parents.                                                                                                                                                            |
| `InvalidListChildren`              | Unusual or invalid direct list children.                                                                                                                                                       |
| `MalformedListNodes`               | Empty or malformed list structures.                                                                                                                                                            |
| `TablesTest`                       | Table structure result.                                                                                                                                                                        |
| `TableCount`                       | Number of table structure elements.                                                                                                                                                            |
| `InvalidTRParents`                 | `TR` elements with invalid parents.                                                                                                                                                            |
| `InvalidCellParents`               | `TH`/`TD` elements with invalid parents.                                                                                                                                                       |
| `TablesWithoutHeaders`             | Tables with no header cells.                                                                                                                                                                   |
| `IrregularTables`                  | Tables with uneven row/column structure that may require manual review.                                                                                                                        |

When `--debug` is used, additional debug fields may be included:

| Field           | Description                                            |
| --------------- | ------------------------------------------------------ |
| `_log`          | Internal log of triggered checks and diagnostic notes. |
| `fonts`         | Count of detected fonts.                               |
| `numTxtObjects` | Count of detected text-object operators.               |

</details>

<details>
<summary>
<strong>`out/distribution.csv`</strong>
</summary>

<br>

Summary of file counts per crawled site.

Example:

```csv
site,files,not-pdf
projects.accesscomputing.uw.edu,8,5
```

</details>

<details>
<summary>
<strong>`out/office-files.json`</strong>
</summary>

<br>

Aggregated site-level statistics.

Example:

```json
{
  "example.org": {
    "files": 10,
    "pdf": 4,
    "pdf-exempt": 0,
    "pdf-non-exempt": 4,
    "pdf-form": 1,
    "pdf-blocking-pb-access": 1,
    "pcent-pdf": 40,
    "pcent-form": 10,
    "pcent-pdf-blocking-pb-access": 25
  }
}
```

</details>

## Usage: analyze a single PDF

You can also run the PDF checker directly against one file without crawling a website.

### Raw JSON output

```bash
poetry run simpla11ypdf tojson path/to/file.pdf --pretty
```

With debug fields:

```bash
poetry run simpla11ypdf tojson path/to/file.pdf --debug --pretty
```

The raw JSON output returns the flat internal scanner result, including all individual fields used by the CSV output.

### PDF Accessibility Checker JSON Report

```bash
poetry run simpla11ypdf tojsonreport path/to/file.pdf --pretty
```

The structured accessibility report output groups results into report categories:

- `Summary`
- `Detailed Report`
- `PDF Metadata`

Example shape:

```json
{
  "Summary": {
    "Description": "The checker found no problems in this document.",
    "Needs manual check": 0,
    "Passed manually": 0,
    "Failed manually": 0,
    "Skipped": 0,
    "Passed": 19,
    "Warning": 0,
    "Failed": 0
  },
  "Detailed Report": {
    "Document": [],
    "Page Content": [],
    "Forms": [],
    "Alternate Text": [],
    "Tables": [],
    "Lists": [],
    "Headings": []
  },
  "PDF Metadata": {}
}
```

The structured report is intended for applications that want a more human-readable accessibility check, which matches the format of other industry-standard PDF accessibility reports.

In the default report mode, scanner warnings are reported with `"Status": "Warning"`. This is used for issues that may require manual review but are not treated as definite failures by the scanner.

#### PDF Accessibility Checker JSON Report: Compatible mode

```bash
poetry run simpla11ypdf tojsonreport path/to/file.pdf --compatible --pretty
```

Compatible mode includes additional rules that this scanner does not fully automate, but which recreates the exact data shape as other industry-standard PDF accessibility reports.

- Unsupported checks like "Tab order" and "Character encoding" are returned as `Skipped`.

- Manual checks like "Logical Reading Order" and "Color contrast" are returned as `Needs manual check`.

In compatible mode, scanner warnings are reported as `"Failed"` with `"Severity": "Warning"` when debug output is enabled. This preserves compatibility with report formats that do not have a separate warning status.

This is useful if a consuming application expects the same report categories as other industry-standard PDF accessibility reports.

### PDF structure debug output

To inspect the PDF structure tree for debugging, use the `structure` command:

```bash
poetry run simpla11ypdf structure path/to/file.pdf
```

Limit the number of structure items printed:

```bash
poetry run simpla11ypdf structure path/to/file.pdf --limit 100
```

This command is intended for debugging, which is useful during development.

## Using the scanner from Python

After installing the package, the scanner can be imported and used directly:

```python
from simpla11ypdf.scanner import check_file

result = check_file("path/to/file.pdf")
print(result["Accessible"])
print(result["TaggedTest"])
```

To produce structured report JSON from Python:

```python
from simpla11ypdf.scanner import check_file
from simpla11ypdf.report import build_json_report

result = check_file("path/to/file.pdf")
report = build_json_report(result, compatible=False)

print(report["Summary"])
```

## Project structure

The PDF scanner is split into small modules:

```text
simpla11ypdf/
  scanner.py              # Orchestrates all checks for one PDF
  constants.py            # Output field definitions
  dates.py                # Date parsing helpers
  image_detection.py      # Page-level image XObject detection
  figure_content.py       # Maps marked-content MCIDs to image-backed Figure content
  models.py               # Shared data model
  report.py               # Structured report JSON output
  structure.py            # Structure tree traversal and normalization
  text_analysis.py        # Text/font detection

  checks/
    document.py           # Check metadata, title, tagging, protection, language, bookmarks, text
    tagged_content.py     # Page content stream checks for untagged text and image XObjects
    figures.py            # Figure and alternate text checks
    headings.py           # Heading hierarchy checks
    lists.py              # List structure checks
    tables.py             # Table structure checks
    forms.py              # AcroForm, XFA and form field checks
    annotations.py        # Annotation and link checks
    alt_text.py           # Nested alt text and hides-annotation checks
```

## Tests

The project includes a pytest suite with example PDF fixtures for every PDF check.

Run tests with:

```bash
pytest
```

The tests cover:

- tagging
- tagged content / untagged page content and image XObjects
- title
- language
- bookmarks
- protection
- empty text / image-only PDFs
- figures and alternate text
- nested alternate text
- hides-annotation patterns
- annotations and links
- forms, field descriptions and tagged form field widget structure
- headings
- lists
- tables

The fixture PDFs live under:

```text
tests/fixtures/
```

Each check has targeted pass, fail, warning and not-applicable scenarios where relevant.

## License

This software is developed by the Information and press service of the luxembourgish government and licensed under the MIT license.

This software was initially developed by the [Information and press service](https://sip.gouvernement.lu/en.html) of the Luxembourgish government and licensed under the MIT license.

It was expanded upon by [Bloom Works | Public benefit company](https://www.bloomworks.digital/) with more PDF structure checks, tests, and a new JSON output mode.
