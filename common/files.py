import os

def isDirectoryEmpty(directory):
    try:
        if not os.listdir(directory):
            return True
    except Exception as e:
        print("there was an exception: ",e)
        return True
    return False

def getOneLineOneWord(file): # VORSICHT: not tested!!!
    try:
        with open(file, "r") as f:
            lines = f.readlines()
        return lines
    except:
        return []

#def appendLine(file,line):