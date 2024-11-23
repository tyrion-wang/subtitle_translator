import typer
from src.subtitle_translator.config import read_config
from src.subtitle_translator.srt_translator import translate_srt
from src.subtitle_translator.logger import enable_logging

app = typer.Typer()

@app.command()
def main(config_file: str = "config.ini"):
    api_key, base_url, model, temperature, input_file, debug_mode, batch_size, log_enabled, empty_line_placeholder = read_config(config_file)
    enable_logging(log_enabled)

    output_bilingual_file, output_target_lang_file = translate_srt(input_file, batch_size=batch_size, debug_mode=debug_mode, model=model, temperature=temperature)
    typer.echo(f"双语字幕翻译完成，输出文件：{output_bilingual_file}")
    typer.echo(f"单语字幕翻译完成，输出文件：{output_target_lang_file}")

if __name__ == "__main__":
    app()
