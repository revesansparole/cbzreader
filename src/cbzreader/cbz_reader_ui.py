import cbz_reader_cfg as sh
from PyQt5.QtCore import QObject, SIGNAL
from PyQt5.QtWidgets import (QAction, QColor, QIcon, QShortcut)
from image_view import ImageView

from . import icons_rc

def setup_ui(mw):
    mw._im_view = ImageView()
    mw.setCentralWidget(mw._im_view)
    QObject.connect(mw._im_view, SIGNAL("click right"), mw.display_next)
    QObject.connect(mw._im_view, SIGNAL("click left"), mw.display_prev)
    QObject.connect(mw._im_view, SIGNAL("wheel"), mw.flip_pages)
    QObject.connect(mw._im_view, SIGNAL("knife"), mw.cut_image)

    mw.setMinimumSize(100, 100)
    mw.setWindowIcon(QIcon(":images/cbzreader.png"))

    pal = mw.palette()
    pal.setColor(pal.Window, QColor(0, 0, 0))
    mw.setPalette(pal)

    trig = SIGNAL("triggered(bool)")

    QShortcut("Escape", mw, mw.action_escape)

    ############################################
    #
    #	menu file
    #
    ############################################
    mw._ac_open = QAction("Open", mw)
    mw._ac_open.setIcon(QIcon(":images/open.png"))
    QObject.connect(mw._ac_open, trig, mw.action_open)
    QShortcut(sh.open, mw, mw._ac_open.trigger)

    mw._ac_save = QAction("Save", mw)
    mw._ac_save.setIcon(QIcon(":images/save.png"))
    QObject.connect(mw._ac_save, trig, mw.action_save)
    QShortcut(sh.save, mw, mw._ac_save.trigger)

    mw._ac_save_as = QAction("Save as", mw)
    QObject.connect(mw._ac_save_as, trig, mw.action_save_as)
    QShortcut(sh.save_as, mw, mw._ac_save_as.trigger)

    mw._ac_snapshot = QAction("Snapshot", mw)
    mw._ac_snapshot.setIcon(QIcon(":images/snapshot.png"))
    QObject.connect(mw._ac_snapshot, trig, mw.action_snapshot)
    QShortcut(sh.snapshot, mw, mw._ac_snapshot.trigger)

    mw._ac_next_cbz = QAction("Next cbz", mw)
    mw._ac_next_cbz.setIcon(QIcon(":images/next_cbz.png"))
    QObject.connect(mw._ac_next_cbz, trig, mw.action_next_cbz)
    QShortcut(sh.next_cbz, mw, mw._ac_next_cbz.trigger)

    mw._ac_prev_cbz = QAction("Prev cbz", mw)
    mw._ac_prev_cbz.setIcon(QIcon(":images/prev_cbz.png"))
    QObject.connect(mw._ac_prev_cbz, trig, mw.action_prev_cbz)
    QShortcut(sh.prev_cbz, mw, mw._ac_prev_cbz.trigger)

    mw._ac_close = QAction("Close", mw)
    QObject.connect(mw._ac_close, trig, mw.action_close)
    QShortcut(sh.close, mw, mw._ac_close.trigger)

    menu_file = mw.menuBar().addMenu("File")
    menu_file.addAction(mw._ac_open)
    menu_file.addAction(mw._ac_next_cbz)
    menu_file.addAction(mw._ac_prev_cbz)
    menu_file.addSeparator()
    menu_file.addAction(mw._ac_save)
    menu_file.addAction(mw._ac_save_as)
    menu_file.addAction(mw._ac_snapshot)
    menu_file.addSeparator()
    menu_file.addAction(mw._ac_close)

    ############################################
    #
    #	menu view
    #
    ############################################
    mw._ac_next = QAction("Next", mw)
    mw._ac_next.setIcon(QIcon(":images/next.png"))
    QObject.connect(mw._ac_next, trig, mw.display_next)
    for txt in sh.next:
        QShortcut(txt, mw, mw._ac_next.trigger)

    mw._ac_prev = QAction("Prev", mw)
    mw._ac_prev.setIcon(QIcon(":images/prev.png"))
    QObject.connect(mw._ac_prev, trig, mw.display_prev)
    QShortcut(sh.prev, mw, mw._ac_prev.trigger)

    mw._ac_full_page = QAction("Page", mw)
    mw._ac_full_page.setCheckable(True)
    mw._ac_full_page.setChecked(False)
    QObject.connect(mw._ac_full_page, trig, mw.toggle_full_page)
    QShortcut(sh.full_page, mw, mw._ac_full_page.trigger)

    mw._ac_rotate = QAction("Rotate", mw)
    QObject.connect(mw._ac_rotate, trig, mw.rotate_view)
    QShortcut(sh.rotate, mw, mw._ac_rotate.trigger)

    mw._ac_full_screen = QAction("Full Screen", mw)
    QObject.connect(mw._ac_full_screen, trig, mw.toggle_full_screen)
    for txt in sh.full_screen:
        QShortcut(txt, mw, mw._ac_full_screen.trigger)

    #	mw._ac_show_pages_only = QAction("Pages only", mw)
    #	mw._ac_show_pages_only.setCheckable(True)
    #	mw._ac_show_pages_only.setChecked(False)
    #	QObject.connect(mw._ac_show_pages_only, trig, mw.action_pages_only)

    mw._ac_show_box_hints = QAction("Box hints", mw)
    mw._ac_show_box_hints.setCheckable(True)
    mw._ac_show_box_hints.setChecked(True)
    QObject.connect(mw._ac_show_box_hints, trig, mw.action_box_hints)

    mw._ac_show_mouse = QAction("Show mouse", mw)
    mw._ac_show_mouse.setCheckable(True)
    mw._ac_show_mouse.setChecked(True)
    QObject.connect(mw._ac_show_mouse, trig, mw.action_show_mouse)

    menu_view = mw.menuBar().addMenu("View")
    menu_view.addAction(mw._ac_next)
    menu_view.addAction(mw._ac_prev)
    menu_view.addAction(mw._ac_full_page)
    menu_view.addSeparator()
    menu_view.addAction(mw._ac_rotate)
    menu_view.addAction(mw._ac_full_screen)
    menu_view.addSeparator()
    #	menu_view.addAction(mw._ac_show_pages_only)
    menu_view.addAction(mw._ac_show_box_hints)
    menu_view.addAction(mw._ac_show_mouse)

    ############################################
    #
    #	menu edition
    #
    ############################################
    mw._ac_info = QAction("Info", mw)
    QObject.connect(mw._ac_info, trig, mw.image_info)
    QShortcut(sh.info, mw, mw._ac_info.trigger)

    mw._ac_del = QAction("Delete", mw)
    QObject.connect(mw._ac_del, trig, mw.delete_current)
    QShortcut(sh.delete, mw, mw._ac_del.trigger)

    mw._ac_updown = QAction("Upside Down", mw)
    QObject.connect(mw._ac_updown, trig, mw.image_updown)
    QShortcut(sh.updown, mw, mw._ac_updown.trigger)

    mw._ac_swap_left = QAction("Swap left", mw)
    QObject.connect(mw._ac_swap_left, trig, mw.swap_left)
    QShortcut(sh.swap_left, mw, mw._ac_swap_left.trigger)

    mw._ac_swap_right = QAction("Swap right", mw)
    QObject.connect(mw._ac_swap_right, trig, mw.swap_right)
    QShortcut(sh.swap_right, mw, mw._ac_swap_right.trigger)

    mw._ac_cut_height = QAction("Cut image height", mw)
    QObject.connect(mw._ac_cut_height, trig, mw.cut_height)
    QShortcut(sh.cut_height, mw, mw._ac_cut_height.trigger)

    mw._ac_cut_width = QAction("Cut image width", mw)
    QObject.connect(mw._ac_cut_width, trig, mw.cut_width)
    QShortcut(sh.cut_width, mw, mw._ac_cut_width.trigger)

    menu_edition = mw.menuBar().addMenu("Edition")
    menu_edition.addAction(mw._ac_del)
    menu_edition.addAction(mw._ac_updown)
    menu_edition.addAction(mw._ac_cut_height)
    menu_edition.addAction(mw._ac_cut_width)
