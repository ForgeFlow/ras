import time

def nowInSecondsAndMilliseconds():
    t = time.time()
    return (str(int((t - int(t/100)*100)))+ "s " + \
            str(int((t - int(t)) *1000))  + "ms")
