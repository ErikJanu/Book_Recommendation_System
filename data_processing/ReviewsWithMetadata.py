import pandas as pd
from datasets import Dataset


class ReviewsWithMetadata:
    def __init__(self, book_review_data):
        self.book_reviews = book_review_data
        self.metadata = pd.read_csv('data/books_data.csv')
        self.books_and_metadata = pd.DataFrame()
        self.book_dataset = None

    def explore_data(self):
        print(f"Shape of the grouped dataframe: {self.book_reviews.shape}")
        print(f"Metadata: {self.metadata.head()}")
        print(f"Metadata example: {self.metadata.iloc[20]}")

    def create_merged_dataset(self):
        self.books_and_metadata = pd.merge(self.book_reviews, self.metadata, how='left', on='Title')
        print(f"First look at merged data: {self.books_and_metadata.head()}")
        # drop information not needed
        self.books_and_metadata = self.books_and_metadata.drop(
            ['ratingsCount', 'infoLink', 'publishedDate', 'publisher', 'previewLink'], axis=1)
        # fill NA rows with "-"
        self.books_and_metadata = self.books_and_metadata.fillna("-")
        print(f"Final merged dataset: {self.books_and_metadata.head()}")

    def write_merged_data_to_file(self):
        self.books_and_metadata.to_csv('data/book_reviews_and_metadata_grouped.csv', encoding='utf-8', index=False)

    def create_huggingface_dataset(self):
        def concatenate_text(examples):
            return {
                "text": examples["Title"]
                + " \n "
                + examples["review/summary"]
                + " \n "
                + examples["review/text"]
                + " \n "
                + examples["description"]
                + " \n "
                + examples["authors"]
                + " \n "
                + examples["categories"]
            }

        self.book_dataset = Dataset.from_pandas(self.books_and_metadata)
        self.book_dataset = self.book_dataset.map(concatenate_text)

    def save_huggingface_dataset_to_disk(self):
        self.book_dataset.save_to_disk('data/book_dataset')
