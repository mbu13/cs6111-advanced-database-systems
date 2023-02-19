# CS6111: Project 1
## Names and UNIs
Ryan Grossmann
(rg3398)

Matthew Bu
(mb4753)

## Keys
  * Search ID: fb8c9f64780d3213f
  * API Key: AIzaSyBh546gYpsBnKcTEdBi-jagSb9gEIoRj6s
  
## Files
  * README.md
  * main.py
  * requirements.txt
  * stop.txt
  
## How To Run
  * All necessary modules are listed in `requirements.txt`
      * sudo apt-get install python3-pip
      * sudo apt-get install python3.7
      * sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
      * sudo pip3 install --upgrade google-api-python-client
      * sudo pip3 install -r requirements.txt
  * Run the command  `python3 main.py <google api key> <google engine id> <precision> <query>`
  * When prompted, respond with either `Y` or `N` (case-sensitive) corresponding to a relevant or non-relevant document

## Internal Design
  * Libraries:
      * `sys` - for getting the program's input parameters (api key, engine id, precision, query)
      * `json` - for displaying the webpage summaries during relevance feedback
      * `math` - for math operations
      * `urllib.request` - for opening urls
      * `bs4` - for parsing the webpages
   * Functions:
      * `def get_google_search_items(api_key, engine_id, words):` - for searching Google and returning a list of webpages
      * `def get_formatted_items(items):` - for formatting the webpage summaries
      * `def get_relevant_docs(output):` - for getting the relevant webpages from user input
      * `def word_frequency(text, stop):` - for getting the term frequencies of a webpage
      * `def doc_freq(tf_list):` - for getting the document frequencies of each word
      * `def get_website(output, stop):` - for opening the webpage and formatting the body
      * `def get_maxes(tfidf, query, df):` - for getting a list of potential new query terms
      * `def main():`

## Query-Modification
  * After the first relevance feedback session, we download the main body of each relevant webpage
  * We compute the term frequency for each relevant webpage
  * We compute the document frequency for each word
  * We sort the term frequency vectors for each relevant webpage from largest to smallest
  * We take the top 5 terms (in terms of term frequency) from each relevant webpage and sort them largest to smallest by document frequency
  * We take this list of terms and compute the average distance from each query words and sort the list from smallest distance to largest
  * We take the top 2 terms and find if the terms typically come before or after the query words
  * We add the top 2 words to the query in the typical position that they are found

## Additional Information
  * website parsing code was copied from stackoverflow
      * https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
