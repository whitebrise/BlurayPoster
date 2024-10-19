"""
媒体库必须继承所有抽象类方法
"""

import json
import logging
import requests
import websocket
import threading
import time
from abstract_classes import *

logger = logging.getLogger(__name__)


class Emby(Media):
    def __init__(self, player: Player, tv: TV, av: AV, config: dict):
        super().__init__(player, tv, av, config)
        try:
            self._host = config.get('Host')
            self._user_name = config.get('Username')
            self._password = config.get('Password')
            self._exclude_video_ext = config.get("ExcludeVideoExt")
            if self._exclude_video_ext is None:
                self._exclude_video_ext = []
            self._client = config.get("Client")
            self._device = config.get("Device")
            self._device_id = config.get("DeviceId")
            self._version = config.get('Version')
            self._block_devices = config.get('BlockDevices')
            if self._block_devices is None:
                self._block_devices = []
            self._repeat_filter_timeout = config.get("RepeatFilterTimeout", 120)
            self._session = None
            self._block_sessions = []
            self._user_id = "abcd"
            self._access_token = None
            self._ws = None
            self._ws_thread = None
            self._play_item = None
            self._played_info = {}
        except Exception as e:
            raise MediaException(e)

    def _get_headers(self):
        """
        获取http的headers
        :return:
        """
        authorization = ('Emby UserId="{}", Client="{}", Device="{}", DeviceId="{}", Version="{}"'
                         .format(self._user_id, self._client, self._device, self._device_id, self._version))
        headers = {"X-Emby-Authorization": authorization, "Content-Type": "application/json",
                   "Accept": "application/json"}
        if self._access_token is not None:
            headers["X-MediaBrowser-Token"] = self._access_token
        return headers

    def _login(self):
        """
        登录emby
        :return:
        """
        try:
            url = "{}/emby/Users/AuthenticateByName".format(self._host)
            headers = self._get_headers()
            body = {
                "Username": self._user_name,
                "Pw": self._password
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 200:
                result = res.json()
                self._access_token = result["AccessToken"]
                self._user_id = result["User"]["Id"]
                logger.info("Login successful")
                self._register_device()
                return True
            else:
                logger.error(f"Failed to login: {res.status_code} {res.text}")
                return False
        except Exception as e:
            logger.error(f"Exception during login: {e}")
            return False

    def _register_device(self):
        """
        注册设备
        :return:
        """
        try:
            url = "{}/emby/Sessions/Capabilities/Full".format(self._host)
            headers = self._get_headers()
            body = {
                "PlayableMediaTypes": ["Audio", "Video"],
                "SupportsMediaControl": True,
                "SupportedCommands": ["Play", "Pause", "Stop"]
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 204:
                logger.debug("Device registered successfully")
            else:
                logger.error(f"Failed to register device: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during device registration: {e}")

    def _query_item(self, item_ids):
        """
        查询影片信息
        :param item_ids:
        :return:
        """
        try:
            url = "{}/emby/Items".format(self._host)
            headers = self._get_headers()
            body = "Fields=Path,MediaStreams&Ids={}".format(item_ids)
            res = requests.get(url=url, headers=headers, params=body)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            logger.error(f"Exception during device registration: {e}")

    def _on_ws_message(self, ws, message):
        logger.debug(f"Emby WebSocket Message Received: {message}")
        msg = json.loads(message)
        self._handle_msg(msg)

    def _on_ws_error(self, ws, error):
        logger.error(f"Emby WebSocket Error: {error}")

    def _on_ws_open(self, ws):
        logger.debug("Emby WebSocket Connection Opened")

    def _on_ws_close(self, ws, close_status_code, close_msg):
        logger.error(f"Emby WebSocket Close, code: {close_status_code}, msg: {close_msg}")

    def _connect_websocket(self):
        """
        连接ws
        :return:
        """
        retry_count = 0
        while True:
            try:
                websocket_url = (self._host.replace("http", "ws") + "/embywebsocket?api_key="
                                 + self._access_token + "&deviceId=" + self._device_id)
                self._ws = websocket.WebSocketApp(
                    websocket_url,
                    on_message=self._on_ws_message,
                    on_error=self._on_ws_error,
                    on_close=self._on_ws_close,
                    on_open=self._on_ws_open,
                    header=self._get_headers
                )
                self._ws.run_forever(ping_interval=10)
                self._ws = None
                retry_count += 1
                wait_time = min(60, (2 ** retry_count))
                logger.error(f"Attempting to reconnect in {wait_time} seconds...")
                time.sleep(wait_time)
                if retry_count >= 10:
                    retry_count = 0
            except websocket.WebSocketException as e1:
                logger.error(f"Emby WebSocket error: {e1}")
                time.sleep(5)  # 等待一段时间再尝试重连
            except Exception as e2:
                logger.error(f"Emby Other error: {e2}")
                time.sleep(5)  # 等待一段时间再尝试重连

    def _handle_msg(self, msg_data):
        """
        根据消息类型选择处理方式
        :param msg_data:
        :return:
        """
        msg_type = msg_data["MessageType"]
        if msg_type == "Play":
            self._handle_play(msg_data["Data"])
        elif msg_type == "Playstate":
            self._handle_play_state(msg_data["Data"])
        elif msg_type == "UserDataChanged":
            self._handle_user_data_change(msg_data["Data"])

    def _handle_play(self, data):
        pass

    def _handle_play_state(self, data):
        pass

    def _handle_user_data_change(self, data):
        """
        处理播放用户数据
        :param data:
        :return:
        """
        if self._user_id == data["UserId"]:
            user_data_list = data["UserDataList"]
            user_data = user_data_list[0]
            # 防止重复播放
            if (user_data["ItemId"] in self._played_info
                    and time.time() - self._played_info[user_data["ItemId"]] <= self._repeat_filter_timeout):
                self.on_message("Warning", "{}s 内不允许播放相同的影片".format(self._repeat_filter_timeout))
                return
            item_infos = self._query_item(user_data["ItemId"])
            if item_infos is not None and "Items" in item_infos and len(item_infos["Items"]) > 0:
                for item in item_infos["Items"]:
                    path = item["Path"]
                    if item["IsFolder"] is True:
                        continue
                    if path.split('.')[-1] in self._exclude_video_ext:
                        logger.info(f"exclude video, path: {path}")
                        continue
                    self._play_item = item
                    logger.info(f"prepare to play this video, path: {path}")
                    self._run_player()
                    return
                self._play_item = None

    def _get_all_sessions(self):
        """
        获取所有session
        :return:
        """
        try:
            self._block_sessions.clear()
            self._session = None
            if len(self._block_devices) <= 0:
                return True
            url = "{}/emby/Sessions".format(self._host)
            headers = self._get_headers()
            res = requests.get(url=url, headers=headers)
            if res.status_code == 200:
                logger.debug("get sessions successfully")
                result = res.json()
                for session in result:
                    for block_session in self._block_devices:
                        if session["DeviceName"] == block_session:
                            self._block_sessions.append(session)
                            break
                        elif session["DeviceName"] == self._device:
                            self._session = session
                            break
                if len(self._block_sessions) < len(self._block_devices):
                    logger.warning("not all block devices find their sessions")
                return self._session is not None
            else:
                logger.error(f"Failed to get sessions: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during get sessions: {e}")
        return False

    def _session_playing_stop(self, session_id):
        """
        阻止session播放
        :return:
        """
        try:
            url = "{}/emby/Sessions/{}/Playing/Stop".format(self._host, session_id)
            headers = self._get_headers()
            body = {
                "Command": "Stop",
                "SeekPositionTicks": 0,
                "ControllingUserId": "string"
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res. status_code == 204:
                logger.debug("media play stop successfully")
                return True
            else:
                logger.error(f"Failed to stop play media: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during stop media: {e}")
        return False

    def _session_playing(self, session_id):
        """
        报告已播放
        :param session_id:
        :return:
        """
        try:
            url = "{}/emby/Sessions/Playing".format(self._host)
            headers = self._get_headers()
            body = {
                "CanSeek": True,
                "ItemId": self._play_item["Id"],
                "SessionId": session_id,
                "IsPaused": False,
                "IsMuted": False,
                "PositionTicks": 0,
                "PlayMethod": "DirectPlay",
                "RepeatMode": "RepeatNone"
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 204:
                logger.debug("notify emby the movie start successfully")
                return True
            else:
                logger.error(f"Failed to notify emby the movie start: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during notify emby the movie start: {e}")
        return False

    def _session_play_progress(self, session_id, position_ticks, total_ticks, is_paused=False, is_muted=False):
        """
        报告播放进程
        :param session_id:
        :param position_ticks:
        :param total_ticks:
        :param is_paused:
        :param is_muted:
        :return:
        """
        try:
            url = "{}/emby/Sessions/Playing/Progress".format(self._host)
            headers = self._get_headers()
            body = {
                "CanSeek": True,
                "ItemId": self._play_item["Id"],
                "SessionId": session_id,
                "IsPaused": is_paused,
                "IsMuted": is_muted,
                "PositionTicks": position_ticks,
                "RunTimeTicks": total_ticks,
                "PlayMethod": "DirectPlay",
                "RepeatMode": "RepeatNone",
                "EventName": "timeupdate"
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 204:
                logger.debug("media report progress successfully")
                return True
            else:
                logger.error(f"Failed to report progress: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during report progress: {e}")
        return False

    def _session_play_stopped(self, session_id, position_ticks, is_paused=False, is_muted=False):
        """
        报告播放结束
        :param session_id:
        :param position_ticks:
        :param is_paused:
        :param is_muted:
        :return:
        """
        try:
            url = "{}/emby/Sessions/Playing/Stopped".format(self._host)
            headers = self._get_headers()
            body = {
                "CanSeek": True,
                "ItemId": self._play_item["Id"],
                "SessionId": session_id,
                "IsPaused": is_paused,
                "IsMuted": is_muted,
                "PositionTicks": position_ticks,
                "PlayMethod": "DirectPlay",
                "RepeatMode": "RepeatNone",
                "EventName": "timeupdate"
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 204:
                logger.debug("notify emby the movie stopped successfully")
                return True
            else:
                logger.error(f"Failed to notify emby the movie stopped: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during notify emby the movie stopped: {e}")
        return False

    def _set_if_watched(self, watched):
        """
        设置影片是否观看
        :return:
        """
        try:
            url = "{}/emby/Users/{}/PlayedItems/{}".format(self._host, self._user_id, self._play_item["Id"])
            headers = self._get_headers()
            if watched:
                res = requests.post(url=url, headers=headers)
            else:
                res = requests.delete(url=url, headers=headers)
            if res.status_code == 204:
                logger.debug("set video watched status successfully")
                return True
            else:
                logger.error(f"Failed to set video watched status: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during set video watched status: {e}")
        return False

    def _session_send_message(self, session_id, header, message, timeout_ms):
        """
        发送通知消息
        :param session_id:
        :param header:
        :param message:
        :param timeout_ms:
        :return:
        """
        try:
            url = "{}/emby/Sessions/{}/Message".format(self._host, session_id)
            headers = self._get_headers()
            body = {
                "Id": "Stop",
                "Text": message,
                "Header": header,
                "TimeoutMs": timeout_ms
            }
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 204:
                logger.debug("send message successfully")
                return True
            else:
                logger.error(f"Failed to send message: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"Exception during send message: {e}")
        return False

    def _run_player(self):
        """
        调用player播放器
        :return:
        """
        if self._player is None:
            logger.error("no player is ready")
            return False
        if self._play_item is None:
            logger.error("no video info")
            return False
        # 阻止正在串流的播放
        if self._get_all_sessions() is not True:
            return False
        for block_session in self._block_sessions:
            self._session_playing_stop(block_session["Id"])
        # 播放
        return self._player.play(self._play_item["Path"], self._play_item["Container"],
                                 self.on_message, self.on_play_begin,
                                 self.on_play_in_progress, self.on_play_end)

    def _connect(self):
        """
        连接Emby服务器
        :return:
        """
        if self._access_token is None:
            if not self._login():
                logger.error("Login failed. Unable to connect to emby.")
                return
        self._ws_thread = threading.Thread(target=self._connect_websocket)
        self._ws_thread.daemon = True
        self._ws_thread.start()
        logger.info("WebSocket thread started")

    def on_message(self, header, message):
        """
        消息回调事件
        :param header:
        :param message:
        :return:
        """
        for block_session in self._block_sessions:
            self._session_send_message(block_session["Id"], header, message, timeout_ms=3500)

    def on_play_begin(self, **kwargs):
        """
        播放开始事件
        :param kwargs:
        :return:
        """
        # 记录下此时的播放时间
        self._played_info[self._play_item["Id"]] = time.time()
        for block_session in self._block_sessions:
            # # 报告已开始
            # self._session_playing(self._session["Id"])
            pass
        # 然后通知tv,av
        if self._tv is not None:
            self._tv.play_begin(self.on_message)
        if self._av is not None:
            self._av.play_begin(self.on_message)

    def on_play_in_progress(self, **kwargs):
        """
        播放中事件
        :param kwargs:
        :return:
        """
        # position_ticks = kwargs["position_ticks"]
        # total_ticks = kwargs["total_ticks"]
        # for block_session in self._block_sessions:
        #     self._session_play_progress(block_session["Id"], position_ticks, total_ticks)
        pass

    def on_play_end(self, **kwargs):
        """
        播放结束事件
        :return:
        """
        # 删掉播放很久的影片信息
        played_info_copy = self._played_info.copy()
        now_time = time.time()
        for item_id, last_played_time in played_info_copy.items():
            if now_time - last_played_time > self._repeat_filter_timeout:
                self._played_info.pop(item_id)
        # 报告结束
        position_ticks = kwargs["position_ticks"]
        total_ticks = kwargs["total_ticks"]
        # for block_session in self._block_sessions:
        #     self._session_play_stopped(block_session["Id"], position_ticks)
        # 设置影片已播放(观看超过70%设置为已观看)
        if total_ticks >= 6000000000 and position_ticks >= 0.7 * total_ticks:
            self._set_if_watched(True)
        # else:
        #     self._set_if_watched(False)

        # 通知av,tv
        if self._tv is not None:
            self._tv.play_end(self.on_message)
        if self._av is not None:
            self._av.play_end(self.on_message)
        self._play_item = None

    def start_before(self, **kwargs):
        # 初始化启动其他设备
        if self._player is not None:
            self._player.start_before()
        if self._tv is not None:
            self._tv.start_before()
        if self._av is not None:
            self._av.start_before()

    def start(self, **kwargs):
        # 启动自己, 并开始监听流程
        self._connect()
        pass
