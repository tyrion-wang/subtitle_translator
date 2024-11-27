#!/bin/bash
# 脚本用于编译翻译文件 .po 到 .mo
for lang in en zh; do
    msgfmt locale/$lang/LC_MESSAGES/messages.po -o locale/$lang/LC_MESSAGES/messages.mo
done
echo "Translation files compiled successfully."