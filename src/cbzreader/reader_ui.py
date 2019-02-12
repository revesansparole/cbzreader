from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QShortcut)

from . import cbz_reader_cfg as sh
from .icons_rc import qInitResources
from .image_view import ImageView

qInitResources()


class UI:
    pass


def setup_ui(mw):
    mw.ui = UI()

    mw.setWindowTitle("cbzreader")
    mw.setMinimumSize(600, 600)
    mw.setWindowIcon(QIcon(":images/cbzreader.png"))

    mw.view_page = ImageView()
    mw.setCentralWidget(mw.view_page)

    menubar = mw.menuBar()

    # Menu files
    mw.ui.action_open = QAction(QIcon(":images/open.png"), '&Open', mw)
    QShortcut(sh.open, mw, mw.ui.action_open.trigger)

    mw.ui.action_prev_book = QAction(QIcon(":images/prev_cbz.png"), "&Prev book", mw)
    QShortcut(sh.prev_book, mw, mw.ui.action_prev_book.trigger)

    mw.ui.action_next_book = QAction(QIcon(":images/next_cbz.png"), "&Next book", mw)
    QShortcut(sh.next_book, mw, mw.ui.action_next_book.trigger)

    mw.ui.action_save = QAction(QIcon(":images/save.png"), "&Save", mw)
    QShortcut(sh.save, mw, mw.ui.action_save.trigger)

    mw.ui.action_save_as = QAction("Save as", mw)
    QShortcut(sh.save_as, mw, mw.ui.action_save_as.trigger)

    mw.ui.action_snapshot = QAction(QIcon(":images/snapshot.png"), "Snapshot", mw)
    QShortcut(sh.snapshot, mw, mw.ui.action_snapshot.trigger)

    mw.ui.action_close = QAction("&Close", mw)
    QShortcut(sh.close, mw, mw.ui.action_close.trigger)

    menu_file = menubar.addMenu('&File')
    menu_file.addAction(mw.ui.action_open)
    menu_file.addAction(mw.ui.action_prev_book)
    menu_file.addAction(mw.ui.action_next_book)
    menu_file.addSeparator()
    menu_file.addAction(mw.ui.action_save)
    menu_file.addAction(mw.ui.action_save_as)
    menu_file.addAction(mw.ui.action_snapshot)
    menu_file.addSeparator()
    menu_file.addAction(mw.ui.action_close)

    # Menu view
    mw.ui.action_full_screen = QAction("&Full Screen", mw)
    for txt in sh.full_screen:
        QShortcut(txt, mw, mw.ui.action_full_screen.trigger)

    mw.ui.action_next_page = QAction(QIcon(":images/next.png"), "&Next", mw)
    for txt in sh.next:
        QShortcut(txt, mw, mw.ui.action_next_page.trigger)

    mw.ui.action_prev_page = QAction(QIcon(":images/prev.png"), "&Prev", mw)
    QShortcut(sh.prev, mw, mw.ui.action_prev_page.trigger)

    mw.ui.action_rotate = QAction('&Rotate', mw)
    QShortcut(sh.rotate, mw, mw.ui.action_rotate.trigger)

    mw.ui.action_show_mouse = QAction("&Show mouse", mw)
    mw.ui.action_show_mouse.setCheckable(True)
    mw.ui.action_show_mouse.setChecked(True)

    menu_view = menubar.addMenu('&View')
    menu_view.addAction(mw.ui.action_full_screen)
    menu_view.addSeparator()
    menu_view.addAction(mw.ui.action_prev_page)
    menu_view.addAction(mw.ui.action_next_page)
    menu_view.addSeparator()
    menu_view.addAction(mw.ui.action_rotate)
    menu_view.addSeparator()
    menu_view.addAction(mw.ui.action_show_mouse)
