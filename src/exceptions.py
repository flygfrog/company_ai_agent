class AppException(Exception):
    """项目业务异常基类。"""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class LLMServiceError(AppException):
    """大模型服务调用异常。"""

    def __init__(self, message: str = "大模型服务暂时不可用"):
        super().__init__(
            message=message,
            status_code=502,
            error_code="LLM_SERVICE_ERROR",
        )