"""
Copyright (C) 2025 whitebrise

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
"""

import requests
import logging
from abstract_classes import TV, TVException


logger = logging.getLogger(__name__)


class SonyBravia(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', None)
            self._key = self._config.get('Key', None)
            self._hdmi = self._config.get('HDMI', 1)
            self._subHdmi = self._config.get('SubHDMI', 1)
            self._play_stop_uri = self._config.get('PlayStopUri', None)
            self._uri = "http://{}/sony/".format(self._ip)
            self._app_list = []
        except Exception as e:
            raise TVException(e)

    def _get_power_status(self):
        """
        获取电源状态
        :return:
        """
        try:
            url = self._uri + "system"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "getPowerStatus",
                "id": 1,
                "params": [],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return result["result"][0]["status"]
            logger.error("get tv power status error, reason: {}".format(res.text))
        except Exception as e:
            logger.error("get tv power status exception, error: {}".format(e))
        return None

    def _change_power_status(self, power_status):
        """
        开/关电视
        :param power_status:
        :return:
        """
        try:
            url = self._uri + "system"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "setPowerStatus",
                "id": 1,
                "params": [
                    {"status": power_status}
                ],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return True
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _get_current_external_inputs_status(self):
        """
        获取外部hdmi信息
        :return:
        """
        try:
            url = self._uri + "avContent"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "getCurrentExternalInputsStatus",
                "id": 1,
                "params": [
                ],
                "version": "1.1"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return result
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _get_web_app_status(self):
        """
        获取正在使用的app
        :return:
        """
        try:
            url = self._uri + "appControl"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "getWebAppStatus",
                "id": 1,
                "params": [
                ],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return result
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _get_application_list(self):
        """
        获取app列表
        :return:
        """
        try:
            url = self._uri + "appControl"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "getApplicationList",
                "id": 1,
                "params": [
                ],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    self._app_list = result["result"][0]
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _get_application_status_list(self):
        """
        获取web应用状态
        :return:
        """
        try:
            url = self._uri + "appControl"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "getApplicationStatusList",
                "id": 1,
                "params": [
                ],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return result
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _set_active_app(self, uri):
        """
        激活app
        :param uri:
        :return:
        """
        try:
            url = self._uri + "appControl"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "setActiveApp",
                "id": 1,
                "params": [{
                    "uri": uri
                }],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return True
        except Exception as e:
            logger.error("change tv power status error: {}".format(e))
        return False

    def _change_hdmi(self, hdmi):
        """
        修改hdmi输入
        :return:
        """
        try:
            url = self._uri + "avContent"
            header = {
                "X-Auth-Psk": self._key,
                "Content-Type": "text/plain;charset=UTF-8"
            }
            data = {
                "method": "setPlayContent",
                "id": 1,
                "params": [
                    {"uri": "extInput:hdmi?port={}".format(hdmi)}
                ],
                "version": "1.0"
            }
            res = requests.post(url=url, headers=header, json=data)
            if res.status_code == 200:
                result = res.json()
                if "result" in result:
                    return True
        except Exception as e:
            logger.error("change tv channel error: {}".format(e))
        return False

    def _check_tv_open(self):
        """
        检测TV是否开启，可以自动开启的TV就将其开启
        :return:
        """
        if self._get_power_status() is None:
            logger.error("need to power on the tv")
            return False
        self._change_power_status(True)
        return True

    def _search_app_name(self, app_name):
        """
        关键字查找app
        :param app_name:
        :return:
        """
        for item in self._app_list:
            if app_name.lower() in item["title"].lower():
                return item["uri"]
        return None

    def start_before(self, **kwargs):
        """
        初始化执行
        :param kwargs:
        :return:
        """
        pass

    def play_begin(self, on_message, **kwargs):
        """
        播放开始
        :param on_message:
        :param kwargs:
        :return:
        """
        if self._check_tv_open() is not True:
            return False
        if 'subPlayer' in kwargs:
            self._change_hdmi(self._subHdmi)
            return
        self._change_hdmi(self._hdmi)

    def play_end(self, on_message, **kwargs):
        """
        播放结束
        :param on_message:
        :param kwargs:
        :return:
        """
        # 控制播放结束后操作，默认返回emby app
        if self._play_stop_uri is None:
            self._get_application_list()
            emby_uri = self._search_app_name("emby")
            if emby_uri is not None:
                self._set_active_app(emby_uri)
        else:
            results = str.split(self._play_stop_uri, "=")
            key = results[0]
            value = results[1]
            if key.lower() == "hdmi":
                self._change_hdmi(value)
            elif key.lower() == "app":
                self._get_application_list()
                app_uri = self._search_app_name(value)
                if app_uri is not None:
                    self._set_active_app(app_uri)
