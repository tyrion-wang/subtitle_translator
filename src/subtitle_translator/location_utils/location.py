import gettext
import locale
from .config import LOCALE_DIR, DEFAULT_LANGUAGE

class Location:
    _instance = None  # 单例实例

    def __new__(cls, *args, **kwargs):
        """
        单例模式：确保只有一个实例
        """
        if cls._instance is None:
            cls._instance = super(Location, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, domain="default"):
        """
        初始化本地化模块
        :param domain: 翻译文件的域名（默认 "default"）
        """
        if not self._initialized:  # 确保只初始化一次
            self.domain = domain
            self.language = DEFAULT_LANGUAGE
            self.translation = None
            self.load_translation()
            self._initialized = True

    def detect_system_language(self):
        """
        检测系统语言，返回语言代码。
        """
        system_locale = locale.getlocale()
        if system_locale and system_locale[0]:
            if system_locale[0].startswith("zh"):
                return "zh"
        return "en"

    def load_translation(self):
        """
        加载当前语言的翻译
        """
        try:
            self.translation = gettext.translation(
                domain=self.domain, localedir=LOCALE_DIR, languages=[self.language]
            )
            self.translation.install()
        except FileNotFoundError:
            gettext.install(self.domain)  # 使用默认翻译

    def set_language(self, language):
        """
        设置语言并重新加载翻译
        :param language: 语言代码（如 "zh" 或 "en"）
        """
        self.language = language
        self.load_translation()

    def get_text(self, message):
        """
        翻译消息
        :param message: 原始字符串
        :return: 翻译后的字符串
        """
        return self.translation.gettext(message) if self.translation else message

localizer = Location()
detect_system_language = localizer.detect_system_language
load_translation = localizer.load_translation
set_language = localizer.set_language
_ = localizer.get_text
# globals()['detect_system_language'] = localizer.detect_system_language
# globals()['load_translation'] = localizer.load_translation
# globals()['set_language'] = localizer.set_language
# globals()['get_text'] = localizer.get_text


