# RAGFlow API Skills

> 🤖 **AI Agent 专用 RAGFlow 集成技能包**  
> 📦 版本：1.0.0  
> 📅 创建时间：2026-03-27  
> 🌟 特点：零配置上手、完整示例、故障自诊断

---

## 📖 快速开始

### 1 分钟配置

```bash
# 1. 复制配置模板
cp config/example.env config/ragflow.env

# 2. 编辑配置文件
vim config/ragflow.env

# 3. 测试连接
python python/client.py --test
```

### 核心功能

```python
from ragflow_client import RAGFlow

# 初始化客户端
client = RAGFlow(
    base_url="http://your-ragflow-server.com",
    api_key="your-api-key"
)

# 查询知识库
result = client.query("润滑脂的主要成分是什么？")
print(result.answer)
```

---

## 📦 目录结构

```
ragflow-api-skill/
├── README.md                 # 本文件
├── SKILL.md                  # AI Agent 技能说明
├── python/
│   └── client.py             # RAGFlow API 客户端 (含配置、模型及异常定义)
├── config/
│   ├── example.env           # 配置模板
│   └── error_codes.md        # 错误码详解
├── docs/
│   ├── troubleshooting.md    # 故障排查指南
│   └── best_practices.md     # 最佳实践
└── examples/
    └── basic_usage.py        # 基础使用示例

```

---

## 🎯 功能特性

### ✅ 核心功能
- [x] 知识库管理（创建/查询/删除）
- [x] 文档上传（支持多格式批量上传）
- [x] 文档解析（自动分块/向量化）
- [x] 语义检索（向量相似度搜索）
- [x] 知识库问答（基于文档的 QA）
- [x] 聊天助手（创建/对话/会话管理）
- [x] OpenAI 兼容 API（无缝切换）

### 🔧 增强功能
- [x] 自动重试机制（网络故障处理）
- [x] 连接池管理（性能优化）
- [x] 流式响应（实时输出）
- [x] 错误诊断（自动检测配置问题）
- [x] 日志记录（调试/审计）

---

## 🛠️ 安装与配置

### 环境要求

- Python 3.8+
- RAGFlow 服务器（本地部署或云服务）
- 网络连接（访问 RAGFlow API）

### 安装依赖

```bash
pip install requests python-dotenv
```

### 配置文件

创建 `config/ragflow.env`：

```bash
# RAGFlow 服务器地址
RAGFLOW_BASE_URL=http://192.168.31.72

# API Key（在 RAGFlow Web UI 获取）
RAGFLOW_API_KEY=your-api-key-here

# 默认知识库 ID（可选）
RAGFLOW_DEFAULT_KB_ID=your-kb-id

# 请求超时（秒）
RAGFLOW_TIMEOUT=30

# 最大重试次数
RAGFLOW_MAX_RETRIES=3
```

### 验证配置

```bash
python python/client.py --test
```

**成功输出**：
```
✅ RAGFlow 连接成功！
服务器：http://192.168.31.72
API Key: 有效
知识库数量：17
```

---

## 📖 使用指南

### 1. 初始化客户端

```python
from ragflow_client import RAGFlow

# 从配置文件加载
client = RAGFlow.from_env()

# 或手动指定
client = RAGFlow(
    base_url="http://your-server.com",
    api_key="your-api-key"
)
```

### 2. 知识库管理

```python
# 列出所有知识库
kbs = client.list_knowledge_bases()
for kb in kbs:
    print(f"{kb.name}: {kb.document_count} 文档")

# 创建知识库
kb = client.create_knowledge_base("我的知识库")

# 删除知识库
client.delete_knowledge_base(kb_id)
```

### 3. 文档上传

```python
# 上传单个文档
doc = client.upload_document(
    kb_id="your-kb-id",
    file_path="./document.pdf"
)

# 批量上传
docs = client.upload_documents(
    kb_id="your-kb-id",
    file_paths=["./doc1.pdf", "./doc2.docx"]
)

# 解析文档
client.parse_documents(kb_id, [doc.id for doc in docs])
```

### 4. 知识库查询

```python
# 简单查询
result = client.query("润滑脂的主要成分？")
print(result.answer)

# 带引用
result = client.query("润滑脂成分？", show_references=True)
for ref in result.references:
    print(f"- {ref.document_name}: {ref.content[:100]}")

# 指定知识库
result = client.query(
    "润滑脂成分？",
    kb_ids=["kb-id-1", "kb-id-2"]
)
```

### 5. 聊天助手

```python
# 创建助手
assistant = client.create_chat_assistant(
    name="润滑脂专家",
    kb_ids=["your-kb-id"]
)

# 对话
response = client.chat(
    assistant_id=assistant.id,
    message="如何选择高温润滑脂？"
)
print(response.answer)

# 多轮对话
session = client.create_session(assistant.id)
client.chat(assistant.id, "你好", session_id=session.id)
client.chat(assistant.id, "详细介绍一下", session_id=session.id)
```

---

## 🔍 故障诊断

### 运行诊断工具

```bash
python python/client.py --diagnose
```

### 常见问题

#### 1. 连接失败
```
错误：ConnectionError: Failed to establish connection
解决：
  1. 检查 RAGFLOW_BASE_URL 是否正确
  2. 确认服务器是否运行
  3. 检查网络连接
```

#### 2. 认证失败
```
错误：401 Unauthorized
解决：
  1. 检查 RAGFLOW_API_KEY 是否正确
  2. 在 RAGFlow Web UI 重新生成 API Key
  3. 确认 API Key 未过期
```

#### 3. 文档解析失败
```
错误：Failed to bind embedding model
解决：
  1. 在 RAGFlow Web UI 检查嵌入模型配置
  2. 使用本地模型（推荐 Ollama + bge-m3）
  3. 或配置国内可访问的 API 服务
```

详见：[docs/troubleshooting.md](docs/troubleshooting.md)

---

## 📚 示例代码

查看 `examples/` 目录：

| 文件 | 说明 |
|------|------|
| `basic_usage.py` | 基础使用示例（涵盖知识库、文档与问答等常用功能） |


**运行示例**：
```bash
python examples/basic_usage.py
```

---

## 🔐 安全建议

### API Key 管理
- ✅ 使用环境变量存储 API Key
- ✅ 不要将 `ragflow.env` 提交到版本控制
- ✅ 定期轮换 API Key
- ✅ 限制 API Key 权限范围

### 网络安全
- ✅ 使用 HTTPS（生产环境）
- ✅ 配置防火墙规则
- ✅ 限制 API 访问 IP

---

## 📊 API 限制

| 项目 | 限制 |
|------|------|
| 请求超时 | 30 秒（可配置） |
| 最大重试 | 3 次（可配置） |
| 单次上传 | 10 个文件 |
| 文件大小 | ≤100MB |
| 并发请求 | 建议≤10/s |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境
```bash
git clone https://github.com/your-repo/ragflow-api-skill.git
cd ragflow-api-skill
pip install -r requirements.txt
```

### 测试
```bash
python -m pytest tests/
```

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [RAGFlow](https://github.com/infiniflow/ragflow) - 强大的 RAG 引擎
- 贡献者和使用者

---

## 📞 支持

- 📧 Email: guge199205@gmail.com
- 💬 GitHub Issues: [提交问题](https://github.com/your-repo/ragflow-api-skill/issues)
- 📖 文档：https://ragflow-api-skill.readthedocs.io

---

**最后更新**: 2026-03-27  
**维护者**: 潘潘 🥧
