import sys
import json

from googleapiclient.discovery import build

def main():
    if len(sys.argv) < 5:
        print('Required input format: <google api key> <google engine id> <precision> <query>')
        return

    GOOGLE_API_KEY = sys.argv[1]
    GOOGLE_ENGINE_ID = sys.argv[2]
    PRECISION = float(sys.argv[3])
    WORDS = sys.argv[4:]

    print(GOOGLE_API_KEY, GOOGLE_ENGINE_ID, PRECISION, WORDS)

    service = build(
        "customsearch", "v1", developerKey="GOOGLE_API_KEY"
    )

    res = (
        service.cse()
        .list(
            q="lectures",
            cx="017576662512468239146:omuauf_lfve",
        )
        .execute()
    )
    print(json.dumps(res, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()