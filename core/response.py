from typing import Any, Optional, Union, Dict, List
from robyn import Response, status_codes
import json

class ApiResponse:
    """统一的API响应处理类"""
    
    @staticmethod
    def success(
        data: Optional[Union[Dict, List, str, int, float]] = None,
        message: str = "success",
        status_code: int = status_codes.HTTP_200_OK
    ) -> Response:
        """
        成功响应
        :param data: 响应数据
        :param message: 响应消息
        :param status_code: HTTP状态码
        :return: Response对象
        """
        response_data = {
            "code": status_code,
            "message": message,
            "data": data
        }
        return Response(
            description=json.dumps(response_data, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            status_code=status_code
        )
    
    @staticmethod
    def error(
        message: str = "error",
        status_code: int = status_codes.HTTP_400_BAD_REQUEST,
        data: Optional[Any] = None
    ) -> Response:
        """
        错误响应
        :param message: 错误消息
        :param status_code: HTTP状态码
        :param data: 额外的错误数据
        :return: Response对象
        """
        response_data = {
            "code": status_code,
            "message": message,
            "data": data
        }
        return Response(
            description=json.dumps(response_data, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            status_code=status_code
        )
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        """
        资源未找到响应
        :param message: 错误消息
        :return: Response对象
        """
        return ApiResponse.error(message, status_codes.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def validation_error(message: str = "Validation error", errors: Optional[Dict] = None) -> Response:
        """
        验证错误响应
        :param message: 错误消息
        :param errors: 具体的验证错误信息
        :return: Response对象
        """
        return ApiResponse.error(message, status_codes.HTTP_422_UNPROCESSABLE_ENTITY, errors)
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> Response:
        """
        未授权响应
        :param message: 错误消息
        :return: Response对象
        """
        return ApiResponse.error(message, status_codes.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message: str = "Forbidden") -> Response:
        """
        禁止访问响应
        :param message: 错误消息
        :return: Response对象
        """
        return ApiResponse.error(message, status_codes.HTTP_403_FORBIDDEN)
