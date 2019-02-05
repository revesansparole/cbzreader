from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QLabel


class ImageView(QLabel):
    """Display a single image whose size is adapted to window size
    """

    def __init__(self, *args):
        super().__init__(*args)

        self._img = None
        self._pix_none = QPixmap(300, 300)  # pixmap used when image is none
        self._pix_none.fill(QColor(100, 100, 255))
        p = QPainter(self._pix_none)
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(3)
        p.setPen(pen)
        p.drawText(50, 50, "Bad image file format")

        self._ratio = 1.  # format ratio between img size and screen size
        self._transfo = Image.ROTATE_90  # transformation applied to the displayed image

        self.setAlignment(Qt.AlignCenter)

    def set_image(self, img):
        self._img = img
        self.update_pixmap()

    def transfo(self):
        return self._transfo

    def set_transfo(self, transfo):
        self._transfo = transfo

    def rotate(self):
        """Rotate view 90deg counter clockwise
        """
        if self._transfo is None:
            self._transfo = Image.ROTATE_90
        elif self._transfo == Image.ROTATE_90:
            self._transfo = Image.ROTATE_180
        elif self._transfo == Image.ROTATE_180:
            self._transfo = Image.ROTATE_270
        elif self._transfo == Image.ROTATE_270:
            self._transfo = None
        else:
            raise UserWarning("how did you reach this point? possible")

        self.update_pixmap()


    def update_pixmap(self):
        if self._img is None:
            self.setPixmap(self._pix_none)
        else:
            if self._transfo is None:
                img = self._img
            else:
                img = self._img.transpose(self._transfo)

            # find scale to fit screen
            w, h = img.size
            wa = self.width() / float(w)
            ha = self.height() / float(h)
            ratio = min(wa, ha)
            self._ratio = ratio

            # create Qt image
            iq = ImageQt(img)
            pix = QPixmap.fromImage(iq.scaled(int(w * ratio)
                                              , int(h * ratio)
                                              , Qt.IgnoreAspectRatio
                                              , Qt.SmoothTransformation))

            self.setPixmap(pix)

    def resizeEvent(self, event):
        QLabel.resizeEvent(self, event)
        self.update_pixmap()

    def paintEvent(self, event):
        QLabel.paintEvent(self, event)
