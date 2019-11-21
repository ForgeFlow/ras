import logging
import os
import time

import psutil
from oot import Field, OotXmlRpc, OotAmqp, api

from .button import Button

_logger = logging.getLogger(__name__)

volume = 99
duration = 0.1
hz = 440


class RasLauncher(OotXmlRpc, OotAmqp):
    template = "eficent.ras"
    model = "hr.employee"
    function = "register_attendance"
    admin_id = Field(name="Admin key", required=True)

    def __init__(
        self,
        connection,
        reader,
        display,
        buzzer,
        up_pwr,
        up,
        down_pwr,
        down,
        version,
        path,
    ):
        super().__init__(connection)
        self.version = version
        self.path = path
        self.display = display
        self.display._welcome_logo()
        self.reader = reader
        self.buzzer = buzzer
        self.minutes = 0
        self.admin = False
        self.confirm_button = False
        self.menu_id = 0
        self.menus = [
            ("Estandar usage", False, False),
            ("Demo usage", False, self.print_card),
            ("Reboot", self.reboot, False),
            ("Reset", self.reset, False),
        ]
        name, self.confirm, self.function = self.menus[self.menu_id]
        self.showing_on_display = True
        self.button_up = Button(up_pwr, up, self.button_result("up"))
        self.button_down = Button(down_pwr, down, self.button_result("down"))

    def button_result(self, value):
        def button_function(channel):
            self.queue.put((value, {"button": True}))

        return button_function

    def print_card(self, key, **kwargs):
        return {"status": "ok", "action_msg": key}

    @api.oot
    def get_data_mfrc522(self, **kwargs):
        time.sleep(5.0)
        while True:
            uid = self.reader.scan_card()
            if uid:

                return uid

    def start_execute_function(self, function, *args, queue=False, **kwargs):
        p = psutil.Process(os.getpid())
        # set to lowest priority, this is windows only, on Unix use ps.nice(19)
        p.nice(6)

    def amqp_demo(self, channel, basic_deliver, properties, body):
        print(body)
        _logger.info(body.decode("utf-8"))
        self.queue.put(body.decode("UTF-8"))

    def get_default_amqp_options(self):
        res = super().get_default_amqp_options()
        res["demo"] = self.amqp_demo
        return res

    @api.oot
    def display_show(self):
        while True:
            if (
                not (time.localtime().tm_min == self.minutes)
                and not self.showing_on_display
            ):
                self.minutes = time.localtime().tm_min  # refreshed only
                self.display._display_time()
            time.sleep(0.5)

    def _run(self):
        self.showing_on_display = False
        self.display._display_time()
        super()._run()

    def check_key(self, key, **kwargs):
        self.showing_on_display = True
        if key == self.admin_id:
            return {"admin_key": True}
        if not self.admin:
            self.display.display_msg("Connecting...")
            if self.function:
                return self.function(key, **kwargs)
            result = super().check_key(key, **kwargs)
            _logger.info(result)
            return result
        if kwargs.get("button", False):
            return {"status": "ok", "button": key}
        return {}

    def menu_selection(self, key, result, **kwargs):
        if not result.get("button"):
            return
        if result.get("button") == "down":
            if self.confirm_button:
                self.confirm_button = False
            self.menu_id = (self.menu_id + 1) % len(self.menus)
            name, self.confirm, self.pre_function = self.menus[self.menu_id]
            self.display.display_msg(name)
            return
        if not self.confirm or self.confirm_button:
            if self.confirm_button:
                self.confirm(key=key, result=result, **kwargs)
            self.admin = False
            self.confirm_button = False
            self.display._display_time()
            self.function = self.pre_function
        else:
            self.confirm_button = True
            self.display.display_msg("Are you sure?")

    def reset(self, **kwargs):
        _logger.info("Reseting data")
        if self.connection_path:
            os.remove(self.connection_path)
        self.reboot(**kwargs)

    def process_result(self, key, result, **kwargs):
        if result.get("admin_key", False):
            _logger.info("Entering on admin")
            self.admin = not self.admin
            self.menu_id = 0
            if self.admin:
                self.button_down.poweron()
                self.button_up.poweron()
                name, self.confirm, self.pre_function = self.menus[self.menu_id]
                self.display.display_msg(name)
            else:
                self.button_down.poweroff()
                self.button_up.poweroff()
                self.showing_on_display = False
                self.display._display_time()
            return
        if self.admin:
            return self.menu_selection(key, result, **kwargs)
        if result.get("status", "ko") == "ok":
            self.display.display_msg(result.get("action_msg", "Checked"))
            if result.get("action", "check_out") == "check_in":
                self.buzzer.play(
                    [
                        (volume, hz, duration * 2),
                        (volume, hz * 1.28, duration * 2),
                        (volume, 5, duration * 2),
                    ]
                )
            else:
                self.buzzer.play(
                    [(volume, hz * 1.26, duration), (volume, hz, duration)]
                )
        else:
            self.buzzer.play(
                [
                    (volume, hz * 4, duration / 4),
                    (volume, 20, duration / 2),
                    (volume, hz * 4, duration / 4),
                    (volume, 20, duration / 2),
                    (volume, hz * 4, duration / 4),
                    (volume, 20, duration / 2),
                    (volume, hz * 4, duration / 4),
                    (volume, 20, duration / 2),
                    (volume, hz * 4, duration / 4),
                    (volume, 20, duration / 2),
                ]
            )
            self.display.display_msg("CONTACT YOUR ADMIN")
        time.sleep(2)
        self.showing_on_display = False
        self.display._display_time()
