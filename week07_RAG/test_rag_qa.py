"""离线回归：索引变更、重建、k参数、来源及边界；不调用云端。"""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from langchain_core.embeddings import Embeddings
import rag_qa as rag


class TestEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self.embed_query(t) for t in texts]
    def embed_query(self, text):
        return [x / 255 for x in hashlib.sha256(text.encode()).digest()[:8]]


class RAGTests(unittest.TestCase):
    def test_chunk_sources_and_limit(self):
        docs=rag.load_chunks()
        self.assertGreaterEqual(len(docs),5)
        self.assertTrue(all(len(d.page_content)<=500 for d in docs))
        self.assertEqual(len({d.metadata['chunk_id'] for d in docs}),len(docs))
        self.assertTrue(all(d.metadata['source'] and d.metadata['section'] for d in docs))

    def test_index_reuse_rebuild_and_changed_corpus(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(rag,'OllamaEmbeddings',return_value=TestEmbeddings()):
            corpus=Path(folder)/'test.txt';persist=Path(folder)/'index'
            corpus.write_text('## A\n原始资料甲\n\n## B\n原始资料乙')
            first=rag.get_store(corpus=corpus,persist=persist)
            self.assertEqual(len(first.get()['ids']),2)
            self.assertIs(first,rag.get_store(corpus=corpus,persist=persist))
            rebuilt=rag.get_store(True,corpus=corpus,persist=persist)
            self.assertEqual(len(rebuilt.get()['ids']),2)
            corpus.write_text('## C\n只保留新资料丙')
            changed=rag.get_store(corpus=corpus,persist=persist)
            self.assertEqual(changed.get()['documents'],['## C\n只保留新资料丙'])
            self.assertNotEqual(changed._collection.name,rebuilt._collection.name)

    def test_k_not_stuck_in_cache(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(rag,'OllamaEmbeddings',return_value=TestEmbeddings()):
            corpus=Path(folder)/'test.txt';corpus.write_text('## A\n甲\n\n## B\n乙\n\n## C\n丙')
            args=dict(corpus=corpus,persist=Path(folder)/'index')
            self.assertEqual(len(rag.get_retriever(1,**args).invoke('甲')),1)
            self.assertEqual(len(rag.get_retriever(2,**args).invoke('甲')),2)

    def test_query_normalization_keeps_subject_and_other_versions(self):
        self.assertEqual(rag.retrieval_query('根据GF 0025—2021，四维基准包括什么？'),'四维基准包括什么？')
        self.assertEqual(rag.retrieval_query('根据GF 0025—2020，四维基准包括什么？'),'根据GF 0025—2020，四维基准包括什么？')
        self.assertEqual(rag.retrieval_query('四级有多少词？'),'四级有多少词？')

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):rag.get_retriever(0)
        with self.assertRaises(ValueError):rag.retrieve_documents('  ')
        with self.assertRaises(ValueError):rag.call_llm('问题','invalid')
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'empty.txt';p.write_text(' ')
            with self.assertRaises(ValueError):rag.load_chunks(p)

    def test_missing_and_invalid_citations_are_not_hidden(self):
        docs=rag.load_chunks()[:1]
        with patch.object(rag,'retrieve_documents',return_value=docs),patch.object(rag,'call_llm',return_value={'answer':'错误引用[S99]' }):
            result=rag.rag_qa_details('问题')
            self.assertEqual(result['invalid_citations'],['S99'])
            self.assertFalse(result['has_citation'])
            self.assertEqual(result['sources'][0]['text'],docs[0].page_content)
        self.assertIn('资料中未提及',rag.build_prompt('问题','资料'))


if __name__=='__main__':unittest.main()
