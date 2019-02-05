from glob import glob
from os import mkdir, remove, rename, rmdir
from pickle import dump, dumps, load, loads
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMessageBox)
from os.path import basename, dirname, exists, expanduser, join, splitext

from . import cbz_reader_ui

box_filename = "_img_boxes.pkl"
im_exts = (".png", ".jpg", ".jpeg", ".gif")


class CBZReader(QMainWindow):
    """Read cbz files
    """

    def __init__(self, cbzname=None):
        QMainWindow.__init__(self, None)

        # private attributes
        self._cbz_file = None  # ref on currently opened zip
        self._buf_dir = None  # name of directory that store buffered images
        self.clear()

        # setup gui
        cbz_reader_ui.setup_ui(self)

        # load previously stored state
        last = self.load_state()
        if cbzname is not None:
            self.open(cbzname)
        elif last is not None and last[0] is not None:
            if exists(last[0]):
                self.open(*last)

        self.update_title()

    def clear(self):
        if self._cbz_file is not None:
            self._cbz_file.close()
            self._cbz_file = None

        self._cbz_name = None  # name of currently opened file

        self._im_names = []  # list of images names in the archive
        self._im_boxes = {}  # associate list of boxes to some images

        self._page_ind = 0  # index of currenty displayed image
        self._box_ind = None  # index of currently displayed box
        # if None, means full page

        self._im_buf = [None] * 2  # buffer of images to be displayed

        self._file_modified = False  # flag activated if current file is edited

        # clean buffer directory
        if self._buf_dir is not None:
            for name in glob(join(self._buf_dir, "*.*")):
                remove(name)

            rmdir(self._buf_dir)
            self._buf_dir = None

    ########################################################
    #
    #	accessors
    #
    ########################################################
    def display_pages_only(self):
        """Tells wether we display boxes when possible
        or plain pages all the time
        """
        return self._ac_full_page.isChecked()

    def hide_mouse_cursor(self):
        """Tells wether mouse cursor is hidden
        in full screen mode
        """
        return not self._ac_show_mouse.isChecked()

    def create_buffer_dir(self):
        """Create a new empty directory
        """
        ind = 0
        while exists("_tmp_buf_%.4d" % ind):
            ind += 1

        self._buf_dir = "_tmp_buf_%.4d" % ind
        mkdir(self._buf_dir)

    def bufname(self, name):
        """Returns the name of the file in the buffer
        directory associated to this image.
        """
        return join(self._buf_dir, basename(name))

    def current_page(self):
        """Return current page in buffer 0
        """
        return self._im_buf[0]

    def current_box(self):
        """Return coordinate of current box or None
        """
        if self._box_ind is None:
            return None

        name = self._im_names[self._page_ind]
        return self._im_boxes[name][self._box_ind]

    def current_image(self):
        """Return the current page|box that needs to be
        displayed
        """
        page = self.current_page()
        if page is None:
            return None

        box = self.current_box()
        if box is None or self.display_pages_only():
            return page
        else:
            return page.crop(box)

    def update_title(self):
        if self._cbz_name is None:
            title = "No Book"
        else:
            title = splitext(basename(self._cbz_name))[0]
            title += " %d / %d" % (self._page_ind + 1, len(self._im_names))
            if self._box_ind is not None and not self.display_pages_only():
                title += " (%d)" % self._box_ind

        self.setWindowTitle(title)

    def update_display(self):
        """read current image in buffer and display it
        """
        self._im_view.set_image(self.current_image())
        if self.display_pages_only() and self._ac_show_box_hints.isChecked():
            name = self._im_names[self._page_ind]
            try:
                boxes = self._im_boxes[name]
                self._im_view.set_boxes(boxes)
            except KeyError:
                self._im_view.set_boxes(None)
        else:
            self._im_view.set_boxes(None)

        self._im_view.update()

        # update menu
        self._ac_full_page.setEnabled(self._box_ind is not None)

    def _load_img(self, name):
        bufname = self.bufname(name)
        if exists(bufname):
            try:
                img = Image.open(bufname)
            except IOError:  # bad image format
                return None
            img.load()
        else:
            data = self._cbz_file.read(name)
            f = open(bufname, 'wb')
            f.write(data)
            f.close()

            try:
                img = Image.open(bufname)
            except IOError:  # bad image format
                return None

            if img.mode == "RGB":
                img.load()
            else:
                img = img.convert("RGB")
                img.save(bufname)

        return img

    def _next_file(self):
        if self._cbz_name is None:
            return None

        cbz_names = sorted(glob(join(dirname(self._cbz_name), "*.cbz")))
        if len(cbz_names) == 1:  # no other cbz in this directory
            return None

        ind = cbz_names.index(self._cbz_name)
        if (ind + 1) == len(cbz_names):  # last file in directory
            return None

        return cbz_names[ind + 1]

    def _prev_file(self):
        if self._cbz_name is None:
            return None

        cbz_names = sorted(glob(join(dirname(self._cbz_name), "*.cbz")))
        if len(cbz_names) == 1:  # no other cbz in this directory
            return None

        ind = cbz_names.index(self._cbz_name)
        if ind == 0:  # first file in directory
            return None

        return cbz_names[ind - 1]

    ########################################################
    #
    #	Viewer state
    #
    ########################################################
    def load_state(self):
        """Load previously stored state of the viewer
        """
        name = expanduser("~/.cbz_reader.cfg")
        if exists(name):
            try:
                state = load(open(name, 'r'))
            except EOFError:
                return None

            # show options
            show = state.get("pages only", False)
            self._ac_full_page.setChecked(show)

            show = state.get("box hints", True)
            self._ac_show_box_hints.setChecked(show)

            show = state.get("show mouse", True)
            self._ac_show_mouse.setChecked(show)

            # set view transformation
            self._im_view.set_transfo(state.get("transfo", None))

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
        last = (self._cbz_name, self._page_ind, self._box_ind)
        state = {"transfo": self._im_view.transfo()
            , "geom": str(self.saveGeometry())
            , "widget state": str(self.saveState())
            , "full screen": self.isFullScreen()
            , "last": last
            , "pages only": self._ac_full_page.isChecked()
            , "box hints": self._ac_show_box_hints.isChecked()
            , "show mouse": self._ac_show_mouse.isChecked()}
        dump(state, open(expanduser("~/.cbz_reader.cfg"), 'w'))

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
                self.save(self._cbz_name)
            elif clicked == but_new:
                self.action_save_as()

        self.clear()

    def closeEvent(self, event):
        self.save_state()
        self.safe_close_file()

    def action_escape(self):
        if self._im_view.knife() is not None:  # close knife tool
            self._im_view.set_knife(None)
        elif self.isFullScreen():  # close full screen
            self.toggle_full_screen()
        else:  # close viewer
            self.close()

    def action_close(self):
        self.close()

    def open(self, name, page_ind=0, box_ind=0):
        """Open given archive file at the given page
        """
        self.safe_close_file()

        # open cbz file
        self._cbz_name = name

        self._cbz_file = ZipFile(name, 'r')
        self._im_names = [n for n in self._cbz_file.namelist() \
                          if splitext(n)[1].lower() in im_exts]
        self._im_names.sort()

        # try to load cut file
        if box_filename in self._cbz_file.namelist():
            self._im_boxes = loads(self._cbz_file.read(box_filename))
            for name in set(self._im_boxes) - set(self._im_names):  # TODO test
                del self._im_boxes[name]

        self._file_modified = False

        if page_ind < 0:
            self._page_ind = max(0, len(self._im_names) + page_ind)
        else:
            self._page_ind = min(page_ind, len(self._im_names) - 1)

        # bufferize
        self.create_buffer_dir()

        name = self._im_names[self._page_ind]
        self._im_buf[0] = self._load_img(name)
        if name in self._im_boxes:
            if box_ind < 0:
                box_ind += len(self._im_boxes[name])
            self._box_ind = box_ind
        else:
            self._box_ind = None

        # display
        self.update_title()
        self.update_display()

        # bufferize second frame
        if (self._page_ind + 1) < len(self._im_names):
            name = self._im_names[self._page_ind + 1]
            self._im_buf[1] = self._load_img(name)
        else:
            self._im_buf[1] = None

    def action_open(self):
        name = QFileDialog.getOpenFileName(self
                                           , "Open book"
                                           , "."
                                           , "Ebook Files (*.cbz);;All (*.*)")

        if not name.isNull():
            self.open(str(name))

    def save(self, name):
        """Save current archive under given name
        """
        self.setEnabled(False)  # save is potentialy a long operation
        QApplication.instance().processEvents()

        tmp_name = self.bufname(name)
        fw = ZipFile(tmp_name, 'w')

        # write images
        boxes = self._im_boxes
        self._im_boxes = {}
        for i, imname in enumerate(self._im_names):
            bufname = self.bufname(imname)
            pname = ("page%.4d" % i) + splitext(basename(imname))[1]
            # copy boxes
            try:
                self._im_boxes[pname] = boxes[imname]
            except KeyError:
                pass

            # write image
            if exists(bufname):
                fw.write(bufname, pname, ZIP_DEFLATED)  # TODO date info
            else:
                print(imname)
                data = self._cbz_file.read(imname)
                info = ZipInfo(pname)
                info.compress_type = ZIP_DEFLATED
                fw.writestr(info, data)

        # write boxes
        if len(self._im_boxes) > 0:
            data = dumps(self._im_boxes)
            info = ZipInfo(box_filename)
            info.compress_type = ZIP_DEFLATED
            fw.writestr(info, data)

        fw.close()

        self._cbz_file.close()
        if exists(name):
            remove(name)
        rename(tmp_name, name)

        # reinit viewer
        self._file_modified = False
        self.open(name, self._page_ind, self._box_ind)  # TODO update bufname and
        # other variable instead to gain some speed

        self.setEnabled(True)

    def action_save(self):
        if self._cbz_name is None:
            self.action_save_as()
        else:
            self.save(self._cbz_name)

    def action_save_as(self):
        name = QFileDialog.getSaveFileName(self
                                           , "Save book"
                                           , "."
                                           , "Ebook Files (*.cbz);;All (*.*)")

        if name is not None:
            self.save(str(name))

    def action_snapshot(self):
        """Save currently displayed image in a file
        """
        if self.current_image() is None:
            return

        name = QFileDialog.getSaveFileName(self
                                           , "Save Image"
                                           , "."
                                           , "img Files (*.png);;All (*.*)")

        print("snap", name)
        if name is not None:
            self.current_image().save(str(name))

    def action_next_cbz(self):
        """Open next file
        """
        name = self._next_file()
        if name is not None:
            self.open(name, 0, 0)

    def action_prev_cbz(self):
        """Open previous file
        """
        name = self._prev_file()
        if name is not None:
            self.open(name, 0, 0)

    ########################################################
    #
    #	display
    #
    ########################################################
    def display_next(self):
        """Display next image in file or next file if
        current is the last image in file
        """
        name = self._im_names[self._page_ind]

        # try to display next box in the same image
        if self._box_ind is not None and not self.display_pages_only():
            boxes = self._im_boxes[name]
            if (self._box_ind + 1) < len(boxes):
                self._box_ind += 1
                self.update_display()
                self.update_title()
                return

        # if no more images, display next file
        if (self._page_ind + 1) == len(self._im_names):
            name = self._next_file()
            if name is not None:
                self.open(name, 0, 0)
            return

        # display next image
        self._page_ind += 1
        self._im_buf[0] = self._im_buf[1]
        name = self._im_names[self._page_ind]
        if name in self._im_boxes:
            self._box_ind = 0
        else:
            self._box_ind = None

        self.update_display()
        self.update_title()

        # load buffer with next next image
        if (self._page_ind + 1) < len(self._im_names):
            name = self._im_names[self._page_ind + 1]
            self._im_buf[1] = self._load_img(name)
        else:
            self._im_buf[1] = None

    def display_prev(self):
        """Display previous image in file or previous file if
        current is the last image in file
        """
        name = self._im_names[self._page_ind]

        # try to display prev box in the same image
        if self._box_ind is not None and not self.display_pages_only():
            if (self._box_ind - 1) >= 0:
                self._box_ind -= 1
                self.update_display()
                self.update_title()
                return

        # if no more images, display prev file
        if self._page_ind == 0:
            name = self._prev_file()
            if name is not None:
                self.open(name, -1, -1)
            return

        # display previous page
        self._page_ind -= 1

        self._im_buf[1] = self._im_buf[0]

        name = self._im_names[self._page_ind]
        self._im_buf[0] = self._load_img(name)
        if name in self._im_boxes:
            self._box_ind = len(self._im_boxes[name]) - 1
        else:
            self._box_ind = None

        self.update_display()
        self.update_title()

    def toggle_full_page(self):
        """Display the full pages instead of current box
        """
        if not self._ac_full_page.isEnabled():
            return

        self.update_display()
        self.update_title()

    def flip_pages(self, nb_pages):
        """flip through pages (not through boxes)

        contrary to display_prev or display_next, does not change
        file when reaching end of file

        nb_pages limited internaly to 10
        """
        nb_pages = min(10, max(-10, nb_pages))

        i = max(0, min(len(self._im_names) - 1, self._page_ind + nb_pages))
        self._page_ind = i

        name = self._im_names[self._page_ind]
        if name in self._im_boxes:
            self._box_ind = 0
        else:
            self._box_ind = None

        self.update_title()
        self._im_buf[0] = self._load_img(name)

        self.update_display()

        if (self._page_ind + 1) < len(self._im_names):
            name = self._im_names[self._page_ind + 1]
            self._im_buf[1] = self._load_img(name)
        else:
            self._im_buf[1] = None

    def rotate_view(self):
        self._im_view.rotate()

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

    def image_info(self):
        """Display informations about current image in
        a dialog
        """
        name = self._im_names[self._page_ind]
        if self._im_buf[0] is None:
            info_str = "Bad image file format"
        else:
            w, h = self._im_buf[0].size
            info_str = "%s\nsize: (%d,%d)" % (name, w, h)

        if self._box_ind is not None and not self.display_pages_only():
            boxes = self._im_boxes[name]
            info_str += "\nbox (%d): " % self._box_ind
            info_str += "(%d, %d, %d, %d)" % boxes[self._box_ind]

        QMessageBox.information(self, "Image info", info_str)

    def action_box_hints(self, state):
        if not state:
            self._im_view.set_boxes(None)
            self._im_view.update()

    def action_show_mouse(self, state):
        print("show", state)

    ########################################################
    #
    #	edition
    #
    ########################################################
    def edit_full_page_warning(self):
        if self.display_pages_only():
            QMessageBox.warning(self
                                , "Edition warning"
                                , "Disable display full page first")
            return True

        return False

    def delete_current(self):
        """Delete currently displayed image from list
        of images
        """
        if self.edit_full_page_warning():
            return

        # try to remove box
        if self._box_ind is not None:
            name = self._im_names[self._page_ind]
            boxes = self._im_boxes[name]
            del boxes[self._box_ind]
            if len(boxes) == 0:
                del self._im_boxes[name]
                self._box_ind = None
            elif self._box_ind == len(boxes):
                self._box_ind -= 1

            self._file_modified = True
            self.update_title()
            self.update_display()
            return

        # need to remove whole page
        if len(self._im_names) == 1:
            print("last file")
            return

        # delete image name
        del self._im_names[self._page_ind]
        # no need to remove boxes since none associated

        self._file_modified = True

        # reload current image
        if self._page_ind < len(self._im_names):
            self._im_buf[0] = self._im_buf[1]
        else:
            self._page_ind -= 1
            name = self._im_names[self._page_ind]
            self._im_buf[0] = self._load_img(name)

        if self.display_pages_only():
            self._box_ind = None
        else:
            name = self._im_names[self._page_ind]
            if name in self._im_boxes:
                self._box_ind = 0
            else:
                self._box_ind = None

        self.update_title()
        self.update_display()

        # reload buffer
        if (self._page_ind + 1) < len(self._im_names):
            name = self._im_names[self._page_ind + 1]
            self._im_buf[1] = self._load_img(name)
        else:
            self._im_buf[1] = None

    def image_updown(self):
        """Transpose image upside down
        """
        if self.edit_full_page_warning():
            return

        if self._box_ind is not None:
            print("need to delete boxes first")
            return

        page = self.current_page()
        if page is None:
            return

        # transpose image
        name = self._im_names[self._page_ind]
        page = page.transpose(Image.ROTATE_180)

        # update view
        self._im_buf[0] = page
        self.update_display()

        # update buffer file
        page.save(self.bufname(name))
        self._file_modified = True

    def swap_left(self):
        """Swap current image/box with previous one
        """
        if self.edit_full_page_warning():
            return

        bi = self._box_ind
        pi = self._page_ind
        if bi is not None:  # swap boxes
            if bi == 0:
                return

            name = self._im_names[pi]
            boxes = self._im_boxes[name]
            boxes[bi - 1], boxes[bi] = boxes[bi], boxes[bi - 1]
            self._box_ind -= 1
        else:  # swap pages
            if pi == 0:
                return

            names = self._im_names
            self._im_buf[1] = self._load_img(names[pi - 1])
            names[pi - 1], names[pi] = names[pi], names[pi - 1]
            self._page_ind -= 1

        self.update_title()
        self._file_modified = True

    def swap_right(self):
        """Swap current image/box with next one
        """
        if self.edit_full_page_warning():
            return

        print("swap right")

    def cut_height(self):
        """Activate knife
        """
        if self.edit_full_page_warning():
            return

        if self._im_view.knife() == "height":
            self._im_view.set_knife(None)
        else:
            self._im_view.set_knife("height")

    def cut_width(self):
        """Activate knife
        """
        if self.edit_full_page_warning():
            return

        if self._im_view.knife() == "width":
            self._im_view.set_knife(None)
        else:
            self._im_view.set_knife("width")

    def cut_box(self):  # TODO
        """Activate knife
        """
        if self.edit_full_page_warning():
            return

        if self._im_view.knife() == "box":
            self._im_view.set_knife(None)
        else:
            self._im_view.set_knife("box")

    def cut_image(self, ori, pos):
        """Actually perform image cut
        """
        if self.edit_full_page_warning():
            return

        page = self.current_page()
        if page is None:
            return

        box = self.current_box()
        if box is None:
            x1 = 0
            y1 = 0
            x2, y2 = page.size
        else:
            x1, y1, x2, y2 = box

        if ori == "height":  # crop box fmt is (x1,y1,x2,y2)
            b1 = (x1, y1, x2, y1 + pos)
            b2 = (x1, y1 + pos, x2, y2)
        else:  # cut page verticaly
            b1 = (x1, y1, x1 + pos, y2)
            b2 = (x1 + pos, y1, x2, y2)

        name = self._im_names[self._page_ind]
        if self._box_ind is None:
            self._im_boxes[name] = [b1, b2]
            self._box_ind = 1
        else:
            boxes = self._im_boxes[name]
            del boxes[self._box_ind]
            boxes.insert(self._box_ind, b2)
            boxes.insert(self._box_ind, b1)
            self._box_ind += 1

        self.update_display()
        self.update_title()
        self._file_modified = True
