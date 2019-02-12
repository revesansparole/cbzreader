"""
An explorer is used to navigate through the different cbz files in a directory
and display the content of each.
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from PIL import Image

im_exts = ("png", "jpg", "jpeg", "gif")


class Explorer:
    def __init__(self, pth=None):
        """Create an explorer initialize on given path.

        Args:
            pth (str): path to current file
        """
        self._pth = None  # path to currently opened book
        self._cbz = None  # handle to opened zip book
        self._buf_dir = None  # directory to write images temporarily

        if pth is not None:
            self.set_book(Path(pth))

    def _clear_buffer_dir(self):
        """Remove all images in buffer_dir and actual dir itself.

        Returns:
            (None)
        """
        if self._buf_dir is not None:
            for pth in self._buf_dir.glob("*.*"):
                pth.unlink()

            self._buf_dir.rmdir()
            self._buf_dir = None

    def _create_buffer_dir(self):
        """Create a new empty directory

        Returns:
            (None)
        """
        assert self._buf_dir is None  # need to clear it first

        ind = 0
        while Path(f"_tmp_buf_{ind:04d}").exists():
            ind += 1

        self._buf_dir = Path(f"_tmp_buf_{ind:04d}")
        self._buf_dir.mkdir()

    def close(self):
        """Cleanly close the explorer.

        Returns:
            (None)
        """
        self._clear_buffer_dir()
        self._cbz = None

    def set_book(self, pth):
        """Open given book as current.

        Args:
            pth (Path): Path to book to open

        Returns:
            (None)
        """
        assert pth.suffix == ".cbz"

        self._clear_buffer_dir()

        self._pth = pth
        self._cbz = ZipFile(pth, 'r')

    def current_book(self):
        """Path to currently open book.

        Returns:
            (Path)
        """
        return self._pth

    def next_book(self):
        """Open next book in current directory.

        Raises: IndexError if current file is last file in dir.

        Returns:
            (None)
        """
        books = sorted(self._pth.parent.glob("*.cbz"))
        ind = books.index(self._pth)
        if ind == len(books) - 1:
            raise IndexError("Current book is last book in dir")

        self.set_book(books[ind + 1])

    def prev_book(self):
        """Open previous book in current directory.

        Raises: IndexError if current file is first file in dir.

        Returns:
            (None)
        """
        books = sorted(self._pth.parent.glob("*.cbz"))
        ind = books.index(self._pth)
        if ind == 0:
            raise IndexError("Current book is first book in dir")

        self.set_book(books[ind - 1])

    def _buffer_name(self, page, ext):
        """Construct a valid buffer name

        Args:
            page (int): index of page
            ext (str): file extension to use

        Returns:
            (Path)
        """
        return self._buf_dir / f"page{page:05d}.{ext}"

    def _already_bufferized(self, page):
        """Check if page already in buffer.

        Args:
            page (int): index of page to look for

        Returns:
            (Path|None): None if nothing is found
        """
        for ext in im_exts:
            page_pth = self._buffer_name(page, ext)
            if page_pth.exists():
                return page_pth

    def buffer(self, page=0):
        """Extract and write given page into associated buffer.

        Raises: AssertionError if no current book.

        Notes: only perform write operation if page not already buffered.

        Args:
            page (int): index of page to write

        Returns:
            (Path): path to image in buffer
        """
        assert self._pth is not None

        if self._buf_dir is None:
            self._create_buffer_dir()

        page_pth = self._already_bufferized(page)
        if page_pth is not None:
            return page_pth

        pages = sorted([n for n in self._cbz.namelist() if n.split(".")[-1].lower() in im_exts])

        assert 0 <= page < len(pages)

        data = self._cbz.read(pages[page])
        page_pth = self._buffer_name(page, pages[page].split(".")[-1].lower())
        with page_pth.open('wb') as fhw:
            fhw.write(data)

        return page_pth

    def page_number(self):
        """Number of pages in current book.

        Returns:
            (int)
        """
        return len([n for n in self._cbz.namelist() if n.split(".")[-1].lower() in im_exts])

    def open_page(self, page):
        """Read page and return image.

        Raises: UserWarning if bad image format.

        Args:
            page (int): index of page in current book

        Returns:
            (Image)
        """
        pth = self.buffer(page)
        try:
            img = Image.open(str(pth))
        except IOError:
            raise UserWarning(f"Bad image format '{pth}'")

        if img.mode == "RGB":
            img.load()
        else:
            img = img.convert("RGB")
            img.save(str(pth))  # overwrite buffer to avoid doing it each time

        return img

    def save_book(self, pth):
        """Save current book on disk.

        Args:
            pth (Path): path to archive to create

        Returns:
            (None)
        """
        with ZipFile(pth, 'w') as fw:
            for i in range(self.page_number()):
                img = self.open_page(i)
                data = BytesIO()
                img.save(data, 'jpeg')

                info = ZipInfo(f"page{i:04d}.jpg", datetime.now().timetuple()[:6])
                info.compress_type = ZIP_DEFLATED
                fw.writestr(info, data.getvalue())
