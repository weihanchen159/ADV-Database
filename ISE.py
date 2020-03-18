from googleapiclient.discovery import build

import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

from stanfordnlp.server import CoreNLPClient

import sys

# 1 = per:schools_attended, 2 = per:employee_or_member_of, 3 = per:cities_of_residence, 4 = org:top_members_employees
r = sys.argv[1]
# Extraction Confidence Threshold: 0-1
t = float(sys.argv[2])
# Seed Query
s = sys.argv[3]
# Number of tuples that we request in the output
k = int(sys.argv[4])

relation = {'1':'per:schools_attended', '2':'per:employee_or_member_of', '3':'per:cities_of_residence', '4':'org:top_members_employees'}
required_entity = {'per:schools_attended':['ORGANIZATION', 'PERSON'], 'per:employee_or_member_of':['ORGANIZATION', 'PERSON'], 'per:cities_of_residence':['PERSON', ('LOCATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY')], 'org:top_members_employees':['ORGANIZATION', 'PERSON']}
r = relation[r]
required_entity = required_entity[r]

print('Parameters:\n')
print('Relation = ', r, '\n')
print('Threshold = ', t, '\n')
print('Query = ', s, '\n')
print('# of Tuples = ', k, '\n')
print('Loading necessary libraries; This should take a minute or so ...\n')

with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner'], timeout=300000, memory='4G', endpoint="http://localhost:9000") as pipeline1:
	with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner','depparse', 'coref', 'kbp'], timeout=300000, memory='4G', endpoint="http://localhost:9001") as pipeline2:
		query = s
		iter = 0
		res = {}
		Q_set = set()
		Q_set.add(query)
		URL_set = set()
		while len(res) < 10:
			print('=========== Iteration: ',iter,' - Query: ',query,' ===========\n')
			# Retrieve top-10 Relevant Results From Google
			service = build("customsearch", "v1", developerKey="AIzaSyD7LtB-16PwWj4vrPkq3BmFonIk4oXaKi4")
			search_res = service.cse().list(q=query, cx='011699874424413628847:oswjbylewld', ).execute()
			for i in range(len(search_res['items'])):
				URL = search_res['items'][i]['link']
				print('URL (',i+1,' / 10):', URL, '\n')
				if URL in URL_set:
					print('Already seen this URL, skip...')
					continue
				URL_set.add(URL)
				print('Fetching text from url ...\n')
				req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
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
					text = ' '.join(chunk for chunk in chunks if chunk)
					print('Truncating webpage text from size (num characters) ', len(text), ' to 20000 ...\n')
					text = text[:20000]
				except HTTPError or TimeoutError:
					print('Unable to fetch URL. Continuing.\n')
					continue
				print('Webpage length (num characters): ', len(text), '\n')
				print('Annotating the webpage using [tokenize, ssplit, pos, lemma, ner] annotators ...\n')
				ann = pipeline1.annotate(text)
				print('Extracted ', len(ann.sentence) ,' sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...\n')
				cnt_kbp = 0
				cnt_effect = 0
				for j in range(len(ann.sentence)):
					if (j+1) % 5 == 0 or (j+1) == len(ann.sentence):
						print('Processed ', j+1, ' / ', len(ann.sentence), ' sentences\n')
					required_temp = required_entity[:]
					if r == 'per:cities_of_residence':
						temp1, temp2 = required_temp[0], required_temp[1]
						required_temp = 2
						for k in range(len(ann.sentence[j].token)):
							token = ann.sentence[j].token[k]
							if  token.ner == temp1:
								required_temp -= 1
								temp1 = None
								if not required_temp:
                                                                        # reform the sentence
									sentence = ''.join([t.word + t.after for t in ann.sentence[j].token[:-1]]) + ann.sentence[j].token[-1].word
									break
							elif  token.ner in temp2:
								required_temp -= 1
								temp2 = []
								if not required_temp:
                                                                        # reform the sentence
									sentence = ''.join([t.word + t.after for t in ann.sentence[j].token[:-1]]) + ann.sentence[j].token[-1].word
									break

					else:
						for k in range(len(ann.sentence[j].token)):
							token = ann.sentence[j].token[k]
							if token.ner in required_temp:
								required_temp.remove(token.ner)
								if not required_temp:
									# reform the sentence
									sentence = ''.join([t.word + t.after for t in ann.sentence[j].token[:-1]]) + ann.sentence[j].token[-1].word
									break
					if required_temp:
						continue

					cnt_kbp += 1
					print('sentence: ', sentence)
					ann2 = pipeline2.annotate(sentence)
					for kbp_triple in ann2.sentence[0].kbpTriple:
						if kbp_triple.relation == r:
							print('=== Extracted Relation ===')
							print('Sentence: [', j+1, '] ',sentence, '\n')
							print('Confidence: ', kbp_triple.confidence, '; Subject: ', kbp_triple.subject, '; Object: ', kbp_triple.object, ';\n')
							if kbp_triple.confidence < t:
								print('Confidence is lower than threshold confidence. Ignoring this.\n')
							else:
								cnt_effect += 1
								print('Adding to set of extracted relations\n')
								if (kbp_triple.subject, kbp_triple.object) in res:
									res[(kbp_triple.subject, kbp_triple.object)] = max(res[(kbp_triple.subject, kbp_triple.object)], kbp_triple.confidence)
								else:
									res[(kbp_triple.subject, kbp_triple.object)] = kbp_triple.confidence

				print('Extracted kbp annotations for ', cnt_kbp, ' out of total ', len(ann.sentence), ' sentences\n')
				print('Relations extracted from this website: ', cnt_effect, ' (Overall: ', len(res), ')\n')

			
			iter += 1
			print('================== ALL RELATIONS (', len(res), ') =================')
			result = sorted(res.items(), key = lambda x: x[1], reverse=True)
			for i in range(len(result)):
				print('Confidence: ', result[i][1], ' 	 | Subject: ', result[i][0][0], ' 	 | Object: ', result[i][0][1], '\n')
			for i in range(len(result)):
				temp_q = str(result[i][1]) + ' ' + result[i][0][0] + ' ' + result[i][0][1]
				if temp_q not in Q_set:
					query = temp_q
					break

		
