from PyQt5.QtWidgets import (
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import (
    SearchLineEdit,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    FluentIcon,
    PushButton,
    RoundMenu,
    Action,
)
from qfluentwidgets import setTheme, Theme


import pandas as pd
from .table_model import CSVTableModel


class MainWindow(FluentWindow):
    """This class represents the main window of the application. It contains a data table, buttons for basic operations, and a search bar for filtering the data.

    Attributes:
        main_widget (QWidget): The main widget of the application.
        main_layout (QVBoxLayout): The main layout of the application.
        table_view (QTableView): The table view for displaying the data.
        search_bar (SearchLineEdit): The search bar for filtering the data.
        button_container (QWidget): The container for the buttons.
        button_layout (QHBoxLayout): The layout for the buttons.
        open_button (PushButton): The button for opening a file.
        save_button (PushButton): The button for saving the file.
        save_as_button (PushButton): The button for saving the file as.
        theme_button (PushButton): The button for toggling the theme.
        dark_theme (bool): Whether the dark theme is enabled.
        current_file (str): The path of the currently loaded file.
        table_model (CSVTableModel): The model for the table view.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern CSV Viewer")
        self.resize(1700, 900)
        self.center_window()

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
        self.table_model = CSVTableModel()
        self.table_view.setModel(self.table_model)

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

        This method is responsible for creating and setting up all UI components
        such as the button container, search bar and table view. It also adds the
        main widget to the window and sets the current item in the navigation
        interface to the main interface.
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

        # Table view
        self.table_view = QTableView(self.main_widget)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setHighlightSections(True)
        self.table_view.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self.table_view.verticalHeader().hide()

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

    def show_header_context_menu(self, position):
        """
        Shows a context menu for the table header at the given position.
        The context menu is used to remove columns from the table.

        Args:
            position (QPoint): Point where the context menu should be shown.
        """
        if self.table_model.get_data() is None:
            return

        column_index = self.table_view.horizontalHeader().logicalIndexAt(position)
        if column_index < 0:
            return

        # Get column name
        column_name = self.table_model.get_data().columns[column_index]

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
        if self.table_model.get_data() is None:
            return

        # Get selected rows
        selected_rows = set()
        for index in self.table_view.selectionModel().selectedIndexes():
            selected_rows.add(index.row())

        # Create rounded context menu
        menu = RoundMenu(parent=self)

        # Action to add new row
        menu.addAction(
            Action(
                FluentIcon.ADD,
                "Add New Row",
                triggered=lambda: self.add_row(
                    max(selected_rows)
                    if selected_rows
                    else self.table_model.rowCount() - 1
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
        Deletes the selected rows from the table view.

        This method checks if there are any selected rows in the table view and
        if so, it removes them from the table model and shows an info message.
        """
        rows = set(index.row() for index in self.table_view.selectedIndexes())
        if not rows:
            return

        try:
            # Sort rows in descending order to avoid index issues
            for row in sorted(rows, reverse=True):
                self.table_model.remove_row(row)
            self.show_info_message(f"Deleted {len(rows)} row(s)")
        except Exception as e:
            self.show_error_message(f"Error deleting row(s): {str(e)}")

    def delete_column(self, column_index):
        try:
            self.table_model.remove_column(column_index)
            self.show_info_message(f"Column deleted successfully")
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

    def open_file(self):
        """
        Opens a CSV file.

        This method shows a file dialog for the user to select a CSV file. If a
        file is selected, it loads the file into the table model and shows an
        info message.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            try:
                # Load CSV without using first column as index
                df = pd.read_csv(file_name)
                self.table_model.update_data(df)
                self.current_file = file_name
                self.show_info_message(f"File loaded: {file_name}")
            except Exception as e:
                self.show_error_message(f"Error opening file: {str(e)}")

    def save_file(self):
        """
        Saves the current file.

        If the current file is not `None` and the table model has data, this
        method saves the data from the table model to the current file without
        indices and shows an info message. If there is an error, it shows an
        error message.

        If the current file is `None`, it calls the `save_file_as` method to
        show a file dialog to the user to select a file to save to.
        """
        if self.current_file and self.table_model.get_data() is not None:
            try:
                # Save without indices
                self.table_model.get_data().to_csv(self.current_file, index=False)
                self.show_info_message("File saved successfully")
            except Exception as e:
                self.show_error_message(f"Error saving file: {str(e)}")

    def save_file_as(self):
        """
        Saves the current file as a new file.

        This method shows a file dialog to the user to select a file to save
        to. If a file is selected, it calls the `save_file` method to save the
        data from the table model to the selected file without indices and
        shows an info message. If there is an error, it shows an error message.
        """
        if self.table_model.get_data() is not None:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            if file_name:
                try:
                    # Save without indices
                    self.table_model.get_data().to_csv(file_name, index=False)
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
        Searches for the given text in the data.

        This method searches for the given text in all columns of the data and
        updates the table model with the filtered data. The search is always
        performed on the original data to avoid "stuck" searches.
        """
        if self.table_model.get_data() is None:
            return

        try:
            # Update search text in model for highlighting
            self.table_model.set_search_text(text.strip())

            # Always load original data for search
            if self.current_file:
                original_df = pd.read_csv(self.current_file)
            else:
                return

            # If no search text, show all data
            if not text.strip():
                self.table_model.update_data(original_df)
                return

            # Search in all columns on original data
            mask = (
                original_df.astype(str)
                .apply(lambda x: x.str.contains(text, case=False))
                .any(axis=1)
            )
            filtered_df = original_df[mask]
            self.table_model.update_data(filtered_df)
        except Exception as e:
            self.show_error_message(f"Error searching data: {str(e)}")

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
            if self.table_model.add_row(after_row_index):
                self.show_info_message("New row added successfully")
        except Exception as e:
            self.show_error_message(f"Error adding row: {str(e)}")
