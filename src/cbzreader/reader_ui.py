from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QShortcut)

from . import cbz_reader_cfg as sh
from .icons_rc import qInitResources
from .image_view import ImageView

qInitResources()


def setup_ui(mw):
    mw.setWindowTitle("cbzreader")
    mw.setMinimumSize(600, 600)

    mw.view_page = ImageView()
    mw.setCentralWidget(mw.view_page)

    menubar = mw.menuBar()
    # Menu files
    mw.action_open = QAction(QIcon(":images/open.png"), '&Open', mw)
    QShortcut(sh.open, mw, mw.action_open.trigger)

    mw.action_prev_book = QAction(QIcon(":images/prev_cbz.png"), "&Prev book", mw)
    QShortcut(sh.prev_book, mw, mw.action_prev_book.trigger)

    mw.action_next_book = QAction(QIcon(":images/next_cbz.png"), "&Next book", mw)
    QShortcut(sh.next_book, mw, mw.action_next_book.trigger)

    menu_file = menubar.addMenu('&File')
    menu_file.addAction(mw.action_open)
    menu_file.addAction(mw.action_prev_book)
    menu_file.addAction(mw.action_next_book)

    # Menu view
    mw.action_full_screen = QAction("&Full Screen", mw)
    for txt in sh.full_screen:
        QShortcut(txt, mw, mw.action_full_screen.trigger)

    mw.action_next_page = QAction(QIcon(":images/next.png"), "&Next", mw)
    for txt in sh.next:
        QShortcut(txt, mw, mw.action_next_page.trigger)

    mw.action_prev_page = QAction(QIcon(":images/prev.png"), "&Prev", mw)
    QShortcut(sh.prev, mw, mw.action_prev_page.trigger)

    mw.action_rotate = QAction('&Rotate', mw)
    QShortcut(sh.rotate, mw, mw.action_rotate.trigger)

    mw.action_show_mouse = QAction("&Show mouse", mw)
    mw.action_show_mouse.setCheckable(True)
    mw.action_show_mouse.setChecked(True)

    menu_view = menubar.addMenu('&View')
    menu_view.addAction(mw.action_full_screen)
    menu_view.addSeparator()
    menu_view.addAction(mw.action_prev_page)
    menu_view.addAction(mw.action_next_page)
    menu_view.addSeparator()
    menu_view.addAction(mw.action_rotate)
    menu_view.addSeparator()
    menu_view.addAction(mw.action_show_mouse)
