import sys
import csv
import itertools
from collections import defaultdict
import pandas as pd
import pandasql as sql

def one_item_sets(DF, sup):
    # initialize large 1-item set dictionary
    large = {}

    # Get all DBNs that occur more than min_sup 
    # havent decided if we are going to consider dbn since it only occurs 7 times maximum
    total = DF.shape[0]
    min_sup = sup * total

    print(total, min_sup)

    q1 = "SELECT DBN, COUNT(DBN) as count FROM DF GROUP BY DBN HAVING count >= {} ORDER BY count DESC".format(min_sup)
    dbn = sql.sqldf(q1, locals())
    dbn = dbn.iloc[:,0]
    dbn = dbn.values.tolist()
    large = dict.fromkeys(dbn, 7)

    # get all years that occur more then min_sup
    q2 = "SELECT Year, COUNT(Year) as count FROM DF GROUP BY Year HAVING count >= {} ORDER BY count DESC".format(min_sup)
    year = sql.sqldf(q2, locals())
    year1 = year.iloc[:,0]
    year1 = year1.values.tolist()
    year2 = year.iloc[:,1]
    year2 = year2.values.tolist()
    for i, val in enumerate(year1):
        large[val] = year2[i]

    # get all total enrollments that occue more than min_sup
    for i in range(19):
        val1 = i * 250
        val2 = val1 + 249
        q3 = "SELECT COUNT(ALL total_enrollment) as count FROM DF WHERE total_enrollment BETWEEN {} AND {}".format(val1, val2)
        enrollment = sql.sqldf(q3, locals())
        enroll = enrollment.iloc[0]['count']
        key = 'enrollment {}-{}'.format(val1, val2)
        if enroll >= min_sup:
            large[key] = enroll

    # iterate over remaining columns (which are all percentages)
    # and separate into groups by 10% eg. 1-10%, 11-20%
    cols = list(DF.columns)
    for i in range(10):
        val1 = i * 10 + 1
        val2 = val1 + 9
        
        for j in range(16):
            q4 = "SELECT COUNT(ALL '{}') as count FROM DF WHERE '{}' BETWEEN {} AND {}".format(cols[j], cols[j], val1, val2)
            table = sql.sqldf(q4, locals())
            t = table.iloc[0]['count']
            key = '{} {}-{}%'.format(cols[j], val1, val2)
            if t >= min_sup:
                large[key] = t

    return large


def getSupports(CR, allItems, sup, supports):
    freq = set()
    sub_supports = defaultdict(int)

    for item in CR:
        for itemSet in allItems:
            if item.issubset(itemSet):
                supports[item] += 1
                sub_supports[item] += 1

    for item, supCount in sub_supports.items():
        support = float(supCount / len(allItems))
        if(support >= sup):
            freq.add(item)

    return freq

def apriori(filename, sup, conf):
    itemSets = []
    C1 = set()
    R = 2

    with open(filename, 'r') as file:
        lines = csv.reader(file)
        for line in lines:
            line = list(filter(None, line))
            line = set(line)
            for item in line:
                C1.add(frozenset([item]))
            itemSets.append(line)

    freq = {}
    supports = defaultdict(int)

    L1 = getSupports(C1, itemSets, sup, supports)
    curr = L1

    # Repeat until LR is null
    while(curr):
        freq[R-1] = curr

        CR = [a.union(b) for a in curr for b in curr if len(a.union(b)) == R]
        CR = set(CR)

        temp = CR.copy()
        for item in CR:
            subsets = itertools.combinations(item, R-1)
            for subset in subsets:
                if(frozenset(subset) not in curr):
                    temp.remove(item)
                    break
        CR = temp
        curr = getSupports(CR, itemSets, sup, supports)
        R = R + 1

    # Calculate rules
    rules = []
    for _, itemSet in freq.items():
        for item in itemSet:
            subsets = itertools.chain.from_iterable(itertools.combinations(item, r) for r in range(1, len(item)))
            for s in subsets:
                c = float(supports[item] / supports[frozenset(s)])
                if(c > conf):
                    rules.append([set(s), set(item.difference(s)), c])

    rules.sort(key=lambda x: x[2])
    return freq, rules

def main():
    # get program arguments and check values
    if len(sys.argv) < 4:
        print('Required input format: python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>')
        return
    DATASET = sys.argv[1]
    MIN_SUP = float(sys.argv[2])
    MIN_CONF = float(sys.argv[3])

    if MIN_SUP < 0 or MIN_SUP > 1:
        print("min_sup must be between 0 and 1")
        return
    
    if MIN_CONF < 0 or MIN_CONF > 1:
        print("min_sup must be between 0 and 1")
        return
    # open dataset as a pandas dataframe
    DF = pd.read_csv(DATASET)
    # get all large 1-item sets
    #L1 = one_item_sets(DF, MIN_SUP)
    # run apriori alg on dataset
    frequency, ANSWER = apriori(DATASET, MIN_SUP, MIN_CONF)
    print(ANSWER)


if __name__ == "__main__":
    main()
