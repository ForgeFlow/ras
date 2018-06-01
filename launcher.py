import menu
import os
import deletesubstring

if __name__ == '__main__':
    update =  menu.m_functionality()
    print "UPDATE: " + str(update)
    if update == True:
        os.system('sh /home/pi/Raspberry_Code/update_repo.sh')
        deletesubstring.del_update()
        os.system('sudo reboot')

