import typer
import os
from .config import read_config, ConfigManager
from .srt_translator import translate_srt
from .logger import enable_logging
# from .location_utils.location import Location
from .location_utils.location import _

app = typer.Typer()

@app.command()
def main(
    input_file: str = typer.Argument(None, help=_("input-file-path")),  # 将输入文件设为可选
    config_file: str = typer.Option("config.ini", help=_("config-patch")),  # 可选参数，带默认值
    target_language: str = typer.Option("zh", help=_("config-default-is-zh")),  # 新增参数，默认为中文
    show_config: bool = typer.Option(False, "--config-path", help=_("show-config-file-path"))  # 新增参数，用于显示配置文件路径
):
    if show_config:
        config_manager = ConfigManager()
        config_manager._initialize(config_file)  # 初始化配置管理器
        full_config_path = config_manager.get_config_path()  # 获取配置文件路径
        typer.echo(full_config_path)  # 输出完整路径
        return

    if not input_file:
        typer.echo(_("missing-input-file"))
        return

    # 从配置文件读取配置项
    api_key, base_url, model, temperature, debug_mode, batch_size, log_enabled, empty_line_placeholder, max_tokens = read_config(config_file)
    enable_logging(log_enabled)

    # 翻译字幕，传入 target_language 参数
    output_bilingual_file, output_target_lang_file = translate_srt(
        input_file,
        batch_size=batch_size,
        debug_mode=debug_mode,
        model=model,
        temperature=temperature,
        target_language=target_language,
        max_tokens=max_tokens  # 传入 max_tokens
    )
    typer.echo(_("output-bilingual-sub").format(file=output_bilingual_file))
    typer.echo(_("output-single-sub").format(file=output_bilingual_file))

if __name__ == "__main__":
    app()
