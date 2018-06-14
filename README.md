## How to install and configure Raspbian on a RPi Zero W (for the RFID attendance project) ##

Some different libraries and codes from other repositories are employed to be able to run our program. Thanks to them from here for these great programs, and all the recognitions for them for the use of their code.

Test 17.

## General configuration in Ubuntu 16.04 ##

1. Download the Raspbian Lite image from [The Raspberry official site](https://www.raspberrypi.org/downloads/raspbian/) as a ZIP.

2. Download [Etcher](https://etcher.io/) to flash the SD card.

3. Insert the SD card in the PC.

4. Execute Etcher. Once it is opened, select the Raspbian Lite image, select the SD card as drive and click in "Flash!". It will take several minutes.

5. Once the SD card has been flashed, go to the two generated partitions (boot and rootfs), in terminal or using the filesystem (folders).

6. To enable the ssh (we will use it to connect to the RPi), create a blank file called "ssh" (no extension needed) at the boot partition (not the boot folder of the rootfs partition).

7. Go to the rootfs partition and open the file etc/wpa_supplicant/wpa_supplicant.conf (beware and be sure you are not at your computer folders, you have to modify the SD ones!).

8. Add the following lines to the end (substituting the contents into the ):

       network={
         ssid="my network name"
         psk="my network password"
       }

   *For other possible network configurations, see https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

9. Add the country code too (to choose the correct frequency bands), as follows (you can find yours at [Country Codes List](http://www.nationsonline.org/oneworld/country_code_list.htm) - ISO ALPHA-2 Code):

       country=XX

10. Go to etc/network/ and open the "interfaces" file.

11. Find this block in the file (if it is not present, go to the next step):

        allow-hotplug wlan0
        iface wlan0 inet manual
            wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

12. Substitute the block with (if it is not present, just add the next block to the end of the file):

        auto wlan0
        allow-hotplug wlan0
        iface wlan0 inet dhcp
            wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

    *There is the possibility of fixing the IP (static) so it is easier to find. See https://medium.com/@DavidMaitland/raspberry-pi-zero-headless-setup-92fb72daf88d for more details.

13. Unmount the partitions and eject the SD card.

14. Introduce it in the RPi Zero, and plug the cable to give it power.

15. Wait for some time so that the RPi can configure itself.

16. Open a terminal in your computer to connect through SSH to the RPi. There are several ways (from easier to more complex/annoying):

    16.1. Try the next command:

       > ssh pi@raspberrypi.local
      
    If it worked, it will ask you for a password. Introduce "raspberry" (default password), and you will be able to manage the RPi through terminal by SSH. Go to step 17 now.

    *If you have another RPi connected or you had in the past, it may not work. Use $ssh-keygen -R raspberrypi.local first to clear any previous reference to raspberry.local.

    16.2. If the previous method didn't worked, we need to find the RPi IP adress. To do that, there are two possibilities:
    
       16.2.1. Use nmap:
          
       > sudo apt-get install nmap
       
       > nmap -sn 192.168.1.0/24
                  
       It will show all the connected devices to the WiFi network by their IPs. The problem is that you won't know which one matches your RPi. You will need to try until you find them, or use the command before connecting the RPi, so that the IP that appears when it is connected would be the right one.
          
       16.2.2. Download a smartphone app called Fing. Once it is installed, when you initialize it, it will look for the connected devices to the same network than it, and it will tell you the device description. Look for "Raspberry Pi". 
     
    16.3. Once we know the RPi IP adress, use the next command with the proper IP:

       > ssh pi@192.168.1.XX

    If it worked, it will ask you for a password. Introduce "raspberry" (default password), and you will be able to manage the RPi through terminal by SSH. Go to step 17 now.

17. Now, let's configure the RPi for our use. Introduce the following command to opne the configuration page:

    > sudo raspi-config

18. Use the "Change User Password" option, and set your own password.

19. Use the "Advanced Options" to "Extend Filesystem".

20. At "Interfacing Options", enable SPI and I2C.

21. Then, go to "Finish" in the main page and reboot.

22. When the RPi SSH connections comes back to be possible, log in using your new password.

23. Update and upgrade (*1):

    > sudo apt-get -y update
    
    > sudo apt-get -y upgrade

24. Check if the SPI is really enabled using:

    > ls -l /dev/spidev*

    You must see two devices, one for each SPI bus.

25. Use the following commands to install some additional packages for the I2C:

    > sudo apt-get install -y python-smbus
    
    > sudo apt-get install -y i2c-tools

26. Check the I2C using:

    > ls -l /dev/i2c*

27. Install important programs/packages:

    > sudo apt-get install git
    
    > sudo apt-get install python-dev -y




## WiFi AP mode configuration (these steps are taken from the author's repository: https://github.com/jasbur/RaspiWiFi/tree/master) ##


1. Clone the repository and enter the folder:

    > cd
    
    > git clone https://github.com/jasbur/RaspiWiFi.git
    
    > cd Raspiwifi

2. Run the next command (the installation will take several minutes):

    > sudo python3 initial_setup.py

    This script will install all necessary prerequisites, copy configuration files, and reboot. When it finishes booting it should present itself in
    "Configuration Mode" as a WiFi access point with the name "RaspiWiFi Setup".

3. To enter again the RPi (these following steps are also useful for the normal use of the WiFi AP mode):

    - Connect to the "RaspiWiFi Setup" access point using any other WiFi enabled device.

    - Navigate to http://10.0.0.1:9191 using any web browser on the device you connected with.

    - Select the WiFi connection you'd like your Raspberry Pi to connect to from the drop down list and enter its wireless password on the page provided. If no
      encryption is enabled, leave the password box blank.

    - Click the "Connect" button.

    - At this point your Raspberry Pi will reboot and connect to the access point specified.

4. Finally, enter the RPi again using SSH as it was explained before.




## SPI and MFRC522 configuration ##

1. Clone the following repository and enter its folder:

    > cd
    
    > git clone https://github.com/lthiery/SPI-Py.git
    
    > cd SPI-py

2. Install the SPI module necessary for the MFRC522 library:

    > sudo python setup.py install

3. Then, clone the MFRC522 repository and enter its folder:

    > cd
    
    > git clone https://github.com/mxgxw/MFRC522-python.git
    
    > cd MFRC522-python

4. Connect the RFID Reader to the RPi Zero GPIO pins. The template for the explanation is: *RPI-GPIO-pin:RFIDReader-pin*.
   Concretely (I will refer here to the physical position of the GPIO pins, it can be found at https://pinout.xyz/pinout/io_pi_zero#):

    - GPIO_17(3.3V_Power_Supply):3.3V
    - GPIO_19(MOSI):MOSI
    - GPIO_20(GND):GND
    - GPIO_21(MISO):MISO
    - GPIO_22:RST
    - GPIO_23(SCLK):SCK
    - GPIO_24:SDA

5. Make a test to check that the installation has been succesful:

    > python Read.py

   Pass a card next to the RFID card, and it should be written at the terminal.



## SH1106 OLED screen configuration ##

1. Install some necessary packages:

    > cd
    
    > sudo apt-get install python-dev python-pip libfreetype6-dev libjpeg-dev build-essential

2. Install the luma.oled (https://luma-oled.readthedocs.io/en/latest/) package (it will take several minutes):

    > sudo -H pip install --upgrade luma.oled

3. Wire up the display to the RPi (same explanation template than for the MFRC522):

    - GPIO_1(3.3_Power_Supply):VDD
    - GPIO_3(SDA):SDA
    - GPIO_5(SCL):SCK
    - GPIO_6(GND):GND

4. Execute the following commands to confugire the user rights and install some necessary packages:
  
    > sudo usermod -a -G i2c,spi,gpio pi
    
    > sudo apt install python-dev python-pip libfreetype6-dev libjpeg-dev build-essential
    
    > sudo apt install libsdl-dev libportmidi-dev libsdl-ttf2.0-dev libsdl-mixer1.2-dev libsdl-image1.2-dev

5. Reboot (sudo reboot) and enter again the RPi through SSH.

6. Clone the repository and enter its folder:

    > cd
    
    > git clone https://github.com/rm-hull/luma.examples.git
    
    > cd luma.examples

7. Install the luma libraries using (it will take several minutes):

   > sudo -H pip install -e .

8. To test that everything is properly installed, run one of the examples (they can be found and explained at https://github.com/rm-hull/luma.examples):

    > cd examples
    
    > python pi_logo.py -d sh1106

   If the Raspberry Pi logo is displayed at the screen properly, the installation was succesful.

9. To make the SH1106 the default display (now, the default one is the SSD1306), let's edit one of the luma.core files:

    > sudo nano /usr/local/lib/python2.7/dist-packages/luma/core/cmdline.py

   Go to the "create_parser(description)" method, and change the following line:

        " general_group.add_argument('--display', '-d', type=str, default=display_choices[0], help='Display type, supports real devices or emulators. Allowed values are: {0}'.format(', '.join(display_choices)), choices=display_choices, metavar='') "
   
   By:

       " general_group.add_argument('--display', '-d', type=str, default=display_choices[6], help='Display type, supports real devices or emulators. Allowed values are: {0}'.format(', '.join(display_choices)), choices=display_choices, metavar='') "

   So that the default field is loaded with the 6th element of the display_choices list (SH1106) instead of the 0th (SSD1306).

10. Finally, test again the screen functioning but using:

    > python pi_logo.py

    If the Raspberry Pi logo is displayed at the screen properly, this final configuration was succesful.



## RFID - OLED - ODOO & Configuration Server program configuration ##

1. Clone the repository:

    > cd
    
    > git clone https://github.com/lurobe94/Raspberry_Code.git
    
2. Install Flask for the server:

    > pip install Flask
    
3. Test the server to create the data.json file, which the main program will read to get the Odoo parameters:

    > cd Raspberry_Code
    
    > sudo python hello-template.py
    
    Enter using any web browser to the Raspberry IP address (192.168.1.XX), and the login portal will appear. Enter the credentials (they can be changed in hello-template.py) and the configuration portal will appear. Enter then the Odoo parameters, a RFID card ID for the administrator, and do not select the update option, as you just clone it.
    
    The data.json file must have been generated in the repository. Check the parameters are right.

4. Test the main program by:

    > python launcher.py

   The program should work as expected. You can use the administrator RFID card to end the program.

5. To configure the RPi to run the program at boot, edit the rc.local file:

    > sudo nano /etc/rc.local 
    
   First, add these lines below the line "By default this script does nothing", to generate a log file for debugging errors.
   
       exec 2> /tmp/rc.local.log  
       exec 1>&2                  
       set -x                     
   Add at the end, but before the "exit 0" line, the following: 
   
       python /home/pi/Raspberry_Code/launcher.py & 
       pyhton /home/pi/Raspberry_Code/hello-template.py &
   
   Check the path, it can be different if you structured the folders in another way.
   Don't forget the " & ", so that the programs runs in separated processes and the RPi can initialize itself without problems.



## Final test ##

To test that everything is properly configured, use the following commands:

   > rm -f data.json
   
   > cd
   
   > python Raspberry_Code/manual_reset.py

So that the data.json is deleted (and you can test the whole functioning of the device) and the Raspberry is rebooted, as well as the WiFi parameters are erased.
In this way, you must see first the screen that tells you to enter to the WiFi network, and that once you configure the WiFi, the program asks you to go to the configuration portal, and once you enter the parameters, the main program is executed properly.


*****************************************************************************************************************************************************************

(*1) To save energy and speed up the device:

   - Boot up into multi-user mode (disabling the GUI on boot):

     > sudo systemctl set-default multi-user.target
     
   - To disable the HDMI, edit "/etc/rc.local" and add (above "exit 0"): "/usr/bin/tvservice -o"


