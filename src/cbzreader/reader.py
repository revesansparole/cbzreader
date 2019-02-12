from pathlib import Path

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QShortcut)

from .explorer import Explorer
from .reader_ui import setup_ui


class Reader(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._ex = Explorer()
        self._current_page = None
        self._book_pth = None

        self.init_gui()

    def init_gui(self):
        setup_ui(self)
        self.update_title()

        # menu file
        self.ui.action_open.triggered.connect(self.action_load)
        self.ui.action_prev_book.triggered.connect(self.prev_book)
        self.ui.action_next_book.triggered.connect(self.next_book)
        self.ui.action_save.triggered.connect(self.action_save)
        self.ui.action_save_as.triggered.connect(self.action_save_as)

        # menu view
        self.ui.action_full_screen.triggered.connect(self.toggle_full_screen)
        self.ui.action_prev_page.triggered.connect(self.prev_page)
        self.ui.action_next_page.triggered.connect(self.next_page)
        self.ui.action_rotate.triggered.connect(self.rotate_page)

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

    def update_title(self):
        if self._book_pth is None:
            title = "No Book"
        else:
            book_name = self._book_pth.name
            cur_page = self._current_page + 1
            nb_pages = self._ex.page_number()
            title = f"{book_name} {cur_page:d} / {nb_pages:d}"

        self.setWindowTitle(title)

    def load(self, pth, current_page=0):
        """Load pth as current open book.
        """
        self._ex.set_book(pth)
        self._book_pth = self._ex.current_book()

        current_page = max(0, current_page)
        current_page = min(self._ex.page_number() - 1, current_page)
        self._current_page = current_page

        img = self._ex.open_page(self._current_page)
        self.view_page.set_image(img)
        self.update_title()

    def action_load(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Books (*.cbz)")
        if file_names:
            pth, = file_names
            self.load(Path(pth))

    def prev_book(self):
        try:
            self._ex.prev_book()
            self._book_pth = self._ex.current_book()

            self._current_page = 0
            img = self._ex.open_page(self._current_page)
            self.view_page.set_image(img)
            self.update_title()
        except IndexError:
            print("First book already")

    def next_book(self):
        try:
            self._ex.next_book()
            self._book_pth = self._ex.current_book()

            self._current_page = 0
            img = self._ex.open_page(self._current_page)
            self.view_page.set_image(img)
            self.update_title()
        except IndexError:
            print("Last book already")

    def save(self, pth):
        """Save current archive under given name
        """
        self.setEnabled(False)  # save is potentially a long operation
        QCoreApplication.instance().processEvents()

        self._ex.save_book(pth)

        # reopen book to reinit viewer
        self.load(pth, self._current_page)

        self.setEnabled(True)

    def action_save(self):
        if self._current_page is None:
            print("load a book first")
            return

        if self._book_pth is None:
            self.action_save_as()
        else:
            self.save(self._book_pth)

    def action_save_as(self):
        if self._current_page is None:
            print("load a book first")
            return

        name, _ = QFileDialog.getSaveFileName(self
                                              , "Save book"
                                              , "."
                                              , "Ebook Files (*.cbz);;All (*.*)")

        if name is not None:
            self.save(Path(name))

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
        self.update_title()

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
        self.update_title()
