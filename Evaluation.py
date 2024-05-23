import pandas as pd
from Embeddings import Embeddings
from Index import Index

embeddings = Embeddings()
golden_df = pd.read_csv('golden_dataset.csv', sep=';')
# creating list of all titles
all_titles = [golden_df["Title 1"], golden_df["Title 2"], golden_df["Title 3"], golden_df["Title 4"], golden_df["Title 5"]]
all_titles = pd.concat(all_titles).tolist()
print(all_titles)

all_questions = [golden_df["search phrase to use"]]
all_questions = pd.concat(all_questions).tolist()
print(all_questions)

score = 0

for search_phrase in all_questions:
    question_embedding = embeddings.get_embeddings([search_phrase]).numpy()
    scores, samples = Index().get_indexed_dataset().get_nearest_examples(
        "embeddings", question_embedding, k=30
    )

    recommended_books_dataframe = pd.DataFrame.from_dict(samples)
    recommended_books_dataframe["scores"] = scores
    recommended_books_dataframe.sort_values("scores", ascending=True, inplace=True)
    # checking first 20 results:
    recommended_books_dataframe = recommended_books_dataframe.head(20)

    for idx, row in recommended_books_dataframe.iterrows():
        if row["Title"] in all_titles:
            print(f"Found: {search_phrase} result: {row['Title']} \n")
            score += 1

print(f"***Maximum score possible: 5 results, 9 questions --> 45***")
print(f"Actual score: {score}")