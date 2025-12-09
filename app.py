import base64
import os
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from llm_node import process_image_base64
from main import process_image_with_graph
from response_models import (
    UnifiedResponse, TaskResponse, TaskResultResponse, HealthResponse,
    APIInfoResponse, AllTasksResponse, ProcessingStatus, ProcessingMethod,
    success_response, create_task_response,
    create_task_result_response, create_image_processing_response, success_response_with_data, ImageProcessingResult
)

app = FastAPI(title="图片处理API", description="上传图片并通过graph进行处理")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储处理结果的字典（临时存储，实际应用中应使用数据库）
processing_results = {}

# 支持的图片格式
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp"
}

def get_image_base64(file_content: bytes, file_format: str) -> str:
    """将图片内容转换为base64格式"""
    # 根据文件类型确定MIME类型
    mime_type = {
        "jpg": "jpeg",
        "jpeg": "jpeg",
        "png": "png",
        "gif": "gif",
        "bmp": "bmp",
        "webp": "webp"
    }.get(file_format.lower(), "jpeg")

    base64_str = base64.b64encode(file_content).decode('utf-8')
    return base64_str

@app.get("/", response_model=UnifiedResponse[APIInfoResponse])
async def root():
    """根路径，返回API信息"""
    api_info = APIInfoResponse(
        message="图片处理API",
        version="1.0.0",
        endpoints={
            "upload": "/upload-image",
            "status": "/status/{task_id}",
            "health": "/health",
            "sync_process": "/process-image-sync",
            "results": "/results"
        }
    )
    return success_response_with_data("API信息", data=api_info.model_dump())

@app.get("/health", response_model=UnifiedResponse[HealthResponse])
async def health_check():
    """健康检查接口"""
    health = HealthResponse(
        status="healthy",
        version="1.0.0"
    )
    return success_response_with_data("服务健康", data=health.model_dump())

@app.post("/upload-image", response_model=UnifiedResponse[TaskResponse])
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> UnifiedResponse[TaskResponse]:
    """
    上传图片并异步处理

    Args:
        file: 上传的图片文件

    Returns:
        包含任务ID的响应
    """
    try:
        # 验证文件类型
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片格式。支持的格式: {', '.join(SUPPORTED_IMAGE_TYPES)}"
            )

        # 验证文件大小（10MB限制）
        file_size = 0
        content = await file.read()
        file_size = len(content)

        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="文件大小不能超过10MB"
            )

        # 获取文件格式
        file_format = file.filename.split('.')[-1] if file.filename else "jpg"

        # 生成任务ID
        task_id = f"task_{len(processing_results) + 1}_{os.urandom(4).hex()}"

        # 初始化任务状态
        processing_results[task_id] = {
            "status": ProcessingStatus.PROCESSING,
            "message": "图片正在处理中...",
            "result": None,
            "error": None
        }

        # 添加后台任务
        background_tasks.add_task(
            process_image_background,
            task_id=task_id,
            image_content=content,
            file_format=file_format
        )

        task_response = create_task_response(
            task_id=task_id,
            status=ProcessingStatus.PROCESSING,
            message="图片上传成功，正在处理中..."
        )
        return success_response_with_data("图片上传成功", data=task_response.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理上传文件时发生错误: {str(e)}"
        )

async def process_image_background(task_id: str, image_content: bytes, file_format: str):
    """
    后台任务：使用graph处理图片
    """
    try:
        # 将图片转换为base64
        image_base64 = get_image_base64(image_content, file_format)

        # 使用graph处理图片（推荐方式）
        graph_result = process_image_with_graph(image_base64)

        if graph_result["success"]:
            # 更新任务状态 - 成功
            processing_results[task_id] = create_task_result_response(
                task_id=task_id,
                status=ProcessingStatus.COMPLETED,
                message="图片处理完成（通过graph）",
                result=graph_result["data"],
                processing_method=ProcessingMethod.GRAPH
            ).model_dump()
        else:
            # graph处理失败，回退到直接调用
            fallback_result = process_image_base64(image_base64)
            processing_results[task_id] = create_task_result_response(
                task_id=task_id,
                status=ProcessingStatus.COMPLETED,
                message="图片处理完成（回退处理）",
                result=fallback_result,
                processing_method=ProcessingMethod.FALLBACK,
                graph_error=graph_result["error"]
            ).model_dump()

    except Exception as e:
        # 更新任务状态为失败
        processing_results[task_id] = create_task_result_response(
            task_id=task_id,
            status=ProcessingStatus.FAILED,
            message="图片处理失败",
            error=str(e),
            processing_method=ProcessingMethod.FAILED
        ).model_dump()

@app.get("/status/{task_id}", response_model=UnifiedResponse[TaskResultResponse])
async def get_processing_status(task_id: str) -> UnifiedResponse[TaskResultResponse]:
    """
    获取处理状态

    Args:
        task_id: 任务ID

    Returns:
        处理状态和结果
    """
    if task_id not in processing_results:
        raise HTTPException(status_code=404, detail="任务ID不存在")

    result = processing_results[task_id]
    return success_response_with_data("查询成功", data=result)

@app.get("/results", response_model=UnifiedResponse[AllTasksResponse])
async def list_all_results() -> UnifiedResponse[AllTasksResponse]:
    """
    获取所有处理结果

    Returns:
        所有任务的处理结果
    """
    all_tasks = AllTasksResponse(
        total_tasks=len(processing_results),
        results=processing_results
    )
    return success_response_with_data("查询成功", data=all_tasks.model_dump())

@app.delete("/results/{task_id}", response_model=UnifiedResponse)
async def delete_result(task_id: str) -> UnifiedResponse:
    """
    删除处理结果

    Args:
        task_id: 任务ID

    Returns:
        删除结果
    """
    if task_id not in processing_results:
        raise HTTPException(status_code=404, detail="任务ID不存在")

    del processing_results[task_id]
    return success_response(message=f"任务 {task_id} 的结果已删除")

@app.post("/process-image-sync", response_model=UnifiedResponse[Dict[str, Any]])
async def process_image_sync(file: UploadFile = File(...)) -> UnifiedResponse[ImageProcessingResult]:
    """
    同步处理图片 - 直接使用graph处理

    Args:
        file: 上传的图片文件

    Returns:
        直接返回处理结果
    """
    try:
        # 验证文件类型
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片格式。支持的格式: {', '.join(SUPPORTED_IMAGE_TYPES)}"
            )

        # 验证文件大小（5MB限制用于同步处理）
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=400,
                detail="同步处理文件大小不能超过5MB，请使用异步接口"
            )

        # 获取文件格式
        file_format = file.filename.split('.')[-1] if file.filename else "jpg"

        # 将图片转换为base64
        image_base64 = get_image_base64(content, file_format)

        # 使用graph处理图片
        result = process_image_with_graph(image_base64)

        if result["success"]:
            response = create_image_processing_response(
                success=True,
                message="图片处理成功",
                analysis_result=result["data"],
                processing_method=ProcessingMethod.GRAPH
            )
            return response
        else:
            # graph处理失败，回退到直接调用
            fallback_result = process_image_base64(image_base64)
            response = create_image_processing_response(
                success=True,
                message="图片处理成功（回退处理）",
                analysis_result=fallback_result,
                processing_method=ProcessingMethod.FALLBACK,
                graph_error=result["error"]
            )
            return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理图片时发生错误: {str(e)}"
        )

if __name__ == "__main__":
    print("启动FastAPI服务器...")
    print("访问 http://localhost:8080/docs 查看API文档")
    print("访问 http://localhost:8080/ 查看API信息")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )