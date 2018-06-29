#!/bin/bash

cd /home/pi

echo 1

curl 'https://download.wetransfer.com/eu2/128d2bcdfd026f2fd5abc14c866e1fea20180629063243/RASv2.tar.gz?token=eyJhbGciOiJIUzI1NiJ9.eyJ1bmlxdWUiOiIxMjhkMmJjZGZkMDI2ZjJmZDVhYmMxNGM4NjZlMWZlYTIwMTgwNjI5MDYzMjQzIiwicHJvZmlsZSI6ImV1MiIsImZpbGVuYW1lIjoiUkFTdjIudGFyLmd6IiwiZXNjYXBlZCI6ImZhbHNlIiwiZXhwaXJlcyI6MTUzMDI1NDk0MSwid2F5YmlsbF91cmwiOiJodHRwOi8vcHJvZHVjdGlvbi5iYWNrZW5kLnNlcnZpY2UuZXUtd2VzdC0xLnd0OjkyOTIvd2F5YmlsbC92MS9hNTkyNTBmMjc3NTQ4MDg1ZDM0ZDE0MTE2MzQ3NGM4YWIyMjNjZjk4OTFlODVkMjA3NGM2NWJjYTU3MTkifQ.KksXxjraNMNlwfnlW9vkv4o6Bs8D4tr4lmyFhvcPTCY' --location --output RASv2.tar.gz

# THIS LINE OF THE DOWNLOAD NEEDS TO BE CHANGED TO THE SOURCE OF THE FILES.
# THERE CAN BE DIFFERENT DOWNLOAD FILES FOR THE DIFFERENT VERSIONS

echo 2

rm -R /home/pi/RASv2

echo 3

tar -zxf RASv2.tar.gz -C /home/pi/

echo 4

