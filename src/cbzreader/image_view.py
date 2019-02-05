import Image
from ImageQt import ImageQt
from PyQt5.QtCore import Qt, SIGNAL
from PyQt5.QtGui import QColor, QLabel, QPainter, QPen, QPixmap


class ImageView(QLabel):
    """Display a single image whose size is adapted to window size
    """

    def __init__(self, *args):
        QLabel.__init__(self, *args)
        self._img = None
        self._pix_none = QPixmap(300, 300)  # pixmap used when image is none
        self._pix_none.fill(QColor(100, 100, 255))
        p = QPainter(self._pix_none)
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(3)
        p.setPen(pen)
        p.drawText(50, 50, "Bad image file format")

        self._ratio = 1.  # format ratio between img size and screen size
        self._transfo = Image.ROTATE_90  # transformation applied
        # to the displayed image

        self._click_start = None  # used to find mouse clicks

        self._knife = None  # tool used to cut an image
        self._knife_pos = (10, 10)

        self._boxes = None  # boxes to display on top of image

        self._hints = False  # display lines for perfect image ratio

        self.setAlignment(Qt.AlignCenter)

    def knife(self):
        return self._knife

    def set_knife(self, knife):
        if self._img is None:
            return

        self._knife = knife
        self._knife_pos = (10, 10)

        if knife is None:
            self.setMouseTracking(False)
        else:
            self.setMouseTracking(True)

        self.update()

    def set_boxes(self, boxes):
        self._boxes = boxes

    def set_image(self, img):
        self._img = img
        self._boxes = None
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

    def pix_pos(self, x, y):
        """Transform widget coordinates in pixmap coordinates
        Return None if coordinates are outside of pixmap
        """
        w = self.width()
        h = self.height()
        pw = self.pixmap().width()
        ph = self.pixmap().height()

        if self._transfo is None:
            px = x - (w - pw) / 2
            if px < 0 or px > pw:
                return None

            py = y - (h - ph) / 2
            if py < 0 or py > ph:
                return None

        elif self._transfo == Image.ROTATE_90:
            px = ph - (y - (h - ph) / 2)
            if px < 0 or px > ph:
                return None

            py = x - (w - pw) / 2
            if py < 0 or py > pw:
                return None

        elif self._transfo == Image.ROTATE_180:
            px = pw - (x - (w - pw) / 2)
            if px < 0 or px > pw:
                return None

            py = ph - (y - (h - ph) / 2)
            if py < 0 or py > ph:
                return None

        elif self._transfo == Image.ROTATE_270:
            px = y - (h - ph) / 2
            if px < 0 or px > ph:
                return None

            py = pw - (x - (w - pw) / 2)
            if py < 0 or py > pw:
                return None

        else:
            raise UserWarning("transfo unknown")

        return px, py

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

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self, event)
        if self._knife is not None:
            return

        self._click_start = event.pos()

    def mouseMoveEvent(self, event):
        if self._knife is None:
            return

        self._knife_pos = (event.pos().x(), event.pos().y())

        self.update()

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self, event)
        if self._knife is not None:
            knife = str(self._knife)
            view_pos = self._knife_pos
            #			self.set_knife(None)

            pix_pos = self.pix_pos(*view_pos)
            if pix_pos is None:
                return

            if knife == "height":
                pos = int(pix_pos[1] / self._ratio)
            elif knife == "width":
                pos = int(pix_pos[0] / self._ratio)
            else:
                return

            print
            "viewpos", view_pos
            print
            "pixpos", pix_pos
            self.emit(SIGNAL("knife"), knife, pos)
            return

        if self._click_start is None:
            return

        if (event.pos() - self._click_start).manhattanLength() < 8:
            self._click_start = None
            if event.button() == Qt.LeftButton:
                self.emit(SIGNAL("click left"))
            else:
                self.emit(SIGNAL("click right"))

    def wheelEvent(self, event):
        QLabel.wheelEvent(self, event)
        self.emit(SIGNAL("wheel"), event.delta() / -120)

    def display_knife(self, painter):
        """Display knife as a line
        """
        if self._knife == "height":
            if self._transfo in (Image.ROTATE_90, Image.ROTATE_270):
                x1 = self._knife_pos[0]
                x2 = x1
                y1 = 0
                y2 = self.height()
            else:
                x1 = 0
                x2 = self.width()
                y1 = self._knife_pos[1]
                y2 = y1
        elif self._knife == "width":  # cut in width
            if self._transfo in (Image.ROTATE_90, Image.ROTATE_270):
                x1 = 0
                x2 = self.width()
                y1 = self._knife_pos[1]
                y2 = y1
            else:
                x1 = self._knife_pos[0]
                x2 = x1
                y1 = 0
                y2 = self.height()

        painter.setPen(QPen(QColor(255, 0, 0)))
        painter.drawLine(x1, y1, x2, y2)

    def display_boxes(self, painter):
        """Draw boxes on top of image
        """
        if self._transfo is not None:
            return

        painter.setPen(QPen(QColor(255, 0, 255)))
        ratio = self._ratio
        dx = (self.width() - self.pixmap().width()) / 2
        dy = (self.height() - self.pixmap().height()) / 2
        for i, (x1, y1, x2, y2) in enumerate(self._boxes):
            x = dx + x1 * ratio
            y = dy + y1 * ratio
            w = (x2 - x1) * ratio
            h = (y2 - y1) * ratio
            painter.drawRect(x, y, w, h)
            painter.drawText(x + 2, y + 10, "%d" % i)

    def display_hints(self, painter):
        """Draw lines to show perfect image ratio
        """
        if self._transfo is not None:
            return

        painter.setPen(QPen(QColor(255, 0, 255)))
        w = self.pixmap().width()
        h = w * 1920 / 1200  # TODO other screen resolution
        painter.drawLine(0, h, self.width(), h)

    def paintEvent(self, event):
        QLabel.paintEvent(self, event)
        p = QPainter(self)

        if self._boxes is not None:
            self.display_boxes(p)

        if self._hints:
            self.display_hints(p)

        if self._knife is not None:
            self.display_knife(p)
