# :book: Book Recommendation System :books:

This project uses book reviews from [this Kaggle dataset](https://www.kaggle.com/datasets/mohamedbakhet/amazon-books-reviews) for Book recommendations. A simple GUI asks for a query so that a (modifiable) number of books is recommended. By double-clicking on a book title or author, reviews will be shown in an additional window.

 
# Requirements
- Poetry
- Python 3.11

# Additional data
Files not included in this repository:
- The Kaggle Dataset
- The Embedded dataset

# To create the Embedded dataset:
- Download Kaggle dataset
- Run Preprocessing.py (will take several hours)

# Usage
In the project directory do:
- poetry shell
- poetry install
- python3 Main.py to run the program *or* run the Main.py in an IDE such as PyCharm.