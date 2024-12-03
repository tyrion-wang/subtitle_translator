from .location_utils.location import detect_system_language, set_language
# 检测系统语言并设置
set_language(detect_system_language())
# set_language("en")
from .srt_translator import translate_srt
from .config import read_config
from .logger import log

__all__ = ["translate_srt", "read_config", "log"]
