"""
此类为抽象类，需要增加其他设备必须继承该类并重写方法
start_before用于初始化设备等
...
"""

from abc import ABC, abstractmethod
from typing import Callable


class PlayerException(Exception):
    """
    播放器异常
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Player(ABC):
    """
    播放器基类
    """
    def __init__(self, config: dict):
        self._config = config

    @abstractmethod
    def start_before(self, **kwargs):
        pass

    @abstractmethod
    def play(self, media_path: str, container: str, on_message: Callable[[str, str], None], on_play_begin,
             on_play_in_progress, on_play_end, **kwargs):
        pass


class TVException(Exception):
    """
    电视异常
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class TV(ABC):
    """
    电视基类
    """
    def __init__(self, config: dict):
        self._config = config

    @abstractmethod
    def start_before(self, **kwargs):
        pass

    @abstractmethod
    def play_begin(self, on_message: Callable[[str, str], None], **kwargs):
        pass

    @abstractmethod
    def play_end(self, on_message: Callable[[str, str], None], **kwargs):
        pass


class AVException(Exception):
    """
    功放异常
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class AV(ABC):
    """
    功放基类
    """
    def __init__(self, config: dict):
        self._config = config

    @abstractmethod
    def start_before(self, **kwargs):
        pass

    @abstractmethod
    def play_begin(self, on_message: Callable[[str, str], None], **kwargs):
        pass

    @abstractmethod
    def play_end(self, on_message: Callable[[str, str], None], **kwargs):
        pass


class MediaException(Exception):
    """
    媒体异常
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Media(ABC):
    """
    媒体基类
    """
    def __init__(self, player: Player, tv: TV, av: AV, config: dict, subPlayer: Player):
        self._player = player
        self._tv = tv
        self._av = av
        self._config = config
        self._subPlayer = subPlayer

    @abstractmethod
    def start_before(self, **kwargs):
        pass

    @abstractmethod
    def on_message(self, header: str, message: str):
        """
        消息回调事件
        :param header:
        :param message:
        :return:
        """
        pass

    @abstractmethod
    def on_play_begin(self, **kwargs):
        """
        播放开始事件
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def on_play_in_progress(self, **kwargs):
        """
        播放中事件
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def on_play_end(self, **kwargs):
        """
        播放结束事件
        :return:
        """
        pass

    @abstractmethod
    def start(self, **kwargs):
        pass
