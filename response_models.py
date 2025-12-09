from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# 定义泛型类型变量
T = TypeVar('T')

class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingMethod(str, Enum):
    """处理方法枚举"""
    GRAPH = "graph"
    FALLBACK = "fallback"
    DIRECT = "direct"
    FAILED = "failed"

class BaseResponse(BaseModel, Generic[T]):
    """基础响应类"""
    success: bool = Field(description="请求是否成功")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str = Field(description="任务ID")
    status: ProcessingStatus = Field(description="任务状态")
    message: str = Field(description="任务消息")

class TaskResultResponse(BaseModel):
    """任务结果响应"""
    task_id: str = Field(description="任务ID")
    status: ProcessingStatus = Field(description="任务状态")
    message: str = Field(description="任务消息")
    result: Optional[Any] = Field(default=None, description="处理结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    processing_method: Optional[ProcessingMethod] = Field(default=None, description="处理方法")
    graph_error: Optional[str] = Field(default=None, description="Graph处理错误（如果使用回退方式）")

class ImageProcessingResult(BaseModel):
    """图片处理结果"""
    analysis_result: str = Field(description="AI分析结果")
    processing_time: Optional[float] = Field(default=None, description="处理时间（秒）")
    image_info: Optional[Dict[str, Any]] = Field(default=None, description="图片信息")

class AllTasksResponse(BaseModel):
    """所有任务响应"""
    total_tasks: int = Field(description="总任务数")
    results: Dict[str, TaskResultResponse] = Field(description="所有任务结果")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="API版本")
    uptime: Optional[str] = Field(default=None, description="运行时间")

class APIInfoResponse(BaseModel):
    """API信息响应"""
    message: str = Field(description="API描述")
    version: str = Field(description="API版本")
    endpoints: Dict[str, str] = Field(description="可用端点")

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str = Field(description="错误详情")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    path: Optional[str] = Field(default=None, description="请求路径")

# 预定义的成功响应
def success_response(message: str = "操作成功", data: Any = None) -> BaseResponse:
    """创建成功响应"""
    return BaseResponse(
        success=True,
        message=message,
        data=data
    )

def success_response_with_data(message: str = "操作成功", data: Any = None) -> BaseResponse:
    """创建带数据的成功响应"""
    return BaseResponse(
        success=True,
        message=message,
        data=data
    )

# 预定义的错误响应
def error_response(message: str = "操作失败", error: str = None) -> BaseResponse:
    """创建错误响应"""
    return BaseResponse(
        success=False,
        message=message,
        error=error
    )

def error_response_with_data(message: str = "操作失败", error: str = None, data: Any = None) -> BaseResponse:
    """创建带数据的错误响应"""
    return BaseResponse(
        success=False,
        message=message,
        error=error,
        data=data
    )

# 便捷的任务响应创建函数
def create_task_response(task_id: str, status: ProcessingStatus, message: str) -> TaskResponse:
    """创建任务响应"""
    return TaskResponse(
        task_id=task_id,
        status=status,
        message=message
    )

def create_task_result_response(
    task_id: str,
    status: ProcessingStatus,
    message: str,
    result: Any = None,
    error: str = None,
    processing_method: ProcessingMethod = None,
    graph_error: str = None
) -> TaskResultResponse:
    """创建任务结果响应"""
    return TaskResultResponse(
        task_id=task_id,
        status=status,
        message=message,
        result=result,
        error=error,
        processing_method=processing_method,
        graph_error=graph_error
    )

def create_image_processing_response(
    success: bool,
    message: str,
    analysis_result: str = None,
    processing_method: ProcessingMethod = None,
    error: str = None,
    graph_error: str = None
) -> BaseResponse[ImageProcessingResult]:
    """创建图片处理响应"""
    data = None
    if success and analysis_result:
        data = ImageProcessingResult(
            analysis_result=analysis_result
        )

    response_data = None
    if data:
        # 为ImageProcessingResult添加额外的元数据
        response_data = {
            **data.dict(),
            "processing_method": processing_method.value if processing_method else None,
            "graph_error": graph_error
        }

    return BaseResponse(
        success=success,
        message=message,
        data=response_data,
        error=error
    )