from fcs.utils import add_freecad_to_path, print_warning, merge_params
add_freecad_to_path()

from os.path import exists

import FreeCAD

from fcs.constants import *
from fcs.spreadsheet import Spreadsheet
from fcs.varset import get_varset_params, create_varsets_from_params, remove_all_varsets


def apply_params(file_path: str, params: dict, save_as: str = None):

    assert SPREADSHEET_COL_NAME in params
    assert SPREADSHEET_COL_VAL in params
    assert SPREADSHEET_COL_DESC in params

    assert exists(file_path), f"Couldn't find file '{file_path}'"
    assert file_path.split(".")[-1] == FREECAD_EXTENSION, f"Invalid file '{file_path}'"
    assert save_as is None or exists(save_as)
    assert save_as is None or save_as.split(".")[-1] == FREECAD_EXTENSION, f"Invalid file '{save_as}'"

    # Open file
    print(f"Opening {file_path}")
    doc = FreeCAD.open(file_path)

    # Get spreadsheet
    sheet = Spreadsheet(doc=doc)

    # Get old params to check if any will be deleted
    old_params = merge_params(
        sheet.extract_params(),
        get_varset_params(doc=doc)
    )
    for name, val, desc in zip(old_params[SPREADSHEET_COL_NAME], old_params[SPREADSHEET_COL_VAL], old_params[SPREADSHEET_COL_DESC]):
        if name not in params[SPREADSHEET_COL_NAME]:
            print_warning(f"Parameter will be deleted: name = '{name}', val = {val}, desc = '{desc}'")

    # Apply new parameters
    sheet.apply_params(params=params)
    remove_all_varsets(doc=doc)
    create_varsets_from_params(doc=doc, params=params, spreadsheet=sheet.name)

    # Recompute the model and save changes
    print("Recomputing and saving changes")
    doc.recompute()
    if save_as is None:
        doc.save()
    else:
        doc.saveAs(save_as)


if __name__ == "__main__":

    from pathlib import Path
    script_dir = Path(__file__).resolve().parent
    demo_in_file = str(Path(f"{script_dir}/../../examples/part.FCStd").resolve())
    demo_out_file = str(Path(f"{script_dir}/../../examples/part_new.FCStd").resolve())

    from fcs.extract_params import extract_params
    params = extract_params(demo_in_file)

    from pint import UnitRegistry
    ureg = UnitRegistry()
    params[SPREADSHEET_COL_NAME].append("test")
    params[SPREADSHEET_COL_VAL].append(78 * ureg("mm"))
    params[SPREADSHEET_COL_DESC].append("")

    apply_params(demo_in_file, params, demo_out_file)
