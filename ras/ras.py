import logging
import time

from oot import OotAmqp

_logger = logging.getLogger(__name__)

volume = 99
duration = 0.1
hz = 440


class RasLauncher(OotAmqp):
    template = "eficent.ras"
    oot_input = "rfid_read"

    def __init__(self, connection, reader, display, buzzer, version, path):
        super().__init__(connection)
        self.version = version
        self.path = path
        self.display = display
        self.display._welcome_logo()
        self.reader = reader
        self.buzzer = buzzer
        self.minutes = 0
        self.functions.append(
            [self.display_show]
        )
        self.functions.append(
            [self.get_data_mfrc522]
        )
        self.showing_on_display = True

    def get_data_mfrc522(self, **kwargs):
        time.sleep(5.0)
        while True:
            uid = self.reader.scan_card()
            if uid:
                return uid

    def amqp_demo(self, channel, basic_deliver, properties, body):
        _logger.info(body)
        self.queue.put(body.decode('UTF-8'))

    def get_default_amqp_options(self):
        res = super().get_default_amqp_options()
        res["demo"] = self.amqp_demo
        return res

    def display_show(self):
        while True:
            if not (time.localtime().tm_min == self.minutes) and not self.showing_on_display:  # Display is
                self.minutes = time.localtime().tm_min  # refreshed only
                self.display._display_time()

    def _run(self):
        self.showing_on_display = False
        super()._run()

    def check_key(self, key, **kwargs):
        self.showing_on_display = True
        self.display.display_msg('Connecting...')
        return super().check_key(key, **kwargs)

    def process_result(self, key, result, **kwargs):
        if result.get("status", "ko") == "ok":
            self.display.display_msg(result.get("action_msg", "Checked"))
            if result.get('action', 'check_out') == 'check_in':
                self.buzzer.play([(volume, hz, duration), (volume, hz * 1.28, duration)])
            else:
                self.buzzer.play([(volume, hz * 1.28, duration), (volume, hz, duration)])
        else:
            self.buzzer.play([(volume, hz * 1.26, duration), (volume, hz, duration)])
            self.display.display_msg("CONTACT YOUR ADMIN")
        time.sleep(2)
        self.showing_on_display = False
        self.display._display_time()
