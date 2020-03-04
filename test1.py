from stanfordnlp.server import CoreNLPClient
from stanfordnlp.pipeline import *


# example text
print('---')
print('input text')
print('')

text =  "In June 2006, Gates announced that he would be transitioning from full-time work at Microsoft to part-time work and full-time work at the Bill & Melinda Gates Foundation"

print(text)

# set up the client
print('---')
print('starting up Java Stanford CoreNLP Server...')

# set up the client
with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner'],
                   timeout=30000, memory='16G') as client:
        ann = client.annotate(text)
        res = ''
        for i in range(len(ann.sentence)):
            temp = ["PERSON"]
            sentence = ann.sentence[i]
            for i in sentence.token:
                if not temp:
                    break
                elif i.ner in temp:
                    temp.remove(i.ner)
            if not temp:
                tem2 = ''.join(i.word + i.after for i in sentence.token)
                print(tem2)
                res += tem2
with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp'],
                   timeout=30000, memory='16G') as client2:
    ann2 = client2.annotate(tem2)
    print(ann2.sentence[0].kbpTriple)


                # with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp'],
                #                    timeout=30000, memory='16G') as client2:
                #     ann2 = client2.annotate(tem2)
                #     print(ann2.sentence[0].kbpTriple)









#print(ann.sentence[0].token[0].ner)
#import stanfordnlp.
#
# MODELS_DIR = '.'
# nlp = stanfordnlp.Pipeline(processors='tokenize,pos', models_dir=MODELS_DIR, treebank='en_ewt', use_gpu=True, pos_batch_size=3000) # Build the pipeline, specify part-of-speech processor's batch size
# doc = nlp("Barack Obama was born in Hawaii.") # Run the pipeline on input text
# doc.sentences[0].print_tokens() # Look at the result
