import sys
import json
import math
import urllib.request
import bs4

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
    nr = []
    for i, doc in enumerate(output):
        print(json.dumps(doc, indent=4))
        rel = input("Relevant (Y/N)? ")
        while rel != "Y"  and rel != "N":
            rel = input("Relevant (Y/N)? Only type Y or N ")
        if rel == 'Y':
            precision += 1
            relevant.append(output[i])
        elif rel == 'N':
            nr.append(output[i])
        
    return precision/10, relevant, nr

def word_frequency(text, stop):
    tflist = {}
    doc = text.lower().split("\n")
    for word in doc:
        if word not in stop:
            if word not in tflist:
                tflist[word] = 0
            tflist[word] += 1
    return tflist

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

def get_website(output, stop):
    tf_list = []
    for i, doc in enumerate(output):
        link = doc['url']
        htmlfile = urllib.request.urlopen(link).read()
        soup = bs4.BeautifulSoup(htmlfile, features="html.parser").find('body')
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        tf = word_frequency(text, stop)
        tf_list.append(tf)
    return tf_list

def main():
    if len(sys.argv) < 5:
        print('Required input format: <google api key> <google engine id> <precision> <query>')
        return

    GOOGLE_API_KEY = sys.argv[1]
    GOOGLE_ENGINE_ID = sys.argv[2]
    PRECISION = float(sys.argv[3])
    WORDS = sys.argv[4:]
    f = open('stop.txt', 'r')
    stop = f.read()
    # Make search API call
    items = get_google_search_items(GOOGLE_API_KEY, GOOGLE_ENGINE_ID, WORDS)
    
    # Format items to desired output
    output = get_formatted_items(items)
    if len(output) < 10:
        print("======================\n"
            + "Query: " + str(WORDS) + 
            "\nQuery returned less than 10 results, done")
        exit("")

    # prompt user for relevance feedback
    precision, relevant, not_relevant = get_relevant_docs(output)

    # check if first ten documents are good enough
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
    
    # get the word frequency for each document
    # tf_list = get_website(relevant, stop) # list of dicts
    # get the document frequency for each word
    # df = doc_freq(tf_list) # dict
    # print(df)

    link = output[8]['url']
    try:
        htmlfile = urllib.request.urlopen(link).read()
    except urllib.error.HTTPError as e:
        print(e.reason)
    soup = bs4.BeautifulSoup(htmlfile, features="html.parser").find('body')
    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    tf = word_frequency(text, stop)
    print(tf)
    

if __name__ == "__main__":
    main()
    # test