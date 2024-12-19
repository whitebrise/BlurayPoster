import time
import logging
import requests
import json
import threading
import urllib.parse
from abstract_classes import Player, PlayerException
from base64 import b64encode

logger = logging.getLogger(__name__)


class Coreelec(Player):


    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', 10)
            self._use_nfs = self._config.get('NFSPrefer', True)
            self._port = self._config.get('Port', 8080)
            self._http_host = f"http://{self._ip}:{self._port}/jsonrpc"
            self._mapping_path_list = self._config.get('MappingPath')
            self._play_start_timeout = self._config.get('PlayStartTimeout', 5)
            self._play_end_timeout = self._config.get('PlayEndTimeout', 5)
            self._subPlayer = self._config.get('SubPlayer', False)
            self._device_list = []
            self._on_message = None
            self._on_play_begin = None
            self._on_play_in_progress = None
            self._on_play_end = None
            self._user = self._config.get('User', "")
            self._password = self._config.get('Password', "")
            self._bytes_user = f"{self._user}:{self._password}".encode('utf-8')
            self._Auth_str = b64encode(self._bytes_user).decode('utf-8')
            self._headers = {
                "Authorization": "Basic {}".format(self._Auth_str),
                "Content-Type": "application/json",
            }
            """ a29kaTpjbHExMjM0NTY= """
            self._position_ticks = 0
            self._total_ticks = 0
            self._play_status = -1
        except Exception as e:
            raise PlayerException(e)

    @staticmethod
    def dict_to_url_encoded_json(data: dict) -> str:
        return urllib.parse.quote(json.dumps(data))

    @staticmethod
    def extract_path_parts(path):
        # 替换路径分隔符
        normalized_path = path.replace('\\\\', '\\').replace('\\', '/').replace("//", "/")
        # 分割路径
        parts = normalized_path.split('/')
        # 提取路径部分
        server = parts[1]
        filename = parts[-1]
        folder = '/'.join(parts[2:-1])
        return server, folder, filename

    def _get_play_info(self):
        """
        获取全局信息
        :return:
        """
        try:
            request_body = [{"jsonrpc": "2.0", "method": "Player.GetProperties", "params": [1, ["playlistid", "speed",
                                                                                                "position", "totaltime",
                                                                                                "time", "percentage",
                                                                                                "shuffled", "repeat",
                                                                                                "canrepeat",
                                                                                                "canshuffle", "canseek",
                                                                                                "partymode"]],
                             "id": 1}]
            res = requests.post(self._http_host, headers=self._headers, data=json.dumps(request_body))
            if res.status_code == 200:
                result = res.json()
                if result[0] is not None:
                    return result[0]
        except Exception as e:
            logger.error(f"get samba share folder failed, error: {e}")
        return None

    def _track_play_status(self):
        """
        跟踪播放进度
        :return:
        """

        self._play_status = 0
        last_qry_time = time.time()
        last_report_time = 0
        timeout = 15

        while True:
            time.sleep(1)
            play_info = self._get_play_info()
            logger.debug(play_info)
            if play_info is None:
                if time.time() - last_qry_time > timeout:
                    break
                else:
                    continue
            if self._play_status == 0:
                if play_info["result"]["speed"] == 1:
                    self._play_status = 1
                    logger.debug("set playing status to 1")
                    if self._subPlayer is True:
                        self._on_play_begin(subPlayer=1)
                    else:
                        self._on_play_begin()
                elif time.time() - last_qry_time > timeout:
                    break
                else:
                    continue
            elif self._play_status == 1:
                if not (play_info["result"]["speed"] == 0 and play_info["result"]["position"] == -1):
                    if time.time() - last_report_time > 60:
                        total_hours = play_info["result"]["totaltime"]["hours"]
                        total_minutes = play_info["result"]["totaltime"]["minutes"]
                        total_seconds = play_info["result"]["totaltime"]["seconds"]
                        total_milliseconds = play_info["result"]["totaltime"]["milliseconds"]

                        elapse_hours = play_info["result"]["time"]["hours"]
                        elapse_minutes = play_info["result"]["time"]["minutes"]
                        elapse_seconds = play_info["result"]["time"]["seconds"]
                        elapse_milliseconds = play_info["result"]["time"]["milliseconds"]
                        self._total_ticks = total_hours * 3600000000 + total_minutes * 60000000 + total_seconds * 1000000 + total_milliseconds * 1000
                        self._position_ticks = elapse_hours * 3600000000 + elapse_minutes * 60000000 + elapse_seconds * 1000000 + elapse_milliseconds * 1000

                        self._on_play_in_progress(position_ticks=self._position_ticks, total_ticks=self._total_ticks)
                        last_report_time = time.time()
                        logger.debug("update play position ticks: {}".format(self._position_ticks))

                else:
                    logger.debug("play end break")
                    break
            last_qry_time = time.time()
        # 报告已结束
        self._on_play_end(position_ticks=self._position_ticks, total_ticks=self._total_ticks)
        logger.debug("play end")
        self._position_ticks = 0
        self._total_ticks = 0
        self._play_status = -1

    def _clear(self):
        """
        清除播放列表
        :return:
        """
        try:
            request_body = [{"jsonrpc": "2.0", "method": "Playlist.Clear", "params": [1], "id": 68}]
            res = requests.post(self._http_host, headers=self._headers, data=json.dumps(request_body))
            if res.status_code == 200:
                result = res.json()
                if "OK" in res.text:
                    return True
                logger.error("play file failed, reason: {}, path: {}".format(res.text, request_body))

        except Exception as e:
            logger.error(logger.error(f"play file exception, error: {e}"))
            return False

    def _insert(self, path, isDirectory):
        """
        添加播放列表
        :return:
        """
        try:
            if isDirectory:
                request_body = [{"jsonrpc": "2.0", "method": "Playlist.Insert", "params": [1, 0, {
                "directory": path}], "id": 69}]
            else:
                request_body = [{"jsonrpc":"2.0","method":"Playlist.Insert","params":[1,0,{
                    "file": path}],"id":23}]
            res = requests.post(self._http_host, headers=self._headers, data=json.dumps(request_body))
            if res.status_code == 200:
                result = res.json()
                if "OK" in res.text:
                    return True
                logger.error("insert file failed, reason: {}, path: {}".format(res.text, request_body))

        except Exception as e:
            logger.error(logger.error(f"insert file exception, error: {e}"))
            return False

    def _play(self, path, isDirectory):
        """
        播放文件
        :param nfs_prefer:
        :param path:
        :return:
        """
        try:
            logger.debug("play {}".format(path))

            if not self._clear():
                return False

            if not self._insert(path, isDirectory):
                return False

            # 设置请求的 URL 和头部信息

            request_body = [{"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"position":0,"playlistid":1},"options":{}},"id":70}]

            # 发起 POST 请求
            res = requests.post(self._http_host, headers=self._headers, data=json.dumps(request_body))

            if res.status_code == 200:
                result = res.json()
                if "OK" in res.text:
                    return True
                logger.error("play file failed, reason: {}, path: {}".format(res.text, request_body))
        except Exception as e:
            logger.error(f"play file exception, error: {e}")
            return False

    def start_before(self, **kwargs):
        """
        启动前
        :return:
        """
        pass

    def play(self, media_path: str, container, on_message, on_play_begin, on_play_in_progress, on_play_end, **kwargs):
        """
        播放影片
        :param media_path:
        :param container:
        :param on_message:
        :param on_play_begin:
        :param on_play_in_progress:
        :param on_play_end:
        :param kwargs:
        :return:
        """
        if self._play_status >= 0:
            return on_message("Notification", "movie is playing or prepare to playing, wait!")
        # 转换目录
        media_path = (media_path.replace('\\\\', '\\').
                      replace("\\", "/").replace("//", "/"))
        real_path = media_path
        for mapping_path in self._mapping_path_list:
            real_path = real_path.replace(mapping_path["Media"], mapping_path["NFS"], 1) if self._use_nfs \
                else real_path.replace(mapping_path["Media"], mapping_path["SMB"], 1)
        real_path = real_path.replace("//", "/")
        logger.debug("transfer path, from: {}, to: {}".format(media_path, real_path))
        sever, folder, file = self.extract_path_parts(real_path)
        logger.debug("curt path, sever: {}, folder:  {}, file: {}".format(sever, folder, file))
        if self._use_nfs:
            real_path = "nfs://"+real_path
        else:
            real_path = "smb://"+real_path
        if container == "mkv" or container == "mp4" or container == "iso":
            if not self._play(real_path, False):
                return on_message("Error", "cannot play {}".format(media_path))
        else:
            if not self._play(real_path, True):
                return on_message("Error", "cannot play {}".format(media_path))


        # 开始播放并监控播放进度
        self._on_message = on_message
        self._on_play_begin = on_play_begin
        self._on_play_in_progress = on_play_in_progress
        self._on_play_end = on_play_end
        thread = threading.Thread(target=self._track_play_status)
        thread.daemon = True
        thread.start()
