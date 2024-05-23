import pandas as pd
import sys, re, base64
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, \
    QTextBrowser, QSlider
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


### GUI ###
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Book Recommendation System")
        self.setGeometry(100, 100, 640, 480)

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
        # maximum value of the slider
        self.slider.setMaximum(20)
        # initial value of the slider
        self.slider.setValue(5)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.show_slider_value)
        self.layout.addWidget(self.slider)

        ## calling show_slider_value so that the initial value
        ## is shown on start screen (otherwise only shown when changed)
        self.show_slider_value(self.slider.value())

        self.submit_button = QPushButton("Recommend books!")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addWidget(self.submit_button)

        self.result_browser = QTextBrowser()
        self.layout.addWidget(self.result_browser)

        self.central_widget.setLayout(self.layout)

    def on_submit(self, value):
        question = self.question_text_edit.toPlainText()
        question_embedding = get_embeddings([question]).numpy()
        question_embedding.shape

        scores, samples = book_review_dataset.get_nearest_examples(
            "embeddings", question_embedding, k=self.slider.value()
        )

        samples_df = pd.DataFrame.from_dict(samples)
        samples_df["scores"] = scores
        samples_df.sort_values("scores", ascending=False, inplace=True)

        result_text = f"You asked: {question}. Here's my recommendation:\n\n"

        html_content = ""
        for _, row in samples_df.iterrows():
            authors = ", ".join(re.findall(r"'(.*?)'", row['authors']))
            category = ", ".join(re.findall(r"'(.*?)'", row['categories']))

            html_content += f'<p><strong>Title:</strong> {row["Title"]}</p>'

            if row['image'] != "-":
                response = requests.get(row["image"])
                image_data = response.content
                encoded_image = base64.b64encode(image_data).decode("utf-8")

                html_content += f'<br><img src="data:image/jpeg;base64,{encoded_image}" style="max-width: 100%; height: auto;"><br><br>'

            html_content += f'<p><strong>Authors:</strong> {authors}</p>'
            html_content += f'<p><strong>Categories:</strong> {category}</p>'
            # Split the summary and review by newline character + enumerate
            summary_paragraphs = [f'<p><strong>Summary {i + 1}:</strong> {line}</p>' for i, line in
                                  enumerate(row["review/summary"].split("\n"))]
            html_content += "".join(summary_paragraphs)
            review_paragraphs = [f'<p><strong>Review {i + 1}:</strong> {line}</p>' for i, line in
                                 enumerate(row["review/text"].split("\n"))]
            html_content += "".join(review_paragraphs)

            html_content += f'<p><strong>Score:</strong> {row["scores"]}</p>'

        self.result_browser.setHtml(html_content)

        self.result_browser.setAlignment(Qt.AlignLeft)
        self.result_browser.setLineWrapMode(QTextBrowser.WidgetWidth)
        self.result_browser.setOpenExternalLinks(True)

    def show_slider_value(self, value):
        self.slider_label.setText(f"Selected number of recommendations: {value}")


if __name__ == "__main__":
    app = 0  # to clean app on restart to avoid kernel crashes
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())