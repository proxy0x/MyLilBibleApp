import sys
from PyQt5.QtWidgets import QApplication
from gui.gui import PDFViewer

def main():
    app = QApplication(sys.argv)
    window = PDFViewer(app)  # Pass app to PDFViewer
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

