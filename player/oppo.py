import socket
import time
import logging
import requests
import json
import threading
import urllib.parse
from abstract_classes import Player, PlayerException


logger = logging.getLogger(__name__)


class Oppo(Player):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', 10)
            self._udp_timeout = self._config.get('UdpTimeout', 10)
            self._auth = self._config.get('Auth', [])
            self._use_nfs = self._config.get('NFSPrefer', True)
            self._udp_server_address = (self._ip, 7624)
            self._http_host = f"http://{self._ip}:436"
            self._mapping_path_list = self._config.get('MappingPath')
            self._play_start_timeout = self._config.get('PlayStartTimeout', 5)
            self._play_end_timeout = self._config.get('PlayEndTimeout', 5)
            self._device_list = []
            self._on_message = None
            self._on_play_begin = None
            self._on_play_in_progress = None
            self._on_play_end = None
            self._position_ticks = 0
            self._total_ticks = 0
            self._play_status = -1
        except Exception as e:
            raise PlayerException(e)

    def _open_oppo_http(self):
        """
        开启OPPO HTTP协议
        :return:
        """
        open_http_success = False
        udp_msg = "NOTIFY OREMOTE LOGIN"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)  # 设置非阻塞模式
        start_time = time.time()
        while True:
            # 发送消息
            sock.sendto(bytes(udp_msg, "utf-8"), self._udp_server_address)
            # 尝试接收响应
            try:
                data, server = sock.recvfrom(1024)
                msg = data.decode("utf-8")
                if "REPORT ADDRESS TO OREMOTE" in msg:
                    open_http_success = True
                    logger.debug("open the oppo http success")
                    break
            except BlockingIOError:
                # 如果没有数据则继续发送
                time.sleep(1)  # 等待 1 秒再重试
            except Exception:
                break
            # 检查是否超时
            if time.time() - start_time > self._udp_timeout:
                logger.error(f"open the oppo http failed, timeout: {self._udp_timeout}s")
                break
        sock.close()
        return open_http_success

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

    def _sign_in(self):
        """
        oppo认证
        :return:
        """
        try:
            params = {
                "appIconType": 1,
                "appIpAddress": "192.168.1.8",
            }
            url = self._http_host + "/signin?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error(f"sign in the oppo http failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"sign in the oppo http exception, error: {e}")
        return False

    def _get_device_list(self):
        """
        获取网络设备列表
        :return:
        """
        try:
            url = self._http_host + "/getdevicelist"
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return result["devicelist"]
            logger.error(f"get device list failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"get device list exception, error: {e}")
        return None

    def _login_samba_with_out_id(self, host):
        """
        登录smb
        :param host:
        :return:
        """
        try:
            params = {
                "serverName": host,
            }
            url = self._http_host + "/loginSambaWithOutID?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error(f"login samba failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"login samba exception, error: {e}")
        return False

    def _mount_shared_folder(self, host, folder, username, password):
        """
        挂载smb目录
        :return:
        """
        try:
            params = {
                "server": host,
                "folder": folder,
                "bWithID": 1,
                "userName": username,
                "password": password,
                "bRememberID": 1
            }
            url = self._http_host + "/mountSharedFolder?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error(f"mount samba shared folder failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"mount samba shared folder exception, error: {e}")
        return False

    def _get_samba_share_folder_list(self):
        """
        获取挂载的smb目录
        :return:
        """
        try:
            url = self._http_host + "/getSambaShareFolderlist"
            res = requests.get(url)
            b = res.content.rsplit(b'\x01')
            files = []
            num = 1
            for c in b:
                if c.find(b'\x02') == -1:
                    index = 0
                    ult = 0
                    d = c
                    while index != -1:
                        index = c.find(b'\x00', index)
                        if index == -1:
                            d = d[ult:]
                        else:
                            ult = index + 1
                            index = index + 1
                    e = d.decode('utf-8')
                    if e != '':
                        file = {"id": num, "folder": e}
                        num = num + 1
                        files.append(file)
            return files
        except Exception as e:
            logger.error(f"get samba share folder failed, error: {e}")
        return None

    def _get_nfs_share_folder_list(self):
        """
        获取挂载的nfs目录
        :return:
        """
        try:
            url = self._http_host + "/getNfsShareFolderlist"
            res = requests.get(url)
            print(res.text)
            b = res.content.rsplit(b'\x01')
            files = []
            num = 1
            for c in b:
                if c.find(b'\x02') == -1:
                    index = 0
                    ult = 0
                    d = c
                    while index != -1:
                        index = c.find(b'\x00', index)
                        if index == -1:
                            d = d[ult:]
                        else:
                            ult = index + 1
                            index = index + 1
                    e = d.decode('utf-8')
                    if e != '':
                        file = {"id": num, "folder": e}
                        num = num + 1
                        files.append(file)
            return files
        except Exception as e:
            logger.error(f"get nfs share folder failed, error: {e}")
        return None

    def _get_file_list(self, path):
        """
        获取挂载的文件目录
        :return:
        """
        try:
            params = {
                "mediatype": 3,
                "flag": 1,
                "filetype": 1,
                "path": path,
            }
            url = self._http_host + "/getfilelist?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            print(res.text)
            b = res.content.rsplit(b'\x01')
            files = []
            num = 1
            for c in b:
                if c.find(b'\x02') == -1:
                    index = 0
                    ult = 0
                    d = c
                    while index != -1:
                        index = c.find(b'\x00', index)
                        if index == -1:
                            d = d[ult:]
                        else:
                            ult = index + 1
                            index = index + 1
                    e = d.decode('utf-8')
                    if e != '':
                        file = {"id": num, "folder": e}
                        num = num + 1
                        files.append(file)
            return files
        except Exception as e:
            logger.error(f"get nfs share folder failed, error: {e}")
        return None

    def _login_nfs(self, host):
        """
        登录nfs
        :param host:
        :return:
        """
        try:
            params = {
                "serverName": host
            }
            url = self._http_host + "/loginNfsServer?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error(f"login nfs failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"login nfs exception, error: {e}")
        return False

    def _mount_nfs_shared_folder(self, host, folder):
        """
        挂载nfs目录
        :param host:
        :param folder:
        :return:
        """
        try:
            params = {
                "server": host,
                "folder": folder,
            }
            print("mount path, {}".format(params))
            url = self._http_host + "/mountNfsSharedFolder?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error(f"mount nfs share folder failed, reason: {res.text}")
        except Exception as e:
            logger.error(f"mount nfs share folder exception, error: {e}")
        return False

    def _check_folder_has_bdmv(self, nfs_prefer, path):
        """
        播放bdmv
        :param nfs_prefer:
        :param path:
        :return:
        """
        try:
            params = {
                "folderpath": f"/mnt/nfs1/{path}" if nfs_prefer else f"/mnt/cifs1/{path}",
            }
            url = self._http_host + "/checkfolderhasbdmv?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error("play bdmv folder failed, reason: {}, path: {}".format(res.text, params["folderpath"]))
        except Exception as e:
            logger.error(f"play bdmv folder exception, error: {e}")
        return False

    def _play_normal_file(self, nfs_prefer, path):
        """
        播放文件
        :param nfs_prefer:
        :param path:
        :return:
        """
        try:
            params = {
                "path": f"/mnt/nfs1/{path}" if nfs_prefer else f"/mnt/cifs1/{path}",
                "playMode": 0,
                "extraNetPath": "192.168.88.50",
                "appDeviceType": 2,
                "type": 1,
                "index": 0
            }
            url = self._http_host + "/playnormalfile?" + self.dict_to_url_encoded_json(params)
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return True
            logger.error("play file failed, reason: {}, path: {}".format(res.text, params))
        except Exception as e:
            logger.error(f"play file exception, error: {e}")
        return False

    def _get_movie_play_info(self):
        """
        获取正在播放的影片信息
        :return:
        """
        try:
            url = self._http_host + "/getmovieplayinfo"
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return result
        except Exception as e:
            logger.error(f"get samba share folder failed, error: {e}")
        return None

    def _get_playing_time(self):
        """
        获取播放时间
        :return:
        """
        try:
            url = self._http_host + "/getplayingtime"
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    if result["cur_time"] > 0:
                        self._position_ticks = result["cur_time"] * 10000000
                    if result["total_time"] > 0:
                        self._total_ticks = result["total_time"] * 10000000
                    return True
        except Exception as e:
            logger.error(f"get samba share folder failed, error: {e}")
        return None

    def _get_global_info(self):
        """
        获取全局信息
        :return:
        """
        try:
            url = self._http_host + "/getglobalinfo"
            res = requests.get(url)
            if res.status_code == 200:
                result = res.json()
                if "success" in result and result["success"]:
                    return result
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
        timeout = 5
        while True:
            time.sleep(1)
            global_info = self._get_global_info()
            if global_info is None:
                if time.time() - last_qry_time > timeout:
                    break
                else:
                    continue
            if self._play_status == 0:
                if global_info["is_video_playing"] is True:
                    self._play_status = 1
                    self._on_play_begin()
            elif self._play_status == 1:
                if global_info["is_video_playing"] is True:
                    if time.time() - last_report_time > 60:
                        self._get_playing_time()
                        self._on_play_in_progress(position_ticks=self._position_ticks, total_ticks=self._total_ticks)
                        last_report_time = time.time()
                else:
                    break
            last_qry_time = time.time()
        # 报告已结束
        self._on_play_end(position_ticks=self._position_ticks, total_ticks=self._total_ticks)
        self._position_ticks = 0
        self._total_ticks = 0
        self._play_status = -1

    def _wait_for_get_device_list(self):
        """
        等待获取所有协议和目录
        :return:
        """
        while True:
            try:
                if self._open_oppo_http() is True and self._sign_in() is True:
                    device_list = self._get_device_list()
                    if device_list is not None and len(device_list) > 0:
                        self._device_list = device_list
            except Exception as e:
                logger.error(f"get device_list exception, error: {e}")
            finally:
                time.sleep(5)

    def start_before(self, **kwargs):
        """
        启动前
        :return:
        """
        thread = threading.Thread(target=self._wait_for_get_device_list)
        thread.daemon = True
        thread.start()

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
        real_path = media_path
        for mapping_path in self._mapping_path_list:
            real_path = media_path.replace(mapping_path["Media"], mapping_path["NFS"], 1) if self._use_nfs \
                else media_path.replace(mapping_path["Media"], mapping_path["SMB"], 1)
        sever, folder, file = self.extract_path_parts(real_path)
        if self._use_nfs:
            if not self._login_nfs(sever):
                return on_message("Error", "cannot login nfs")
            if not self._mount_nfs_shared_folder(sever, folder):
                return on_message("Error", "cannot mount nfs folder")
        else:
            if not self._login_samba_with_out_id(sever):
                return on_message("Error", "cannot login smb")
            used_key = None
            for auth_item in self._auth:
                if self._mount_shared_folder(sever, folder, auth_item["Username"], auth_item["Password"]) is True:
                    used_key = auth_item
                    break
            if used_key is None:
                return on_message("Error", "cannot mount smb folder")
            # 用过的key移到队尾
            self._auth.remove(used_key)
            self._auth.append(used_key)
        if container != "bluray":
            if not self._play_normal_file(self._use_nfs, file):
                return on_message("Error", "cannot play normal file, {}".format(media_path))
        else:
            if not self._check_folder_has_bdmv(self._use_nfs, file):
                return on_message("Error", "cannot play bdmv folder, {}".format(media_path))
        # 开始播放并监控播放进度
        self._on_message = on_message
        self._on_play_begin = on_play_begin
        self._on_play_in_progress = on_play_in_progress
        self._on_play_end = on_play_end
        thread = threading.Thread(target=self._track_play_status)
        thread.daemon = True
        thread.start()
