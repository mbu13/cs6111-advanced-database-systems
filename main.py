import sys
import json
import math

from googleapiclient.discovery import build

MAX_ITEMS = 10

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

def get_relevant_docs(output):
    precision = 0
    relevant = []
    for i, doc in enumerate(output):
        print(json.dumps(doc, indent=4))
        rel = input("Relevant (Y/N)? ")
        while rel != "Y"  and rel != "N":
            rel = input("Relevant (Y/N)? Only type Y or N ")
        if rel == 'Y':
            precision += 1
            relevant.append(output[i])
        
    return precision/10, relevant

def word_frequency(doc_set):
    tf_list = list({} for i in range(len(doc_set)))
    for i, result in enumerate(doc_set):
        sent = result['description'].lower().split()
        for word in sent:
            if word not in tf_list[i]:
                tf_list[i][word] = 0
            tf_list[i][word] += 1
    return tf_list

def doc_freq(tf_list):
    df = {}
    for result in tf_list:
        for key in result:
            if key not in df:
                df[key] = 0
            df[key] += 1
    return df

def tf_idf(tf_list, df, N):
    score_list = tf_list
    for i, result in enumerate(score_list):
        for key in result:
            score_list[i][key] = (1 + math.log(result[key], 10)) * (math.log(N/df[key],10))

    return score_list

def main():
    if len(sys.argv) < 5:
        print('Required input format: <google api key> <google engine id> <precision> <query>')
        return

    GOOGLE_API_KEY = sys.argv[1]
    GOOGLE_ENGINE_ID = sys.argv[2]
    PRECISION = float(sys.argv[3])
    WORDS = sys.argv[4:]

    # Make search API call
    items = get_google_search_items(GOOGLE_API_KEY, GOOGLE_ENGINE_ID, WORDS)
    
    # Format items to desired output
    output = get_formatted_items(items)
    if len(output) < 10:
        print("======================\n"
            + "Query: " + str(WORDS) + 
            "\nQuery returned less than 10 results, done")
        exit("")

    precision, relevant = get_relevant_docs(output)
    if precision >= PRECISION:
        print("======================\n"
            + "Query: " + str(WORDS) + "\nPrecision: " + str(precision) + 
            "\nDesired precision reached, done")
        exit("")

    if precision == 0:
        print("======================\n"
            + "Query: " + str(WORDS) + "\nPrecision: " + str(precision) + 
            "\nPrecision = 0, Done")
        exit("")

    # TODO: analyze relevant doc descriptions
    #       query expansion (Rocchio's alrgorithm)
    tf_list = word_frequency(output)
    df = doc_freq(tf_list)
    print(tf_list)
    print(df)


if __name__ == "__main__":
    main()
    # test