import openai
import srt
import time
import configparser
import os
from tqdm import tqdm

# 读取配置文件
def read_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    
    # 获取当前脚本所在的目录，并与配置文件名拼接出配置文件的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的路径
    config_path = os.path.join(script_dir, config_file)  # 拼接配置文件的路径

    config.read(config_path)  # 读取配置文件
    
    # 读取配置项
    api_key = config['openai']['api_key']
    input_file = config['srt']['input_file']
    output_file = config['srt']['output_file']
    debug_mode = config.getboolean('settings', 'debug_mode')  # 转换为布尔值
    
    return api_key, input_file, output_file, debug_mode

# 设置OpenAI API密钥
def setup_openai(api_key):
    openai.api_key = api_key

# 翻译函数
def translate_text(text, source_language='en', target_language='zh', debug_mode=False):
    if debug_mode:
        # 如果是调试模式，模拟API延迟并返回测试翻译结果
        time.sleep(0.1)  # 模拟延迟
        print(f"字幕内容log：{text}")
        return f"测试翻译：'{text}'"
    else:
        # 使用openai.ChatCompletion.create()进行翻译
        messages = [
            {"role": "system", "content": "You are a helpful assistant that translates text."},
            {"role": "user", "content": f"Translate the following text from {source_language} to {target_language}: {text}"}
        ]

        response = openai.ChatCompletion.create(  # 正确的API调用方式
            model="gpt-4",  # 使用聊天模型，例如 gpt-4
            messages=messages,
            max_tokens=1000,
            temperature=0.3
        )

        translated_text = response['choices'][0]['message']['content'].strip()
        return translated_text

# 读取SRT文件并进行翻译
def translate_srt(input_file, output_file, debug_mode=False):
    with open(input_file, 'r', encoding='utf-8') as f:
        srt_data = list(srt.parse(f.read()))  # 转为列表，方便后续处理
    
    total_lines = len(srt_data)  # 总行数
    translated_subtitles = []
    
    # 使用tqdm来显示进度条
    for idx, subtitle in enumerate(tqdm(srt_data, desc="翻译进度", total=total_lines, unit="行")):
        original_text = subtitle.content
        translated_text = translate_text(original_text, debug_mode=debug_mode)
        
        # 生成双语字幕
        bilingual_text = f"{original_text}\n{translated_text}"
        
        # 创建新的字幕项
        translated_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end, content=bilingual_text)
        translated_subtitles.append(translated_subtitle)
    
    # 写入新的SRT文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_subtitles))

# 主函数
if __name__ == "__main__":
    # 读取配置文件
    api_key, input_srt_file, output_srt_file, debug_mode = read_config('config.ini')
    
    # 设置OpenAI API密钥
    setup_openai(api_key)
    
    # 调用函数进行字幕翻译
    translate_srt(input_srt_file, output_srt_file, debug_mode=debug_mode)
    print(f"字幕翻译完成，输出文件：{output_srt_file}")
