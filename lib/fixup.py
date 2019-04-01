import os

def ensure_autostart_after_crash():
    end_of_line = '\n'

    fixup = 'Restart=always'+ end_of_line + \
            'RestartSec=3'+ end_of_line

    index = '[Service]' # insert fixup
                        # just after index

    file_to_be_updated = '/lib/systemd/system/ras-launcher.service'

    with open(file_to_be_updated, 'r') as f:
        lines   = f.readlines()
        if fixup not in f.read():
            f.close()
            with open(file_to_be_updated, 'w') as f:
                for line in lines:
                    if line.strip(end_of_line) == index:
                        f.write(index + end_of_line + fixup)
                    else:
                        f.write(line)
            f.close()
            os.system('systemctl daemon-reload')
            os.system('systemctl restart ras-launcher')

#make_service_to_autostart()

