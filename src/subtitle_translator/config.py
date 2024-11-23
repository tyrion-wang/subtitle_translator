import configparser
import os

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize()
        return cls._instance

    def initialize(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()

        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, config_file)

        # 如果配置文件不存在，创建默认配置文件
        if not os.path.exists(self.config_path):
            self.config['settings'] = {
                'currentAI': 'openai',
                'debug_mode': 'False',
                'batch_size': '3',
                'log_enabled': 'True',
                'empty_line_placeholder': '******'
            }
            self.config['srt'] = {'input_file': 'your_subtitle_file.srt'}
            self.config['openai'] = {
                'api_key': 'openai_api_key',
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-4o',
                'temperature': '1.5'
            }
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            print(f"配置文件 {config_file} 已创建，请填写必要的配置信息后重新运行程序。")
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

def read_config(config_file='config.ini'):
    config_manager = ConfigManager()
    config_manager.initialize(config_file)
    config = config_manager.config

    current_ai = config['settings']['currentAI']
    api_key = config[current_ai]['api_key']
    base_url = config[current_ai]['base_url']
    model = config[current_ai]['model']
    temperature = config_manager.getfloat(current_ai, 'temperature')
    input_file = config['srt']['input_file']
    debug_mode = config_manager.getboolean('settings', 'debug_mode')
    batch_size = config_manager.getint('settings', 'batch_size')
    log_enabled = config_manager.getboolean('settings', 'log_enabled')
    empty_line_placeholder = config['settings'].get('empty_line_placeholder', '******')

    return api_key, base_url, model, temperature, input_file, debug_mode, batch_size, log_enabled, empty_line_placeholder
