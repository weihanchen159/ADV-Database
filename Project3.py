import csv
import collections
import sys

# INTEGRATED-DATASET.csv, min_sup, min_conf
filepath = sys.argv[1]
min_sup = float(sys.argv[2])
min_conf = float(sys.argv[3])

# Initialize final result list
finalres = []

# Some helper functions
def remove_dic(dic,value):
    dic = {k:v for k,v in dic.items() if v >= value}
    return dic

def can_combine(k1,k2):
    return len(k1)+1 == len(set(k1+k2))

def combine(k1,k2):
    return tuple(sorted(list(set(k1+k2))))

def check(tem,dic):
    for i in range(len(tem)):
        if tem[:i] + tem[i+1:] not in dic:
            return False
    if tem in dic:
        return False

    return True


# Deal with itemset with size equals to 1
csvFile = open(filepath, "r")
reader = csv.reader(csvFile)
result = collections.Counter()
#result = collections.defaultdict(int)
row = 0
for item in reader:
    row += 1
    result.update(item)
    #for i in range(len(item)):
    #    result[item[i]] += 1
result2 = remove_dic(result,row*min_sup)
#result2_ = sorted(result2.items(),key = lambda item:item[1])
finalres += result2.items()
csvFile.close()

# Deal with itemset with size equals to 2
csvFile = open(filepath, "r")
reader = csv.reader(csvFile)
result3 = collections.defaultdict(int)
result3 = {tuple(sorted([k1,k2])):0 for k1 in result2.keys() for k2 in result2.keys() if k1 != k2}
for item2 in reader:
    comb = [(k1,k2) for k1 in item2 for k2 in item2]
    for c in comb:
        if c in result3:
            result3[c] += 1
result3 = remove_dic(result3,row*min_sup)
#result3_ = sorted(result3.items(),key = lambda item:item[1])
finalres += result3.items()
csvFile.close()

# Deal with itemset with size is bigger than or equals to 3
cnt = 0
res = []
res.append(result3)

while True:
    tem = collections.defaultdict(int)
    res.append(tem)

    csvFile = open(filepath, "r")
    reader = csv.reader(csvFile)

    for k1 in res[cnt].keys():
        for k2 in res[cnt].keys():
            if can_combine(k1, k2):
                k3 = combine(k1, k2)
                if check(k3, result3):
                    res[cnt+1][k3] = 0
    for item3 in reader:
        item3 = set(item3)
        for k in res[cnt+1].keys():
            length = len(k)
            cnt_ = 0
            for i in k:
                if i in item3:
                    cnt_ += 1
            if cnt_ == length:
                res[cnt+1][k] += 1
    res[cnt+1] = remove_dic(res[cnt+1], row*min_sup)
    if not res[cnt+1]:
        break
    tem2 = sorted(res[cnt+1].items(), key=lambda item: item[1])
    finalres += tem2
    cnt += 1
    csvFile.close()
finalres = sorted(finalres,key = lambda x:x[1],reverse = True)


# High-confidence association rules
sup_dic = {tuple(x[0]):x[1] for x in finalres}
finalres2 = []
for itemset, sup in sup_dic.items():
    if len(itemset) > 1:
        for i in range(len(itemset)):
            left = itemset[:i] + itemset[i+1:]
            if left in sup_dic:
                conf = sup / sup_dic[left]
                if conf >= min_conf:
                    finalres2.append((left, itemset[i], conf, sup))

finalres2 = sorted(finalres2,key=lambda x:x[2],reverse=True)

# Ouput result
f = open("output.txt",'w')
text0 = "==Frequent itemsets (min_sup=%.2f" %(min_sup*100) + '%)'
f.write(text0)
f.write("\n")
for i in finalres:
    f.write('[' + str(i[0]) + '], ' + str(i[1]/row*100) + '%')
    f.write("\n")

text1 = "==High-confidence association rules (min_conf=%.2f" %(min_conf*100) + '%)'
f.write(text1)
f.write("\n")
for i in finalres2:
    f.write('[' + str(i[0]) + '] => [' + str(i[1]) + '] ' + '(Conf: ' + str(i[2]*100) + '%, Supp: ' + str(i[3]*100/row) + '%)')
    f.write("\n")

