"""无网络检查前六周交付文件、链接、日志与实验结构；不能替代教师评分。"""
import csv
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'submission_manifest.json').read_text(encoding='utf-8'))
    errors=[]
    checks=0
    def check(condition,message):
        nonlocal checks
        checks+=1
        if not condition:errors.append(message)

    for name in manifest['required_files']:
        p=ROOT/name
        check(p.is_file() and p.stat().st_size>0,'缺少或空文件：'+name)
        if not p.is_file():continue
        content=p.read_text(encoding='utf-8')
        check(not re.search(r'sk-[A-Za-z0-9_-]{16,}|Bearer\s+[A-Za-z0-9_-]{24,}',content),'疑似密钥：'+name)
        if p.suffix=='.md':
            # 仅检查正文中的标准 Markdown 链接，跳过代码块和外部链接。
            prose=re.sub(r'```.*?```','',content,flags=re.S)
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)',prose):
                if re.match(r'^[a-zA-Z]+:',target) or target.startswith('#'):continue
                target=unquote(target.split('#')[0])
                check((p.parent/target).exists(),f'失效链接：{name} -> {target}')
    for left,right in manifest['identical_copies']:
        check((ROOT/left).read_bytes()==(ROOT/right).read_bytes(),f'副本不一致：{left} / {right}')

    prompts=['出题','教案扩展','生词筛查','作文批改','课堂活动','语法讲练','留学课业诊断']
    for name in prompts:
        s=(ROOT/'prompt-library'/f'{name}.md').read_text(encoding='utf-8')
        check(all(t in s for t in ['【角色】','【任务】','【要求】','【示例】','适用说明','最佳示例']),f'提示词结构不全：{name}')
    iterations=json.loads((ROOT/'prompt-library/evidence/iteration_20261026.json').read_text(encoding='utf-8'))['rounds']
    check([r['round'] for r in iterations]==['R0','R1','R2','R3'],'迭代轮次不足')
    for row in iterations:
        check(bool(row['request']['messages'][0]['content']) and bool(row['response']['choices'][0]['message']['content']),'缺少迭代原始输入输出')
        check(row['response']['choices'][0]['finish_reason']=='stop','迭代回答被截断')

    with (ROOT/'data/生词表.csv').open(encoding='utf-8-sig',newline='') as f:words=list(csv.DictReader(f))
    selected=[w['词汇'] for w in words if w['HSK等级']=='4']
    check(len(words)==13 and len(selected)==4,'词表计数变化，请复核记录')
    exercise=(ROOT/'练习.txt').read_text(encoding='utf-8')
    check(all(w in exercise for w in selected),'练习未覆盖全部目标词')
    record=(ROOT/'AI辅助编程实录.md').read_text(encoding='utf-8')
    check(all(t in record for t in ['## 1.','## 2.','## 3.','## 4.','```python','原因']),'编程实录四段不全')
    log=(ROOT/'chat_log.txt').read_text(encoding='utf-8')
    check(all(f'三题批量 {n}' in log for n in [1,2,3]),'缺少三题问答日志')
    check(log.count('\nQ: ')>=3 and log.count('\nA: ')>=3,'问答正文不全')
    for params in ['temperature=0.0','temperature=1.5','max_tokens=15','max_tokens=800']:
        check(params in log,'缺少参数实验：'+params)
    counts=[tuple(map(int,m)) for m in re.findall(r'prompt=(\d+), completion=(\d+), total=(\d+)',log)]
    check(len(counts)==9 and all(a+b==c for a,b,c in counts),'日志用量不一致')

    w5=ROOT/'week05_本地部署'
    questions=json.loads((w5/'questions.json').read_text(encoding='utf-8'))
    expected={q['id']:q['prompt'] for q in questions}
    check(len(expected)>=5,'W5不足五题')
    for file in ['local_qwen2.5_0.5b.json','local_qwen2.5_1.5b.json','cloud_deepseek-chat.json']:
        data=json.loads((w5/'results'/file).read_text(encoding='utf-8'))
        rows=data['questions']
        check({q['id']:q['prompt'] for q in rows}==expected,'不同模型题目不一致：'+file)
        check(all(q['answer'] and q['elapsed_seconds']>0 for q in rows),'回答或耗时缺失：'+file)
    check('.env' in (ROOT/'.gitignore').read_text(encoding='utf-8'),'未忽略.env')
    if errors:
        print('\n'.join('FAIL '+e for e in errors))
        print(f'{len(errors)} failures / {checks} checks')
        return 1
    print(f'PASS {checks} checks：必交文件、相对链接、同步副本、提示词结构、原始日志与同题实验均通过。')
    print('人工验收仍需：'+'；'.join(manifest['manual_checks']))
    return 0

if __name__=='__main__':sys.exit(main())
