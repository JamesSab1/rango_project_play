import json
import urllib.parse
import urllib.request

def read_webhose_key():
    """Reads the Webhose API key from a file called 'search.key'.
    Returns either None (no key found), or a string representing the key.
    Remember: put search.key in your .gitignore file to avoid committing it!"""

    webhose_api_key = None
    filename='search.txt'
    try:
        with open(filename, 'r') as f:
            webhose_api_key = f.readline().strip()
        
    except:
        raise IOError('search.key file not found')

    return webhose_api_key

def run_query(search_terms, size=10):
    """Given a string containing search items (query), and a number of results
    to return (default 10), returns a list of results from the Webhose API,
    with each result consisting of a title, link and summary."""

    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError('Webhose key not found')

    #base URL for the Webhose API
    root_url = 'http://webhose.io/search'

    #format the query string - escape special characters
    query_string = urllib.parse.quote(search_terms)
    #print(query_string)
    #string formatting to construct complete API URL

    search_url = ('{root_url}?token={key}&format=json&q={query}''&sort=relevancy&size={size}').format(root_url=root_url, key=webhose_api_key, query=query_string, size=size)
    #print(search_url)
    results = []

    try:
        #connects to Webhose API and converts response to Python dict
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        json_response = json.loads(response)

        #loop through posts, appending each to the results list as a dict
        #characters 200 or less
        for post in json_response['posts']:
            results.append({'title':post['title'],'link':post['url'],'summary':post['text'][:200]})
    except:
        print("Error when querying the Webhose API")
        
    return results
    

#execution bit
if __name__ == '__main__':
    print("Starting Rango population script...")
    search = input('What are your search terms?')
    query_results = run_query(search)
    print(query_results)
    
        

