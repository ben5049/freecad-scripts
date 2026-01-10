from os import name
from os.path import join, exists
from sys import path

from fcs.constants import *


def add_freecad_to_path():

    freecad_python_library = ""
    freecad_path = ""

    os_name = name

    # Windows
    if os_name == "nt":
        freecad_python_library = "FreeCAD.pyd"
        freecad_path = "C:\\Program Files\\FreeCAD 1.0\\bin"

    # Linux
    elif os_name == "posix":
        freecad_python_library = "FreeCAD.so"
        raise NotImplementedError("Linux not yet supported")

    # Unknown
    else:
        raise NotImplementedError(f"Unsupported OS '{os_name}'")

    assert exists(join(freecad_path, freecad_python_library)), f"Couldn't find '{freecad_python_library}' in '{freecad_path}'"
    path.append(freecad_path)

def print_warning(text: str = "", **kwargs):
    print(f"\033[33mWARNING: {text}\033[0m", **kwargs)

def pint_to_freecad(unit: str):

    unit = str(unit)

    if unit == "millimeter":
        return "mm"
    if unit == "degree":
        return "deg"
    else:
        print_warning(f"Couldn't convert unit '{unit}', returning unconverted")

    return unit

def merge_params(params1, params2):

    assert params1 is not None
    assert params2 is not None

    to_return = params1.copy()

    # Add optional descriptions column
    if PARAM_DESC not in params1:
        to_return[PARAM_DESC] = [""] * len(params1[PARAM_NAME])

    names2 = params2.get(PARAM_NAME)
    vals2  = params2.get(PARAM_VAL)
    descs2 = params2.get(PARAM_DESC)

    # Add optional descriptions column
    if descs2 is None:
        descs2 = [""] * len(names2)

    for name, val, desc in zip(names2, vals2, descs2):
        if name not in params1[PARAM_NAME]:
            to_return[PARAM_NAME].append(name)
            to_return[PARAM_VAL].append(val)
            to_return[PARAM_DESC].append(desc)

    return to_return