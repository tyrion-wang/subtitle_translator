import openai
import srt
import time
import configparser
import os
from tqdm import tqdm
from openai import OpenAI

# 全局变量，用于控制日志打印
log_enabled = False
warning_logs = []  # 存储警告信息
empty_line_placeholder = "******"  # 默认替换空行的占位符

# 读取配置文件
def read_config(config_file='config.ini'):
    global log_enabled, empty_line_placeholder
    config = configparser.ConfigParser()

    # 获取当前脚本所在的目录，并与配置文件名拼接出配置文件的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的路径
    config_path = os.path.join(script_dir, config_file)  # 拼接配置文件的路径

    # 如果配置文件不存在，创建默认配置文件
    if not os.path.exists(config_path):
        config['openai'] = {'api_key': 'YOUR_OPENAI_API_KEY', 'model': 'gpt-4o', 'temperature': '0.3'}
        config['srt'] = {'input_file': 'input_file.srt'}
        config['settings'] = {'debug_mode': 'True', 'log_enabled': 'True', 'batch_size': '5', 'empty_line_placeholder': '******'}
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
    log_enabled = config.getboolean('settings', 'log_enabled')  # 读取日志开关
    batch_size = config.getint('settings', 'batch_size')  # 读取批次大小
    empty_line_placeholder = config['settings'].get('empty_line_placeholder', '******')  # 读取空行占位符

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

# 保存警告日志到文件
def save_warnings(input_file):
    if warning_logs:
        warning_file = os.path.splitext(input_file)[0] + "__翻译错误警告.txt"
        with open(warning_file, 'w', encoding='utf-8') as f:
            for warning in warning_logs:
                f.write(warning + "\n=================================\n")

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
        time.sleep(0.5)  # 模拟延迟
        return [f"测试翻译：'{text}'" for text in texts]
    else:
        # 使用新的OpenAI接口进行翻译
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        combined_text = '<<UNIQUE_SEPARATOR>>'.join(texts)  # 将多行文本合并为一个字符串，使用特殊分割符

        if '<<UNIQUE_SEPARATOR>>' in combined_text:
            messages = [
                {"role": "user",
                 "content": f"Translate the following text from {source_language} to {target_language} in a natural and conversational tone suitable for subtitles. The '<<UNIQUE_SEPARATOR>>' characters are critical markers for separating different parts of the text. Follow these specific guidelines: 1. Do not translate, remove, or modify the '<<UNIQUE_SEPARATOR>>' markers in any way.2. Ensure that the number of '<<UNIQUE_SEPARATOR>>' markers in the translated text matches exactly with the original text.3. Translate each segment independently, keeping the boundaries defined by the '<<UNIQUE_SEPARATOR>>'.4. Do not add any additional '<<UNIQUE_SEPARATOR>>' at the end of the translation.5. Add redundancy where appropriate to ensure that the translated text follows the same sequence as the original text, making sure each part aligns smoothly.The goal is for each translated segment to correspond directly with each original segment, preserving emotional tone and clarity for subtitle usage. Here is the text to translate: {combined_text}"}
            ]
        else:
            messages = [
                {"role": "user",
                 "content": f"Translate the following text from {source_language} to {target_language} in a natural and conversational tone suitable for subtitles. Ensure the translation preserves the emotional tone of the original and is easy to understand for a general audience.: {combined_text}"}
            ]

        translated_combined_text = call_openai_chat_completion(client, messages, model=model, temperature=temperature, max_retries=max_retries)
        translated_texts = translated_combined_text.split('<<UNIQUE_SEPARATOR>>')

        # 检查翻译后的行数是否与原始行数一致，或者翻译结果是否为空字符串
        if len(translated_texts) != len(texts) or any(not text.strip() for text in translated_texts):
            warning_message = f"警告：翻译后的行数与原始行数不匹配或翻译结果为空，可能存在错误。\n原始文本：{texts}\n翻译结果：{translated_texts}"
            warning_logs.append(warning_message)
            log(warning_message)
        return translated_texts

# 读取SRT文件并进行翻译
def translate_srt(input_file, source_language='en', target_language='zh', batch_size=5, debug_mode=False, model='gpt-4o', temperature=0.3):
    with open(input_file, 'r', encoding='utf-8') as f:
        srt_data = list(srt.parse(f.read()))  # 转为列表，方便后续处理

    total_lines = len(srt_data)  # 总行数
    translated_subtitles = []
    translated_texts_only = []

    i = 0
    # 使用tqdm来显示进度条
    with tqdm(total=total_lines, desc="翻译进度", unit="行") as pbar:
        while i < total_lines:
            current_batch = []
            current_length = 0

            # 默认按照batch_size决定一次性提交多少行字幕进行翻译
            while i < total_lines and current_length < batch_size:
                current_batch.append(srt_data[i])
                current_length += 1
                i += 1

            # 如果当前批次的最后一句不完整，继续添加直到完整
            while i < total_lines and not current_batch[-1].content.endswith(('.', '!', '?')):
                current_batch.append(srt_data[i])
                i += 1

            original_texts = [subtitle.content for subtitle in current_batch]
            translated_texts = translate_text_batch(original_texts, source_language=source_language, target_language=target_language, debug_mode=debug_mode, model=model, temperature=temperature)

            # 确保 translated_texts 的数量与 original_texts 一致
            if len(translated_texts) < len(original_texts):
                translated_texts.extend([empty_line_placeholder] * (len(original_texts) - len(translated_texts)))

            # 确保 translated_texts 中没有空字符串，将空字符串替换为占位符
            translated_texts = [text if text.strip() else empty_line_placeholder for text in translated_texts]

            # 创建新的字幕项，生成双语字幕
            for subtitle, translated_text in zip(current_batch, translated_texts):
                bilingual_text = f"{subtitle.content}\n{translated_text}"
                translated_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end,
                                                   content=bilingual_text)
                translated_subtitles.append(translated_subtitle)

                # 生成单语字幕内容
                translated_texts_only_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end,
                                                              content=translated_text)
                translated_texts_only.append(translated_texts_only_subtitle)

            pbar.update(len(current_batch))

    # 生成输出文件名
    output_bilingual_file = os.path.splitext(input_file)[0] + f"_combined_{source_language}_{target_language}.srt"
    output_target_lang_file = os.path.splitext(input_file)[0] + f"_{target_language}.srt"

    # 写入新的双语SRT文件
    with open(output_bilingual_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_subtitles))

    # 写入新的单语SRT文件（目标语言）
    with open(output_target_lang_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_texts_only))

    # 保存警告日志
    save_warnings(input_file)

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
