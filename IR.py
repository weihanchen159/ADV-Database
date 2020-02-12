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
#nltk.download()

# Retrieve top-10 Relevant Results From Google
service = build("customsearch", "v1", developerKey="AIzaSyBKlE390a0krI3_Oe-zk-_Pdf7J0J7Oo1I")
    
res = service.cse().list(q='lectures', cx='000568897140034501999:kyspcqzrszq',).execute()

URL = []
for i in range(len(res['items'])):
    URL.append(res['items'][i]['link'])

# Retrieve website context
TEXT = []
for i in range(len(URL)):
    req = urllib.request.Request(URL[i], headers={'User-Agent': 'Mozilla/5.0'})
    #html = urllib.request.urlopen(url).read()
    try:
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html)
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()
    
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        TEXT.append(text)
    except HTTPError:
        TEXT.append(res['items'][i]['snippet'])

# Tokenize, take the stem of the words, remove stop words
def get_tokens(text):
    lowers = text.lower()
    #remove the punctuation using the character deletion step of translate
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    no_punctuation = lowers.translate(remove_punctuation_map)
    tokens = nltk.word_tokenize(no_punctuation)
    return tokens

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

TOKENS = [get_tokens(text) for text in TEXT]
FILTERED = [[w for w in tokens if not w in stopwords.words('english')] for tokens in TOKENS]
stemmer = PorterStemmer()
STEMMED = [stem_tokens(filtered, stemmer) for filtered in FILTERED]
corpus = [' '.join(stemmed) for stemmed in STEMMED]

vectorizer = TfidfVectorizer(min_df=1)
vectorizer.fit_transform(corpus)
feature_name = vectorizer.get_feature_names()
tfidf = vectorizer.fit_transform(corpus).toarray()
