# RAGFlow 错误码详解

## HTTP 状态码

| 状态码 | 说明 | 解决方法 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权 | 检查 API Key 是否正确 |
| 403 | 禁止访问 | 检查权限设置 |
| 404 | 资源不存在 | 检查 ID 是否正确 |
| 500 | 服务器内部错误 | 联系管理员 |
| 503 | 服务不可用 | 稍后重试 |
| 504 | 网关超时 | 检查网络连接 |

## RAGFlow 业务错误码

| 错误码 | 说明 | 解决方法 |
|--------|------|----------|
| 101 | 数据集名称重复 | 使用不同的名称 |
| 102 | 无权访问资源 | 检查权限或资源归属 |
| 1001 | Chunk ID 无效 | 检查文档是否解析成功 |
| 1002 | Chunk 更新失败 | 重试或联系管理员 |

## 常见错误场景

### 1. 认证失败
```
错误：401 Unauthorized
原因：API Key 无效或过期
解决：
  1. 在 RAGFlow Web UI 重新生成 API Key
  2. 更新配置文件中的 RAGFLOW_API_KEY
  3. 确认 API Key 未过期
```

### 2. 连接失败
```
错误：ConnectionError: Failed to establish connection
原因：无法连接到 RAGFlow 服务器
解决：
  1. 检查 RAGFLOW_BASE_URL 是否正确
  2. 确认服务器是否运行
  3. 检查网络连接和防火墙设置
```

### 3. 文档解析失败
```
错误：1002 - Failed to bind embedding model
原因：嵌入模型配置错误或网络不可达
解决：
  1. 在 RAGFlow Web UI 检查嵌入模型配置
  2. 使用本地模型（推荐 Ollama + bge-m3）
  3. 或配置国内可访问的 API 服务
```

### 4. 查询无结果
```
现象：查询返回空结果
原因：
  1. 文档未解析
  2. 相似度阈值过高
  3. 问题表述不清晰
解决：
  1. 检查文档解析状态
  2. 降低 similarity_threshold
  3. 使用更具体的问题
```

### 5. 上传失败
```
错误：No file part!
原因：文件上传格式错误
解决：
  1. 使用 multipart/form-data 格式
  2. 检查文件路径是否正确
  3. 确认文件大小不超过限制（100MB）
```

## 调试技巧

### 1. 启用调试日志
```bash
export RAGFLOW_DEBUG=true
python python/client.py --test
```

### 2. 查看详细错误
```python
try:
    result = client.query("问题")
except RAGFlowError as e:
    print(f"错误码：{e.code}")
    print(f"错误信息：{e.message}")
    print(f"完整异常：{e}")
```

### 3. 使用诊断工具
```bash
python python/client.py --diagnose
```

## 性能优化

### 1. 调整超时时间
```bash
# 大文件上传时增加超时
export RAGFLOW_TIMEOUT=120
```

### 2. 增加重试次数
```bash
# 网络不稳定时增加重试
export RAGFLOW_MAX_RETRIES=5
```

### 3. 批量操作
```python
# 批量上传而不是单个上传
docs = client.upload_documents(kb_id, file_paths)
```

## 获取帮助

- 📖 文档：README.md
- 💬 Issues: GitHub Issues
- 📧 邮件：support@example.com
