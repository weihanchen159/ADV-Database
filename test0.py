import nltk
import math
import string
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem.porter import *
from sklearn.feature_extraction.text import TfidfVectorizer





text1 = "Python is a 2000 made-for-TV horror movie directed by Richard \
Clabaugh. The film features several cult favorite actors, including William \
Zabka of The Karate Kid fame, Wil Wheaton, Casper Van Dien, Jenny McCarthy, \
Keith Coogan, Robert Englund (best known for his role as Freddy Krueger in the \
A Nightmare on Elm Street series of films), Dana Barron, David Bowe, and Sean \
Whalen. The film concerns a genetically engineered snake, a python, that \
escapes and unleashes itself on a small town. It includes the classic final\
girl scenario evident in films like Friday the 13th. It was filmed in Los Angeles, \
 California and Malibu, California. Python was followed by two sequels: Python \
 II (2002) and Boa vs. Python (2004), both also made-for-TV films."

text2 = "Python, from the Greek word (πύθων/πύθωνας), is a genus of \
nonvenomous pythons[2] found in Africa and Asia. Currently, 7 species are \
recognised.[2] A member of this genus, P. reticulatus, is among the longest \
snakes known."

text3 = "The Colt Python is a .357 Magnum caliber revolver formerly \
manufactured by Colt's Manufacturing Company of Hartford, Connecticut. \
It is sometimes referred to as a \"Combat Magnum\".[1] It was first introduced \
in 1955, the same year as Smith &amp; Wesson's M29 .44 Magnum. The now discontinued \
Colt Python targeted the premium revolver market segment. Some firearm \
collectors and writers such as Jeff Cooper, Ian V. Hogg, Chuck Hawks, Leroy \
Thompson, Renee Smeets and Martin Dougherty have described the Python as the \
finest production revolver ever made."

# def get_tokens(text):
#     lowers = text.lower()
#     #remove the punctuation using the character deletion step of translate
#     remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
#     no_punctuation = lowers.translate(remove_punctuation_map)
#     tokens = nltk.word_tokenize(no_punctuation)
#     return tokens

# tokens = get_tokens(text1)
# tokens = get_tokens(text1)
# count = Counter(tokens)
# #print (count.most_common(10))
#
# def stem_tokens(tokens, stemmer):
#     stemmed = []
#     for item in tokens:
#         stemmed.append(stemmer.stem(item))
#     return stemmed
#
# tokens = get_tokens(text1)
# filtered = [w for w in tokens if not w in stopwords.words('english')]
# stemmer = PorterStemmer()
# stemmed = stem_tokens(filtered, stemmer)
# count = Counter(stemmed)
# print(count)
corpus = [text1,text2,text3]
vectorizer = TfidfVectorizer(min_df=1,stop_words='english')
vectorizer.fit_transform(corpus)
t1 = vectorizer.get_feature_names()
t2 = vectorizer.fit_transform(corpus).toarray()
print(vectorizer)
res = t2[0]
for i in range(1,len(t2)):
    res += t2[i]
nums = list(res)
temp=[]
Inf = 0
for i in range(10):
  temp.append(nums.index(max(nums)))
  nums[nums.index(max(nums))]=Inf
temp.sort()
print(temp)
result = []
for i in range(len(temp)):
    result.append(t1[temp[i]])
result.reverse()
print(result)
