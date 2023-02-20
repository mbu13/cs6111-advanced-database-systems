import sys
import json
import math
import urllib.request
import bs4
import numpy as np
import sys
from collections import defaultdict

from googleapiclient.discovery import build

TOP_N_CLOSEST = 2
MAX_POSSIBLE_TERMS = 5
MAX_ITEMS = 10
CACHE = {}

def get_google_search_items(api_key, engine_id, words):
    service = build(
        "customsearch", "v1", developerKey=api_key
    )

    res = (
        service.cse()
        .list(
            q=" ".join(words),
            cx=engine_id,
        )
        .execute()
    )

    # Get top ten items
    items = res['items'][:MAX_ITEMS]
    return items

def get_formatted_items(items):
    def get_attr(item):
        return {'title': item['title'], 'url': item['link'], 'description': item['snippet']}
    return [get_attr(i) for i in items]

"""
    Function to get the relevant webpages from the 10 googled webpages

    input: list of webpages
    output: list of webpages relevant to query 
"""
def get_relevant_docs(output):
    # initialize return variables
    precision = 0
    relevant = []

    # iterate over each google webpage
    for i, doc in enumerate(output):
        # print webpage summary and prompt user for relevance feedback
        print(json.dumps(doc, indent=4))
        rel = input("Relevant (Y/N)? ")

        # make sure user input is in correct format
        while rel != "Y"  and rel != "N":
            rel = input("Relevant (Y/N)? Only type Y or N ")
        # add webpage to relevant list if user inputs "Y"
        if rel == 'Y':
            precision += 1
            relevant.append(output[i])
    
    return precision/10, relevant

"""
    Function to compute the term frequency for each relevant webpage

    input: webpage text (string), list of stop words
    output: dictionary of term frequencies 
"""
def word_frequency(text, stop):
    # initialize dictionary
    tflist = {}

    # for each word in the webpage, increment the term frequency
    for word in text:
        if word not in stop:
            if word not in tflist:
                tflist[word] = 0
            tflist[word] += 1
    return tflist

"""
    Function to get the document frequency for each term in the relevane webpages

    input: list of term frequency dictionaries
    output: dictionary of document frequencies 
"""
def doc_freq(tf_list):
    # initialize document frequency dictionary
    df = defaultdict(int)

    # increment each word in the document once if it appears in the document
    for result in tf_list:
        for key in result:
            if key not in df:
                df[key] = 0
            df[key] += 1
    return df

"""
    Function to get the tf-idf scores for each document

    input: list term freqency dictionaries, dictionary of document frequencies,
           number of relevant documents
    output: list of tf-idf dictionaries 
"""
def tf_idf(tf_list, df, N):
    score_list = tf_list

    # for each term in the document, compute the tf-idf score
    for i, result in enumerate(score_list):
        for key in result:
            score_list[i][key] = (1 + math.log(result[key], 10)) * (math.log(N/df[key],10))

    return score_list

"""
    Function to get the term frequencies from the body of each webpage

    input: list of webpages, list of stop words
    output: list of term frequency dictionaries
"""
def get_website(output):
    # get stop words
    f = open('stop.txt', 'r')
    stop = f.read()

    # initialize return variable
    tf_list = []
    text_list = []

    # for each webpage
    for i, doc in enumerate(output):
        # get the webpage url
        link = doc['url']
        # try to open the website, go to the next webpage if error is given
        try:
            # if already in cache, no need to make another request
            if CACHE.get(link):
                htmlfile = CACHE[link]
            else:
                htmlfile = urllib.request.urlopen(link).read()
                CACHE[link] = htmlfile
        except urllib.error.HTTPError as e:
            continue
        # parse the webpage for the body
        soup = bs4.BeautifulSoup(htmlfile, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = ' '.join(soup.stripped_strings).lower().split(' ')

        # calculate term frequecies of the webpage body
        tf = word_frequency(text, stop)
        # add term frequency dictionary to list
        tf_list.append(tf)
        text_list.append(text)

    print("TEXT: ", len(text_list), "\n")
    return tf_list, text_list

"""
    Function to get the best new querying terms

    input: list of term frequency dictionaries, initial query,
           document frequency dictionary
    output: sorted list of new query words 
"""
def get_maxes(tfidf, query, df):
    # initialize return variable
    keys = []

    # for each webpage
    for lis in tfidf:
        # initialize counter variable
        count = 0

        # sort dictionary by term frequency greatest to least
        lis = sorted(lis.items(), key=lambda kv: kv[1])
        lis.reverse()

        # for each term in the dictionary
        for tup in lis:
            # get the term with the highest term frequency
            k = str(tup[0])
            # get the term frequency
            v = tup[1]
            # check to see if the term is already in the query
            if k not in query:
                # add term to list
                keys.append(tuple((k,v, df[k])))
                # make sure each document provides at most 5 possible terms
                count += 1
                if count > 4:
                    break
    
    # sort the list of terms by document frequency
    sort = sorted(keys, key=lambda tup: tup[2])
    sort.reverse()
    return sort


"""
    Caclulate the similarity between two vectors
"""
'''
def get_similarity_score(v1, v2):
    dot = np.dot(v1, v2)
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    return dot / (v1_norm * v2_norm)
'''
"""
    Gets the relevant documents sorted by decreasing order of cosine
    of the document vector to the query vector
"""
'''
def get_ranked_documents(query, relevant, df):
    query_vector = np.array([])
    for word in query:
        frequency = df[word]
        np.append(query_vector, [frequency])

    # loop through documents to calculate vectors as it relates to the query
    tf_list = get_website(relevant)
    tups = []

    for i, tf in enumerate(tf_list):
        doc_vector = np.array([])
        for word in query:
            # TODO check this logic, tf vs df
            if not tf.get(word):
                continue

            frequency = tf[word]
            np.append(doc_vector, [frequency])

        # Compare vectors
        score = get_similarity_score(query_vector, doc_vector)
        tups.append((i, score))

    # sort by increasing order of scores
    tups = sorted(tups, key=lambda x: x[1])

    return [relevant[x[0]] for x in tups]
'''

"""
    Calculate average word distance between the new candidate words
    and the original query words
"""
def get_proximities(keys, query, docs):
    candidate_words = set([k[0] for k in keys])

    def get_distance(candidate_word, query_word, doc):
        if not doc:
            return None

        # calculate distance between two words in a given doc

        # try all possible indexes of each word to minimize distance
        min_dist = None
        for i, src in enumerate(doc):
            if src == query_word:
                for j, dst in enumerate(doc):
                    if dst == candidate_word:
                        if not min_dist:
                            min_dist = abs(j - i)
                        else:
                            min_dist = min(min_dist, abs(j - i))

        if min_dist == sys.maxsize:
            print('ERROR ', doc)

        return min_dist

    proximities = []
    for word in candidate_words:
        distances = []

        for q in query:
            for d in docs:
                distance = get_distance(word, q, d)

                if not distance:
                    continue

                distances.append(distance)
        
        avg = sum(distances) / len(distances)
        proximities.append((word, avg))

    tups = sorted(proximities, key=lambda x: x[1])
    return [x[0] for x in tups]


def main():
    if len(sys.argv) < 5:
        print('Required input format: <google api key> <google engine id> <precision> <query>')
        return

    GOOGLE_API_KEY = sys.argv[1]
    GOOGLE_ENGINE_ID = sys.argv[2]
    PRECISION = float(sys.argv[3])
    WORDS = sys.argv[4].split()
    
    def run_query(words):
        # Make search API call
        items = get_google_search_items(GOOGLE_API_KEY, GOOGLE_ENGINE_ID, words)

        # Format items to desired output
        output = get_formatted_items(items)
        if len(output) < 10:
            print("======================\n"
                + "Query: " + str(words) + 
                "\nQuery returned less than 10 results, done")
            return None, 0

        # prompt user for relevance feedback
        precision, relevant = get_relevant_docs(output)

        # check if first ten documents are good enough
        if precision >= PRECISION:
            print("======================\n"
                + "Query: " + str(words) + "\nPrecision: " + str(precision) + 
                "\nDesired precision reached, done")
            return None, precision

        # check if all documents are not relevant
        if precision == 0:
            print("======================\n"
                + "Query: " + str(words) + "\nPrecision: " + str(precision) + 
                "\nPrecision = 0, Done")
            return None, 0
        
        # get the word frequency for each document
        tf_list, text_list = get_website(relevant) # list of dicts
        # check if none of the webpages could be analyzed
        if len(tf_list) == 0:
            print("======================\n"
                + "Query: " + str(words) + "\nPrecision: " + str(precision) + 
                "\nNone of the webpages could be analyzed, done")
            return None, precision

        # get the document frequency for each word
        df = doc_freq(tf_list) # dict

        # tfidf = tf_idf(tf_list, df, len(tf_list))

        # get sorted list of potential words to query on (sorted based on df)
        keys = get_maxes(tf_list, str(words).lower(), df) # list of tuple(word, tf, df)
        k = []
        if len(tf_list) > 1:
            for i in keys:
                if i[2] != 1:
                    k.append(i)

        # get top words to append to query
        prox = get_proximities(k, words, text_list)

        return prox[0:TOP_N_CLOSEST], precision


    # Run queries until precision is reached
    query = WORDS
    while(True):
        print("Parameters:\nClient key  = {}\nEngine key  = {}\nQuery       = {}\nPrecision   = {}\nGoogle Search Results:\n======================\n".format(GOOGLE_API_KEY, GOOGLE_ENGINE_ID, " ".join(query), PRECISION))

        augment, precision = run_query(query)
        if not augment:
            print("ERROR: ", augment)
            return
        
        print("======================\nFEEDBACK SUMMARY\nQuery {}\nPrecision {}\nStill below the desired precision of {}\nAugmenting by  {}".format(" ".join(query), precision, PRECISION, " ".join(augment)))
        
        query = query + augment


if __name__ == "__main__":
    main()
    # test