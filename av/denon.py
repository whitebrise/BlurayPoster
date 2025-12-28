"""
Copyright (C) 2025 whitebrise

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
"""
import asyncio
import time

import denonavr
import logging
from typing import Callable

from abstract_classes import AV, AVException

logger = logging.getLogger(__name__)


class Denon(AV):
    def __init__(self, config: dict):
        super().__init__(config)
        self._denon = None
        try:
            self._ip = self._config.get('IP')
            self._play_start_uri = self._config.get('PlayStartUri')
            self._play_stop_uri = self._config.get('PlayStopUri')
        except Exception as e:
            raise AVException(e)

    def start_before(self, **kwargs):
        pass

    async def _change_hdmi(self, hdmi):
        if self._denon is None:
            self._denon = denonavr.DenonAVR(self._ip)
            await self._denon.async_setup()
        await self._denon.async_update()
        await self._denon.async_set_input_func(hdmi)
        await self._denon.async_telnet_disconnect()

    def play_begin(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_start_uri is None:
            return
        steps = str.split(self._play_start_uri, "&")
        for step in steps:
            command, operate = str.split(step, "=")
            logger.debug("denon play begin command: {}, operate: {}".format(command, operate))
            if command.lower() == 'sleep':
                time.sleep(int(operate))
                continue
            elif command.lower() == 'hdmi':
                asyncio.run(self._change_hdmi(operate))
            else:
                logger.warning("denon not support this command: {}, operate: {}".format(command, operate))
            time.sleep(0.5)

    def play_end(self, on_message: Callable[[str, str], None], **kwargs):
        if self._play_stop_uri is None:
            return
        steps = str.split(self._play_stop_uri, "&")
        for step in steps:
            command, operate = str.split(step, "=")
            logger.debug("denon play end command: {}, operate: {}".format(command, operate))
            if command.lower() == 'sleep':
                time.sleep(int(operate))
                continue
            elif command.lower() == 'hdmi':
                asyncio.run(self._change_hdmi(operate))
            else:
                logger.warning("denon not support this command: {}, operate: {}".format(command, operate))
            time.sleep(0.5)
