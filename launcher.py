import logging.config
import os

import psutil
import RPi.GPIO as GPIO
from oot.device import Buzzer, CardReader
from oot.upgrade import upgrade
from packaging import version as packaging_version

import ras.migrations as migrations
from ras import Display, RasLauncher

p = psutil.Process(os.getpid())
#p.nice(6)  # give the launcher process a low priority

GPIO.setmode(GPIO.BOARD)

path = os.path.dirname(os.path.realpath(__file__))

log_folder = path + "/log"

if not os.path.isdir(log_folder):
    os.mkdir(log_folder)

logging.config.fileConfig(path + "/ras.logging.conf")

data_folder = path + "/data"

if not os.path.isdir(data_folder):
    os.mkdir(data_folder)


with open(os.path.join(path, "version"), "r") as f:
    version = f.read()

current_version = "0"
if os.path.exists(os.path.join(data_folder, "version")):
    with open(os.path.join(data_folder, "version"), "r") as f:
        current_version = f.read()

if upgrade(
    packaging_version.parse(current_version),
    packaging_version.parse(version),
    path,
    migrations,
):
    with open(os.path.join(data_folder, "version"), "w") as f:
        f.write(version)

display = Display(path)
RasLauncher(
    data_folder + "/data.json",
    CardReader(spd=10000),
    display,
    Buzzer(12, 13),
    35, 31, 35, 29,
    version,
    path,
).run()
