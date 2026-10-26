"""用固定虚构作文真实比较四轮提示词。只发送通用教学素材，不打印密钥。"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
ESSAY = "昨天我去图书馆。我看书两小时了。我很高兴的。虽然下雨，所以我还是去了。"
PROMPTS = [
    ("R0", "请批改下面这篇完全虚构的中文短文，限300字。"),
    ("R1", "你是国际中文教师。批改下面的完全虚构短文。依次输出优点、问题、修改建议，限300字。"),
    ("R2", "你是国际中文教师。批改完全虚构的短文。依次输出优点、问题、修改建议。每个问题引用原句，标注错因，给出可替换句及原因；错因只选语序、搭配、关联词、时量、结构助词。不能确定的标待核对，不凑错误，不改写整篇，不增加人物经历。限400字。"),
    ("R3", "你是国际中文教师。批改完全虚构短文。仅输出：一、优点（引用原文一句）；二、问题表（原句|错因|改后|原因）；三、修改建议（一个可执行练习）。错因只选语序、搭配、关联词、时量、结构助词。不确定的写待核对。不凑错误，不整篇代写、不新增动机或经历。示例行：我学习汉语两小时了。|时量|我学了两个小时的汉语。|若表达已完成的一段活动，时量置于动词后并明确体意义；需结合语境。保留图书馆、两小时、开心、下雨仍去这四项信息。不要假设年级或水平，不给未经标定的分数。限450字。"),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'evidence'/'iteration_20261026.json')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('结果已存在；请指定新文件以保留历史记录。')
    for line in args.env_file.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#') and '=' in line:
            k,v=line.split('=',1)
            os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
    key=os.environ.get('DEEPSEEK_API_KEY')
    if not key or key.startswith('your_'):raise SystemExit('未配置有效密钥。')
    url=os.environ.get('DEEPSEEK_BASE_URL','https://api.deepseek.com/v1').rstrip('/')+'/chat/completions'
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'source':'2026-10-26 补交复测，不追溯为9月实验','essay':ESSAY,'rounds':[]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for name,prompt in PROMPTS:
        payload={'model':'deepseek-chat','messages':[{'role':'user','content':prompt+'\n短文：'+ESSAY}],'temperature':0.2,'max_tokens':750}
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
        start=time.perf_counter()
        try:
            with urllib.request.urlopen(req,timeout=90) as response:data=json.load(response)
        except Exception as e:
            raise SystemExit('请求失败：'+type(e).__name__+'；已成功轮次保留。') from None
        result['rounds'].append({'round':name,'request':payload,'elapsed_seconds':round(time.perf_counter()-start,3),'response':data})
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(name,'saved',data.get('usage',{}).get('total_tokens'),flush=True)

if __name__=='__main__':main()
