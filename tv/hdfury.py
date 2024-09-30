"""
HDfury Vertex2 or VRRoom hdmi设备
"""
import requests
import logging
from abstract_classes import TV, TVException

logger = logging.getLogger(__name__)


class Hdfury(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', None)
            self._hdmi = self._config.get('HDMI', 1)
            self._play_stop_uri = self._config.get('PlayStopUri', None)
            self._uri = "http://{}/".format(self._ip)
        except Exception as e:
            raise TVException(e)



    def _change_hdmi(self, hdmi):
        """
        修改hdmi输入
        :return:
        """
        try:
            url = self._uri + "cmd?insel={}%204".format(hdmi)
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
        self._change_hdmi(self._hdmi)

    def play_end(self, on_message, **kwargs):
        """
        播放结束
        :param on_message:
        :param kwargs:
        :return:
        """
        # 控制播放结束后操作，只支持不同的hdmi
        if self._play_stop_uri is not None:
            results = str.split(self._play_stop_uri, "=")
            key = results[0]
            value = results[1]
            if key.lower() == "hdmi":
                self._change_hdmi(value)

