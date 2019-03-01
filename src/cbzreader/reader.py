import pickle
from pathlib import Path

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QMessageBox, QShortcut)

from .explorer import Explorer
from .reader_ui import setup_ui


class Reader(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._ex = Explorer()
        self._current_page = None
        self._file_modified = False

        self.init_gui()

        last_open = self.load_state()
        if last_open is not None and last_open[0] is not None:
            if last_open[0].exists():
                self.load(*last_open)

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

        # menu viewedit
        self.ui.action_info.triggered.connect(self.image_info)
        self.ui.action_delete.triggered.connect(self.delete_current)
        self.ui.action_updown.triggered.connect(self.image_updown)
        self.ui.action_swap_left.triggered.connect(self.swap_left)
        self.ui.action_swap_right.triggered.connect(self.swap_right)

        QShortcut("Escape", self, self.action_escape)

    def closeEvent(self, event):
        self.save_state()
        self.safe_close_file()
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
        return not self.ui.action_show_mouse.isChecked()

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
        if self._ex.current_book() is None:
            title = "No Book"
        else:
            book_name = self._ex.current_book().name
            cur_page = self._current_page + 1
            nb_pages = self._ex.page_number()
            title = f"{book_name} {cur_page:d} / {nb_pages:d}"

        self.setWindowTitle(title)

    ########################################################
    #
    #	Viewer state
    #
    ########################################################
    def load_state(self):
        """Load previously stored state of the viewer
        """
        state_pth = Path.home() / ".cbz_reader.cfg"
        if state_pth.exists():
            try:
                state = pickle.load(state_pth.open('rb'))
            except EOFError:
                return None

            # show options
            show = state.get("show mouse", True)
            self.ui.action_show_mouse.setChecked(show)

            # set view transformation
            self.ui.view_page.set_transfo(state.get("transfo", None))

            # set viewer geometry
            try:
                self.restoreGeometry(state["geom"])
            except KeyError:
                pass
            # set widget state
            try:
                self.restoreState(state["widget state"])
            except KeyError:
                pass
            # full screen options
            if state.get("full screen", False):
                self.menuBar().hide()
                if self.hide_mouse_cursor():
                    self.setCursor(Qt.BlankCursor)

            # reload last open file
            return state.get("last", None)

    def save_state(self):
        """Save current state of the viewer in a file
        """
        state_pth = Path.home() / ".cbz_reader.cfg"
        last = (self._ex.current_book(), self._current_page)
        state = {"transfo": self.ui.view_page.transfo(),
                 "geom": bytes(self.saveGeometry()),
                 "widget state": bytes(self.saveState()),
                 "full screen": self.isFullScreen(),
                 "last": last,
                 "show mouse": self.ui.action_show_mouse.isChecked()}

        pickle.dump(state, state_pth.open('wb'))

    ########################################################
    #
    #	file
    #
    ########################################################
    def safe_close_file(self):
        # edition?
        if self._file_modified:
            msg = QMessageBox(self)
            msg.setText("File modified")
            msg.setInformativeText("Want to save?")
            but_overwrite = msg.addButton("Overwrite", msg.AcceptRole)
            but_new = msg.addButton("New file", msg.AcceptRole)
            but_no = msg.addButton("No", msg.RejectRole)
            msg.setDefaultButton(but_new)

            msg.exec_()

            clicked = msg.clickedButton()
            if clicked == but_no:
                # do nothing
                pass
            elif clicked == but_overwrite:
                self.save(self._ex.current_book())
            elif clicked == but_new:
                self.action_save_as()

        self._ex.close_book()

    def load(self, pth, current_page=0):
        """Load pth as current open book.
        """
        self.safe_close_file()

        self._ex.set_book(pth)
        self._file_modified = False

        current_page = max(0, current_page)
        current_page = min(self._ex.page_number() - 1, current_page)
        self._current_page = current_page

        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
        self.update_title()

    def action_load(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Books (*.cbz)")
        if file_names:
            pth, = file_names
            self.load(Path(pth))

    def prev_book(self):
        try:
            pth = self._ex.prev_book()
            self.load(pth)
        except IndexError:
            print("First book already")

    def next_book(self):
        try:
            pth = self._ex.next_book()
            self.load(pth)
        except IndexError:
            print("Last book already")

    def save(self, pth):
        """Save current archive under given name
        """
        self.setEnabled(False)  # save is potentially a long operation
        QCoreApplication.instance().processEvents()

        self._ex.save_book(pth)
        self.update_title()
        self._file_modified = False

        self.setEnabled(True)

    def action_save(self):
        if self._current_page is None:
            print("load a book first")
            return

        if self._ex.current_book() is None:
            self.action_save_as()
        else:
            self.save(self._ex.current_book())

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

    ########################################################
    #
    #	view
    #
    ########################################################
    def rotate_page(self):
        if self._current_page is None:
            print("load a book first")
            return

        self.ui.view_page.rotate()

    def prev_page(self):
        if self._current_page is None:
            print("load a book first")
            return

        if self._current_page == 0:
            print("first page already")
            return

        self._current_page -= 1
        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
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
        self.ui.view_page.set_image(img)
        self.update_title()

    ########################################################
    #
    #	edit
    #
    ########################################################
    def image_info(self):
        """Display information about current image in
        a dialog
        """
        if self._current_page is None:
            print("load a book first")
            return

        img = self._ex.open_page(self._current_page)
        info_str = f"size: {img.size[0]:d}, {img.size[1]:d}"

        QMessageBox.information(self, "Image info", info_str)

    def delete_current(self):
        """Delete current page from book.
        """
        if self._current_page is None:
            print("load a book first")
            return

        self._ex.delete_page(self._current_page)

        if self._current_page == self._ex.page_number():
            self._current_page -= 1
            if self._current_page < 0:
                print("empty book")
                self._file_modified = False
                self._ex.close_book()
                self.ui.view_page.set_image(None)
                self.update_title()
                return

        self._file_modified = True
        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
        self.update_title()

    def image_updown(self):
        """Transpose image upside down
        """

        if self._current_page is None:
            print("load a book first")
            return

        # transpose image
        self._ex.transpose(self._current_page)
        self._file_modified = True

        # update view
        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
        self.update_title()

    def swap_left(self):
        """Swap page with previous one.
        """
        if self._current_page is None:
            print("load a book first")
            return

        if self._current_page == 0:
            print("First page already")
            return

        # swap pages
        self._ex.swap(self._current_page, self._current_page - 1)
        self._current_page -= 1
        self._file_modified = True

        # update view
        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
        self.update_title()

    def swap_right(self):
        """Swap page with next one.
        """
        if self._current_page is None:
            print("load a book first")
            return

        if self._current_page == self._ex.page_number() - 1:
            print("Last page already")
            return

        # swap pages
        self._ex.swap(self._current_page, self._current_page + 1)
        self._current_page += 1
        self._file_modified = True

        # update view
        img = self._ex.open_page(self._current_page)
        self.ui.view_page.set_image(img)
        self.update_title()
