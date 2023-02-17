import sys
import json

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
    for i in output:
        print(json.dumps(i, indent=4))
        rel = input("Relevant (Y/N)? ")
        while rel != "Y"  and rel != "N":
            rel = input("Relevant (Y/N)? Only type Y or N ")
        if rel == 'Y':
            precision += 1
            relevant.append(output[i])
        
    return precision/10, relevant
        

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
    precision, relevant = get_relevant_docs(output)
    print(precision)
    print(json.dumps(relevant, indent=4))
        



if __name__ == "__main__":
    main()
    # test