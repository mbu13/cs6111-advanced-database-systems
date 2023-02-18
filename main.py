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

def word_frequency(relevant):
    doc_list = list({} for i in range(len(relevant)))
    for i, result in enumerate(relevant):
        sent = result['description'].lower().split()
        for word in sent:
            if word not in doc_list[i]:
                doc_list[i][word] = 0
            doc_list[i][word] += 1
    return doc_list

def doc_freq(freq):
    doc = {}
    for rel in freq:
        for key in rel:
            if key not in doc:
                doc[key] = 0
            doc[key] += 1
    return doc

def tf_idf(freq, doc, N):
    scores = {}
    for key in freq:
        scores[key] = (1 + math.log(freq[key], 10)) * (math.log(N/doc[key], 10))
    return scores

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
    freq = word_frequency(relevant)
    doc = doc_freq(freq)
    scores = tf_idf(freq, doc, len(relevant))
    print(freq)



if __name__ == "__main__":
    main()
    # test