"""代码包根目录、日志路径和 .env 加载入口。"""

import os


ROOT = os.path.dirname(os.path.abspath(__file__))


def root_path(*parts):
    return os.path.join(ROOT, *parts)


def load_env():
    env_file = root_path(".env")
    if not os.path.exists(env_file):
        return False
    try:
        from dotenv import load_dotenv
    except ImportError:
        # 只解析简单 KEY=VALUE，不执行 .env 中的任何命令。
        with open(env_file, encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        return True
    load_dotenv(env_file, override=False)
    return True
