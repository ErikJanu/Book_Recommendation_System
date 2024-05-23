import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download("punkt")

print(stopwords.words('english'))


def remove_stopwords(words):
    filtered = [word for word in words if word not in stopwords.words('english')]
    return filtered


def stem(words):
    return [ps.stem(word) for word in words]


# Initialize Python porter stemmer
ps = PorterStemmer()

# set to potentially improve performance
stop_words = set(stopwords.words('english'))


def preprocess(words):
    #replace full stop with space
    words = re.sub("[.]", ' ', words)
    #remove special characters and numbers
    words = re.sub("[^A-Za-z0-9' ]+", '', words)
    #tokenize
    words = words.split()
    #remove stopwords + stem
    filtered = [word for word in words if word not in stopwords.words('english')]
    return filtered


# batch processing because of dataset size
def process_batch(batch):
    batch['review/summary'] = batch['review/summary'].apply(preprocess)
    batch['review/text'] = batch['review/text'].apply(preprocess)
    batch['title/orig'] = batch['Title']
    batch['title/prep'] = batch['Title'].apply(preprocess)
    return batch


def split_dataframe(df, chunk_size=25):
    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    return chunks


batches = split_dataframe(review_df)

with multiprocessing.Pool() as pool:
    processed_batches = list(tqdm(pool.imap(process_batch, batches), total=len(batches), desc="Processing batches"))

processed_df = pd.concat(processed_batches, ignore_index=True)

# Duplicating the title value for more weight when I later combine it with the review text
prep_review_df['review/summary'] = prep_review_df['review/summary'] + ", " + prep_review_df['review/summary']

# Lowercasing
prep_review_df['final'] = prep_review_df['final'].apply(lambda x: x.lower())

# Removing Stopwords
def remove_stopwords(words):
    filtered = [word for word in words if word not in stopwords.words('english')]
    return filtered

from tqdm import tqdm
#prep_review_df['preprocessed'] = prep_review_df['final'].apply(remove_stopwords)
tqdm.pandas(desc="Processing")
prep_review_df['preprocessed'] = prep_review_df['final'].progress_apply(remove_stopwords)

import multiprocessing

# set to potentially improve performance
stop_words = set(stopwords.words('english'))

def remove_stopwords(words):
    filtered = [word for word in words if word not in stopwords.words('english')]
    return filtered

# batch processing because of dataset size
def process_batch(batch):
    batch['preprocessed'] = batch['final'].apply(remove_stopwords)
    return batch

def split_dataframe(df, chunk_size=50):
    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    return chunks

batches = split_dataframe(prep_review_df)

with multiprocessing.Pool() as pool:
    processed_batches = list(tqdm(pool.imap(process_batch, batches), total=len(batches), desc="Processing batches"))

processed_df = pd.concat(processed_batches, ignore_index=True)

# Removing special characters and punctuation
import re
prep_review_df['final'] = prep_review_df['final'].apply(lambda x: re.sub("[^A-Za-z0-9' ]+", '', x))

# Tokenizing + Lemmatization
import spacy
spacy.cli.download("en_core_web_sm")
spacy_model = spacy.load("en_core_web_sm")

def lemmatize_with_spacy(words):
    doc = spacy_model(" ".join(words))
    return [token.lemma_ for token in doc]

from tqdm import tqdm
tqdm.pandas(desc="Lemmatizing")
prep_review_df['final'] = prep_review_df['final'].progress_apply(lemmatize_with_spacy)

# Tokenizing + Stemming + Counting
import nltk
from nltk.stem import PorterStemmer
nltk.download("punkt")

# Initialize Python porter stemmer
ps = PorterStemmer()

def stem(words):
    return [ps.stem(word) for word in words]

from tqdm import tqdm
tqdm.pandas(desc="Stemming")
prep_review_df['final'] = prep_review_df['final'].progress_apply(stem)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
X = vec.fit_transform(review_df['final'])

count_df = pd.DataFrame(data= X.toarray(), columns = vec.get_feature_names_out())

# Unigrams and Bigram as defaultdict
from collections import defaultdict
from nltk.util import ngrams

# using defaultdict so that I can later just append items to keys whether they exist or not
unigram_index = defaultdict(list)
bigram_index = defaultdict(list)


def save_1_gram(text, idx, category):
    for word in text:
        unigram_index[word].append([idx, category])


def save_2_gram(text, idx, category):
    bigrams = list(ngrams(text, 2))
    for bigram in bigrams:
        bigram_index[" ".join(bigram)].append([idx, category])


# batch processing because of dataset size
def process_batch(batch):
    for idx, row in batch.iterrows():
        # save 1-grams to index
        save_1_gram(row['review/summary'], idx, "review/summary")
        save_1_gram(row['review/text'], idx, "review/text'")
        save_1_gram(row['title/prep'], idx, "title/prep")
        save_1_gram(row['authors'].split(), idx, "authors")

        # save 2-grams to index
        save_2_gram(row['review/summary'], idx, "review/summary")
        save_2_gram(row['review/text'], idx, "review/text'")
        save_2_gram(row['title/prep'], idx, "title/prep")
        save_2_gram(row['authors'].split(), idx, "authors")


def split_dataframe(df, chunk_size=25):
    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    return chunks


batches = split_dataframe(merged_processed_df)

with multiprocessing.Pool() as pool:
    processed_batches = list(tqdm(pool.imap(process_batch, batches), total=len(batches), desc="Indexing batches..."))

