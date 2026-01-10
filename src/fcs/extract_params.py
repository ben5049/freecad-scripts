from fcs.utils import add_freecad_to_path, merge_params
add_freecad_to_path()

from os.path import exists

import FreeCAD

from fcs.constants import *
from fcs.spreadsheet import Spreadsheet
from fcs.varset import get_varset_params


def extract_params(file_path: str) -> dict:

    assert exists(file_path), f"Couldn't find file '{file_path}'"
    assert file_path.split(".")[-1] == FREECAD_EXTENSION, f"Invalid file '{file_path}'"

    # Open file
    print(f"Opening {file_path}")
    doc = FreeCAD.open(file_path)

    # Get spreadsheet, extract params
    sheet = Spreadsheet(doc=doc)
    params = sheet.extract_params()

    # Get varsets params and merge
    params = merge_params(params, get_varset_params(doc=doc))

    return params


if __name__ == "__main__":

    from pathlib import Path
    script_dir = Path(__file__).resolve().parent
    demo_file = str(Path(f"{script_dir}/../../examples/part.FCStd").resolve())

    params = extract_params(demo_file)

    from pandas import DataFrame as df
    print(df.from_dict(params))
