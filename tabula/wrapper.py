"""This module is a wrapper of tabula, which enables extract tables from PDF.

This module extract tables from PDF into pandas DataFrame. Currently, the
implementation of this module uses subprocess.

Todo:
  * Use py4j and handle multiple tables in a page

"""

import json
import os
import shlex
import subprocess

JAR_NAME = "tabula-0.9.2-jar-with-dependencies.jar"
JAR_DIR = os.path.abspath(os.path.dirname(__file__))
JAR_PATH = os.path.join(JAR_DIR, JAR_NAME)


def read_pdf(input_path, encoding='utf-8', java_options=None, options='', pages=1, guess=False, area=None,
             lattice=False, stream=False, password=None, columns=None, output_format='JSON', output_path=None,
             batch=None, silent=False):
    """Read tables in PDF.

    Args:
        input_path (str):
            File path of tareget PDF file.
        encoding (str, optional):
            Encoding type for pandas. Default is 'utf-8'
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        options (str, optional):
            Raw option string for tabula-java.
        pages (str, int, :obj:`list` of :obj:`int`, optional):
            An optional values specifying pages to extract from. It allows
            `str`,`int`, :obj:`list` of :obj:`int`.
            Example: '1-2,3', 'all' or [1,2]
        guess (bool, optional):
            Guess the portion of the page to analyze per page.
        area (:obj:`list` of :obj:`float`, optional):
            Portion of the page to analyze(top,left,bottom,right).
            Example: [269.875,12.75,790.5,561]. Default is entire page
        lattice (bool, optional):
            Force PDF to be extracted using lattice-mode extraction
            (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
        stream (bool, optional):
            Force PDF to be extracted using stream-mode extraction
            (if there are no ruling lines separating each cell)
        password (str, optional):
            Password to decrypt document. Default is empty
        silent (bool, optional):
            Suppress all stderr output.
        columns (list, optional):
            X coordinates of column boundaries.
            Example: [10.1, 20.2, 30.3]
        output_format (str, optional):
            Format for output file or extracted object. (CSV, TSV, JSON)
        batch (str, optional):
            Convert all .pdfs in the provided directory. This argument should be direcotry.
        output_path (str, optional):
            Output file path. File format of it is depends on `format`.
            Same as `--outfile` option of tabula-java.

    Returns:
        Extracted pandas DataFrame or list.
    """

    if java_options is None:
        java_options = []

    elif isinstance(java_options, str):
        java_options = [java_options]

    options = build_options(options=options, pages=pages, guess=guess, area=area, lattice=lattice, stream=stream,
                            password=password, columns=columns, output_format=output_format, output_path=output_path,
                            batch=batch, silent=False)

    args = ["java"] + java_options + ["-jar", JAR_PATH] + options + [input_path]
    output = subprocess.check_output(args)
    if len(output) == 0:
        return

    if output_path:
        return
    if output_format and output_format.upper() != 'JSON':
        return output.decode(encoding)
    return json.loads(output.decode(encoding))


def build_options(options='', pages=1, guess=False, area=None, lattice=False, stream=False,
                  password=None, columns=None, output_format='JSON', output_path=None, batch=None, silent=False):
    """Build options for tabula-java

    Args:
        options (str, optional):
            Raw option string for tabula-java.
        pages (str, int, :obj:`list` of :obj:`int`, optional):
            An optional values specifying pages to extract from. It allows
            `str`,`int`, :obj:`list` of :obj:`int`.
            Example: '1-2,3', 'all' or [1,2]
        guess (bool, optional):
            Guess the portion of the page to analyze per page.
        area (:obj:`list` of :obj:`float`, optional):
            Portion of the page to analyze(top,left,bottom,right).
            Example: [269.875,12.75,790.5,561]. Default is entire page
        lattice (bool, optional):
            Force PDF to be extracted using lattice-mode extraction
            (if there are ruling lines separating each cell, as in a PDF of an Excel spreadsheet)
        stream (bool, optional):
            Force PDF to be extracted using stream-mode extraction
            (if there are no ruling lines separating each cell)
        password (str, optional):
            Password to decrypt document. Default is empty
        silent (bool, optional):
            Suppress all stderr output.
        columns (list, optional):
            X coordinates of column boundaries.
            Example: [10.1, 20.2, 30.3]
        output_format (str, optional):
            Format for output file or extracted object. (CSV, TSV, JSON)
        batch (str, optional):
            Convert all .pdfs in the provided directory. This argument should be direcotry.
        output_path (str, optional):
            Output file path. File format of it is depends on `format`.
            Same as `--outfile` option of tabula-java.

    Returns:
        Built dictionary of options
    """
    __options = []
    # handle options described in string for backward compatibility
    __options += shlex.split(options)

    # parse options
    if pages:
        __pages = pages
        if isinstance(pages, int):
            __pages = str(pages)
        elif type(pages) in [list, tuple]:
            __pages = ",".join(map(str, pages))

        __options += ["--pages", __pages]

    if guess:
        __options.append("--guess")

    if area:
        __area = area
        if type(area) in [list, tuple]:
            __area = ",".join(map(str, area))

        __options += ["--area", __area]

    if output_format:
        if output_format.upper() not in ('JSON', 'TSV', 'CSV'):
            raise ValueError('Unknown output format, expected JSON, TSV or CSV')
        __options += ["--format", output_format]

    if output_path:
        __options += ["--outfile", output_path]

    if lattice:
        __options.append("--lattice")

    if stream:
        __options.append("--stream")

    if columns:
        __columns = ",".join(map(str, columns))
        __options += ["--columns", __columns]

    if password:
        __options += ["--password", password]

    if batch:
        __options += ["--batch", batch]

    if silent:
        __options.append("--silent")

    return __options
