from googleapiclient.discovery import build

import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
import string
import collections
from sklearn.feature_extraction.text import TfidfVectorizer
# nltk.download()

import numpy as np

import sys

# $ python IR.py query precision
query = sys.argv[1].split()
origin_q = query
precision = float(sys.argv[2])


# Tokenize, take the stem of the words, remove stop words
def get_tokens(text):
    lowers = text.lower()
    # remove the punctuation using the character deletion step of translate
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    no_punctuation = lowers.translate(remove_punctuation_map)
    tokens = nltk.word_tokenize(no_punctuation)
    return tokens


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


while True:
    # Retrieve top-10 Relevant Results From Google
    service = build("customsearch", "v1", developerKey="AIzaSyD7LtB-16PwWj4vrPkq3BmFonIk4oXaKi4")
    res = service.cse().list(q=' '.join(query), cx='011699874424413628847:oswjbylewld', ).execute()

    # count the number of relevant results
    cnt = 0
    # store relevant results, (and its index in the retreival list, type: [(url1, index1), (url2, index2), ...])
    URL = []
    TEXT = []

    for i in range(len(res['items'])):
        print(i + 1, 'Title: ', res['items'][i]['title'], '\n')
        print('URL: ', res['items'][i]['link'], '\n')
        print('Description: ', res['items'][i]['snippet'], '\n')
        print('\n\n')
        reply = input("Relevant (Y/N)?")
        if reply == 'Y':
            URL.append((res['items'][i]['link'], i))
            TEXT.append(res['items'][i]['snippet'])
            cnt += 1

    if cnt >= precision * 10:
        print('FEEDBACK SUMMARY\n')
        print('Query: ', origin_q, '\n')
        print('Precision: ', cnt / 10, '\n')
        print('Desired precision reached, done\n')
        break
    elif cnt == 0:
        print('FEEDBACK SUMMARY\n')
        print('Query: ', origin_q, '\n')
        print('Precision: ', cnt / 10, '\n')
        print('No relevant result, terminate\n')
        break
    else:
        print('FEEDBACK SUMMARY\n')
        print('Query: ', origin_q, '\n')
        print('Current Query: ', query, '\n')
        print('Precision: ', cnt / 10, '\n')
        print('Not yet reach desired precision, continue\n')

    # Retrieve website context
    for i in range(len(URL)):
        req = urllib.request.Request(URL[i][0], headers={'User-Agent': 'Mozilla/5.0'})
        # If the access being denied, append the short description to TEXT
        try:
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()  # rip it out

            # get text
            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            TEXT.append(text)
        except HTTPError or TimeoutError:
            TEXT.append(res['items'][URL[i][1]]['snippet'])

    # Tokenize the context
    TOKENS = [get_tokens(text) for text in TEXT]
    FILTERED = [[w for w in tokens if not w in stopwords.words('english')] for tokens in TOKENS]
    stemmer = PorterStemmer()
    STEMMED = [stem_tokens(filtered, stemmer) for filtered in FILTERED]
    corpus = [' '.join(stemmed) for stemmed in STEMMED]

    # reserve original words, so that we can add unprocessed word back to the query
    bag_of_words = []
    for filtered in FILTERED:
        bag_of_words.extend(filtered)
    count = collections.Counter(bag_of_words)

    # obtain tf-idf matrix, row = number of documents, column = number of tokens (words)
    vectorizer = TfidfVectorizer(min_df=1)
    vectorizer.fit_transform(corpus)
    feature_name = vectorizer.get_feature_names()
    tfidf = vectorizer.fit_transform(corpus).toarray()

    # find candidate word by choosing the token with highest summation value over all the document
    # if this token already exists in the query, take the next highest one
    # from the origin word collection, choose the most frequent word related to this token
    flatten = np.sum(tfidf, axis=0)
    found_new_word = False
    while not found_new_word:
        cand_idx = flatten.argmax()
        cand_root = feature_name[cand_idx]
        if any(q.startswith(cand_root) for q in query):
            flatten = np.delete(flatten, cand_idx)
            continue
        for word, freq in count.most_common(len(count)):
            if word.startswith(cand_root):
                query.append(word)
                break
        found_new_word = True
    

