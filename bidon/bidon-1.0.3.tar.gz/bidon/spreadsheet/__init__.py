"""The spreadsheet package contains a standard model for Spreadsheets, and wrappers around several
common formats conforming to the standard model.
"""

from .base import Cell, CellMode
from .csv import CSVWorkbook
