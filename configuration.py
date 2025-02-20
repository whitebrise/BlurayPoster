"""
Copyright (C) 2025 whitebrise

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version
"""

import yaml
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
            with open(self._path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
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
