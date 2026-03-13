from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Raised when authentication fails (invalid/expired token)."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(HTTPException):
    """Raised when a token is malformed or has an invalid signature."""

    def __init__(self, detail: str = "Invalid token") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ExpiredTokenError(HTTPException):
    """Raised when a token has expired."""

    def __init__(self, detail: str = "Token has expired") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundError(HTTPException):
    """Raised when a user profile cannot be found in the database."""

    def __init__(self, detail: str = "User not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class UserAlreadyExistsError(HTTPException):
    """Raised when attempting to register with an already used email."""

    def __init__(self, detail: str = "A user with this email already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InvalidCredentialsError(HTTPException):
    """Raised when login credentials are wrong."""

    def __init__(self, detail: str = "Invalid email or password") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):
    """Raised when an inactive user attempts to authenticate."""

    def __init__(self, detail: str = "User account is inactive") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class RegistrationError(HTTPException):
    """Raised when registration fails for an unspecified reason."""

    def __init__(self, detail: str = "Registration failed") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class DatabaseError(HTTPException):
    """Raised when an unexpected database error occurs."""

    def __init__(self, detail: str = "A database error occurred") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ExternalServiceError(HTTPException):
    """Raised when an external service (Supabase, etc.) returns an error."""

    def __init__(self, detail: str = "External service error") -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class RefreshTokenError(HTTPException):
    """Raised when a refresh token is invalid, expired, or not found in Redis."""

    def __init__(self, detail: str = "Invalid or expired refresh token") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(HTTPException):
    """Raised when a user does not have permission to perform an action."""

    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundError(HTTPException):
    """Raised when a requested resource cannot be found."""

    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
