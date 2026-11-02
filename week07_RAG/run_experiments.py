"""固定问题做四路真实比较；逐题保存，支持中断续跑，不筛选或改写回答。"""
import argparse
from datetime import datetime
import importlib.metadata
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import rag_qa as rag

QUESTIONS = [
    ('Q1', '根据GF 0025—2021，四级累计词汇量是多少？', '3245个'),
    ('Q2', '根据GF 0025—2021，四级本级新增和累计语法点分别是多少？', '新增76个，累计286个'),
    ('Q3', '根据GF 0025—2021，三级累计词汇量和汉字量分别是多少？', '词汇2245个，汉字900个'),
    ('Q4', '根据GF 0025—2021，高等阶段七至九级的量化指标是否按每级分别统计？', '不分别统计，整体描述'),
    ('Q5', '根据GF 0025—2021，四维基准包括哪些语言要素？', '音节、汉字、词汇、语法'),
    ('Q6', '根据本次等级标准节选，2026年上海HSK四级考试的报名费是多少元？', '资料中未提及'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=rag.WEEK_DIR/'evidence'/'experiment_20261102.json')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    signature = rag.corpus_signature()
    if args.output.exists():
        if not args.resume:
            raise SystemExit('结果已存在；使用新文件名，或 --resume 补齐未完成项')
        data = json.loads(args.output.read_text())
        if data['corpus_signature'] != signature:
            raise SystemExit('语料已改变，请使用新的实验文件')
    else:
        packages=['langchain-community','langchain-text-splitters','langchain-ollama','langchain-chroma','chromadb','openai']
        data = {'started_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                'corpus_signature':signature, 'embedding_model':rag.EMBED_MODEL,
                'chunk_size':rag.CHUNK_SIZE, 'chunk_overlap':rag.CHUNK_OVERLAP, 'k':3,
                'packages':{p:importlib.metadata.version(p) for p in packages}, 'questions':[]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    def save():
        args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for qid, question, expected in QUESTIONS:
        row = next((q for q in data['questions'] if q['id']==qid),None)
        if row is None:
            row = {'id':qid,'question':question,'reference_answer':expected,'runs':{}}
            data['questions'].append(row)
        for mode,prefer in [('bare_local','local'),('bare_api','api'),('rag_local','local'),('rag_api','api')]:
            if mode in row['runs']:
                continue
            if mode.startswith('rag'):
                result = rag.rag_qa_details(question,prefer)
            else:
                result = rag.call_llm('请用中文简答，不超过150字。不确定就明确说不确定。\n问题：'+question,prefer)
            result['recorded_at']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
            row['runs'][mode]=result
            save()
            print(qid,mode,result['actual_engine'],result['elapsed_seconds'],flush=True)
    data['completed_at']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    save()


if __name__=='__main__':
    main()
