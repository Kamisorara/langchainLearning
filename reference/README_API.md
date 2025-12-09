# 图片处理API

基于FastAPI和LangGraph的图片处理服务，支持图片上传并通过AI模型进行分析。

## 功能特性

- 🚀 FastAPI异步框架
- 📸 多格式图片上传支持
- 🤖 AI图片内容分析
- 📊 实时处理状态查询
- 🔍 完整的API文档

## 安装依赖

```bash
pip install -r requirements.txt
# 或者使用uv
uv sync
```

## 环境配置

创建 `.env` 文件并配置API密钥：

```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 启动服务

```bash
python app.py
```

服务将在 `http://localhost:8000` 启动。

## API接口

### 1. 上传图片

**POST** `/upload-image`

```bash
curl -X POST "http://localhost:8000/upload-image" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

响应示例：
```json
{
  "task_id": "task_1_a1b2c3d4",
  "status": "processing",
  "message": "图片上传成功，正在处理中..."
}
```

### 2. 查询处理状态

**GET** `/status/{task_id}`

```bash
curl -X GET "http://localhost:8000/status/task_1_a1b2c3d4"
```

响应示例：
```json
{
  "status": "completed",
  "message": "图片处理完成",
  "result": "{...AI分析结果...}",
  "error": null
}
```

### 3. 获取所有结果

**GET** `/results`

### 4. 删除结果

**DELETE** `/results/{task_id}`

### 5. 健康检查

**GET** `/health`

## 使用Python客户端

```python
import requests
import json

# 上传图片
with open('your_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload-image', files=files)
    task_id = response.json()['task_id']

# 查询结果
status_url = f'http://localhost:8000/status/{task_id}'
result = requests.get(status_url).json()

if result['status'] == 'completed':
    analysis_result = json.loads(result['result'])
    print(f"分析结果: {analysis_result}")
```

## API文档

启动服务后，访问以下地址查看交互式API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## 限制

- 最大文件大小：10MB
- 支持的图片格式：JPEG, PNG, GIF, BMP, WebP

## 错误处理

API使用标准HTTP状态码：

- `200`: 成功
- `400`: 请求错误（文件格式不支持、文件过大等）
- `404`: 资源不存在
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 开发说明

### 项目结构

```
.
├── app.py              # FastAPI主应用
├── main.py             # LangGraph定义
├── llm_node.py         # LLM处理节点
├── .env               # 环境变量配置
├── pyproject.toml     # 项目依赖配置
└── README_API.md      # API文档
```

### 扩展功能

1. **持久化存储**: 当前使用内存存储，生产环境建议使用数据库
2. **用户认证**: 添加JWT或OAuth2认证
3. **批量处理**: 支持多图片批量上传
4. **结果缓存**: 实现图片指纹和结果缓存
5. **异步队列**: 使用Celery或RQ进行任务队列管理

## 许可证

MIT License