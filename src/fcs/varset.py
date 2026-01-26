from fcs.utils import add_freecad_to_path, print_warning, pint_to_freecad
add_freecad_to_path()

from os.path import exists
from FreeCAD import Units

from pint import UnitRegistry, Quantity
ureg = UnitRegistry()

from fcs.constants import *


def get_all_varsets(doc):
    return [obj for obj in doc.Objects if obj.TypeId == OBJ_VARSET]

def get_varset_params(doc) -> dict:

    params = {
        PARAM_NAME: [],
        PARAM_VAL:  [],
        PARAM_DESC: []
    }

    # Iterate through all varsets and their properties
    varsets = get_all_varsets(doc)
    for varset in varsets:
        for prop in varset.PropertiesList:

            # Skip internal properties
            if prop in VARSET_INTERNAL_PROPERTIES:
                continue

            # Skip the label
            if prop == VARSET_LABEL_PROPERTY:
                continue

            # Save the parameters
            if prop not in params[PARAM_NAME]:
                params[PARAM_NAME].append(prop)
                params[PARAM_VAL].append(getattr(varset, prop))
                params[PARAM_DESC].append(None)

    return params

def remove_all_varsets(doc):
    for varset in get_all_varsets(doc):
        doc.removeObject(varset.Name)

def create_varset(doc, label: str):
    return doc.addObject(OBJ_VARSET, label if label is not None else DEFAULT_VARSET)

def create_varsets_from_params(doc, params: dict, spreadsheet: str = None):

    names   = params.get(PARAM_NAME)
    vals    = params.get(PARAM_VAL)
    varsets = params.get(PARAM_VARSET)

    # Make sure there are varset lables
    if varsets is None:
        varsets = [DEFAULT_VARSET] * len(names)

    # Stores the label to object mappings
    varsets_mappings = {}

    # Add each property
    for name, val, varset_label in zip(names, vals, varsets):

        # Get the varset object
        if varset_label not in varsets_mappings:
            varset = create_varset(doc=doc, label=varset_label)
            varsets_mappings[varset_label] = varset
        else:
            varset = varsets_mappings.get(varset_label)

        # Add property
        varset.addProperty(PROPERTY_FLOAT, name)

        # Add value directly
        if spreadsheet is None:
            if isinstance(val, Quantity):
                setattr(varset, name, val.magnitude)
            elif (type(val) is float) or (type(val) is int):
                setattr(varset, name, val)
            else:
                raise TypeError( f"Type of argument 'val' ({val}) must be Quantity, float or int, not {type(val)}")

        # Add value with reference to a spreadsheet
        else:
            varset.setExpression(name, f"{spreadsheet}.{name}")

    # Recompute
    for varset in varsets_mappings.values():
        varset.recompute()
