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

    
    

