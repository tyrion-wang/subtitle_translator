import openai
import srt
import time
import configparser
import os
from tqdm import tqdm
from openai import OpenAI


# 读取配置文件
def read_config(config_file='config.ini'):
    config = configparser.ConfigParser()

    # 获取当前脚本所在的目录，并与配置文件名拼接出配置文件的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的路径
    config_path = os.path.join(script_dir, config_file)  # 拼接配置文件的路径

    # 如果配置文件不存在，创建默认配置文件
    if not os.path.exists(config_path):
        config['openai'] = {'api_key': 'YOUR_OPENAI_API_KEY'}
        config['srt'] = {'input_file': 'input_file.srt', 'output_file': 'output_file.srt'}
        config['settings'] = {'debug_mode': 'True', 'batch_size': '5'}
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"配置文件{config_file}已创建，请填写必要的配置信息后重新运行程序。")
        exit(1)

    config.read(config_path)  # 读取配置文件

    # 读取配置项
    api_key = config['openai']['api_key']
    input_file = config['srt']['input_file']
    output_file = config['srt']['output_file']
    debug_mode = config.getboolean('settings', 'debug_mode')  # 转换为布尔值
    batch_size = config.getint('settings', 'batch_size')  # 读取批次大小

    return api_key, input_file, output_file, debug_mode, batch_size


# 设置OpenAI API密钥
def setup_openai(api_key):
    os.environ['OPENAI_API_KEY'] = api_key


# 翻译函数
def translate_text_batch(texts, source_language='en', target_language='zh', debug_mode=False):
    if debug_mode:
        # 如果是调试模式，模拟API延迟并返回测试翻译结果
        time.sleep(0.1)  # 模拟延迟
        # print(f"字幕内容log：{texts}")
        return [f"测试翻译：'{text}'" for text in texts]
    else:
        # 使用新的OpenAI接口进行翻译
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        combined_text = '\n'.join(texts)  # 将多行文本合并为一个字符串
        messages = [
            {"role": "user",
             "content": f"Translate the following text from {source_language} to {target_language}: {combined_text}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2000,
            temperature=0
        )
        translated_combined_text = response.choices[0].message.content.strip()
        translated_texts = translated_combined_text.split('\n')  # 按行拆分翻译结果
        return translated_texts


# 读取SRT文件并进行翻译
def translate_srt(input_file, output_file, batch_size=5, debug_mode=False):
    with open(input_file, 'r', encoding='utf-8') as f:
        srt_data = list(srt.parse(f.read()))  # 转为列表，方便后续处理

    total_lines = len(srt_data)  # 总行数
    translated_subtitles = []

    # 使用tqdm来显示进度条
    for i in tqdm(range(0, total_lines, batch_size), desc="翻译进度", total=(total_lines // batch_size) + 1, unit="批"):
        batch = srt_data[i:i + batch_size]  # 取出当前批次的字幕
        original_texts = [subtitle.content for subtitle in batch]
        translated_texts = translate_text_batch(original_texts, debug_mode=debug_mode)

        # 创建新的字幕项，生成双语字幕
        for subtitle, translated_text in zip(batch, translated_texts):
            bilingual_text = f"{subtitle.content}\n{translated_text}"
            translated_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start, end=subtitle.end,
                                               content=bilingual_text)
            translated_subtitles.append(translated_subtitle)

    # 写入新的SRT文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_subtitles))


# 主函数
if __name__ == "__main__":
    # 读取配置文件
    api_key, input_srt_file, output_srt_file, debug_mode, batch_size = read_config('config.ini')

    # 设置OpenAI API密钥
    setup_openai(api_key)

    # 调用函数进行字幕翻译
    translate_srt(input_srt_file, output_srt_file, batch_size=batch_size, debug_mode=debug_mode)
    print(f"字幕翻译完成，输出文件：{output_srt_file}")
