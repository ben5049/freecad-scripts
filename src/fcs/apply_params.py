from fcs.utils import add_freecad_to_path, print_warning
add_freecad_to_path()

from os.path import exists

import FreeCAD

from fcs.constants import *
from fcs.spreadsheet import Spreadsheet
from fcs.extract_params import extract_params_from_spreadsheet


def apply_params(file_path: str, params: dict):

    assert SPREADSHEET_COL_NAME in params
    assert SPREADSHEET_COL_VAL in params
    assert SPREADSHEET_COL_DESC in params

    assert exists(file_path), f"Couldn't find file '{file_path}'"
    assert file_path.split(".")[-1] == FREECAD_EXTENSION, f"Invalid file '{file_path}'"

    # Open file
    print(f"Opening {file_path}")
    doc = FreeCAD.open(file_path)

    # Get spreadsheet
    sheet = Spreadsheet(doc=doc)

    # Get old params to check if any will be deleted
    old_params = extract_params_from_spreadsheet(sheet)
    for name, val, desc in zip(old_params[SPREADSHEET_COL_NAME], old_params[SPREADSHEET_COL_VAL], old_params[SPREADSHEET_COL_DESC]):
        if name not in params[SPREADSHEET_COL_NAME]:
            print_warning(f"Parameter will be deleted: name = '{name}', val = {val}, desc = '{desc}'")

    # Apply new parameters
    apply_params_to_spreadsheet(sheet, params)

    # Recompute the model and save changes
    doc.recompute()
    doc.save()

def apply_params_to_spreadsheet(sheet: Spreadsheet, params: dict):

    # Clear the sheet before writing
    sheet.reset()

    # Write the params
    for name, val, desc in zip(params[SPREADSHEET_COL_NAME], params[SPREADSHEET_COL_VAL], params[SPREADSHEET_COL_DESC]):
        sheet.write_row(name=name, val=val, desc=desc)

    # Update
    sheet.recompute()


if __name__ == "__main__":

    from pathlib import Path
    script_dir = Path(__file__).resolve().parent
    demo_file = str(Path(f"{script_dir}/../../examples/part.FCStd").resolve())

    from fcs.extract_params import extract_params
    params = extract_params(demo_file)

    from pint import UnitRegistry, Quantity
    ureg = UnitRegistry()
    params[SPREADSHEET_COL_NAME].append("test")
    params[SPREADSHEET_COL_VAL].append(78 * ureg("mm"))
    params[SPREADSHEET_COL_DESC].append("")

    apply_params(demo_file, params)
