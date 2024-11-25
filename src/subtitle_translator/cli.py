import typer
from .config import read_config
from .srt_translator import translate_srt
from .logger import enable_logging

app = typer.Typer()

@app.command()
def main(
    input_file: str,  # 必填参数：输入的字幕文件路径
    config_file: str = typer.Option("config.ini", help="配置文件路径")  # 可选参数，带默认值
):
    """
    翻译字幕文件

    :param input_file: 输入的 SRT 文件路径
    :param config_file: 配置文件路径
    """
    # 从配置文件读取配置项
    api_key, base_url, model, temperature, debug_mode, batch_size, log_enabled, empty_line_placeholder = read_config(config_file)
    enable_logging(log_enabled)

    # 翻译字幕
    output_bilingual_file, output_target_lang_file = translate_srt(input_file, batch_size=batch_size, debug_mode=debug_mode, model=model, temperature=temperature)
    typer.echo(f"双语字幕翻译完成，输出文件：{output_bilingual_file}")
    typer.echo(f"单语字幕翻译完成，输出文件：{output_target_lang_file}")

if __name__ == "__main__":
    app()
