# import networkmanager.networkmanager as nm
# from dbus.mainloop.glib import DBusGMainLoop
# DBusGMainLoop(set_as_default=True)

# for dev in nm.NetworkManager.GetDevices():
#     print(f"{dev.DeviceType}")
#     if dev.DeviceType != nm.NM_DEVICE_TYPE_WIFI:
#         continue
#     for ap in dev.GetAccessPoints():
#         print('%-30s %dMHz %d%%' % (ap.Ssid, ap.Frequency, ap.Strength))

from common.common import runShellCommand_and_returnOutput as rs

answer = (rs("nmcli --get-values SSID d wifi list --rescan yes")) # it is a bytes literal

answer_string = answer #.decode("utf-8")

answer_list = answer_string.split('\n')

print(answer_list)