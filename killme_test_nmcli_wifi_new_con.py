import subprocess

ssidName = "__nebuchadnezzar__"
ssidPassword = "misiumisiu"
print(f'ssidName : {ssidName}; ssidPassword : {ssidPassword};')
#answer = (rs('nmcli dev wifi con "'+ssidName+'" password '+ssidPassword))
name =ssidName
print(f"name {name}")
subprocess.Popen(["nmcli","dev","wifi", 'con', name, 'password', ssidPassword])