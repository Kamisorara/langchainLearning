from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar, Optional, Any, Dict

from pydantic import BaseModel, Field

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

class UnifiedResponse(BaseModel, Generic[T]):
    """统一响应类 - 适用于所有API响应"""
    # 基础字段
    success: bool = Field(description="请求是否成功")
    message: str = Field(description="响应消息")
    code: int = Field(default=200, description="响应代码")

    # 数据字段
    data: Optional[T] = Field(default=None, description="响应数据")

    # 错误字段
    error: Optional[str] = Field(default=None, description="错误信息")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    error_detail: Optional[Dict[str, Any]] = Field(default=None, description="详细错误信息")

    # 元数据字段
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    path: Optional[str] = Field(default=None, description="请求路径")

    # 任务相关字段（用于异步任务）
    task_id: Optional[str] = Field(default=None, description="任务ID")
    task_status: Optional[ProcessingStatus] = Field(default=None, description="任务状态")
    processing_method: Optional[ProcessingMethod] = Field(default=None, description="处理方法")

    # 分页字段（用于列表响应）
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="分页信息")

    # 统计字段
    total: Optional[int] = Field(default=None, description="总数")
    count: Optional[int] = Field(default=None, description="当前页数量")

# 保持向后兼容的别名
BaseResponse = UnifiedResponse

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

# 统一响应创建函数
def create_response(
    success: bool = True,
    message: str = "操作成功",
    data: Any = None,
    code: int = 200,
    error: str = None,
    error_code: str = None,
    error_detail: Dict[str, Any] = None,
    request_id: str = None,
    path: str = None,
    task_id: str = None,
    task_status: ProcessingStatus = None,
    processing_method: ProcessingMethod = None,
    pagination: Dict[str, Any] = None,
    total: int = None,
    count: int = None
) -> UnifiedResponse:
    """创建统一响应"""
    return UnifiedResponse(
        success=success,
        message=message,
        code=code,
        data=data,
        error=error,
        error_code=error_code,
        error_detail=error_detail,
        request_id=request_id,
        path=path,
        task_id=task_id,
        task_status=task_status,
        processing_method=processing_method,
        pagination=pagination,
        total=total,
        count=count
    )

# 预定义的成功响应
def success_response(message: str = "操作成功", data: Any = None, **kwargs) -> UnifiedResponse:
    """创建成功响应"""
    return create_response(success=True, message=message, data=data, **kwargs)

def success_response_with_data(message: str = "操作成功", data: Any = None, **kwargs) -> UnifiedResponse:
    """创建带数据的成功响应"""
    return create_response(success=True, message=message, data=data, **kwargs)

# 预定义的错误响应
def error_response(message: str = "操作失败", error: str = None, code: int = 400, **kwargs) -> UnifiedResponse:
    """创建错误响应"""
    return create_response(
        success=False,
        message=message,
        error=error,
        code=code,
        **kwargs
    )

def error_response_with_data(
    message: str = "操作失败",
    error: str = None,
    data: Any = None,
    code: int = 400,
    **kwargs
) -> UnifiedResponse:
    """创建带数据的错误响应"""
    return create_response(
        success=False,
        message=message,
        error=error,
        data=data,
        code=code,
        **kwargs
    )

# 任务相关响应
def task_response(task_id: str, status: ProcessingStatus, message: str, **kwargs) -> UnifiedResponse:
    """创建任务响应"""
    return create_response(
        success=True,
        message=message,
        task_id=task_id,
        task_status=status,
        data={"task_id": task_id, "status": status.value, "message": message},
        **kwargs
    )

def task_result_response(
    task_id: str,
    status: ProcessingStatus,
    message: str,
    result: Any = None,
    error: str = None,
    processing_method: ProcessingMethod = None,
    **kwargs
) -> UnifiedResponse:
    """创建任务结果响应"""
    return create_response(
        success=(status == ProcessingStatus.COMPLETED),
        message=message,
        task_id=task_id,
        task_status=status,
        processing_method=processing_method,
        data=result,
        error=error,
        **kwargs
    )

# 图片处理响应
def create_image_processing_response(
    success: bool,
    message: str,
    analysis_result: str = None,
    processing_method: ProcessingMethod = None,
    error: str = None,
    graph_error: str = None,
    processing_time: float = None,
    image_info: Dict[str, Any] = None,
    **kwargs
) -> UnifiedResponse:
    """创建图片处理响应"""
    data = None
    if success and analysis_result:
        data = ImageProcessingResult(
            analysis_result=analysis_result,
            processing_time=processing_time,
            image_info=image_info
        ).dict()

        # 添加处理元数据
        if processing_method or graph_error:
            data["processing_metadata"] = {
                "processing_method": processing_method.value if processing_method else None,
                "graph_error": graph_error
            }

    return create_response(
        success=success,
        message=message,
        data=data,
        error=error,
        processing_method=processing_method,
        **kwargs
    )

# 向后兼容的便捷函数（保留原有API）
def create_task_response(task_id: str, status: ProcessingStatus, message: str) -> UnifiedResponse:
    """创建任务响应（向后兼容）"""
    return task_response(task_id, status, message)

def create_task_result_response(
    task_id: str,
    status: ProcessingStatus,
    message: str,
    result: Any = None,
    error: str = None,
    processing_method: ProcessingMethod = None,
    graph_error: str = None
) -> UnifiedResponse:
    """创建任务结果响应（向后兼容）"""
    # 构建错误详情
    error_detail = None
    if graph_error:
        error_detail = {"graph_error": graph_error}

    return task_result_response(
        task_id=task_id,
        status=status,
        message=message,
        result=result,
        error=error,
        processing_method=processing_method,
        error_detail=error_detail
    )