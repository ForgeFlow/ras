import json, os

def del_update():
    json_file = open('/home/pi/ras/dicts/data.json')
    json_data = json.load(json_file)
    jsonarray = json.dumps(json_data)
    json_file.close()
    os.remove("/home/pi/ras/dicts/data.json")

    try:
        json_noupdate = jsonarray.replace('"update": ["update_software"], ', '')
    except:
        json_noupdate = jsonarray

    print(json_data)
    print(jsonarray)
    print(json_noupdate)

    json_file2 = open('/home/pi/ras/dicts/data.json','w+')
    json_file2.write(json_noupdate)
    json_file2.close()
