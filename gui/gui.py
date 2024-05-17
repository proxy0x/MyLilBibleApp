from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QComboBox, QApplication, QScrollArea, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import os
import fitz  # PyMuPDF library

class PDFViewer(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("MyLilBibleApp")  # Set window title
        self.setGeometry(100, 100, 800, 750)
        self.current_page = 0
        self.pdf_files = []
        self.selected_file = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.init_ui()

    def init_ui(self):
        # Versions label and dropdown
        version_label = QLabel("Versions:")
        version_label.setStyleSheet("color: white; font-size: 18px;")

        self.version_dropdown = QComboBox()
        self.version_dropdown.setStyleSheet("font-size: 18px;")

        # PDF display area
        self.pdf_label = QLabel()
        self.pdf_label.setStyleSheet("background-color: white; border: 2px solid black;")
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setScaledContents(True)

        # Page number label
        self.page_number_label = QLabel()
        self.page_number_label.setStyleSheet("color: white; font-size: 18px;")

        # Page selection input
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Enter Page Number")
        self.page_input.returnPressed.connect(self.go_to_page)

        # Arrow buttons
        arrow_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀")
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet("font-size: 24px;")
        arrow_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("▶")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet("font-size: 24px;")
        arrow_layout.addWidget(self.next_button)

        # Add UI elements to layout
        self.layout.addWidget(version_label, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.version_dropdown, alignment=Qt.AlignHCenter)

        self.layout.addWidget(self.page_input)  # Add page input field

        # Scroll area for PDF display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.pdf_label)
        self.layout.addWidget(scroll_area)

        self.layout.addWidget(self.page_number_label)  # Add page number label

        self.layout.addLayout(arrow_layout)

        # Initialize and load the JavaScript parser
        self.webview = QWebEngineView()
        self.layout.addWidget(self.webview)
        self.load_js_parser()

        # Apply stylesheet
        self.setStyleSheet("""
        QMainWindow {
            background-color: #212121;
        }
        QLabel {
            color: white;
        }
        QPushButton {
            background-color: #757de8;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 18px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #5d63d6;
        }
        QComboBox {
            border: 2px solid #757de8;
            border-radius: 5px;
            padding: 5px;
            font-size: 18px;
        }
        """)

        self.load_pdf_versions()

    def load_pdf_versions(self):
        self.pdf_files = [file.split(".")[0] for file in os.listdir("data/versions") if file.endswith(".pdf")]
        self.version_dropdown.addItem("Select a version")
        self.version_dropdown.addItems(self.pdf_files)
        self.version_dropdown.currentIndexChanged.connect(self.load_page)

    def load_page(self):
        selected_index = self.version_dropdown.currentIndex()
        if selected_index == 0:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.pdf_label.clear()
            self.page_number_label.clear()
            return

        selected_version = self.version_dropdown.currentText()
        pdf_path = os.path.join("data", "versions", f"{selected_version}.pdf")
        if not os.path.exists(pdf_path):
            return

        try:
            with fitz.open(pdf_path) as doc:
                page = doc.load_page(self.current_page)
                pix = page.get_pixmap()
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap(image)
                self.pdf_label.setPixmap(pixmap)
                self.prev_button.setEnabled(self.current_page > 0)
                self.next_button.setEnabled(self.current_page < len(doc) - 1)
                self.page_number_label.setText(f"Page {self.current_page + 1}/{len(doc)}")
        except Exception as e:
            print("Error:", e)

    def next_page(self):
        self.current_page += 1
        self.load_page()

    def prev_page(self):
        self.current_page -= 1
        self.load_page()

    def go_to_page(self):
        try:
            page_number = int(self.page_input.text())
            selected_version = self.version_dropdown.currentText()
            pdf_path = os.path.join("data", "versions", f"{selected_version}.pdf")
            if not os.path.exists(pdf_path):
                return

            with fitz.open(pdf_path) as doc:
                if 0 < page_number <= len(doc):
                    self.current_page = page_number - 1
                    self.load_page()
                else:
                    QMessageBox.warning(self, "Error", "Invalid page number")
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid page number")

    def load_js_parser(self):
        # Load local HTML file into QWebEngineView
        script_dir = os.path.dirname(__file__)
        html_path = os.path.join(script_dir, 'html', 'bible_verse_search.html')
        html_url = QUrl.fromLocalFile(html_path)
        self.webview.load(html_url)
        self.webview.hide()

        # Establish communication between Python and JavaScript
        self.channel = QWebChannel(self.webview)
        self.channel = QWebChannel(self.webview.page())
        self.webview.page().setWebChannel(self.channel)
        self.channel.registerObject("pythonBridge", self)

        # Load JavaScript parser from file
        script_path = os.path.join(script_dir, 'js', 'en_bcv_parser.js')
        with open(script_path, 'r', encoding='utf-8') as file:
            js_code = file.read()
            self.webview.page().runJavaScript(js_code)

if __name__ == "__main__":
    app = QApplication([])
    window = PDFViewer(app)
    window.show()
    app.exec_()
