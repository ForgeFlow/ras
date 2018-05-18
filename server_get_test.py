#!/usr/bin/env python

import requests

payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.get('http://192.168.1.47/ex.json', data=payload) #, auth=('user1', 'password1'))
r1 = requests.get('http://my.webtool/')
r2 = requests.put('http://192.168.1.47/ex.json', data=payload) #, auth=('user1', 'password1'))
print r.text
print r1.text
print r2.text
