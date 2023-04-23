import sys
import pandas as pd
import pandasql as sql

def one_item_sets(DF, sup):
    # initialize large 1-item set dictionary
    large = {}

    # Get all DBNs that occur more than min_sup 
    total = DF.shape[0]
    min_sup = sup * total
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
        if enroll > min_sup:
            large[key] = enroll
    
    # iterate over remaining columns (which are all percentages)
    # and separate into groups by 10% eg. 1-10%, 11-20%
    cols = list(DF.columns)
    for i in range(10):
        val1 = i * 10 + 1
        val2 = val1 + 9
        
        for j in range(16):
            q4 = "SELECT COUNT(ALL {}) as count FROM DF WHERE {} BETWEEN {} AND {}".format(cols[j], cols[j], val1, val2)
            table = sql.sqldf(q4, locals())
            
    
    #TODO: figure out how to extract 1-item sets
    
    return None

def apriori(L1, DF, sup, conf):
    return None

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
    L1 = one_item_sets(DF, MIN_SUP)
    # run apriori alg on dataset
    ANSWER = apriori(L1, DF, MIN_SUP, MIN_CONF)



if __name__ == "__main__":
    main()