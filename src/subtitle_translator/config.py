import configparser
import os
from pathlib import Path
from .location_utils.location import _

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self, config_file='config.ini'):
        if hasattr(self, 'config'):
            return  # 如果已经初始化过，直接返回

        self.config = configparser.ConfigParser()

        # 尝试从环境变量获取配置路径
        config_path = os.getenv('CONFIG_FILE_PATH', None)
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 获取用户主目录下的配置目录
            self.config_path = Path.home() / ".config" / "subtitle_translator" / config_file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # 如果配置文件不存在，创建默认配置文件
        if not self.config_path.exists():
            self.config['settings'] = {
                'currentAI': 'openai',
                'debug_mode': 'False',
                'batch_size': '3',
                'log_enabled': 'True',
                'empty_line_placeholder': '******'
            }
            self.config['openai'] = {
                'api_key': 'openai_api_key',
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-4o',
                'temperature': '1.5',
                'max_tokens': '8192'
            }
            self.config['moonshot'] = {
                'api_key': 'moonshot_api_key',
                'base_url': 'https://api.moonshot.cn/v1',
                'model': 'moonshot-v1-auto',
                'temperature': '0.75',
                'max_tokens': '8192'
            }
            self.config['ollama'] = {
                'api_key': 'ollama_api_key',
                'base_url': 'http://0.0.0.0:4000',
                'model': 'ollama/gemma2:27b',
                'temperature': '1.5',
                'max_tokens': '8192'
            }
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            print(_("config-creation-completed").format(path=self.config_path))
            exit(1)

        self.config.read(self.config_path)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def getint(self, section, option, fallback=None):
        return self.config.getint(section, option, fallback=fallback)

    def getboolean(self, section, option, fallback=None):
        return self.config.getboolean(section, option, fallback=fallback)

    def getfloat(self, section, option, fallback=None):
        return self.config.getfloat(section, option, fallback=fallback)

    def get_config_path(self):
        return str(self.config_path)

def read_config(config_file='config.ini'):
    config_manager = ConfigManager()
    config_manager._initialize(config_file)
    config = config_manager.config

    current_ai = config_manager.get('settings', 'currentAI')
    api_key = config_manager.get(current_ai, 'api_key')
    base_url = config_manager.get(current_ai, 'base_url')
    model = config_manager.get(current_ai, 'model')
    temperature = config_manager.getfloat(current_ai, 'temperature')
    debug_mode = config_manager.getboolean('settings', 'debug_mode')
    batch_size = config_manager.getint('settings', 'batch_size')
    log_enabled = config_manager.getboolean('settings', 'log_enabled')
    empty_line_placeholder = config_manager.get('settings', 'empty_line_placeholder', '******')
    max_tokens = config_manager.getint(current_ai, 'max_tokens', fallback=8192)

    return api_key, base_url, model, temperature, debug_mode, batch_size, log_enabled, empty_line_placeholder, max_tokens
