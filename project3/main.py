import sys
import pandas as pd
import pandasql as sql

def one_item_sets(DF):

    return None

def apriori(L1, DF):
    return None

def main():
    # get program arguments and check values
    if len(sys.argv) < 4:
        print('Required input format: python3 main.py INTEGRATED-DATASET.csv <min_sup> <min_conf>')
        return
    DATASET = sys.argv[1]
    print(DATASET)
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
    
    L1 = one_item_sets(DF)
    ANSWER = apriori(L1, DF)



if __name__ == "__main__":
    main()