from fcs.utils import add_freecad_to_path, print_warning, pint_to_freecad
add_freecad_to_path()

from os.path import exists
from FreeCAD import Units

from pint import UnitRegistry, Quantity
ureg = UnitRegistry()

from fcs.constants import *


def split_coord(coord):
    letters = ''.join(c for c in coord if c.isalpha())
    numbers = ''.join(c for c in coord if c.isdigit())
    return letters, int(numbers)


class Spreadsheet():

    def __init__(self, doc):

        # Get the sheet containing parameters
        # https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/Spreadsheet/App/Sheet.pyi
        self._sheet = doc.getObject(SPREADSHEET_OBJ)

        # Find basic info about the sheet
        self.name_column          = None
        self.value_column         = None
        self.description_column   = None
        self.cols: list[str]      = []
        self.rows: list[int]      = []
        self.title_row            = -1

        self.get_info()

    def get_info(self):

        self.name_column        = None
        self.value_column       = None
        self.description_column = None
        self.cols               = []
        self.rows               = []
        self.title_row          = -1

        for cell_coord in self._sheet.getUsedCells():

            col, row = split_coord(cell_coord)
            cell = self._sheet.get(cell_coord)

            if cell == SPREADSHEET_COL_NAME:
                self.name_column = col
                if self.title_row == -1:
                    self.title_row = row
                else:
                    assert row == self.title_row

            elif cell == SPREADSHEET_COL_VAL:
                self.value_column = col
                if self.title_row == -1:
                    self.title_row = row
                else:
                    assert row == self.title_row

            elif cell == SPREADSHEET_COL_DESC:
                self.description_column = col
                if self.title_row == -1:
                    self.title_row = row
                else:
                    assert row == self.title_row

            if col not in self.cols:
                self.cols.append(col)
            if row not in self.rows:
                self.rows.append(row)

        assert self.name_column is not None, "No name column found"
        assert self.value_column is not None, "No value column found"
        assert self.description_column is not None, "No description column found"
        assert self.cols, "Spreadsheet is empty"
        assert self.rows, "Spreadsheet is empty"
        assert self.title_row != -1, "No title row found"

        self.rows.sort()
        assert self.title_row == min(self.rows)

    def get(self, coord: str, default = ""):

        to_return = None

        try:
            to_return = getattr(self._sheet, coord)
            # to_return = self._sheet.get(coord)
        except ValueError:
            to_return = default
        except AttributeError:
            to_return = default

        return to_return

    def read_row(self, row: int):

        name  = None
        val   = None
        desc  = None

        coord = f"{self.name_column}{row}"
        name = self.get(coord, None)

        coord = f"{self.value_column}{row}"
        val   = self.get(coord, None)
        if name is None:
            name = self._sheet.getAlias(coord)

        if val is not None:

            # Get FreeCAD type https://wiki.freecad.org/Quantity#Unit
            unit_type = val.Unit.Type

            # Convert into pint type https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
            if unit_type == "Length":
                val = val.Value * ureg.millimeter
            elif unit_type == "Angle":
                val = val.Value * ureg.degree
            else:
                raise TypeError(f"Unknown unit type '{unit_type}'")

        coord = f"{self.description_column}{row}"
        desc = self.get(coord, "")

        if name is None:
            name = ""
            print_warning(f"No name found for row with value = {val}")

        if desc is None:
            desc = ""

        return name, val, desc

    def reset(self):

        # Remove content rows. First row is always the title row
        for row in reversed(self.rows[1:]):
            self._sheet.removeRows(str(row), 1)

        # Recompute info
        self.get_info()

    def write_row(self, name: str, val: Quantity | float | int, desc: str = ""):

        assert type(name) is str, f"Type of argument 'name' must be str not {type(name)}"
        assert type(desc) is str, f"Type of argument 'desc' must be str not {type(desc)}"

        # Get the next free row index
        new_row_index = max(self.rows) + 1
        self.rows.append(new_row_index)

        # Set the name and description
        self._sheet.set(f"{self.name_column}{new_row_index}", name)
        self._sheet.set(f"{self.description_column}{new_row_index}", desc)

        # Set the value
        val_coord = f"{self.value_column}{new_row_index}"
        if isinstance(val, Quantity):
            unit = pint_to_freecad(val.units)
            self._sheet.set(val_coord, f"{val.magnitude} {unit}")
        elif (type(val) is float) or (type(val) is int):
            self._sheet.setFloatProperty(val_coord, str(val))
        else:
            raise TypeError( f"Type of argument 'val' ({val}) must be Quantity, float or int, not {type(val)}")

        # Set the alias
        self._sheet.setAlias(val_coord, name)

    def recompute(self):
        self._sheet.recompute()
