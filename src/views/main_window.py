from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QDesktopWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from qfluentwidgets import (
    SearchLineEdit,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    FluentIcon,
    PushButton,
    RoundMenu,
    Action,
    TableWidget,
)
from qfluentwidgets import setTheme, Theme

import pandas as pd


class MainWindow(FluentWindow):
    """This class represents the main window of the application
    . It contains a data table,
    buttons for basic operations, and a search bar for filtering the data.

    Attributes:
        main_widget (QWidget): The main widget of the application.
        main_layout (QVBoxLayout): The main layout of the application.
        table_view (TableWidget): The table widget for displaying the data.
        search_bar (SearchLineEdit): The search bar for filtering the data.
        button_container (QWidget): The container for the buttons.
        button_layout (QHBoxLayout): The layout for the buttons.
        dark_theme (bool): Whether the dark theme is enabled.
        current_file (str): The path of the currently loaded file.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern CSV Viewer")
        self.resize(1700, 900)
        self.center_window()
        self.setWindowIcon(QIcon("assets/icons/icon.png"))

        # Create main widget
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainInterface")
        self.main_layout = QVBoxLayout(self.main_widget)

        # Initialize UI components
        self.setup_ui()
        self.setup_buttons()
        self.setup_connections()

        # Data handling
        self.current_file = None

        # Set initial theme
        self.dark_theme = False
        setTheme(Theme.LIGHT)

    def center_window(self):
        """
        Center the window on the screen.

        This method gets the geometry of the screen and calculates the
        position of the window so that it is centered on the screen.
        """
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def setup_ui(self):
        """
        Setup the main window UI.

        This method is responsible for creating and setting
        up all UI components
        such as the button container, search bar and table view.
        """
        # Button container
        self.button_container = QWidget(self.main_widget)
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.button_container)

        # Search bar
        self.search_bar = SearchLineEdit(self.main_widget)
        self.search_bar.setPlaceholderText("Search in data...")
        self.main_layout.addWidget(self.search_bar)

        # Table view with modern design
        self.table_view = TableWidget(self.main_widget)
        self.table_view.setBorderVisible(True)
        self.table_view.setBorderRadius(8)
        self.table_view.setWordWrap(False)
        self.table_view.verticalHeader().hide()

        # Set context menu policies
        self.table_view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.horizontalHeader().customContextMenuRequested.connect(
            self.show_header_context_menu
        )
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_rows_context_menu)

        self.main_layout.addWidget(self.table_view)

        # Add main widget to window
        self.addSubInterface(self.main_widget, FluentIcon.HOME, "CSV Viewer")
        self.navigationInterface.setCurrentItem("mainInterface")

    def create_null_item(self):
        """
        Creates a table item with NULL text and proper styling.

        Returns:
            QTableWidgetItem: A styled NULL table item
        """
        item = QTableWidgetItem("NULL")
        item.setForeground(QColor(169, 169, 169))  # Dark gray color
        return item

    def update_table_data(self, df):
        """
        Updates the table with data from a pandas DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data to display
        """
        if df is None:
            return

        # Set table dimensions
        self.table_view.setRowCount(len(df))
        self.table_view.setColumnCount(len(df.columns))

        # Set headers
        self.table_view.setHorizontalHeaderLabels(df.columns)

        # Fill table with data
        for i in range(len(df)):
            for j in range(len(df.columns)):
                value = df.iloc[i, j]
                # Convert value to string, handle None/NaN
                if pd.isna(value) or value is None:
                    self.table_view.setItem(i, j, self.create_null_item())
                else:
                    self.table_view.setItem(i, j, QTableWidgetItem(str(value)))

    def open_file(self):
        """
        Opens a CSV file.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            try:
                # Load CSV without using first column as index
                df = pd.read_csv(file_name)
                self.current_file = file_name
                self.update_table_data(df)
                self.show_info_message(f"File loaded: {file_name}")
            except Exception as e:
                self.show_error_message(f"Error opening file: {str(e)}")

    def save_file(self):
        """
        Saves the current file.
        """
        if self.current_file:
            try:
                # Get data from table
                df = self.get_table_data()
                # Save without indices
                df.to_csv(self.current_file, index=False)
                self.show_info_message("File saved successfully")
            except Exception as e:
                self.show_error_message(f"Error saving file: {str(e)}")

    def get_table_data(self):
        """
        Gets the current table data as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The current table data
        """
        rows = self.table_view.rowCount()
        cols = self.table_view.columnCount()
        headers = [self.table_view.horizontalHeaderItem(i).text() for i in range(cols)]

        # Create empty DataFrame
        df = pd.DataFrame(columns=headers)

        # Fill DataFrame with table data
        for i in range(rows):
            row_data = []
            for j in range(cols):
                item = self.table_view.item(i, j)
                if item is None or item.text() == "NULL":
                    row_data.append(None)
                else:
                    row_data.append(item.text())
            df.loc[i] = row_data

        return df

    def show_header_context_menu(self, position):
        """
        Shows a context menu for the table header at the given position.
        The context menu is used to remove columns from the table.

        Args:
            position (QPoint): Point where the context menu should be shown.
        """
        column_index = self.table_view.horizontalHeader().logicalIndexAt(position)
        if column_index < 0:
            return

        # Get column name
        column_name = self.table_view.horizontalHeaderItem(column_index).text()

        # Create rounded context menu
        menu = RoundMenu(parent=self)

        # Action to delete column
        menu.addAction(
            Action(
                FluentIcon.DELETE,
                f"Delete Column '{column_name}'",
                triggered=lambda: self.delete_column(column_index),
            )
        )

        # Show menu at cursor position
        menu.exec_(self.table_view.horizontalHeader().viewport().mapToGlobal(position))

    def show_rows_context_menu(self, position):
        """
        Shows a context menu for the rows at the given position.
        The menu is used to add or remove rows from the table.

        Args:
            position (QPoint): Point where the context menu should be shown.
        """
        # Create rounded context menu
        menu = RoundMenu(parent=self)

        # Get selected rows
        selected_rows = set(item.row() for item in self.table_view.selectedItems())

        # Action to add new row
        menu.addAction(
            Action(
                FluentIcon.ADD,
                "Add New Row",
                triggered=lambda: self.add_row(
                    max(selected_rows)
                    if selected_rows
                    else self.table_view.rowCount() - 1
                ),
            )
        )

        if selected_rows:
            # Add separator
            menu.addSeparator()

            # Action to delete rows
            menu.addAction(
                Action(
                    FluentIcon.DELETE,
                    f"Delete {len(selected_rows)} Selected Row(s)",
                    triggered=self.delete_selected_rows,
                )
            )

        # Show menu at cursor position
        menu.exec_(self.table_view.viewport().mapToGlobal(position))

    def delete_selected_rows(self):
        """
        Deletes the selected rows from the table.
        """
        selected_rows = sorted(
            set(item.row() for item in self.table_view.selectedItems()), reverse=True
        )
        if not selected_rows:
            return

        try:
            for row in selected_rows:
                self.table_view.removeRow(row)
            self.show_info_message(f"Deleted {len(selected_rows)} row(s)")
        except Exception as e:
            self.show_error_message(f"Error deleting row(s): {str(e)}")

    def delete_column(self, column_index):
        """
        Deletes a column from the table.

        Args:
            column_index (int): The index of the column to delete.
        """
        try:
            self.table_view.removeColumn(column_index)
            self.show_info_message("Column deleted successfully")
        except Exception as e:
            self.show_error_message(f"Error deleting column: {str(e)}")

    def setup_buttons(self):
        """
        Sets up the buttons in the button container.

        This method creates the buttons for opening and saving files, and adds
        them to the button container. It also connects the buttons to their
        respective slots.
        """
        # File actions
        open_button = PushButton("Open", self.button_container)
        open_button.setIcon(FluentIcon.FOLDER)
        open_button.clicked.connect(self.open_file)
        self.button_layout.addWidget(open_button)

        save_button = PushButton("Save", self.button_container)
        save_button.setIcon(FluentIcon.SAVE)
        save_button.clicked.connect(self.save_file)
        self.button_layout.addWidget(save_button)

        save_as_button = PushButton("Save As", self.button_container)
        save_as_button.setIcon(FluentIcon.SAVE)
        save_as_button.clicked.connect(self.save_file_as)
        self.button_layout.addWidget(save_as_button)

        # Add spacer
        self.button_layout.addStretch()

        # View actions
        theme_button = PushButton("Toggle Theme", self.button_container)
        theme_button.setIcon(FluentIcon.BRUSH)
        theme_button.clicked.connect(self.toggle_theme)
        self.button_layout.addWidget(theme_button)

    def setup_connections(self):
        """
        Sets up the connections between the UI components.

        This method connects the search bar to the search slot and the table
        view to the show context menu slot.
        """
        self.search_bar.textChanged.connect(self.search_data)

    def save_file_as(self):
        """
        Saves the current file with a new name.
        """
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            try:
                df = self.get_table_data()
                df.to_csv(file_name, index=False)
                self.current_file = file_name
                self.show_info_message("File saved successfully")
            except Exception as e:
                self.show_error_message(f"Error saving file: {str(e)}")

    def toggle_theme(self):
        """
        Toggles the application theme between light and dark.

        This method toggles the application theme between light and dark by
        calling the `setTheme` function from the `qfluentwidgets` module with
        the correct theme.
        """
        self.dark_theme = not self.dark_theme
        setTheme(Theme.DARK if self.dark_theme else Theme.LIGHT)

    def search_data(self, text):
        """
        Searches for the given text in the data and highlights matches.

        This method searches for the given text in all columns of the data,
        shows/hides rows accordingly, and highlights matching text.
        The search is case-insensitive.
        """
        search_text = text.strip().lower()

        # Reset all cell backgrounds and show all rows
        for row in range(self.table_view.rowCount()):
            self.table_view.setRowHidden(row, False)
            for col in range(self.table_view.columnCount()):
                item = self.table_view.item(row, col)
                if item:
                    item.setBackground(Qt.transparent)

        if not search_text:
            return

        # Search and highlight matches
        for row in range(self.table_view.rowCount()):
            row_matches = False
            for col in range(self.table_view.columnCount()):
                item = self.table_view.item(row, col)
                if item:
                    cell_text = item.text().lower()
                    if search_text in cell_text:
                        row_matches = True
                        # Create new item with same text but highlighted
                        new_item = QTableWidgetItem(item.text())
                        new_item.setBackground(
                            QColor(255, 255, 0, 100)
                        )  # Semi-transparent yellow
                        self.table_view.setItem(row, col, new_item)

            # Hide rows that don't match
            if not row_matches:
                self.table_view.setRowHidden(row, True)

    def show_error_message(self, message):
        """
        Shows an error message using an info bar.

        This method shows an error message using an info bar with the given
        message. The info bar is shown at the top of the window and is
        closable. The duration of the info bar is set to 3000 milliseconds.

        Args:
            message (str): The error message to show.
        """
        InfoBar.error(
            title="Error",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def show_info_message(self, message):
        """
        Shows an info message using an info bar.

        This method shows an info message using an info bar with the given
        message. The info bar is shown at the top of the window and is
        closable. The duration of the info bar is set to 2000 milliseconds.

        Args:
            message (str): The info message to show.
        """
        InfoBar.success(
            title="Success",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

    def add_row(self, after_row_index):
        """
        Adds a new empty row after the specified row index.

        Args:
            after_row_index (int): The index after which to insert the new row.
        """
        try:
            new_row_index = after_row_index + 1
            self.table_view.insertRow(new_row_index)

            # Initialize new row with NULL values
            for col in range(self.table_view.columnCount()):
                self.table_view.setItem(new_row_index, col, self.create_null_item())

            self.show_info_message("New row added successfully")
        except Exception as e:
            self.show_error_message(f"Error adding row: {str(e)}")
