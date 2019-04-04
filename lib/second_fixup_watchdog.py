import os

def ensure_watchdog():
    eol = '\n'

    fixup1 = 'max-load-1	'
    fixup2 = 'watchdog-device'
    fixup3 = 'watchdog-timeout       = 15'

    file   = '/etc/watchdog.conf' # file to be updated

    if not os.path.isfile(file):
        os.system('apt-get install watchdog')
        with open(file, 'r') as f:
            lines   = f.readlines()
            f.close()
        with open(file, 'w') as f:
            for line in lines:
                if fixup1 in line:
                    f.write(fixup1 + \
                    "	= 24" + eol )
                elif fixup2 in line:
                    f.write(fixup2 + \
	            '		= /dev/watchdog' + eol )
                else:
                    f.write(line)
            f.write(fixup3 +eol)
            f.close()

        os.system('systemctl start watchdog')
