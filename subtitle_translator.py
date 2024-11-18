import openai
import srt
import time
import configparser
import os
from tqdm import tqdm
from openai import OpenAI

# 全局变量，用于控制日志打印
log_enabled = False

# 读取配置文件
def read_config(config_file='config.ini'):
    global log_enabled
    config = configparser.ConfigParser()

    # 获取当前脚本所在的目录，并与配置文件名拼接出配置文件的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的路径
    config_path = os.path.join(script_dir, config_file)  # 拼接配置文件的路径

    # 如果配置文件不存在，创建默认配置文件
    if not os.path.exists(config_path):
        config['openai'] = {'api_key': 'YOUR_OPENAI_API_KEY', 'model': 'gpt-4o', 'temperature': '0.3'}
        config['srt'] = {'input_file': 'input_file.srt'}
        config['settings'] = {'debug_mode': 'True', 'batch_size': '5', 'log_enabled': 'True'}
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"配置文件{config_file}已创建，请填写必要的配置信息后重新运行程序。")
        exit(1)

    config.read(config_path)  # 读取配置文件

    # 读取配置项
    api_key = config['openai']['api_key']
    model = config['openai']['model']
    temperature = config.getfloat('openai', 'temperature')
    input_file = config['srt']['input_file']
    debug_mode = config.getboolean('settings', 'debug_mode')  # 转换为布尔值
    batch_size = config.getint('settings', 'batch_size')  # 读取批次大小
    log_enabled = config.getboolean('settings', 'log_enabled')  # 读取日志开关

    return api_key, model, temperature, input_file, debug_mode, batch_size

# 设置OpenAI API密钥
def setup_openai(api_key):
    os.environ['OPENAI_API_KEY'] = api_key

# 日志打印函数
def log(log_text, log_value=None):
    if log_enabled:
        if log_value is not None:
            print(f"{log_text}{log_value}")
        else:
            print(f"{log_text}")

# 通用的调用OpenAI翻译接口函数
def call_openai_chat_completion(client, messages, model, max_tokens=8192, temperature=0.3, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            retry_count += 1
            log("请求超时或API错误，正在进行第", retry_count)
    raise ValueError("请求重试多次后仍然失败，可能存在错误。")

# 翻译函数
def translate_text_batch(texts, source_language='en', target_language='zh', debug_mode=False, model='gpt-4o', temperature=0.3, max_retries=3):
    if debug_mode:
        # 如果是调试模式，模拟API延迟并返回测试翻译结果
        time.sleep(0.01)  # 模拟延迟
        return [f"测试翻译：'{text}'" for text in texts]
    else:
        # 使用新的OpenAI接口进行翻译
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        combined_text = '<<UNIQUE_SEPARATOR>>'.join(texts)  # 将多行文本合并为一个字符串，使用特殊分隔符
        messages = [
            {"role": "user",
             "content": f"Translate the following text from {source_language} to {target_language} in a natural and conversational tone suitable for subtitles. Ensure the translation preserves the emotional tone of the original and is easy to understand for a general audience. The '<<UNIQUE_SEPARATOR>>' characters are critical markers for separating different parts of the text. Do not translate, remove, or modify these '<<UNIQUE_SEPARATOR>>' characters, as they are used to ensure the integrity of the text structure.: {combined_text}"}
        ]

        translated_combined_text = call_openai_chat_completion(client, messages, model=model, temperature=temperature, max_retries=max_retries)
        translated_texts = translated_combined_text.split('<<UNIQUE_SEPARATOR>>')

        # 检查翻译后的行数是否与原始行数一致
        if len(translated_texts) != len(texts):
            raise ValueError("翻译后的行数与原始行数不匹配，可能存在错误。")
        return translated_texts

# 读取SRT文件并进行翻译
def translate_srt(input_file, source_language='en', target_language='zh', batch_size=5, debug_mode=False, model='gpt-4o', temperature=0.3):
    with open(input_file, 'r', encoding='utf-8') as f:
        srt_data = list(srt.parse(f.read()))  # 转为列表，方便后续处理

    total_lines = len(srt_data)  # 总行数
    translated_subtitles = []
    translated_texts_only = []

    # 使用tqdm来显示进度条
    for i in tqdm(range(0, total_lines, batch_size), desc="翻译进度", total=(total_lines + batch_size - 1) // batch_size, unit="批"):
        batch = srt_data[i:i + batch_size]  # 取出当前批次的字幕
        original_texts = [subtitle.content for subtitle in batch]
        translated_texts = translate_text_batch(original_texts, source_language=source_language, target_language=target_language, debug_mode=debug_mode, model=model, temperature=temperature)

        # 创建新的字幕项，生成双语字幕
        for subtitle, translated_text in zip(batch, translated_texts):
            bilingual_text = f"{subtitle.content}\n{translated_text}"
            translated_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end,
                                               content=bilingual_text)
            translated_subtitles.append(translated_subtitle)

            # 生成单语字幕内容
            translated_texts_only_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end,
                                                          content=translated_text)
            translated_texts_only.append(translated_texts_only_subtitle)

    # 生成输出文件名
    output_bilingual_file = os.path.splitext(input_file)[0] + f"_combined_{source_language}_{target_language}.srt"
    output_target_lang_file = os.path.splitext(input_file)[0] + f"_{target_language}.srt"

    # 写入新的双语SRT文件
    with open(output_bilingual_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_subtitles))

    # 写入新的单语SRT文件（目标语言）
    with open(output_target_lang_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_texts_only))

    return output_bilingual_file, output_target_lang_file

# 主函数
if __name__ == "__main__":
    # 读取配置文件
    api_key, model, temperature, input_srt_file, debug_mode, batch_size = read_config('config.ini')

    # 设置OpenAI API密钥
    setup_openai(api_key)

    # 调用函数进行字幕翻译
    output_bilingual_file, output_target_lang_file = translate_srt(input_srt_file, batch_size=batch_size, debug_mode=debug_mode, model=model, temperature=temperature)
    log("双语字幕翻译完成，输出文件：", output_bilingual_file)
    log("单语字幕翻译完成，输出文件：", output_target_lang_file)
