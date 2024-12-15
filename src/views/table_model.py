from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor, QFont
import pandas as pd


class CSVTableModel(QAbstractTableModel):
    """
    A table model for displaying and editing CSV data.

    This class represents a table model for displaying and editing CSV data. It
    is based on the QAbstractTableModel class and provides the necessary methods
    for displaying and editing the data.

    The data is stored in a Pandas DataFrame and can be accessed and modified
    using the methods of this class.

    The model also keeps track of which cells have been modified, which can be
    used to save only the modified cells to a file.
    """

    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
        self._modified_cells = set()
        self.NULL_COLOR = QColor(128, 128, 128)
        self.header_font = QFont()
        self.header_font.setBold(True)

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data stored under the given role for the item referred to by the index.

        Args:
            index (QModelIndex): The index of the item.
            role (int): The role of the item.

        Returns:
            Any: The data stored for the item.
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if pd.isna(value) or value == "" or value is None:
                return "NULL"
            return str(value)

        if role == Qt.ForegroundRole:
            value = self._data.iloc[index.row(), index.column()]
            if pd.isna(value) or value == "" or value is None:
                return self.NULL_COLOR
            return None

        if (
            role == Qt.BackgroundRole
            and (index.row(), index.column()) in self._modified_cells
        ):
            return Qt.yellow

        return None

    def setData(self, index, value, role=Qt.EditRole):
        """
        Sets the role data for the item at index to value.

        Args:
            index (QModelIndex): The index of the item.
            value (Any): The value to set.
            role (int): The role for which to set the data.

        Returns:
            bool: True if successful; otherwise returns False.
        """
        if role == Qt.EditRole:
            try:
                if value.strip().upper() == "NULL" or not value.strip():
                    value = None
                self._data.iloc[index.row(), index.column()] = value
                self._modified_cells.add((index.row(), index.column()))
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                print(f"Error setting data: {e}")
                return False
        return False

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the number of rows for the children of the given index.

        Args:
            parent (QModelIndex): The parent index.

        Returns:
            int: The number of rows.
        """
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        """
        Returns the number of columns for the children of the given index.

        Args:
            parent (QModelIndex): The parent index.

        Returns:
            int: The number of columns.
        """
        if parent.isValid():
            return 0
        return len(self._data.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Returns the data stored for the item.

        Args:
            section (int): The section of the header.
            orientation (Qt.Orientation): The orientation of the header.
            role (int): The role for which to get the data.

        Returns:
            Any: The data stored for the item.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        elif role == Qt.FontRole:
            return self.header_font
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def update_data(self, data):
        """
        Updates the data of the model.

        Args:
            data (pandas.DataFrame): The new data to update the model with.
        """
        self.beginResetModel()
        self._data = data
        self._modified_cells.clear()
        self.endResetModel()

    def get_data(self):
        return self._data

    def remove_row(self, row):
        """
        Removes a row from the data.

        Args:
            row (int): The index of the row to remove.

        Returns:
            bool: True if successful; otherwise returns False.
        """
        try:
            if 0 <= row < len(self._data):
                self.beginRemoveRows(QModelIndex(), row, row)
                self._data.drop(self._data.index[row], inplace=True)
                self._data.reset_index(drop=True, inplace=True)
                self.endRemoveRows()
                return True
            return False
        except Exception as e:
            print(f"Error removing row: {e}")
            return False

    def remove_column(self, column_index):
        """
        Removes a column from the data.

        Args:
            column_index (int): The index of the column to remove.

        Returns:
            bool: True if successful; otherwise returns False.
        """
        try:
            if 0 <= column_index < len(self._data.columns):
                self.beginResetModel()
                self._data.drop(self._data.columns[column_index], axis=1, inplace=True)
                self.endResetModel()
                return True
            return False
        except Exception as e:
            print(f"Error removing column: {e}")
            return False

    def add_row(self, after_row_index):
        """
        Adds a new empty row after the specified row index.

        Args:
            after_row_index (int): The index after which to insert the new row.
        """
        try:
            # Create a new empty row with the same columns as the DataFrame
            new_row = pd.DataFrame(
                [[None] * len(self._data.columns)], columns=self._data.columns
            )

            # Insert the new row after the specified index
            self._data = pd.concat(
                [
                    self._data.iloc[: after_row_index + 1],
                    new_row,
                    self._data.iloc[after_row_index + 1 :],
                ]
            ).reset_index(drop=True)

            # Notify views that the model has changed
            self.layoutChanged.emit()
            return True
        except Exception as e:
            print(f"Error adding row: {e}")
            return False
