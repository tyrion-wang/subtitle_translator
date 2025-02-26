import srt
from .logger import log
from .openai_client import call_openai_chat_completion
from .config import ConfigManager
import time
import os
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .location_utils.location import _

warning_logs = []  # 存储警告信息
empty_line_placeholder = "******"  # 默认替换空行的占位符
current_ai = ConfigManager().get('settings', 'currentAI')  # 定义 current_ai 变量

# 保存警告日志到文件
def save_warnings(input_file):
    if warning_logs:
        warning_file = os.path.splitext(input_file)[0] + f"翻译错误警告_{current_ai}.txt"
        with open(warning_file, 'w', encoding='utf-8') as f:
            for warning in warning_logs:
                f.write(warning + "\n=================================\n")

def display_warning(texts, translated_texts):
    """
    用于显示翻译警告信息的函数。
    """
    console = Console()

    # 构造逐行显示的文本内容
    details = "\n".join(
        f"原始文本: {original}\n翻译结果: {translated if translated.strip() else '（空白翻译）'}"
        for original, translated in zip(texts, translated_texts)
    )

    # 创建警告框
    warning_message = "翻译后的行数与原始行数不匹配或翻译结果为空，可能存在错误。"
    panel = Panel.fit(
        f"[yellow bold]Warning:[/yellow bold] {warning_message}\n\n{details}",
        title="Warning",
        title_align="left",
        border_style="red",
    )

    # 输出警告
    console.print(panel)

# 翻译函数
def translate_text_batch(texts, source_language='en', target_language='zh', debug_mode=False, model='gpt-4o', temperature=0.3, max_tokens=8192):
    if debug_mode:
        # 如果是调试模式，模拟API延迟并返回测试翻译结果
        time.sleep(0.5)  # 模拟延迟
        # console = Console()
        # console.print("123123")
        # print("123123123")
        display_warning(texts,texts)
        return [f"测试翻译：'{text}'" for text in texts]
    else:
        # 使用新的OpenAI接口进行翻译
        combined_text = '<< UNIQUE_SEPARATOR >>'.join(texts)  # 将多行文本合并为一个字符串，使用特殊分割符

        if '<< UNIQUE_SEPARATOR >>' in combined_text:
            messages = [
                {"role": "system",
                 "content": "You are a highly precise and detail-oriented translation assistant specializing in subtitle translation. The '<< UNIQUE_SEPARATOR >>' markers are vital for separating different segments of the text, and it is absolutely critical that these markers are preserved exactly as they appear in the original."
                            "Follow these specific instructions strictly:"
                                "1. **Never modify or omit** any '<< UNIQUE_SEPARATOR >>' markers. The translated output **must have the exact same number of '<< UNIQUE_SEPARATOR >>' markers** as the original text."
                                "2. **Translate each segment independently**, ensuring that each part retains the context, and align the corresponding translated segments to the original."
                                "3. Never respond with anything unrelated to the translation text or instructions; only reply with the translated content."
                                "4. Ensure **each part is well-connected in meaning**, but always strictly respect the separation defined by '<< UNIQUE_SEPARATOR >>'."
                                "5. If reordering of content is necessary to ensure natural phrasing in the target language, make sure to re-order each segment accordingly while keeping the separator positions consistent."
                                "6. **Avoid splitting any phrases across segments**—each separated segment must remain independent and semantically intact."
                                "7. Do not add any extra '<< UNIQUE_SEPARATOR >>' markers at the end of the translated text, and make sure not to skip or lose any '<< UNIQUE_SEPARATOR >>' marker."
                                "Your output should aim for the most natural translation possible, while strictly adhering to these guidelines."
                            "For example:"
                                "Original text: Yeah, it is fascinating how quickly<< UNIQUE_SEPARATOR >>these narratives are forming,<< UNIQUE_SEPARATOR >>even though we're still so early in the process."
                                "Incorrect translation: 这是译文这是译文<< UNIQUE_SEPARATOR >>这是译文这是译文。<< UNIQUE_SEPARATOR >>"
                                "Correct translation: 这是译文这是译文<< UNIQUE_SEPARATOR >>这是译文这是译文<< UNIQUE_SEPARATOR >>这是译文这是译文。"
                            # "翻译要求："
                            #     "1. 省略无关词汇：字幕中包含一些插入语、语气词等不需要翻译的内容（例如：you know, like, well等），这些应当省略，不影响整体对话流畅性。"
                            #     "2. 俚语与隐喻：注意原文中的俚语、隐喻等表达。对于这些表达，避免直接逐字翻译，应根据上下文语境进行意译，必要时可以使用与中文文化相符的常见俚语或比喻替代。"
                            #     "3. 口语化、自然化：翻译应尽量避免机械、僵硬的语言，考虑对话的语境，使其更加口语化、自然，符合中文观众的理解习惯。例如，若对话较为亲切或轻松，应避免过于正式或生硬的翻译。"
                            #     "4. 角色性格与语境：根据对话的语境和角色个性，灵活调整翻译风格。例如，年轻角色的对话可以更具活力和随意性，年长角色则可以使用较正式、稳重的语言。"
                            "Translation Requirements:"
                                "1. Omit Irrelevant Words: Subtitles may contain filler words, interjections, or expressions (such as 'you know', 'like', 'well', etc.) that do not need translation. These should be omitted to maintain the overall flow of the dialogue."
                                "2. Slang and Metaphors: Pay attention to slang, metaphors, and other idiomatic expressions in the original text. Instead of translating them literally, please paraphrase based on the context. If necessary, use common Chinese slang or metaphors that match the cultural context."
                                "3. Conversational and Natural: The translation should avoid mechanical, stiff language. Consider the context of the conversation to make the dialogue more colloquial and natural, in line with how Chinese audiences would understand it. For example, if the dialogue is casual or friendly, avoid overly formal or rigid translations."
                                "4. Character Personality and Context: Adjust the translation style based on the context of the conversation and the character's personality. For instance, dialogue from younger characters can be more energetic and casual, while older characters may use a more formal, composed language style."
                            ""},
                {"role": "user",
                 "content": f"Translate the following text from {source_language} to {target_language}: {combined_text}"}
            ]
        else:
            messages = [
                {"role": "system",
                 "content": "You are a highly precise and detail-oriented translation assistant specializing in subtitle translation."
                            "Never respond with anything unrelated to the translation text or instructions; only reply with the translated content."
                            "Your output should aim for the most natural translation possible, while strictly adhering to these guidelines."
                            ""},
                {"role": "user",
                 "content": f"Translate the following text from {source_language} to {target_language}: {combined_text}"}
            ]

        translated_combined_text = call_openai_chat_completion(messages, model=model, temperature=temperature, max_tokens=max_tokens)
        translated_texts = translated_combined_text.split('<< UNIQUE_SEPARATOR >>')

        # 检查翻译后的行数是否与原始行数一致，或者翻译结果是否为空字符串
        if len(translated_texts) != len(texts) or any(not text.strip() for text in translated_texts):
            warning_message = f"==================Warning=================\n翻译后的行数与原始行数不匹配或翻译结果为空，可能存在错误。\n原始文本：{texts}\n翻译结果：{translated_texts}"
            warning_logs.append(warning_message)
            log(warning_message)
        return translated_texts


def translate_srt(input_file, source_language='en', target_language='zh', batch_size=5, debug_mode=False, model='gpt-4o', temperature=0.3, max_tokens=8192):
    with open(input_file, 'r', encoding='utf-8') as f:
        srt_data = list(srt.parse(f.read()))  # 转为列表，方便后续处理

    total_lines = len(srt_data)  # 总行数
    translated_subtitles = []
    translated_texts_only = []

    i = 0
    # 使用tqdm来显示进度条
    with Progress() as progress:
        task = progress.add_task(_("translation-progress-0").format(total=total_lines), total=total_lines)

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
            translated_texts = translate_text_batch(original_texts, source_language=source_language,
                                                    target_language=target_language, debug_mode=debug_mode, model=model,
                                                    temperature=temperature, max_tokens=max_tokens)

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
                translated_texts_only_subtitle = srt.Subtitle(index=subtitle.index, start=subtitle.start,
                                                              end=subtitle.end,
                                                              content=translated_text)
                translated_texts_only.append(translated_texts_only_subtitle)

            progress.update(task, advance=len(current_batch), description=_("translation-progress-current").format(current=i,total=total_lines))

    # 生成输出文件名
    output_bilingual_file = os.path.splitext(input_file)[
                                0] + f"_combined_{source_language}_{target_language}_{current_ai}.srt"
    output_target_lang_file = os.path.splitext(input_file)[0] + f"_{target_language}_{current_ai}.srt"

    # 写入新的双语SRT文件
    with open(output_bilingual_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_subtitles))

    # 写入新的单语SRT文件（目标语言）
    with open(output_target_lang_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(translated_texts_only))

    # 保存警告日志
    save_warnings(input_file)

    return output_bilingual_file, output_target_lang_file
