from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class NotFoundException(AppException):
    def __init__(self, entity: str):
        super().__init__(
            code=f"{entity.upper()}_NOT_FOUND",
            message=f"{entity} not found",
            status_code=404,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ConflictException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=400)


class FileValidationException(AppException):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=400)


class QuotaExceededException(AppException):
    def __init__(self, message: str):
        super().__init__(code="PROJECT_STORAGE_LIMIT", message=message, status_code=400)


class StorageException(AppException):
    def __init__(self, message: str):
        super().__init__(code="STORAGE_ERROR", message=message, status_code=500)
