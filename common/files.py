import os

def isDirectoryEmpty(directory):
    try:
        if not os.listdir(directory):
            return True
    except Exception as e:
        print("there was an exception: ",e)
        return True
    return False