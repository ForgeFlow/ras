#!/usr/bin/env python

import sys, termios, tty, os, time

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

button_delay = 0.2

start_time = time.time()

elapsed_time = 0.0

while elapsed_time <= 30.0:
    char = getch()

    if (char == "p"):
        print("Stop!")
        exit(0)

    if (char == "a"):
        print("Left pressed")
        time.sleep(button_delay)

    elif (char == "d"):
        print("Right pressed")
        time.sleep(button_delay)

    elif (char == "w"):
        print("Up pressed")
        time.sleep(button_delay)

    elif (char == "s"):
        print("Down pressed")
        time.sleep(button_delay)

    elif (char == "1"):
        print("Number 1 pressed")
        time.sleep(button_delay)
    print elapsed_time
    elapsed_time = time.time() - start_time
