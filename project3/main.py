import sys
import pandas as pd
import pandasql as sql

def one_item_sets(DF, sup):
    q = "SELECT DBN, COUNT(DBN) as count FROM DF GROUP BY DBN HAVING count >= {}".format(sup)
    temp = sql.sqldf(q, globals())
    print(temp)
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
    DF = DF.drop(DF.columns[0], axis=1)
    # get all large 1-item sets
    L1 = one_item_sets(DF, MIN_SUP)
    # run apriori alg on dataset
    ANSWER = apriori(L1, DF, MIN_SUP, MIN_CONF)



if __name__ == "__main__":
    main()