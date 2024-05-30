import pandas as pd
import sys, re, base64, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, \
    QTextBrowser, QSlider, QProgressBar, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from transformers import AutoTokenizer, TFAutoModel

model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = TFAutoModel.from_pretrained(model_ckpt, from_pt=True)


### FOR EMBEDDING THE QUERY ###
def cls_pooling(model_output):
    return model_output.last_hidden_state[:, 0]


def get_embeddings(text_list):
    encoded_input = tokenizer(
        text_list, padding=True, truncation=True, return_tensors="tf"
    )
    encoded_input = {k: v for k, v in encoded_input.items()}
    model_output = model(**encoded_input)
    return cls_pooling(model_output)


### gui ###
class BookWidget(QWidget):
    def __init__(self, book):
        super(BookWidget, self).__init__()
        maxTitleLength = 25

        self.layout = QHBoxLayout()

        # Prepare the HTML content
        title = book["Title"]
        if len(title) > maxTitleLength:
            title = title[:maxTitleLength] + "..."
        authors = ", ".join(re.findall(r"'(.*?)'", book['authors']))

        # Fetch and encode image if available
        if book['image'] != "-":
            response = requests.get(book['image'])
            image_data = response.content
            pixmap_image = QPixmap()
            pixmap_image.loadFromData(image_data)

            self.image_label = QLabel()
            self.image_label.setPixmap(pixmap_image)
            self.layout.addWidget(self.image_label)

        self.title = QLabel(title)
        self.authors = QLabel(authors)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.authors)

        # Set the layout for the BookWidget
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Book Recommendation System")
        self.setGeometry(300, 300, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.prompt_text = QLabel()
        self.prompt_text.setText("Enter what you are looking for in a book:")
        self.layout.addWidget(self.prompt_text)

        self.question_text_edit = QTextEdit()
        self.layout.addWidget(self.question_text_edit)
        self.question_text_edit.setFixedHeight(50)

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

        self.bar = QProgressBar(self)
        self.bar.setValue(0)
        self.bar.setAlignment(Qt.AlignCenter)
        self.bar.setStyleSheet("QProgressBar "
                               "{"
                               "border: solid grey;"
                               "border-radius: 15px;"
                               "color: black;"
                               "}"
                               "QProgressBar::chunk "
                               "{"
                               "background-color: #05B8CC;"
                               "border-radius: 15px;"
                               "}")
        self.progress_max = 100
        self.bar.setMaximum(self.progress_max)
        self.layout.addWidget(self.bar)

        self.result_scroll_area = QScrollArea()
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_widget.setLayout(self.result_layout)
        self.result_scroll_area.setWidget(self.result_widget)
        self.result_scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.result_scroll_area)

        self.central_widget.setLayout(self.layout)

    def on_submit(self):
        self.bar.setValue(0)
        total_steps = 10
        question = self.question_text_edit.toPlainText()
        question_embedding = get_embeddings([question]).numpy()

        self.update_progress(1, total_steps)

        scores, samples = book_review_dataset.get_nearest_examples(
            "embeddings", question_embedding, k=20
        )

        self.update_progress(random.randint(0, 30) / 10, total_steps)
        samples_df = pd.DataFrame.from_dict(samples)
        self.update_progress(random.randint(31, 60) / 10, total_steps)
        samples_df["scores"] = scores
        samples_df.sort_values("scores", ascending=False, inplace=True)
        self.update_progress(random.randint(61, 90) / 10, total_steps)
        samples_df = samples_df.head(self.slider.value())

        for i in reversed(range(self.result_layout.count())):
            widget_to_remove = self.result_layout.itemAt(i).widget()
            self.result_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        for idx, row in samples_df.iterrows():
            book_widget = BookWidget(row)
            self.result_layout.addWidget(book_widget)

        self.update_progress(total_steps, total_steps)

    def show_slider_value(self, value):
        self.slider_label.setText(f"Selected number of recommendations: {value}")

    def update_progress(self, step, total_steps):
        progress_value = int((step / total_steps) * self.progress_max)
        self.bar.setValue(progress_value)
        QApplication.processEvents()


if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())