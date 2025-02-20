"""
Copyright (C) 2025 whitebrise

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
"""

import time
import requests
import logging
from typing import Callable


from abstract_classes import AV, AVException


logger = logging.getLogger(__name__)


class Yamaha(AV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP')
            self._play_start_uri = self._config.get('PlayStartUri')
            self._play_stop_uri = self._config.get('PlayStopUri')
            self._uri = "http://{}/".format(self._ip)
        except Exception as e:
            raise AVException(e)

    def _change_hdmi(self, hdmi):
        """
        修改hdmi输入
        :return:
        """
        try:
            url = self._uri + "YamahaExtendedControl/v1/main/setInput?input={}".format(hdmi)
            header = {
                "Accept": "*/*"
            }

            res = requests.get(url=url, headers=header)
            if res.status_code == 200:
                if "OK" == res.text:
                    return True
        except Exception as e:
            logger.error("change hdmi error: {}".format(e))
        return False

    def _get_power_status(self):
        try:
            url = self._uri + "YamahaExtendedControl/v1/main/getStatus"
            header = {
                "Accept": "*/*"
            }
            res = requests.get(url, headers=header)
            if res.status_code == 200:
                ret = res.json()
                if ret["power"] == "on":
                    return True
        except Exception as e:
            logger.error("power status err: {}".format(e))
        return False

    def _change_power(self):
        try:
            url = self._uri + "YamahaExtendedControl/v1/main/setPower?power=on"
            header = {
                "Accept": "*/*"
            }
            res = requests.get(url, headers=header)
            if res.status_code == 200:
                ret = res.json()
                if ret["response_code"] == 0:
                    return True
        except Exception as e:
            logger.error("power status err: {}".format(e))
        return False

    def start_before(self, **kwargs):
        pass

    def play_begin(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_start_uri is None:
            return
        steps = str.split(self._play_start_uri, "&")
        if not self._get_power_status():
            self._change_power()
            time.sleep(3)
        for step in steps:
            command, operate = str.split(step, "=")
            logger.debug("yamaha play begin command: {}, operate: {}".format(command, operate))
            if command.lower() == 'sleep':
                time.sleep(int(operate))
                continue
            elif command.lower() == 'hdmi':
                self._change_hdmi(operate)
            time.sleep(0.5)

    def play_end(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_stop_uri is None:
            return
        steps = str.split(self._play_stop_uri, "&")
        for step in steps:
            command, operate = str.split(step, "=")
            logger.debug("yamaha play end command: {}, operate: {}".format(command, operate))
            if command.lower() == 'sleep':
                time.sleep(int(operate))
                continue
            elif command.lower() == 'hdmi':
                self._change_hdmi(operate)
            time.sleep(0.5)
