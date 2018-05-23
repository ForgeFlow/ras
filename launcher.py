import menu_test2
import os

if __name__ == '__main__':
    update =  menu_test2.foo()
    print "UPDATE: " + str(update)
    if update == True:
        os.system('./update_repo.sh')
        os.system('sudo reboot')

