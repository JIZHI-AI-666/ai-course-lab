#!/bin/zsh
cd "$(dirname "$0")/.." || exit 1
if [[ -x .venv/bin/python ]]; then
    demo_python=.venv/bin/python
elif [[ -x ../w7-venv/bin/python ]]; then
    demo_python=../w7-venv/bin/python
else
    echo '未找到运行环境，请先按 week07_RAG/README.md 安装依赖。'
    read -r '?按回车退出'
    exit 1
fi
"$demo_python" week07_RAG/demo.py
