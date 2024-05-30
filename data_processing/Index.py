from datasets import load_from_disk, concatenate_datasets, Dataset
from pyarrow import Table


class Index():
    def __init__(self):
        first_100k_dataset = load_from_disk('data/first_hundred_k_dataset')
        first_100k_dataset = load_from_disk('data/first_hundred_k_dataset')
        second_100k_dataset = load_from_disk('data/second_hundred_k_dataset')
        last_22k_dataset = load_from_disk('data/third_and_final_dataset')
        full_data = concatenate_datasets([first_100k_dataset, second_100k_dataset, last_22k_dataset])
        full_data.add_faiss_index(column="embeddings")
        self.complete_dataset = full_data

    def get_indexed_dataset(self):
        return self.complete_dataset
