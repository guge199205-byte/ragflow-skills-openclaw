# RAGFlow API Skills - AI Agent 技能说明

> 让任何 AI Agent 都能熟练使用 RAGFlow 知识库

---

## 🎯 技能描述

本技能包提供完整的 RAGFlow API 集成能力，使 AI Agent 能够：
- 管理知识库（创建/查询/删除）
- 上传和解析文档
- 执行语义检索
- 基于知识库问答
- 创建聊天助手

---

## 🤖 AI Agent 使用指南

### 触发条件

当用户提到以下关键词时，应使用本技能：
- "查询知识库"
- "搜索文档"
- "RAGFlow"
- "基于文档回答"
- "上传资料到知识库"
- "创建知识助手"

### 调用示例

#### 1. 知识库查询
```
用户：帮我查一下润滑脂的主要成分
AI: [调用 RAGFlow.query("润滑脂的主要成分")]
```

#### 2. 文档上传
```
用户：把这个 PDF 上传到知识库
AI: [调用 RAGFlow.upload_document(kb_id, file_path)]
```

#### 3. 创建助手
```
用户：创建一个润滑脂专家助手
AI: [调用 RAGFlow.create_chat_assistant(name="润滑脂专家", kb_ids=[...])]
```

---

## 📋 核心 API

### RAGFlow 类

```python
class RAGFlow:
    """RAGFlow API 客户端"""
    
    # 初始化
    def __init__(self, base_url: str, api_key: str)
    @classmethod
    def from_env(cls)  # 从环境变量加载配置
    
    # 知识库管理
    def list_knowledge_bases() -> List[KnowledgeBase]
    def create_knowledge_base(name: str) -> KnowledgeBase
    def delete_knowledge_base(kb_id: str) -> bool
    
    # 文档管理
    def upload_document(kb_id: str, file_path: str) -> Document
    def upload_documents(kb_id: str, file_paths: List[str]) -> List[Document]
    def parse_documents(kb_id: str, doc_ids: List[str]) -> bool
    def list_documents(kb_id: str) -> List[Document]
    
    # 检索与问答
    def query(question: str, kb_ids: List[str] = None) -> QueryResult
    def retrieve(question: str, kb_ids: List[str], top_k: int = 5) -> List[Chunk]
    
    # 聊天助手
    def create_chat_assistant(name: str, kb_ids: List[str]) -> ChatAssistant
    def chat(assistant_id: str, message: str, session_id: str = None) -> ChatResponse
    def create_session(assistant_id: str) -> Session
```

---

## 🔧 配置要求

### 必需配置
```bash
RAGFLOW_BASE_URL=http://your-ragflow-server.com
RAGFLOW_API_KEY=your-api-key
```

### 可选配置
```bash
RAGFLOW_DEFAULT_KB_ID=your-kb-id  # 默认知识库
RAGFLOW_TIMEOUT=30                 # 请求超时（秒）
RAGFLOW_MAX_RETRIES=3              # 最大重试次数
```

---

## ⚠️ 错误处理

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | 认证失败 | 检查 API Key |
| 403 | 权限不足 | 检查知识库权限 |
| 404 | 资源不存在 | 检查 ID 是否正确 |
| 500 | 服务器错误 | 稍后重试 |
| 1001 | Chunk ID 无效 | 检查文档是否解析 |
| 1002 | 解析失败 | 检查嵌入模型配置 |

### 异常处理示例
```python
from ragflow_client import RAGFlow, RAGFlowError

try:
    result = client.query("问题")
except RAGFlowError as e:
    if e.code == 401:
        print("API Key 无效，请检查配置")
    elif e.code == 1001:
        print("文档未解析，请先解析文档")
    else:
        print(f"错误：{e.message}")
```

---

## 📖 最佳实践

### 1. 知识库设计
- 按主题/项目/部门划分知识库
- 单个知识库文档数建议 <1000
- 定期清理过期文档

### 2. 文档上传
- 使用清晰的文件名
- 上传后检查解析状态
- 大文件分批上传

### 3. 查询优化
- 问题表述清晰具体
- 指定相关知识库
- 调整 top_k 参数控制结果数量

### 4. 错误处理
- 实现自动重试机制
- 记录详细错误日志
- 提供友好的错误提示

---

## 🧪 测试方法

### 连接测试
```bash
python python/client.py --test
```

### 功能测试
```bash
python examples/basic_usage.py
```

### 诊断工具
```bash
python python/client.py --diagnose
```

---

## 📚 完整文档

- [README.md](README.md) - 总体说明
- [docs/troubleshooting.md](docs/troubleshooting.md) - 故障排查
- [docs/best_practices.md](docs/best_practices.md) - 最佳实践
- [examples/](examples/) - 代码示例

---

## 🙋 常见问题

**Q: 如何获取 API Key？**  
A: 登录 RAGFlow Web UI → 设置 → API Keys → 创建新 Key

**Q: 文档上传后为什么无法查询？**  
A: 需要等待文档解析完成，检查解析状态

**Q: 如何提高查询准确性？**  
A: 
1. 确保文档已正确解析
2. 调整相似度阈值
3. 使用更具体的问题

---

## 📦 版本信息

- **版本**: 1.0.0
- **创建日期**: 2026-03-27
- **兼容 RAGFlow**: v0.8.0+
- **Python 版本**: 3.8+

---

**维护者**: 潘潘 🥧  
**许可证**: MIT
