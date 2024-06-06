import pandas as pd
import re
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QApplication, QDialog, QMainWindow, \
    QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QSlider, QHBoxLayout, QScrollArea, QSizePolicy, QDesktopWidget
import requests

from data_processing.Embeddings import Embeddings


def normalize_length(content, length=60):
    return content if len(content) < length else content[:length] + "..."


class MainWindow(QMainWindow):
    def __init__(self, dataset):
        self.embeddings = Embeddings()
        self.recommended_books_dataframe = pd.DataFrame()
        self.dataset = dataset

        super().__init__()

        self.setWindowTitle("Book Recommendation System")
        self.screen_width = QDesktopWidget().screenGeometry().width()
        self.screen_height = QDesktopWidget().screenGeometry().height()
        self.resize(int(self.screen_width * 0.4), int(self.screen_height * 0.4))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.topHLayout = QHBoxLayout()
        self.prompt_text = QLabel()
        self.prompt_text.setText("Enter what you are looking for in a book:")
        self.topHLayout.addWidget(self.prompt_text)
        self.topHLayoutWidget = QWidget()
        self.topHLayoutWidget.setLayout(self.topHLayout)
        self.layout.addWidget(self.topHLayoutWidget)

        self.question_text_edit = QTextEdit()
        self.question_text_edit.setFixedHeight(int(self.height() * 0.15))
        self.question_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(self.question_text_edit)

        self.slider_label = QLabel("")
        self.layout.addWidget(self.slider_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setValue(5)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.show_slider_value)
        self.layout.addWidget(self.slider)

        self.show_slider_value(self.slider.value())

        self.submit_button = QPushButton("Recommend books!")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addWidget(self.submit_button)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.cellDoubleClicked.connect(self.show_info)
        self.layout.addWidget(self.table)

        self.central_widget.setLayout(self.layout)

    def on_submit(self):
        question = self.question_text_edit.toPlainText()
        question_embedding = self.embeddings.get_embeddings([question]).numpy()

        # score appears to be similar to euclidean distance -> the lower the better
        scores, samples = self.dataset.get_nearest_examples(
            "embeddings", question_embedding, k=30
        )

        self.recommended_books_dataframe = pd.DataFrame.from_dict(samples)
        self.recommended_books_dataframe["scores"] = scores
        self.recommended_books_dataframe.sort_values("scores", ascending=True, inplace=True)
        self.recommended_books_dataframe = self.recommended_books_dataframe.head(self.slider.value())

        self.table.clearContents()
        self.table.setColumnCount(2)  # title, author
        self.table.setHorizontalHeaderLabels(["Title", "Author"])
        self.table.setRowCount(len(self.recommended_books_dataframe))

        for idx, row in self.recommended_books_dataframe.iterrows():
            title = row["Title"]
            authors = ", ".join(re.findall(r"'(.*?)'", row['authors']))
            if authors == "":
                authors = "Unknown Author"

            title_item = QTableWidgetItem(title)
            author_item = QTableWidgetItem(authors)
            self.table.setItem(idx, 0, title_item)
            self.table.setItem(idx, 1, author_item)

        self.resize_columns()

    def resize_columns(self):
        max_width = self.table.viewport().size().width()
        self.table.setColumnWidth(0, int(max_width * 0.7))
        self.table.setColumnWidth(1, int(max_width * 0.3))

    def show_slider_value(self, value):
        self.slider_label.setText(f"Selected number of recommendations: {value}")

    def show_info(self, row, column):
        item = self.table.item(row, column)
        if item:
            dialog = self.InfoDialog(row, column, item.text(), self.recommended_books_dataframe, self)
            dialog.exec_()

    class InfoDialog(QDialog):
        def __init__(self, row, column, content, dataframe, parent_window, parent=None):
            super().__init__(parent)
            self.parent_window = parent_window
            self.setWindowTitle("Book Information")
            layout = QVBoxLayout()
            self.resize(int(self.parent_window.screen_width * 0.3), int(self.parent_window.screen_height * 0.4))

            title = normalize_length(dataframe.iloc[row]["Title"])
            authors = ", ".join(re.findall(r"'(.*?)'", dataframe.iloc[row]['authors']))
            if authors == "":
                authors = "Unknown Author"
            authors = normalize_length(authors)

            if dataframe.iloc[row]['image'] != "-":
                response = requests.get(dataframe.iloc[row]['image'])
                image_data = response.content
                pixmap_image = QPixmap()
                pixmap_image.loadFromData(image_data)
                image_label = QLabel()
                image_label.setPixmap(pixmap_image)
                image_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(image_label)

            title_label = QLabel(f"<h2>{title}</h2>")
            author_label = QLabel(f"<h3><i>by {authors}</i></h3>")
            title_label.setAlignment(Qt.AlignCenter)
            author_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            layout.addWidget(author_label)

            # minus 40 to consider padding
            max_width = max(title_label.sizeHint().width(), author_label.sizeHint().width(), self.size().width() - 40)

            if "review/summary" in dataframe.columns and "review/text" in dataframe.columns:
                scroll_area = QScrollArea()
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)

                summaries = dataframe.iloc[row]['review/summary'].split('\n')
                reviews = dataframe.iloc[row]['review/text'].split('\n')
                for i, (summary, review) in enumerate(zip(summaries, reviews), start=1):
                    combined_text = f"<b>{summary}: </b>{review}"
                    combined_label = QLabel(combined_text)
                    combined_label.setTextFormat(Qt.RichText)
                    combined_label.setWordWrap(True)
                    combined_label.hasScaledContents()
                    combined_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    # *0.95 to leave some room for scrollbar etc.
                    combined_label.setFixedWidth(int(max_width * 0.95))
                    scroll_layout.addWidget(combined_label)

                scroll_content.setLayout(scroll_layout)
                scroll_area.setWidget(scroll_content)
                layout.addWidget(scroll_area)

            self.setLayout(layout)
