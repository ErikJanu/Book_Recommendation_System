import sqlite3
sql_db = sqlite3.connect('book_index.db')

cursor = sql_db.cursor()

# Create table for 1-grams
cursor.execute('''CREATE TABLE IF NOT EXISTS unigrams (
                    unigram TEXT PRIMARY KEY,
                    origin TEXT,
                    category TEXT,
                    book_id INTEGER)''')

# Create table for 2-grams
cursor.execute('''CREATE TABLE IF NOT EXISTS bigrams (
                    book_id INTEGER PRIMARY KEY,
                    bigram TEXT,
                    origin TEXT,
                    category TEXT)''')

sql_db.commit()


def save_to_db(row):
    category = " ".join(re.findall(r"'(.*?)'", row['categories']))
    authors = re.findall(r"'(.*?)'", row['authors'])
    book_id = row['Id']

    def book_id_exists():
        if book_id in book_ids:
            return True
        else:
            return False

    def save_authors(author_names, origin):
        for author in author_names:
            cursor.execute("INSERT INTO unigrams (book_id, unigram, origin, category) VALUES (?, ?, ?, ?)",
                           (book_id, author, origin, category))

    def save_unigrams(text, origin):
        words = text.split()
        for word in words:
            word = re.sub("[^\w\s]+", "", word)
            if len(word) < 1:
                break
            cursor.execute("INSERT INTO unigrams (unigram, origin, category, book_id) VALUES (?, ?, ?, ?)",
                           (word, origin, category, book_id))

    def save_bigrams(text, origin):
        text = re.sub("[^\w\s]", "", text)
        # if len(word) to avoid empty strings
        words = [word for word in text.split() if len(word)]
        bigrams = [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]
        for bigram in bigrams:
            bigram = re.sub("[^\w\s]+", "", bigram)
            cursor.execute("INSERT INTO bigrams (bigram, origin, category, book_id) VALUES (?, ?, ?, ?)",
                           (bigram, origin, category, book_id))

    ## saving unigrams and bigrams
    save_unigrams(row['review/summary'], "review/summary")
    save_unigrams(row['review/text'], "review/text")

    save_bigrams(row['review/summary'], "review/summary")
    save_bigrams(row['review/text'], "review/text")

    if not book_id_exists():
        save_authors(authors, "author")

        save_unigrams(row['description'], "description")
        save_unigrams(row['title/prep'], "title/prep")

        save_bigrams(row['description'], "description")
        save_bigrams(row['title/prep'], "title/prep")

    book_ids.append(book_id)

    sql_db.commit()

total_iterations = len(merged_processed_df)

for idx, row in tqdm(merged_processed_df.iterrows(), total=total_iterations, desc="Saving index to DB..."):
        save_to_db(row)

cursor.close()
sql_db.close()


# REVERSE!!!!! INDEX

import sqlite3
sql_db = sqlite3.connect('book_index.db')

cursor = sql_db.cursor()

# Create table for books
cursor.execute('''CREATE TABLE IF NOT EXISTS tblBooks (
                    book_id TEXT PRIMARY KEY,
                    title TEXT,
                    authors TEXT,
                    category TEXT NULL,
                    imagelink TEXT NULL,
                    description_prep TEXT NULL,
                    title_prep TEXT)''')

# Create table for unigrams
cursor.execute('''CREATE TABLE IF NOT EXISTS tblUnigrams (
                    unigram_id INTEGER PRIMARY KEY,
                    unigram_text TEXT UNIQUE)''')

# Create table for unigrams index
cursor.execute('''CREATE TABLE IF NOT EXISTS tblUnigramIndex (
                    uni_index_id INTEGER PRIMARY KEY,
                    unigram_id INTEGER,
                    book_id TEXT,
                    unigram_origin TEXT,
                    FOREIGN KEY (unigram_id) REFERENCES tblUnigrams(unigram_id),
                    FOREIGN KEY (book_id) REFERENCES tblBooks(book_id))''')

# Create table for bigrams
cursor.execute('''CREATE TABLE IF NOT EXISTS tblBigrams (
                    bigram_id INTEGER PRIMARY KEY,
                    bigram_text TEXT UNIQUE)''')

# Create table for bigrams index
cursor.execute('''CREATE TABLE IF NOT EXISTS tblBigramIndex (
                    bi_index_id INTEGER PRIMARY KEY,
                    bigram_id INTEGER,
                    book_id TEXT,
                    bigram_origin TEXT,
                    FOREIGN KEY (bigram_id) REFERENCES tblBigrams(bigram_id),
                    FOREIGN KEY (book_id) REFERENCES tblBooks(book_id))''')

sql_db.commit()


def save_to_db(row):
    unigram_id = 0
    bigram_id = 0

    def save_book():
        if row['Id'] not in book_ids:
            authors = ", ".join(re.findall(r"'(.*?)'", row['authors']))
            category = ", ".join(re.findall(r"'(.*?)'", row['categories']))
            cursor.execute(
                "INSERT OR IGNORE INTO tblBooks (book_id, title, authors, category, imagelink) VALUES (?, ?, ?, ?, ?)",
                (row['Id'], row['Title'], authors, category, row['image']))

            if row['description'] != "-":
                save_unigrams(row['description'], "description")
            save_unigrams(row['title/prep'], "title/prep")
            save_bigrams(row['description'], "description")
            save_bigrams(row['title/prep'], "title/prep")

            book_ids.append(row['Id'])

    def save_unigrams(text, origin):
        words = text.split()
        for word in words:
            word = re.sub("[^\w\s]+", "", word)
            if len(word) < 1:
                break
            # save to tblUnigram
            cursor.execute("INSERT OR IGNORE INTO tblUnigrams (unigram_text) VALUES (?)", (word,))
            # save to tblUnigramIndex
            cursor.execute("SELECT unigram_id FROM tblUnigrams WHERE unigram_text = (?)", (word,))
            unigram_id = cursor.fetchone()
            # unigram_id[0] because curser.fetchone() retrieves tuple
            cursor.execute("INSERT INTO tblUnigramIndex (unigram_id, book_id, unigram_origin) VALUES (?, ?, ?)",
                           (unigram_id[0], row['Id'], origin))

    def save_bigrams(text, origin):
        text = re.sub("[^\w\s]", "", text)
        # if len(word) to avoid empty strings
        words = [word for word in text.split() if len(word)]
        bigrams = [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]
        # save to tblBigram
        for bigram in bigrams:
            bigram = re.sub("[^\w\s]+", "", bigram)
            cursor.execute("INSERT OR IGNORE INTO tblBigrams (bigram_text) VALUES (?)", (bigram,))
            # save to tblBigramIndex
            cursor.execute("SELECT bigram_id FROM tblBigrams WHERE bigram_text = (?)", (bigram,))
            bigram_id = cursor.fetchone()
            # bigram_id[0] because curser.fetchone() retrieves tuple
            cursor.execute("INSERT INTO tblBigramIndex (bigram_id, book_id, bigram_origin) VALUES (?, ?, ?)",
                           (bigram_id[0], row['Id'], origin))

    # saving book information
    save_book()

    ## saving unigrams and bigrams
    save_unigrams(row['review/summary'], "review/summary")
    save_unigrams(row['review/text'], "review/text")

    save_bigrams(row['review/summary'], "review/summary")
    save_bigrams(row['review/text'], "review/text")

    sql_db.commit()

total_iterations = len(merged_processed_df)

for idx, row in tqdm(merged_processed_df.iterrows(), total=total_iterations, desc="Saving index to DB..."):
    save_to_db(row)

cursor.close()
sql_db.close()
