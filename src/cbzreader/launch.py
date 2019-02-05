from PyQt5.QtGui import QApplication

from .cbz_reader import CBZReader


def read(cbz_file):
    qapp = QApplication([])

    reader = CBZReader(cbz_file)

    reader.show()

    qapp.exec_()


def launch():
    from sys import argv
    if len(argv) == 1:
        filename = None
    else:
        filename = argv[1]

    read(filename)


if __name__ == '__main__':
    launch()
