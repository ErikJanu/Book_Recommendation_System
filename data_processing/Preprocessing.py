from data_processing.Embeddings import Embeddings
from data_processing.BookReviews import BookReviews
from ReviewsWithMetadata import ReviewsWithMetadata

book_reviews = BookReviews()
book_reviews.explore_reviews()
book_reviews.group_by_book()

reviews_and_metadata = ReviewsWithMetadata(book_reviews)
reviews_and_metadata.explore_data()
reviews_and_metadata.create_merged_dataset()
reviews_and_metadata.write_merged_data_to_file()
reviews_and_metadata.create_huggingface_dataset()
reviews_and_metadata.save_huggingface_dataset_to_disk()


embeddings = Embeddings()
embeddings.create_and_write_embeddings_to_disk()