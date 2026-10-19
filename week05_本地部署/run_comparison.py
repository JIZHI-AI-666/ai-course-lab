"""真实调用本地 Ollama 或 DeepSeek；不记录密钥。仅使用 Python 标准库。"""
import argparse
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone
import urllib.request

ROOT = Path(__file__).resolve().parent

def request(url, payload=None, key=None, local=False):
    headers = {'Content-Type': 'application/json'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request(url, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if local else urllib.request.build_opener()
    with opener.open(req, timeout=180) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['local', 'cloud'], required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.env_file:
        for line in args.env_file.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1)
                os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
    local = args.backend == 'local'
    key = None if local else os.environ.get('DEEPSEEK_API_KEY')
    if not local and (not key or key.startswith('your_')):
        raise SystemExit('缺少有效 DEEPSEEK_API_KEY；未执行云端调用。')
    base = 'http://127.0.0.1:11434' if local else os.environ.get('DEEPSEEK_BASE_URL','https://api.deepseek.com/v1').rstrip('/')
    questions = json.loads((ROOT/'questions.json').read_text())
    path = ROOT/'results'/(args.backend+'_'+args.model.replace(':','_')+'.json')
    if path.exists():
        raise SystemExit(f'结果已存在，请先归档再重跑：{path.name}')
    result = {'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'model':args.model,'backend':args.backend,'temperature':0.2,'max_output_tokens':600,'questions':[]}
    if local:
        # 逐个卸载，确保测得当前模型的冷加载；不同时常驻两个量级。
        for model in request(base+'/api/ps',local=True)['models']:
            request(base+'/api/generate',{'model':model['name'],'keep_alive':0},local=True)
        result['model_info']=request(base+'/api/show',{'model':args.model},local=True).get('details',{})
    for q in questions:
        payload={'model':args.model,'messages':[{'role':'user','content':q['prompt']}],'stream':False}
        if local:
            payload.update(options={'temperature':0.2,'num_predict':600,'num_ctx':4096,'seed':42},keep_alive='10m')
        else:
            payload.update(temperature=0.2,max_tokens=600)
        start=time.perf_counter()
        response=request(base+('/api/chat' if local else '/chat/completions'),payload,key,local)
        elapsed=time.perf_counter()-start
        row={**q,'elapsed_seconds':round(elapsed,4),'answer':response['message']['content'] if local else response['choices'][0]['message']['content'],'finish_reason':response.get('done_reason') if local else response['choices'][0].get('finish_reason')}
        if local:
            row['metrics']={k:response.get(k) for k in ['total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration']}
            row['running_models']=request(base+'/api/ps',local=True)['models']
        else:
            row['usage']=response.get('usage',{})
        result['questions'].append(row)
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(args.model,q['id'],f'{elapsed:.2f}s',row['finish_reason'],flush=True)
    if local:
        request(base+'/api/generate',{'model':args.model,'keep_alive':0},local=True)

if __name__=='__main__':
    main()
