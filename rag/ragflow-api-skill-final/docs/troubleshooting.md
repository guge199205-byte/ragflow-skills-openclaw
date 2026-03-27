# RAGFlow 故障排查指南

## 🔍 诊断流程

### 第 1 步：检查配置
```bash
# 1. 检查环境变量
echo $RAGFLOW_BASE_URL
echo $RAGFLOW_API_KEY

# 2. 运行诊断工具
python python/client.py --diagnose
```

### 第 2 步：测试连接
```bash
python python/client.py --test
```

### 第 3 步：检查知识库
```python
from python.client import RAGFlow
client = RAGFlow.from_env()
kbs = client.list_knowledge_bases()
print(f"知识库数量：{len(kbs)}")
```

---

## ❌ 常见问题

### 问题 1: 连接失败

**症状**:
```
ConnectionError: HTTPConnectionPool(host='192.168.31.72', port=80): 
Max retries exceeded
```

**可能原因**:
1. RAGFlow 服务器未启动
2. 服务器地址配置错误
3. 网络连接问题
4. 防火墙阻止

**解决方法**:
```bash
# 1. 检查服务器状态
curl http://your-ragflow-server.com/

# 2. 检查配置
cat config/ragflow.env | grep BASE_URL

# 3. 测试网络连通性
ping your-ragflow-server.com

# 4. 检查防火墙
telnet your-ragflow-server.com 80
```

---

### 问题 2: API Key 无效

**症状**:
```
AuthenticationError: [401] API Key 无效或已过期
```

**解决方法**:
1. 登录 RAGFlow Web UI
2. 进入 设置 → API Keys
3. 创建新的 API Key
4. 更新 `config/ragflow.env`

---

### 问题 3: 文档解析失败

**症状**:
```
文档状态：FAIL
错误：Failed to bind embedding model
```

**原因**: 嵌入模型配置错误或网络不可达

**解决方法**:

**方案 A: 使用本地模型（推荐）**
```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下载模型
ollama pull bge-m3

# 3. 在 RAGFlow Web UI 配置
# 设置 → 模型管理 → Embedding → 添加 Ollama
```

**方案 B: 使用国内 API**
```bash
# 1. 获取硅基流动 API Key
# 访问：https://cloud.siliconflow.cn/

# 2. 在 RAGFlow 配置
# 设置 → 模型管理 → Embedding → 添加 SiliconFlow
```

---

### 问题 4: 查询无结果

**症状**:
```
查询返回空结果或"无相关内容"
```

**可能原因**:
1. 文档未解析成功
2. 相似度阈值过高
3. 问题表述不清晰
4. 知识库选择错误

**解决方法**:
```python
# 1. 检查文档状态
docs = client.list_documents(kb_id)
for doc in docs:
    print(f"{doc.name}: {doc.status}")

# 2. 降低相似度阈值（在 API 调用时）
result = client.retrieve(question, kb_ids, top_k=10)

# 3. 使用更具体的问题
# 不好："润滑脂"
# 好："润滑脂的主要成分是什么？"

# 4. 确认使用正确的知识库
kbs = client.list_knowledge_bases()
for kb in kbs:
    print(f"{kb.id}: {kb.name}")
```

---

### 问题 5: 上传失败

**症状**:
```
上传失败：文件大小超过限制
或
No file part!
```

**解决方法**:
```python
# 1. 检查文件大小（限制 100MB）
import os
file_size = os.path.getsize('document.pdf')
print(f"文件大小：{file_size / 1024 / 1024:.2f} MB")

# 2. 使用正确的上传格式
# 正确：
with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f)}
    response = session.post(url, files=files)

# 错误：
# 直接发送文件路径而不是文件内容
```

---

### 问题 6: LLM 连接失败

**症状**:
```
聊天助手返回：CONNECTION_ERROR - Connection error
```

**原因**: LLM 服务配置问题

**解决方法**:
1. 在 RAGFlow Web UI 检查 LLM 配置
2. 使用国内 LLM 服务（DeepSeek/通义千问）
3. 或本地部署（Ollama + Qwen2.5）

---

## 🔧 高级调试

### 启用详细日志
```bash
export RAGFLOW_DEBUG=true
python examples/basic_usage.py
```

### 查看原始响应
```python
import requests

response = requests.get(
    'http://your-server.com/api/v1/datasets',
    headers={'Authorization': f'Bearer {api_key}'}
)
print(f"状态码：{response.status_code}")
print(f"响应内容：{response.text}")
```

### 网络抓包
```bash
# 使用 tcpdump 抓包
tcpdump -i any -s 0 -w ragflow.pcap host your-ragflow-server.com

# 使用 Wireshark 分析
wireshark ragflow.pcap
```

---

## 📊 性能优化

### 1. 调整超时
```bash
# 大文件上传
export RAGFLOW_TIMEOUT=120

# 正常查询
export RAGFLOW_TIMEOUT=30
```

### 2. 批量操作
```python
# 批量上传（推荐）
docs = client.upload_documents(kb_id, file_paths)

# 而不是循环单个上传
for file_path in file_paths:
    client.upload_document(kb_id, file_path)
```

### 3. 连接池
```python
# 复用 Session
client = RAGFlow.from_env()
# 多次使用同一个 client 实例
```

---

## 🆘 获取帮助

### 收集诊断信息
```bash
# 1. 系统信息
uname -a
python --version

# 2. 配置信息（隐藏敏感信息）
cat config/ragflow.env | grep -v API_KEY

# 3. 错误日志
python python/client.py --diagnose 2>&1 | tee diagnose.log

# 4. 网络测试
curl -v http://your-ragflow-server.com/api/v1/datasets
```

### 提交 Issue
包含以下信息：
1. 问题描述
2. 复现步骤
3. 错误日志
4. 诊断信息
5. 环境信息

---

## 📚 相关文档

- [README.md](../README.md) - 总体说明
- [error_codes.md](error_codes.md) - 错误码详解
- [best_practices.md](best_practices.md) - 最佳实践

---

**最后更新**: 2026-03-27  
**维护者**: 潘潘团队 🥧
