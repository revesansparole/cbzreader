from pathlib import Path

from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem,
                             QWidget)

from .image_view import ImageView
from .explorer import Explorer


class Reader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_gui()

        self._ex = Explorer()
        self._current_page = None


    def init_gui(self):
        self.setWindowTitle("cbzreader")
        self.setMinimumSize(600, 600)

        g_layout = QGridLayout(self)

        # Select files
        self.load_button = QPushButton("Select Files", self)
        self.load_button.setMinimumHeight(30)
        g_layout.addWidget(self.load_button, 0, 0)
        self.load_button.clicked.connect(self.load_file)

        # image view
        self.img_view = ImageView()
        g_layout.addWidget(self.img_view, 1, 0)

        # rotate and next button
        h_layout = QHBoxLayout()
        self.prev_button = QPushButton("Prev page", self)
        self.prev_button.setMinimumWidth(120)
        self.rotate_button = QPushButton("Rotate", self)
        self.rotate_button.setMinimumWidth(120)
        self.next_button = QPushButton("Next page", self)
        self.next_button.setMinimumWidth(120)
        h_layout.addSpacerItem(QSpacerItem(60, 30, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        h_layout.addWidget(self.prev_button)
        h_layout.addWidget(self.rotate_button)
        h_layout.addWidget(self.next_button)
        self.rotate_button.clicked.connect(self.rotate_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        g_layout.addLayout(h_layout, 2, 0)

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
        self._current_page += 1
        img = self._ex.open_page(self._current_page)
        self.img_view.set_image(img)
