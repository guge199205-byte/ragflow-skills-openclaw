#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow API Client - Python 客户端库

让 AI Agent 轻松集成 RAGFlow 知识库
"""

import os
import time
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# ============== 异常类 ==============

class RAGFlowError(Exception):
    """RAGFlow API 异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class AuthenticationError(RAGFlowError):
    """认证错误"""
    pass


class ConnectionError(RAGFlowError):
    """连接错误"""
    pass


# ============== 数据模型 ==============

@dataclass
class KnowledgeBase:
    """知识库模型"""
    id: str
    name: str
    description: Optional[str]
    document_count: int
    chunk_count: int
    created_at: str


@dataclass
class Document:
    """文档模型"""
    id: str
    name: str
    size: int
    chunk_count: int
    status: str
    created_at: str


@dataclass
class Chunk:
    """文本块模型"""
    id: str
    content: str
    document_id: str
    document_name: str
    similarity: float


@dataclass
class QueryResult:
    """查询结果模型"""
    answer: str
    references: List[Chunk]
    session_id: str


# ============== RAGFlow 客户端 ==============

class RAGFlow:
    """RAGFlow API 客户端"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化 RAGFlow 客户端
        
        Args:
            base_url: RAGFlow 服务器地址
            api_key: API Key
            timeout: 请求超时（秒）
            max_retries: 最大重试次数
        """
        # 如果未提供参数，从环境变量加载
        if base_url is None or api_key is None:
            base_url = os.getenv('RAGFLOW_BASE_URL')
            api_key = os.getenv('RAGFLOW_API_KEY')
            timeout = int(os.getenv('RAGFLOW_TIMEOUT', 30))
            max_retries = int(os.getenv('RAGFLOW_MAX_RETRIES', 3))
        
        if not base_url or not api_key:
            raise ValueError("缺少必需的环境变量：RAGFLOW_BASE_URL 或 RAGFLOW_API_KEY")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
            # 不设置 Content-Type，让不同请求自动设置
        })
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        return cls()
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """发送 HTTP 请求（带重试）"""
        url = f"{self.base_url}{path}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                
                data = response.json()
                
                if response.status_code == 401:
                    raise AuthenticationError(401, "API Key 无效或已过期")
                
                if data.get('code', 0) != 0:
                    raise RAGFlowError(
                        data.get('code', 500),
                        data.get('message', '未知错误')
                    )
                
                return data
                
            except requests.exceptions.ConnectionError as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(503, f"无法连接到服务器：{e}")
                time.sleep(2 ** attempt)
            
            except requests.exceptions.Timeout as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(504, "请求超时")
                time.sleep(2 ** attempt)
        
        raise RAGFlowError(500, "请求失败")
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            kbs = self.list_knowledge_bases()
            return {
                'status': 'success',
                'message': '连接成功',
                'kb_count': len(kbs)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """列出所有知识库"""
        data = self._request('GET', '/api/v1/datasets')
        
        kbs = []
        for kb_data in data.get('data', []):
            kbs.append(KnowledgeBase(
                id=kb_data['id'],
                name=kb_data['name'],
                description=kb_data.get('description'),
                document_count=kb_data['document_count'],
                chunk_count=kb_data['chunk_count'],
                created_at=kb_data['create_date']
            ))
        return kbs
    
    def create_knowledge_base(
        self,
        name: str,
        description: str = None
    ) -> KnowledgeBase:
        """创建知识库"""
        payload = {'name': name}
        if description:
            payload['description'] = description
        
        data = self._request('POST', '/api/v1/datasets', json=payload)
        kb_data = data['data']
        
        return KnowledgeBase(
            id=kb_data['id'],
            name=kb_data['name'],
            description=kb_data.get('description'),
            document_count=0,
            chunk_count=0,
            created_at=kb_data['create_date']
        )
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        """删除知识库"""
        self._request('DELETE', '/api/v1/datasets', json={'ids': [kb_id]})
        return True
    
    def upload_document(self, kb_id: str, file_path: str) -> Document:
        """上传单个文档"""
        url = f"{self.base_url}/api/v1/datasets/{kb_id}/documents"
        
        # 不要设置 Content-Type，让 requests 自动设置为 multipart/form-data
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = self.session.post(url, files=files, headers=headers, timeout=self.timeout)
            data = response.json()
        
        if data.get('code', 0) != 0:
            raise RAGFlowError(data.get('code', 500), data.get('message', '上传失败'))
        
        doc_data = data['data'][0]
        return Document(
            id=doc_data['id'],
            name=doc_data['name'],
            size=doc_data['size'],
            chunk_count=0,
            status=doc_data['run'],
            created_at=doc_data.get('create_date', '')
        )
    
    def parse_documents(self, kb_id: str, doc_ids: List[str]) -> bool:
        """解析文档"""
        self._request('POST', f'/api/v1/datasets/{kb_id}/chunks',
                     json={'document_ids': doc_ids})
        return True
    
    def list_documents(self, kb_id: str) -> List[Document]:
        """列出知识库中的文档"""
        data = self._request('GET', f'/api/v1/datasets/{kb_id}/documents')
        
        docs = []
        for doc_data in data.get('data', {}).get('docs', []):
            docs.append(Document(
                id=doc_data['id'],
                name=doc_data['name'],
                size=doc_data['size'],
                chunk_count=doc_data.get('chunk_count', 0),
                status=doc_data['run'],
                created_at=doc_data.get('create_date', '')
            ))
        return docs
    
    def retrieve(
        self,
        question: str,
        kb_ids: List[str],
        top_k: int = 5
    ) -> List[Chunk]:
        """检索相关文本块"""
        payload = {
            'question': question,
            'dataset_ids': kb_ids,
            'page': 1,
            'page_size': top_k,
            'similarity_threshold': 0.2
        }
        
        data = self._request('POST', '/api/v1/retrieval', json=payload)
        
        chunks = []
        for chunk_data in data.get('data', {}).get('chunks', []):
            chunks.append(Chunk(
                id=chunk_data['id'],
                content=chunk_data['content'],
                document_id=chunk_data['document_id'],
                document_name=chunk_data.get('document_name', ''),
                similarity=chunk_data.get('similarity', 0)
            ))
        return chunks
    
    def query(
        self,
        question: str,
        kb_ids: List[str] = None,
        show_references: bool = True
    ) -> QueryResult:
        """基于知识库问答"""
        if kb_ids is None:
            kb_ids = [os.getenv('RAGFLOW_DEFAULT_KB_ID')]
        
        chunks = self.retrieve(question, kb_ids)
        answer = f"检索到 {len(chunks)} 个相关片段"
        
        return QueryResult(
            answer=answer,
            references=chunks if show_references else [],
            session_id=''
        )


# ============== 命令行工具 ==============

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAGFlow API 客户端')
    parser.add_argument('--test', action='store_true', help='测试连接')
    parser.add_argument('--diagnose', action='store_true', help='诊断问题')
    
    args = parser.parse_args()
    
    try:
        client = RAGFlow.from_env()
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        return
    
    if args.test:
        result = client.test_connection()
        if result['status'] == 'success':
            print(f"✅ RAGFlow 连接成功！")
            print(f"   知识库数量：{result['kb_count']}")
        else:
            print(f"❌ 连接失败：{result['message']}")
    
    elif args.diagnose:
        print("🔍 开始诊断...")
        print("\n1. 检查环境变量")
        print(f"   RAGFLOW_BASE_URL: {os.getenv('RAGFLOW_BASE_URL', '未设置')}")
        print(f"   RAGFLOW_API_KEY: {'已设置' if os.getenv('RAGFLOW_API_KEY') else '未设置'}")
        
        print("\n2. 测试连接")
        result = client.test_connection()
        print(f"   状态：{result['status']}")
        print(f"   消息：{result['message']}")


if __name__ == '__main__':
    main()
