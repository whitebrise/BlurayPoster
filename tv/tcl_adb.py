import logging
import os
from abstract_classes import TV, TVException
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen

logger = logging.getLogger(__name__)

class TclAdbTV(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            self._ip = self._config.get('IP', None)
            self._hdmi = self._config.get('HDMI', 1)
            self._play_stop_uri = self._config.get('PlayStopUri', None)
            
            # 优先从配置获取，否则默认放在 /config 下以便 Docker 持久化
            config_dir = os.environ.get('CONFIG_DIR', '/config')
            default_key_path = os.path.join(config_dir, 'adbkey')
            self._adbkey = self._config.get('ADBKey', default_key_path)
            
            self._device = None
            if not self._ip:
                raise TVException("TCL TV IP is required")
        except Exception as e:
            raise TVException(e)

    def _get_signer(self):
        """
        获取 ADB 签名器，如果 key 不存在则自动生成
        """
        if not os.path.exists(self._adbkey):
            logger.info(f"ADB key file not found, generating new key at: {self._adbkey}")
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(self._adbkey), exist_ok=True)
                keygen(self._adbkey)
            except Exception as e:
                logger.error(f"Failed to generate ADB keys: {e}")
                return None
        
        try:
            with open(self._adbkey, 'r') as f:
                priv = f.read()
            pub = None
            if os.path.exists(self._adbkey + '.pub'):
                with open(self._adbkey + '.pub', 'r') as f:
                    pub = f.read()
            
            return PythonRSASigner(pub, priv)
        except Exception as e:
            logger.error(f"Error loading ADB keys: {e}")
            return None

    def _connect(self):
        """
        连接 ADB 设备
        """
        if self._device and self._device.available:
            return True
            
        try:
            logger.info(f"Connecting to TCL TV via ADB at {self._ip}...")
            
            signer = self._get_signer()
            rsa_keys = [signer] if signer else None
            
            self._device = AdbDeviceTcp(self._ip, 5555, default_transport_timeout_s=9)
            self._device.connect(rsa_keys=rsa_keys, auth_timeout_s=10)
            logger.info(f"ADB connected to {self._ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to TCL TV ADB: {e}")
            self._device = None
            return False

    def _run_shell(self, command):
        """
        运行 shell 命令
        """
        if not self._connect():
            return None
        try:
            logger.debug(f"Running ADB shell: {command}")
            return self._device.shell(command)
        except Exception as e:
            logger.error(f"Error running ADB shell command '{command}': {e}")
            self._device = None # 可能是连接断开了
            return None

    def start_before(self, **kwargs):
        """
        初始化连接
        """
        self._connect()

    def play_begin(self, on_message, **kwargs):
        """
        播放开始，切换 HDMI
        """
        target_id = int(self._hdmi) + 7
        cmd = f"am start -n com.tcl.tv/.TVActivity --ei targetSourceId {target_id} --es referer adb"
        self._run_shell(cmd)

    def play_end(self, on_message, **kwargs):
        """
        播放结束，默认切回 Emby 或根据配置切换
        """
        # 如果配置为 null，默认返回 Emby
        uri = self._play_stop_uri if self._play_stop_uri else "app=emby"
        
        try:
            key, value = uri.split('=')
            if key.lower() == 'hdmi':
                target_id = int(value) + 7
                cmd = f"am start -n com.tcl.tv/.TVActivity --ei targetSourceId {target_id} --es referer adb"
                self._run_shell(cmd)
            elif key.lower() == 'app':
                if value.lower() == 'kodi':
                    self._run_shell("am start -n org.xbmc.kodi/org.xbmc.kodi.Main")
                elif value.lower() == 'emby':
                    self._run_shell("am start -n com.mb.android/com.mb.android.MainActivity")
        except Exception as e:
            logger.error(f"Error in TCL TV play_end: {e}")
