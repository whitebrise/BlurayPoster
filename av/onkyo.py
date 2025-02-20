"""
Copyright (C) 2025 whitebrise

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
"""

import time

import eiscp
import logging
from typing import Callable

from abstract_classes import AV, AVException

logger = logging.getLogger(__name__)


class Onkyo(AV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP')
            self._play_start_uri = self._config.get('PlayStartUri')
            self._play_stop_uri = self._config.get('PlayStopUri')
        except Exception as e:
            raise AVException(e)

    def start_before(self, **kwargs):
        pass

    def play_begin(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_start_uri is None:
            return
        steps = str.split(self._play_start_uri, "&")
        with eiscp.eISCP(self._ip) as receiver:
            for step in steps:
                command, operate = str.split(step, "=")
                logger.debug("onkyo play begin command: {}, operate: {}".format(command, operate))
                if command.lower() == 'sleep':
                    time.sleep(int(operate))
                    continue
                receiver.command('{} {}'.format(command, operate))
                time.sleep(0.5)

    def play_end(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_stop_uri is None:
            return
        steps = str.split(self._play_stop_uri, "&")
        with eiscp.eISCP(self._ip) as receiver:
            for step in steps:
                command, operate = str.split(step, "=")
                logger.debug("onkyo play end command: {}, operate: {}".format(command, operate))
                receiver.command('{} {}'.format(command, operate))
                time.sleep(0.5)
