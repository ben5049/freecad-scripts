from os import name
from os.path import join, exists
from sys import path

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
