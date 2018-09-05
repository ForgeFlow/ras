import os

import lib.menu as menu
import lib.deletesubstring as deletesubstring

if __name__ == '__main__':
    update =  menu.m_functionality()
    print("UPDATE: " + str(update))
    if update == True:
        os.system('sh update_repo.sh')
        deletesubstring.del_update()
        os.system('sudo reboot')

