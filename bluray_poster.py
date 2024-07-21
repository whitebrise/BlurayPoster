import logging
import os
import importlib
import time
from logging.handlers import TimedRotatingFileHandler
from configuration import Configuration
from abstract_classes import *


def setup_logging(log_level_str):
    """
    建立日志，滚动日志，每天一个日志文件，保留最近7天
    :return:
    """
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logger = logging.getLogger()
    log_level = getattr(logging, log_level_str.upper(), logging.DEBUG)
    logger.setLevel(log_level)

    handler = TimedRotatingFileHandler(
        filename=os.path.join(log_directory, 'bluray_poster.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )

    formatter = logging.Formatter(
        '%(asctime)s %(filename)s %(levelname)s, clientID: console, message: %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if log_level == logging.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)


def dynamic_import(module_name, class_name):
    """
    动态导入
    :param module_name:
    :param class_name:
    :return:
    """
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Error importing module {module_name}: {e}")
    try:
        cls = getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(f"Error importing class {class_name} from module {module_name}: {e}")
    return cls


def initialize_component(component_key, config, exception_class):
    """
    初始化指定组件
    :param component_key:
    :param config:
    :param exception_class:
    :return:
    """
    component_config = config.get(component_key)
    if component_config and "Executor" in component_config:
        try:
            module_name, class_name = component_config["Executor"].rsplit('.', 1)
            cls = dynamic_import(module_name, class_name)
            return cls(component_config)
        except ImportError as e:
            logging.error(f"Error importing {component_key}: {e}")
            raise exception_class(f"Error initializing {component_key}")
    else:
        logging.warning(f"Configuration for {component_key} not found or incomplete.")
        return None


def initialize_components(config):
    """
    初始化所有组件
    :param config:
    :return:
    """
    try:
        player = initialize_component("Player", config, PlayerException)
        tv = initialize_component("TV", config, TVException)
        av = initialize_component("AV", config, AVException)

        media_config = config.get("Media")
        if media_config and "Executor" in media_config:
            module_name, class_name = media_config["Executor"].rsplit('.', 1)
            media_class = dynamic_import(module_name, class_name)
            media = media_class(player, tv, av, media_config)
            logging.info("Media operations completed successfully")
            return media
        else:
            raise MediaException("Error initializing Media: Configuration not found or incomplete.")

    except (PlayerException, TVException, AVException, MediaException) as e:
        logging.error(f"Initialization error: {e.message}")


if __name__ == "__main__":
    try:
        config_dir = os.getenv('CONFIG_DIR', 'config') + "/config.json"
        my_config = Configuration(path=config_dir)
        if my_config.initialize():
            setup_logging(my_config.get("LogLevel"))
            logger = logging.getLogger(__name__)
            logger.info("Starting the main application")
            my_media = initialize_components(my_config)
            my_media.start_before()
            my_media.start()
            while True:
                time.sleep(100)
        else:
            print("Failed to initialize configuration")
    except Exception as e:
        print("Failed to start program, ex: {}".format(e))
