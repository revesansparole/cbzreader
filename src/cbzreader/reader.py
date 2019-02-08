from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QShortcut)

from .explorer import Explorer
from .reader_ui import setup_ui


class Reader(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_gui()

        self._ex = Explorer()
        self._current_page = None

    def init_gui(self):
        setup_ui(self)

        self.action_open.triggered.connect(self.load_file)

        self.action_full_screen.triggered.connect(self.toggle_full_screen)
        self.action_prev_page.triggered.connect(self.prev_page)
        self.action_next_page.triggered.connect(self.next_page)
        self.action_rotate.triggered.connect(self.rotate_page)

        QShortcut("Escape", self, self.action_escape)

    def closeEvent(self, event):
        self._ex.close()
        super().closeEvent(event)

    def action_escape(self):
        if self.isFullScreen():  # close full screen
            self.toggle_full_screen()
        else:  # close viewer
            self.close()

    def hide_mouse_cursor(self):
        """Tells whether mouse cursor is hidden
        in full screen mode
        """
        return not self.action_show_mouse.isChecked()

    def toggle_full_screen(self):
        if self.isFullScreen():  # go normal window mode
            self.showNormal()
            self.menuBar().show()
            self.setCursor(Qt.ArrowCursor)
        else:  # go fullscreen mode
            self.menuBar().hide()
            self.showFullScreen()
            if self.hide_mouse_cursor():
                self.setCursor(Qt.BlankCursor)

    def load_file(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Books (*.cbz)")
        if file_names:
            pth, = file_names
            self._ex.set_book(Path(pth))
            self._current_page = 0
            img = self._ex.open_page(self._current_page)
            self.view_page.set_image(img)

    def rotate_page(self):
        if self._current_page is None:
            print("load a book first")
            return

        self.view_page.rotate()

    def prev_page(self):
        if self._current_page is None:
            print("load a book first")
            return

        if self._current_page == 0:
            print("first page already")
            return

        self._current_page -= 1
        img = self._ex.open_page(self._current_page)
        self.view_page.set_image(img)

    def next_page(self):
        if self._current_page is None:
            print("load a book first")
            return

        if self._current_page == self._ex.page_number() - 1:
            print("last page already")
            return

        self._current_page += 1
        img = self._ex.open_page(self._current_page)
        self.view_page.set_image(img)
