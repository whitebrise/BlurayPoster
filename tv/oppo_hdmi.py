"""
OPPO hdmi设备
"""
import time
import socket
import requests
import logging
from player.oppo import Oppo
from abstract_classes import TV, TVException

logger = logging.getLogger(__name__)


class OppoHdmi(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', None)
            self._hdmi = self._config.get('HDMI', 1)
            self._play_stop_uri = self._config.get('PlayStopUri', None)
            self._uri = f"http://{self._ip}:436"
        except Exception as e:
            raise TVException(e)

    def _choose_hdmi(self, hdmi):
        """
        修改hdmi输入 {"key":"NU1"}
        :return:
        """
        try:
            params = {
                "key": f"NU{hdmi}",
            }
            url = self._uri + "/sendremotekey?" + Oppo.dict_to_url_encoded_json(params)
            header = {
                "Accept": "*/*"
            }

            res = requests.get(url=url, headers=header)

            if res.status_code == 200:
                if "true" in res.text:
                    return True
        except Exception as e:
            logger.error("change hdmi error: {}".format(e))
        return False

    def _change_hdmi(self, hdmi):
        """
        修改hdmi输入 {"key":"SRC"}
        :return:
        """
        try:
            params = {
                "key": "SRC",
            }
            url = self._uri + "/sendremotekey?" + Oppo.dict_to_url_encoded_json(params)
            header = {
                "Accept": "*/*"
            }

            time.sleep(3)
            res = requests.get(url=url, headers=header)

            if res.status_code == 200:
                time.sleep(1)
                return self._choose_hdmi(hdmi)
        except Exception as e:
            logger.error("change hdmi error: {}".format(e))
        return False

    def _change_hdmi_socket(self, hdmi):
        """
        切换hdmi
        :param hdmi:
        :return:
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_msg = f"#SIS {hdmi}\r"
        try:
            client_socket.connect((self._ip, 23))
            client_socket.send(bytes(send_msg, "utf-8"))
            rec_msg = client_socket.recv(1024).decode("utf-8")
            if not "@ER" in rec_msg:
                return True
        except Exception as e:
            logger.error("change hdmi socket error: {}".format(e))
        finally:
            client_socket.close()
        return False

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
        pass

    def play_end(self, on_message, **kwargs):
        """
        播放结束
        :param on_message:
        :param kwargs:
        :return:
        """
        # 控制播放结束后操作，只支持hdmi或直通pass
        if self._play_stop_uri is not None:
            results = str.split(self._play_stop_uri, "=")
            key = results[0]
            value = results[1]
            if key.lower() == "hdmi":
                self._change_hdmi_socket(1)
            if key.lower() == "pass":
                self._change_hdmi(4)
