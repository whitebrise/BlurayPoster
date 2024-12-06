"""
LG TV设备
"""

import logging
from abstract_classes import TV, TVException
from pywebostv.connection import WebOSClient
from pywebostv.controls import ApplicationControl, SourceControl


logger = logging.getLogger(__name__)


class LGWebos(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', None)
            self._key = self._config.get('Key', None)
            self._hdmi = self._config.get('HDMI', 1)
            self._subHdmi = self._config.get('SubHDMI', 2)
            self._play_stop_uri = self._config.get('PlayStopUri', None)
            self._store = {'client_key': self._key} if self._key is not None else {}
            self._current_app_id = None
        except Exception as e:
            raise TVException(e)

    def _get_key(self):
        """
        生成key
        :return:
        """
        client = WebOSClient(self._ip, secure=True)
        try:
            client.connect()
            for status in client.register(self._store):
                if status == WebOSClient.PROMPTED:
                    logger.info("need to confirm")
                elif status == WebOSClient.REGISTERED:
                    logger.info("register success")
            return True
        except Exception as e:
            logger.error("error when generate key, {}".format(e))
            return False

    def _change_hdmi(self, hdmi):
        client = WebOSClient(self._ip, secure=True)
        general_new_key = False
        try:
            client.connect()
            for status in client.register(self._store):
                if status == WebOSClient.PROMPTED:
                    logger.info("need to confirm")
                    general_new_key = True
                elif status == WebOSClient.REGISTERED:
                    logger.info("register success")
            if general_new_key:
                logger.info("general a new key, {}".format(self._store))
            app_control = ApplicationControl(client)
            self._current_app_id = app_control.get_current()
            source_control = SourceControl(client)
            source_list = source_control.list_sources()
            source_control.set_source(source_list[self._hdmi - 1])
            return True
        except Exception as e:
            logger.error("error when generate key, {}".format(e))
        return False

    def _set_active_app_by_id(self, app_id):
        """
        根据id精确返回
        :param app_id:
        :return:
        """
        client = WebOSClient(self._ip, secure=True)
        general_new_key = False
        try:
            client.connect()
            for status in client.register(self._store):
                if status == WebOSClient.PROMPTED:
                    logger.info("need to confirm")
                    general_new_key = True
                elif status == WebOSClient.REGISTERED:
                    logger.info("register success")
            if general_new_key:
                logger.info("general a new key, {}".format(self._store))
            app_control = ApplicationControl(client)
            app_list = app_control.list_apps()
            for app in app_list:
                if app["id"] == app_id:
                    app_control.launch(app)
                    return True
        except Exception as e:
            logger.error("error when generate key, {}".format(e))
        return False

    def _set_active_app_by_name(self, app_name):
        """
        根据名称模糊返回
        :param app_name:
        :return:
        """
        client = WebOSClient(self._ip, secure=True)
        general_new_key = False
        try:
            client.connect()
            for status in client.register(self._store):
                if status == WebOSClient.PROMPTED:
                    logger.info("need to confirm")
                    general_new_key = True
                elif status == WebOSClient.REGISTERED:
                    logger.info("register success")
            if general_new_key:
                logger.info("general a new key, {}".format(self._store))
            app_control = ApplicationControl(client)
            app_list = app_control.list_apps()
            for app in app_list:
                if app_name.lower() in app["title"].lower():
                    app_control.launch(app)
                    return True
        except Exception as e:
            logger.error("error when generate key, {}".format(e))
        return False

    def start_before(self, **kwargs):
        """
        获取key
        :param kwargs:
        :return:
        """
        self._get_key()

    def play_begin(self, on_message, **kwargs):
        if 'subPlayer' in kwargs:
            self._change_hdmi(self._subHdmi)
            return
        self._change_hdmi(self._hdmi)

    def play_end(self, on_message, **kwargs):
        if self._play_stop_uri is None:
            self._set_active_app_by_id(self._current_app_id)
        else:
            results = str.split(self._play_stop_uri, "=")
            key = results[0]
            value = results[1]
            if key.lower() == "hdmi":
                self._change_hdmi(value)
            elif key.lower() == "app":
                self._set_active_app_by_name(value)
