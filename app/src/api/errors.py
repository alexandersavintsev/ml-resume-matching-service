from fastapi import HTTPException, status


def http_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return HTTPException(status_code=status_code, detail=payload)


def bad_request(code: str, message: str, details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_400_BAD_REQUEST, code, message, details)


def unauthorized(message: str = "Unauthorized") -> HTTPException:
    return http_error(status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", message)


def forbidden(message: str = "Forbidden") -> HTTPException:
    return http_error(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message)


def not_found(message: str = "Not found") -> HTTPException:
    return http_error(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message)


def conflict(message: str = "Conflict") -> HTTPException:
    return http_error(status.HTTP_409_CONFLICT, "CONFLICT", message)


def insufficient_balance(current: int, required: int) -> HTTPException:
    return http_error(
        status.HTTP_402_PAYMENT_REQUIRED,
        "INSUFFICIENT_BALANCE",
        "Insufficient balance",
        {"current": current, "required": required},
    )
