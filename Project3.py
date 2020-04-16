import csv
import collections
import sys
filepath = sys.argv[1]
min_sup = float(sys.argv[2])
min_conf = float(sys.argv[3])
finalres = []
def remove_dic(dic,value):
    tem = []
    for k,v in dic.items():
        if v < value:
            tem.append(k)
    for i in tem:
        del dic[i]
    return dic
def can_combine(k1,k2):
    length = len(k1)
    tem = set()
    for i in k1:
        if i not in tem:
            tem.add(i)
    for i in k2:
        if i not in tem:
            tem.add(i)
    length2 = len(tem)
    if length+1 == length2:
        return True
    else:
        return False
        
def combine(k1,k2):
    tem = []
    for i in k1:
        if i not in tem:
            tem.append(i)
    for i in k2:
        if i not in tem:
            tem.append(i)
    tem.sort()
    return tuple(tem)

def check(tem,dic):

    for i in tem:
        tem2 = list(tem)
        tem2.remove(i)
        tem2 = tuple(tem2)
        if tem2 not in dic:
            return False
    if tem in dic:
        return False
    return True



csvFile = open(filepath, "r")
reader = csv.reader(csvFile)
result = collections.defaultdict(int)
row = 0
for item in reader:
    row += 1
    for i in range(len(item)):
        result[item[i]] += 1
result2 = remove_dic(result,row*min_sup)
result2_ = sorted(result2.items(),key = lambda item:item[1])
finalres += result2_
print(result2_)
csvFile.close()



csvFile = open(filepath, "r")
reader = csv.reader(csvFile)
result3 = collections.defaultdict(int)
for item2 in reader:
    for k1,v1 in result2.items():
        for k2,v2 in result2.items():
            if k1 in item2 and k2 in item2 and k1!=k2 and (k2,k1) not in result3:
                result3[k1,k2] += 1
result3 = remove_dic(result3,row*min_sup)
result3_ = sorted(result3.items(),key = lambda item:item[1])
finalres += result3_
csvFile.close()
print(result3_)
cnt = 0
res = []
res.append(result3)


while cnt <6:
    tem = collections.defaultdict(int)
    res.append(tem)

    csvFile = open(filepath, "r")
    reader = csv.reader(csvFile)
    for k1,v1 in res[cnt].items():
        for k2, v2 in res[cnt].items():
            if can_combine(k1, k2):
                k3 = combine(k1, k2)
                if check(k3, result3):
                    res[cnt+1][k3] = 0
    for item3 in reader:
        for k,v in res[cnt+1].items():
            length = len(k)
            cnt_ = 0
            for i in k:
                if i in item3:
                    cnt_ += 1
            if cnt_ == length:
                res[cnt+1][k] += 1
    res[cnt+1] = remove_dic(res[cnt+1], row*min_sup)
    tem2 = sorted(res[cnt+1].items(), key=lambda item: item[1])
    finalres += tem2
    cnt += 1
    print(tem2)
    csvFile.close()
finalres = sorted(finalres,key = lambda x:x[1],reverse = True)

finalres2 = []
for i in finalres:
    if type(i[0]) is not tuple:
        for j in finalres:
            if type(j[0]) is tuple and i[0] in j[0]:
                count = j[1]/i[1]
                tem3 = list(j[0])
                for k in range(len(tem3)):
                    if tem3[k] == i[0]:
                        del tem3[k]
                        break
                #tem3 = tem3.remove(i[0])
                if count > min_conf:
                    finalres2.append((tem3,i[0],count))
finalres2 = sorted(finalres2,key=lambda x:x[2],reverse=True)

f = open("output3.txt",'a')
text0 = "==Frequent itemsets (min_sup=%.2f)" %min_sup
f.write(text0)
f.write("\n")
for i in finalres:
    print(i)
    f.write(str(i[0]) + ' ' + str(i[1]/row))
    f.write("\n")
for i in range(10):
    f.write("\n")
text1 = "==High-confidence association rules (min_conf=%.2f)" %min_conf
f.write(text1)
f.write("\n")
for i in finalres2:
    f.write(str(i[0]) + '=>' + str(i[1]) + ' ' + str(i[2]))
    f.write("\n")
print(finalres2)

