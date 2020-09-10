from googleapiclient.discovery import build

import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from stanfordnlp.server import CoreNLPClient

import sys

# $ python IR.py query precision
Method = {1:["PERSON","ORGANIZATION"],2:["PERSON","ORGANIZATION"],3:["PERSON","LOCATION","CITY","STATE_OR_PROVINCE","COUNTRY"],4:["ORGANIZATION","PERSON"]}
Relation = {1:"per:schools_attended",2:"per:employee_or_member_of",3:"per:cities_of_residence",4:"org:top_members_employees"}
method = int(sys.argv[1])
Threshold = float(sys.argv[2])
query = sys.argv[3].split()
origin_q = query
k = int(sys.argv[4])


with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner'], timeout=300000, memory='4G',
                   endpoint="http://localhost:9000") as pipeline1:
    with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp'],
                       timeout=300000, memory='4G', endpoint="http://localhost:9001") as pipeline2:
        memory = {}
        final_res = {}
        while True:
            service = build("customsearch", "v1", developerKey="")
            res = service.cse().list(q=' '.join(query), cx='', ).execute()

            URL = []
            TEXT = []

            for i in range(len(res['items'])):
                URL.append((res['items'][i]['link'], i))
            cnt = 0
            while cnt < 10:
                if URL[cnt][0] in memory:
                    continue
                req = urllib.request.Request(URL[cnt][0], headers={'User-Agent': 'Mozilla/5.0'})
                memory[URL[cnt][0]] = True
                cnt += 1
            # If the access being denied, append the short description to TEXT
                try:
                    print("Fetching text from url ...")
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
                    text = ''.join(chunk for chunk in chunks if chunk)
                except HTTPError or TimeoutError:
                    text = None
                    print('error')
                if text:
                    if len(text)>20000:
                        text = text[:20000]
                    length = len(text)
                    text1 = "Webpage length (num characters) is %d" % length
                    print(text1)
                    ann = pipeline1.annotate(text)
                    res = []
                    print(len(ann.sentence))
                    for i in range(len(ann.sentence)):
                        temp = Method[method].copy()
                        sentence = ann.sentence[i]
                        if method != 3:
                            for i in sentence.token:
                                if not temp:
                                    break
                                elif i.ner in temp:
                                    temp.remove(i.ner)
                        else:
                            for i in sentence.token:
                                if not temp:
                                    break
                                elif i.ner == "PERSON" and "PERSON" in temp:
                                    temp.remove(i.ner)
                                elif i.ner in temp and i.ner in ["LOCATION","CITY","STATE_OR_PROVINCE","COUNTRY"]:
                                    temp.remove("LOCATION")
                                    temp.remove("CITY")
                                    temp.remove("STATE_OR_PROVINCE")
                                    temp.remove("COUNTRY")
                        if not temp:
                            tem2 = ''.join(i.word + i.after for i in sentence.token)
                            res.append(tem2)
                    print(res)
                    # done with first pipeline,res is a list contained some sentences.
                    for i in range(len(res)):
                        print(res[i])
                        ann2 = pipeline2.annotate(res[i])
                        print(i)
                        kbp = ann2.sentence[0].kbpTriple
                        for i in kbp:
                            rel = i.relation
                            con = i.confidence
                            sub = i.subject
                            ob = i.object
                            if rel == Relation[method] and con > Threshold:
                                if (sub,rel,ob) not in final_res:
                                    final_res[(sub,rel,ob)] = con
                                else:
                                    tem = final_res[(sub,rel,ob)]
                                    final_res[(sub,rel,ob)] = max(tem,con)

            final_res2 = sorted(final_res.items(),key = lambda item:item[1],reverse=True)

            if len(final_res2) > k:
                for i in range(k):
                    print(final_res2[i],'\n')
                break
            else:
                query = final_res2[0][0][0] + final_res2[0][0][2]
