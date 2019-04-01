import os

def ensure_autostart_after_crash():
    end_of_line = '\n'

    fixup1 = 'Restart=always'
    fixup2 = 'RestartSec=3'

    index = '[Service]' # insert fixup
                        # just after index

    file_to_be_updated = '/lib/systemd/system/ras-launcher.service'

    with open(file_to_be_updated, 'r') as f:
        lines   = f.readlines()
        print(lines)
        if fixup1 + end_of_line not in lines:
            f.close()
            with open(file_to_be_updated, 'w') as f:
                for line in lines:
                    if line.strip(end_of_line) == index:
                        f.write(index  + end_of_line + \
                                fixup1 + end_of_line + \
                                fixup2 + end_of_line )
                    else:
                        f.write(line)
            f.close()
            os.system('systemctl daemon-reload')
            os.system('systemctl restart ras-launcher')

#ensure_autostart_after_crash()
