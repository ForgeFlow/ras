from urllib.request import urlopen

def can_connect(url):
    # Checks if it can connect tothe specified  url
    # returns True if it can connect
    # and false if it can not connect
    try:
        response = urlopen(url, timeout=10)
        return True
    except:
        return False

