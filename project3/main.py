import sys
import csv
import itertools
from collections import defaultdict
import pandas as pd
import pandasql as sql

'''
This was the original code to get all the large 1-item sets from the data.
It took quite a while to run so we scrapped it in favor of the current method.
We used sql to calculate the large 1-item sets for each column of the dataset.
'''
'''
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
'''

'''
Returns a frequent item set
based support being grreater than
provided min support threshold
'''
def getSupports(CR, all_items, sup, supports, all_freq):
    freq = set()
    sub_supports = defaultdict(int)

    for item in CR:
        for itemSet in all_items:
            if item.issubset(itemSet):
                supports[item] += 1
                sub_supports[item] += 1

    for item, supCount in sub_supports.items():
        support = float(supCount / len(all_items))
        if(support >= sup):
            freq.add(item)
            all_freq[item] = support
    return freq

'''
Get grouped buckets to find more meaningful
association rules for percentage values
'''
def get_buckets(n, k):
    ranges = []
    
    for r in range(0, n, k):
        ranges.append([i for i in range(r, r+k)])
    ranges.append([100])
    return ranges

'''
Main apriori implementation which
reads from a CSV and generates item sets
'''
def apriori(filename, sup, conf):
    items = []
    all_freq = {}
    C1 = set()
    R = 2

    with open(filename, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            rowset = set()
            for col in reader.fieldnames:
                if not row[col]:
                    continue
                if row[col]: # and col not in {'DBN','Year','total_enrollment','Number Tested', 'male_per', 'female_per'}:
                    # Map to a range
                    ranges = get_buckets(100, 20) 
                    group = None
                    for r in ranges:
                        if round(float(row[col])) in r:
                            group = "{}-{}".format(r[0], r[-1])
                            break

                    C1.add(frozenset([col + " " + group]))
                    rowset.add(col + " " + group)
            items.append(rowset)

    freq = {}
    supports = defaultdict(int)

    L1 = getSupports(C1, items, sup, supports, all_freq)
    curr = L1

    # Repeat until LR is null
    while(curr):
        freq[R-1] = curr

        # Union each item
        CR = [a.union(b) for a in curr for b in curr if len(a.union(b)) == R]
        CR = set(CR)

        temp = CR.copy()
        for item in CR:
            # Get all combination subsets
            subsets = itertools.combinations(item, R-1)
            for subset in subsets:
                if(frozenset(subset) not in curr):
                    temp.remove(item)
                    break
        CR = temp
        curr = getSupports(CR, items, sup, supports, all_freq)
        R = R + 1

    # Calculate rules
    rules = []
    for _, itemSet in freq.items():
        for item in itemSet:
            # Get all combination subsets of size in range of length of itemset
            subsets = itertools.chain.from_iterable(itertools.combinations(item, r) for r in range(1, len(item)))
            for s in subsets:
                c = float(supports[item] / supports[frozenset(s)])
                if(c > conf):
                    if len(set(item.difference(s))) > 1:
                        continue
                    rules.append([set(s), set(item.difference(s)), c])

    # Sort by decreasing order
    rules.sort(key=lambda x: -x[2])
    return all_freq, rules

def pretty_print_results(frequency, rules, min_sup, min_conf):
    print('==Frequent itemsets (min_sup={:.1%})'.format(min_sup))
    for item, f in frequency.items():
        print('{}, {:.1%}'.format(list(item), f))
    
    print('==High-confidence association rules (min_conf={:.1%})'.format(min_conf))
    for r in rules:
        print('{}=> {} (Conf: {:.1%}, Supp: {:.1%})'.format(list(r[0]), list(r[1]), r[2], frequency[frozenset(r[0])]))

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
    #DF = pd.read_csv(DATASET)
    # get all large 1-item sets
    #L1 = one_item_sets(DF, MIN_SUP)
    # run apriori alg on dataset
    FREQUENCY, RULES = apriori(DATASET, MIN_SUP, MIN_CONF)
    pretty_print_results(FREQUENCY, RULES, MIN_SUP, MIN_CONF)

if __name__ == "__main__":
    main()
