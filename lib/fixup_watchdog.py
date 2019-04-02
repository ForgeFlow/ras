import os

def ensure_watchdog():
    eol = '\n'

    fixup1 = 'dtparam=watchdog=on'
    fixup2 = 'options bcm2835_wdt heartbeat=14 nowayout=0'
    fixup3 = 'RuntimeWatchdogSec='

    file1 = '/boot/config.txt' # first file to be updated
    file2 = '/etc/modprobe.d/bcm2835-wdt.conf' # second file to be updated
    file3 = '/etc/systemd/system.conf' # third file to be updated

    with open(file1, 'r') as f:
        lines   = f.readlines()
        f.close()
        if fixup1 + eol not in lines:
            with open(file1, 'a') as f:
                f.write(fixup1 + eol)
                f.close()
            with open(file2, 'w') as f:
                f.write(fixup2 + eol)
                f.close()
            with open(file3, 'r') as f:
                lines   = f.readlines()
                f.close()
            with open(file3, 'w') as f:
                for line in lines:
                    if fixup3 in line:
                        f.write(fixup3 + \
                        " = 14" + eol )
                    else:
                        f.write(line)
                f.close()
            os.system('reboot now')
