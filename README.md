## How to install and configure Raspbian on a RPi Zero W (for the RFID attendance project) ##

Some different libraries and codes from other repositories are employed to be able to run our program. Thanks to them from here for these great programs, and all the recognitions for them for the use of their code.

## General configuration in Ubuntu 16.04 ##

1. Download the RFID Raspbian Lite image from [Last Releases](https://github.com/Eficent/ras/releases) as a ZIP.

2. Download [Etcher](https://etcher.io/) to flash the SD card.

3. Insert the SD card in the PC.

4. Execute Etcher. Once it is opened, select the RFID Raspbian Lite image, select the SD card as drive and click in "Flash!". It will take several minutes.

5. Plug SD Card in you RFID Attendance System and boot up, first boot will take 1 or 2 minutes long.

6. An AP Point called RFID Attendance System will prompt on you wifi scanner. Connect to it and join 192.168.42.1 to configure your Wifi connection.

7. Once Wifi connection has been configured properly, device will auto reboot. Wiat 1 or 2 minutes until device screen start.

8. Select RFID - Odoo on menu using second button.

9. If Odoo credentials are not set it up an ip will prompt on screen, browse it with a device connected in same wifi network.

10. By default login access is user: admin password: admin, it could be changed. 

11. Fill up the form and enjoy using your RFID Attendance System.
