from pathlib import Path

from PyQt5.QtWidgets import (QFileDialog, QWidget)

from .explorer import Explorer
from .reader_ui import setup_ui


class Reader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_gui()

        self._ex = Explorer()
        self._current_page = None

    def init_gui(self):
        setup_ui(self)

        self.load_button.clicked.connect(self.load_file)
        self.rotate_button.clicked.connect(self.rotate_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

    def closeEvent(self, event):
        self._ex.close()
        super().closeEvent(event)

    def load_file(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Books (*.cbz)")
        if file_names:
            pth, = file_names
            self._ex.set_book(Path(pth))
            self._current_page = 0
            img = self._ex.open_page(self._current_page)
            self.img_view.set_image(img)

    def rotate_page(self):
        self.img_view.rotate()

    def prev_page(self):
        if self._current_page == 0:
            print("first page already")
            return

        self._current_page -= 1
        img = self._ex.open_page(self._current_page)
        self.img_view.set_image(img)

    def next_page(self):
        if self._current_page == self._ex.page_number() - 1:
            print("last page already")
            return

        self._current_page += 1
        img = self._ex.open_page(self._current_page)
        self.img_view.set_image(img)
