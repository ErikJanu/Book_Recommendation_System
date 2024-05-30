import pandas as pd
import datetime

pd.set_option('display.max_colwidth', None)


class BookReviews:
    def __init__(self):
        self.review_df = pd.read_csv('../data/Books_rating.csv')
        self.grouped_df = pd.DataFrame()

    def explore_reviews(self):

        # Let's look at some reviews
        print(self.review_df.head())
        print(self.review_df.iloc[20])
        print(self.review_df.loc[self.review_df['Id'] == "0826414346"])

        # Find out when these reviews were written
        print(f"Entry with newest review: {self.review_df.loc[self.review_df['review/time'].idxmax()]}")
        print(f"Newest review was written on: {print(datetime.datetime.utcfromtimestamp(1362355200))}")
        print(f"10 oldest reviews were written: {self.review_df['review/time'].nsmallest(10)}")
        # result: -1, --> lets look for oldest actual date
        print(f"Lowest value (>-1) is: {self.review_df['review/time'][self.review_df['review/time'] > -1].min()}")
        min_time = self.review_df['review/time'][self.review_df['review/time'] > -1]
        min_time = datetime.datetime.utcfromtimestamp(min_time.min())

        print(f"And in time that is: {min_time}")
        print("Result: The reviews were written between 1995 and 2013")

        print(f"Shape of the dataset: {self.review_df.shape}")
        self.review_df = self.review_df.drop(['User_id', 'profileName', 'Price'], axis=1)
        self.review_df = self.review_df.drop(['review/helpfulness', 'review/score', 'review/time'], axis=1)
        print(f"Dataset after removing some columns: {self.review_df.head()}")

    def group_by_book(self):
        # checking if books with the same id have different titles with help of ChatGPT
        def id_title_confirmation():
            title_counts = self.review_df.groupby('Id')['Title'].nunique()

            # Checking if there are any IDs with more than one unique title
            different_titles_ids = title_counts[title_counts > 1].index.tolist()

            if different_titles_ids:
                print("There are books with the same ID but different titles.")
                for book_id in different_titles_ids:
                    print(f"ID: {book_id}, Titles: {self.review_df[self.review_df['Id'] == book_id]['title'].unique()}")
            else:
                print("All books with the same ID have the same title.")

        id_title_confirmation()
        self.review_df['review/summary'] = self.review_df['review/summary'].fillna('')
        self.review_df['review/text'] = self.review_df['review/text'].fillna('')

        # Join reviews and summaries (when there are multiple for one book) with newline
        self.grouped_df = self.review_df.groupby('Id').agg(
            {'Title': 'first', 'review/summary': '\n'.join, 'review/text': '\n'.join})
        print(f"Grouped DataFrame: {self.grouped_df.head()}")
