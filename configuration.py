"""
配置管理器
"""
import json
import logging

logger = logging.getLogger(__name__)


class Configuration(object):
    def __init__(self, path):
        self._path = path
        self._config = None

    def initialize(self):
        """
        初始化
        :return:
        """
        try:
            with open(self._path, 'r') as file:
                self._config = json.load(file)
                return True
        except Exception as e:
            logger.error(f"read config file error: {e}")
        return False

    def get(self, key):
        """
        获取指定值
        :param key:
        :return:
        """
        if self._config is not None and key in self._config:
            return self._config[key]
        return None
