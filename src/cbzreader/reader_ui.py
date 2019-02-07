from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem)

from .image_view import ImageView


def setup_ui(mw):
    mw.setWindowTitle("cbzreader")
    mw.setMinimumSize(600, 600)

    g_layout = QGridLayout(mw)

    # Select files
    mw.load_button = QPushButton("Select Files", mw)
    mw.load_button.setMinimumHeight(30)
    g_layout.addWidget(mw.load_button, 0, 0)

    # image view
    mw.img_view = ImageView()
    g_layout.addWidget(mw.img_view, 1, 0)

    # rotate and next button
    h_layout = QHBoxLayout()
    mw.prev_button = QPushButton("Prev page", mw)
    mw.prev_button.setMinimumWidth(120)
    mw.rotate_button = QPushButton("Rotate", mw)
    mw.rotate_button.setMinimumWidth(120)
    mw.next_button = QPushButton("Next page", mw)
    mw.next_button.setMinimumWidth(120)
    h_layout.addSpacerItem(QSpacerItem(60, 30, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
    h_layout.addWidget(mw.prev_button)
    h_layout.addWidget(mw.rotate_button)
    h_layout.addWidget(mw.next_button)
    g_layout.addLayout(h_layout, 2, 0)
