from datasets import load_from_disk
from transformers import AutoTokenizer, TFAutoModel


# Following this guide: https://huggingface.co/learn/nlp-course/chapter5/6?fw=tf
# Using this model for semantic search: https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-dot-v1


class Embeddings:
    def __init__(self):
        self.dataset = load_from_disk('book_dataset')
        self.model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")
        self.model = TFAutoModel.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1", from_pt=True)

    def explore_book_dataset(self):
        print(self.dataset[0])
        print(f"Datatype: {type(self.dataset)}")

    def cls_pooling(self, model_output):
        return model_output.last_hidden_state[:, 0]

    def get_embeddings(self, text_list):
        encoded_input = self.tokenizer(
            text_list, padding=True, truncation=True, return_tensors="tf"
        )
        encoded_input = {k: v for k, v in encoded_input.items()}
        model_output = self.model(**encoded_input)
        return self.cls_pooling(model_output)

    def create_and_write_embeddings_to_disk(self):
        # collecting last hidden state for CLS token

        # -------- FIRST PART OF DATASET -----------
        set_of_100_000 = self.dataset.select(range(100000))
        first_hundred_k_dataset = set_of_100_000.map(
            lambda x: {"embeddings": self.get_embeddings(x["text"]).numpy()[0]}
        )
        first_hundred_k_dataset.save_to_disk('first_hundred_k_dataset')

        # -------- SECOND PART OF DATASET -----------
        set_of_2nd_100_000 = self.dataset.select(range(100000, 200000))
        second_hundred_k_dataset = set_of_2nd_100_000.map(
            lambda x: {"embeddings": self.get_embeddings(x["text"]).numpy()[0]}
        )
        second_hundred_k_dataset.save_to_disk('second_hundred_k_dataset')

        # -------- THIRD PART OF DATASET -----------
        third_and_final_books = self.dataset.select(range(200000, 221998))
        third_and_final_dataset = third_and_final_books.map(
            lambda x: {"embeddings": self.get_embeddings(x["text"]).numpy()[0]}
        )
        third_and_final_dataset.save_to_disk('third_and_final_dataset')
