from fcs.utils import add_freecad_to_path
add_freecad_to_path()

from pathlib import Path
from os.path import exists

import FreeCAD

from fcs.constants import *
from fcs.spreadsheet import Spreadsheet


def extract_params(file_path: str) -> dict:

    params = {
        SPREADSHEET_COL_NAME: [],
        SPREADSHEET_COL_VAL:  [],
        SPREADSHEET_COL_DESC: []
    }

    assert exists(file_path), f"Couldn't find file '{file_path}'"
    assert file_path.split(".")[-1] == FREECAD_EXTENSION, f"Invalid file '{file_path}'"

    # Open file
    print(f"Opening {file_path}")
    doc = FreeCAD.open(file_path)

    # Get spreadsheet
    sheet = Spreadsheet(doc=doc)

    for row in sheet.rows:
        if row == sheet.title_row:
            continue

        name, value, desc = sheet.get_row_info(row)
        params[SPREADSHEET_COL_NAME].append(name)
        params[SPREADSHEET_COL_VAL].append(value)
        params[SPREADSHEET_COL_DESC].append(desc)

    return params


if __name__ == "__main__":

    script_dir = Path(__file__).resolve().parent
    demo_file = str(Path(f"{script_dir}/../../examples/part.FCStd").resolve())

    params = extract_params(demo_file)

    from pandas import DataFrame as df
    print(df.from_dict(params))