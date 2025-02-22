# SubtransAI - AI驱动的字幕翻译工具

SubtransAI 是一个基于AI的字幕翻译工具，支持将SRT格式字幕文件从一种语言翻译成另一种语言，并可生成双语或单语字幕文件。

## 特性

- 🚀 支持多个AI服务提供商 (OpenAI/Moonshot/Ollama)
- 🌍 支持多语言界面 (中文/英文)
- 📝 支持生成双语字幕和单语字幕
- ⚡ 批量翻译提高效率
- 📊 实时显示翻译进度
- ⚙️ 灵活的配置选项

## 安装
```bash
pip install subtransAI
```

## 快速开始

1. 首次运行会在用户目录下创建配置文件:
```bash
~/.config/subtitle_translator/config.ini
```

2. 编辑配置文件，设置AI服务参数:
```ini
[settings]
currentAI = openai  # 可选: Grok、Deepseek、Openai、Moonshot、Ollama 等基于OpenAI api的大模型接口

[openai]
api_key = your_api_key
base_url = https://api.openai.com/v1
model = gpt-4
temperature = 0.3
```

3. 运行翻译:
```bash
subtransAI input.srt
```

## 命令行参数

```bash
subtransAI [OPTIONS] [INPUT_FILE]

参数:
  INPUT_FILE               输入的SRT文件路径
  --config-file TEXT      配置文件路径 [默认: config.ini]
  --target-language TEXT  目标语言 [默认: zh]
  --config-path          显示配置文件路径
  --help                 显示帮助信息
```
## 配置文件说明

配置文件支持以下选项:

```ini
[settings]
currentAI = openai        # 当前使用的AI服务
debug_mode = False        # 调试模式
batch_size = 3           # 批量翻译大小
log_enabled = True       # 是否启用日志
empty_line_placeholder = ****** # 空行占位符

[openai/moonshot/ollama]
api_key = your_api_key   # API密钥
base_url = api_base_url  # API基础URL
model = model_name       # 使用的模型
temperature = 0.3        # 温度参数
```

## 输出文件

工具会生成两个文件:
- `{input_name}_combined_{source}_{target}_{ai}.srt`: 双语字幕
- `{input_name}_{target}_{ai}.srt`: 目标语言字幕

## 开发

1. 克隆仓库:
```bash
git clone https://github.com/tyrion-wang/subtitle_translator.git
``` 

2. 安装开发依赖:
```bash
pip install -e ".[dev]"
```

3. 生成翻译文件:
```bash
./generate_mo.sh
```

## 许可证

MIT License

## 作者

Tyrion (maple_leaf_7@msn.com)

## 问题反馈

如果您遇到任何问题或有建议，请在 [GitHub Issues](https://github.com/tyrion-wang/subtitle_translator/issues) 提出。


