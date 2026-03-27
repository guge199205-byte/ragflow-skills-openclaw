# RAGFlow 最佳实践

## 📖 知识库设计

### 1. 合理划分知识库

**推荐做法**:
```
✅ 按主题划分
  - 润滑脂知识
  - 橡胶技术
  - 涂料配方

✅ 按项目划分
  - 项目 A 文档
  - 项目 B 文档

✅ 按部门划分
  - 研发部
  - 生产部
  - 销售部
```

**不推荐**:
```
❌ 所有文档放在一个知识库
❌ 知识库数量过多（>50）
❌ 知识库命名不清晰
```

### 2. 文档组织

**文件命名规范**:
```
✅ 清晰描述性名称
  - 润滑脂基础成分.md
  - 2026 年 Q1 销售报告.pdf
  - 产品技术规格书_v2.0.docx

❌ 模糊名称
  - 文档 1.md
  - 新建文件.pdf
  - 未命名.docx
```

**文档结构建议**:
```markdown
# 标题

## 1. 概述
简要介绍内容

## 2. 详细内容
分章节详细描述

## 3. 总结
关键要点

## 4. 参考资料
相关链接和文档
```

---

## 📤 文档上传

### 1. 批量上传

**推荐做法**:
```python
# 批量上传（高效）
file_paths = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
docs = client.upload_documents(kb_id, file_paths)

# 等待所有上传完成后再解析
doc_ids = [doc.id for doc in docs]
client.parse_documents(kb_id, doc_ids)
```

**不推荐**:
```python
# 单个上传（低效）
for file_path in file_paths:
    doc = client.upload_document(kb_id, file_path)
    client.parse_documents(kb_id, [doc.id])  # 每次都解析
```

### 2. 文件格式

**推荐格式**:
- ✅ PDF（保留格式）
- ✅ Markdown（轻量级）
- ✅ Word（.docx）
- ✅ Excel（.xlsx，表格数据）
- ✅ TXT（纯文本）

**注意事项**:
- 文件大小 ≤ 100MB
- 避免加密文档
- PDF 最好是文字版（非扫描版）

### 3. 解析策略

**大文档处理**:
```python
# 大文档分批次解析
large_docs = [...]  # 大文件列表
batch_size = 10

for i in range(0, len(large_docs), batch_size):
    batch = large_docs[i:i+batch_size]
    client.parse_documents(kb_id, [doc.id for doc in batch])
    time.sleep(2)  # 避免过载
```

---

## 🔍 查询优化

### 1. 问题表述

**好问题**:
```
✅ "润滑脂的主要成分是什么？"
✅ "锂基润滑脂和钙基润滑脂有什么区别？"
✅ "如何选择高温润滑脂？"
```

**差问题**:
```
❌ "润滑脂"（太宽泛）
❌ "那个...就是...润滑油的那个"（不清晰）
❌ "？？？"（无意义）
```

### 2. 参数调整

**top_k 选择**:
```python
# 精确答案（少量相关）
result = client.retrieve(question, kb_ids, top_k=3)

# 全面了解（大量相关）
result = client.retrieve(question, kb_ids, top_k=10)
```

**相似度阈值**:
```python
# 高准确度（严格匹配）
payload['similarity_threshold'] = 0.5

# 高召回率（宽松匹配）
payload['similarity_threshold'] = 0.1
```

### 3. 多知识库查询

```python
# 跨知识库查询
kb_ids = ['kb1-id', 'kb2-id', 'kb3-id']
result = client.query(question, kb_ids=kb_ids)

# 按优先级排序
# 前面的知识库权重更高
```

---

## 💬 聊天助手

### 1. 助手设计

**系统提示词模板**:
```python
prompt = """
你是{领域}专家助手。

职责:
1. 基于知识库回答问题
2. 提供准确、详细的信息
3. 如不确定，说明"根据现有资料无法确定"

回答风格:
- 专业但不晦涩
- 结构化（分点说明）
- 提供参考资料

限制:
- 不回答与{领域}无关的问题
- 不提供医疗/法律建议
"""

assistant = client.create_chat_assistant(
    name="润滑脂专家",
    kb_ids=[kb_id],
    prompt=prompt
)
```

### 2. 会话管理

**多轮对话**:
```python
# 创建会话
session_id = client.create_session(assistant_id)

# 持续对话
responses = []
questions = ["问题 1", "问题 2", "问题 3"]

for q in questions:
    resp = client.chat(assistant_id, q, session_id=session_id)
    responses.append(resp.answer)
    print(f"AI: {resp.answer}")
```

### 3. 上下文管理

```python
# 长对话定期创建新会话
# 避免上下文过长影响性能
if message_count > 20:
    session_id = client.create_session(assistant_id)
    message_count = 0
```

---

## ⚡ 性能优化

### 1. 连接管理

```python
# 复用客户端实例
client = RAGFlow.from_env()

# 多次使用同一个 client
result1 = client.query("问题 1")
result2 = client.query("问题 2")

# 而不是每次都创建新实例
```

### 2. 超时配置

```bash
# 查询操作（快速）
RAGFLOW_TIMEOUT=30

# 上传大文件
RAGFLOW_TIMEOUT=120

# 批量解析
RAGFLOW_TIMEOUT=300
```

### 3. 重试策略

```python
# 指数退避重试
import time

for attempt in range(3):
    try:
        result = client.query(question)
        break
    except ConnectionError:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt)  # 2s, 4s
```

---

## 🔒 安全实践

### 1. API Key 管理

```bash
# ✅ 使用环境变量
export RAGFLOW_API_KEY=your-key

# ✅ 使用配置文件（不提交到版本控制）
cat config/ragflow.env

# ❌ 硬编码在代码中
api_key = "sk-xxxxx"  # 不要这样做！
```

### 2. 权限控制

```python
# 只读操作使用只读 API Key
# 写操作使用完整权限 API Key

# 定期轮换 API Key
# 每 90 天更换一次
```

### 3. 数据脱敏

```python
# 上传前去除敏感信息
def sanitize_document(content):
    # 去除个人信息
    # 去除商业机密
    # 去除 API Key 等
    return sanitized_content
```

---

## 📊 监控与维护

### 1. 定期检查

```python
# 每周检查文档状态
docs = client.list_documents(kb_id)
failed_docs = [d for d in docs if d.status == 'FAIL']

if failed_docs:
    print(f"发现 {len(failed_docs)} 个解析失败的文档")
    # 重新解析或联系管理员
```

### 2. 清理过期内容

```python
# 定期清理无用知识库
old_kbs = [...]  # 获取过期知识库
for kb in old_kbs:
    client.delete_knowledge_base(kb.id)
```

### 3. 性能监控

```python
# 记录查询响应时间
import time

start = time.time()
result = client.query(question)
duration = time.time() - start

if duration > 5:  # 超过 5 秒
    print(f"查询缓慢：{duration:.2f}s")
```

---

## 🎯 场景示例

### 场景 1: 客服机器人

```python
# 创建客服助手
assistant = client.create_chat_assistant(
    name="产品客服",
    kb_ids=[product_kb_id],
    prompt="你是产品客服助手，回答产品相关问题"
)

# 处理用户咨询
def handle_user_query(user_question):
    response = client.chat(assistant.id, user_question)
    
    if not response.answer:
        return "抱歉，我无法回答这个问题。请联系人工客服。"
    
    return response.answer
```

### 场景 2: 文档检索系统

```python
# 批量上传新文档
new_docs = upload_new_documents()

# 解析文档
client.parse_documents(kb_id, [d.id for d in new_docs])

# 等待解析完成
time.sleep(30)

# 提供检索服务
def search_documents(query):
    chunks = client.retrieve(query, [kb_id], top_k=5)
    return format_results(chunks)
```

### 场景 3: 知识问答系统

```python
# 创建多个专家助手
assistants = {
    'technical': client.create_chat_assistant(...),
    'sales': client.create_chat_assistant(...),
    'support': client.create_chat_assistant(...)
}

# 根据问题类型路由
def answer_question(question, category):
    assistant = assistants[category]
    return client.chat(assistant.id, question)
```

---

## 📚 相关文档

- [README.md](../README.md) - 总体说明
- [troubleshooting.md](troubleshooting.md) - 故障排查
- [error_codes.md](../config/error_codes.md) - 错误码

---

**最后更新**: 2026-03-27  
**维护者**: 潘潘团队 🥧
