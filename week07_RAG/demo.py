"""课堂演示：选择问题，真实检索和生成，使用简洁终端视图。"""
import getpass
import os
import subprocess
import sys
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import rag_qa as rag

QUESTIONS = [
    '根据GF 0025—2021，四级累计词汇量是多少？',
    '根据GF 0025—2021，高等阶段七至九级的量化指标是否按每级分别统计？',
    '根据本次等级标准节选，2026年上海HSK四级考试的报名费是多少元？',
]


def prepare():
    session=requests.Session();session.trust_env=False
    base=os.getenv('LOCAL_BASE_URL','http://127.0.0.1:11434').rstrip('/')
    for attempt in range(12):
        try:
            response=session.get(base+'/api/tags',timeout=2)
            response.raise_for_status()
            names={m['name'] for m in response.json()['models']}
            break
        except requests.RequestException:
            if attempt==0 and sys.platform=='darwin' and base=='http://127.0.0.1:11434':
                subprocess.run(['open','-a','Ollama'],check=False,capture_output=True)
            time.sleep(1)
    else:
        raise RuntimeError('Ollama未就绪，请打开Ollama后重试。')
    if not os.getenv('EMBED_MODEL'):
        rag.EMBED_MODEL='nomic-embed-text:w7-f16' if 'nomic-embed-text:w7-f16' in names else 'nomic-embed-text'
    if not any(n==rag.EMBED_MODEL or n==rag.EMBED_MODEL+':latest' for n in names):
        raise RuntimeError('缺少嵌入模型，请先按README安装 '+rag.EMBED_MODEL)
    key=os.getenv('DEEPSEEK_API_KEY','').strip()
    if not key or key=='your_deepseek_key_here':
        key=getpass.getpass('请输入DeepSeek密钥（不显示、不保存）：').strip()
        if not key:
            raise RuntimeError('未输入密钥，无法进行默认云端演示。')
        os.environ['DEEPSEEK_API_KEY']=key


def main():
    console=Console()
    console.print(Panel(Text('华文小助手\n依据资料回答 · 展示出处 · 检查资料边界'),border_style='cyan'))
    try:
        prepare()
    except Exception as error:
        console.print(Text(str(error),style='yellow'));return 1
    while True:
        console.print(Text('1  查词汇量    2  查统计规则    3  资料外问题\n直接输入自己的问题也可以；输入 q 退出。',style='cyan'))
        choice=input('请选择（回车选1）：').strip()
        if choice.lower()=='q':return 0
        question=QUESTIONS[int(choice or '1')-1] if (choice or '1') in ('1','2','3') else choice
        try:
            with console.status('正在检索资料并生成回答…',spinner='dots'):
                result=rag.rag_qa_details(question,prefer='api')
            rag.display_result(result,console)
        except Exception as error:
            # 不把模型请求、配置或可能包含凭据的完整堆栈投到屏幕上。
            console.print(Text(f'本次运行未完成（{type(error).__name__}）。请检查网络、模型与密钥后重试。',style='yellow'))


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt,EOFError):
        print('\n演示已结束。')
