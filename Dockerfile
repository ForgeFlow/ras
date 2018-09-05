FROM debian:stretch

RUN apt update && apt install -yq \
   python3-smbus i2c-tools git python3-dev python3-pip \
   libfreetype6-dev libjpeg-dev build-essential libsdl-dev \
   libportmidi-dev libsdl-ttf2.0-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libopenjp2-7 && \
   python3-rpi.gpio dnsmasq hostapd isc-dhcp-server && \
   apt clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r ras/requeriments.txt
# Set our working directory
WORKDIR /home/pi/

# Copy requirements.txt first for better cache on later pushes
RUN git clone https://github.com/lthiery/SPI-Py.git && \
    cd SPI-Py && \
    python3 setup.py install && \
    cd .. && \
    rm -R SPI-Py

EXPOSE 80
EXPOSE 3000

COPY . ./ras

RUN cp -f /home/pi/ras/rc.local /etc/
# config-server will run when container starts up on the device

ENTRYPOINT ["ras/docker-entrypoint.sh"]

CMD ["python3","-u","/home/pi/ras/launcher.py"]


# " general_group.add_argument('--display', '-d', type=str, default=display_choices[6], help='Display type, supports real devices or emulators. Allowed values are: {0}'.format(', '.join(display_choices)), choices=display_choices, metavar='') "