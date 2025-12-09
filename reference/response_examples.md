# API响应格式示例

本文档展示了统一回复类实施后的API响应格式。

## 基础响应结构

所有API响应都遵循统一的基础结构：

```json
{
  "success": true,
  "message": "操作结果描述",
  "data": {},
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

## API端点响应示例

### 1. 获取API信息
**GET** `/`

```json
{
  "success": true,
  "message": "API信息",
  "data": {
    "message": "图片处理API",
    "version": "1.0.0",
    "endpoints": {
      "upload": "/upload-image",
      "status": "/status/{task_id}",
      "health": "/health",
      "sync_process": "/process-image-sync",
      "results": "/results"
    }
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 2. 健康检查
**GET** `/health`

```json
{
  "success": true,
  "message": "服务健康",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 3. 上传图片（异步处理）
**POST** `/upload-image`

```json
{
  "success": true,
  "message": "图片上传成功",
  "data": {
    "task_id": "task_1_a1b2c3d4",
    "status": "processing",
    "message": "图片上传成功，正在处理中..."
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 4. 查询任务状态
**GET** `/status/{task_id}`

#### 处理成功（通过Graph）
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "task_id": "task_1_a1b2c3d4",
    "status": "completed",
    "message": "图片处理完成（通过graph）",
    "result": "{\"id\":\"chat123\",\"content\":\"...\"}",
    "error": null,
    "processing_method": "graph"
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

#### 处理成功（回退处理）
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "task_id": "task_2_e5f6g7h8",
    "status": "completed",
    "message": "图片处理完成（回退处理）",
    "result": "{\"id\":\"chat124\",\"content\":\"...\"}",
    "error": null,
    "processing_method": "fallback",
    "graph_error": "Graph processing failed: ..."
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

#### 处理失败
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "task_id": "task_3_i9j0k1l2",
    "status": "failed",
    "message": "图片处理失败",
    "result": null,
    "error": "API key not found",
    "processing_method": "failed"
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 5. 同步处理图片
**POST** `/process-image-sync`

#### 成功处理（通过Graph）
```json
{
  "success": true,
  "message": "图片处理成功",
  "data": {
    "analysis_result": "{\"id\":\"chat125\",\"content\":\"...\"}",
    "processing_time": null,
    "image_info": null,
    "processing_method": "graph"
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 6. 获取所有任务结果
**GET** `/results`

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "total_tasks": 3,
    "results": {
      "task_1_a1b2c3d4": {
        "task_id": "task_1_a1b2c3d4",
        "status": "completed",
        "message": "图片处理完成（通过graph）",
        "result": "{\"id\":\"chat123\",\"content\":\"...\"}",
        "error": null,
        "processing_method": "graph"
      },
      "task_2_e5f6g7h8": {
        "task_id": "task_2_e5f6g7h8",
        "status": "failed",
        "message": "图片处理失败",
        "result": null,
        "error": "Invalid image format",
        "processing_method": "failed"
      }
    }
  },
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

### 7. 删除任务结果
**DELETE** `/results/{task_id}`

```json
{
  "success": true,
  "message": "任务 task_1_a1b2c3d4 的结果已删除",
  "data": null,
  "error": null,
  "timestamp": "2025-12-09T01:32:52.166Z"
}
```

## 错误响应

当发生HTTP错误时，响应格式如下：

### 400 Bad Request
```json
{
  "detail": "不支持的图片格式。支持的格式: image/jpeg, image/jpg, image/png, image/gif, image/bmp, image/webp"
}
```

### 404 Not Found
```json
{
  "detail": "任务ID不存在"
}
```

### 500 Internal Server Error
```json
{
  "detail": "处理上传文件时发生错误: Connection timeout"
}
```

## 状态枚举值

### ProcessingStatus（处理状态）
- `pending`: 等待中
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

### ProcessingMethod（处理方法）
- `graph`: 通过Graph处理
- `fallback`: 回退处理（Graph失败时使用）
- `direct`: 直接处理
- `failed`: 处理失败

## 使用Python客户端

```python
import requests

# 获取API信息
response = requests.get('http://localhost:8080/')
if response.json()['success']:
    print(f"API版本: {response.json()['data']['version']}")

# 上传图片
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8080/upload-image', files=files)

if response.json()['success']:
    task_id = response.json()['data']['task_id']
    print(f"任务ID: {task_id}")

    # 查询状态
    status_response = requests.get(f'http://localhost:8080/status/{task_id}')
    if status_response.json()['success']:
        status = status_response.json()['data']['status']
        print(f"任务状态: {status}")
```