class OsuApiError(Exception):
    """Base exception for osu! API errors"""
    pass


class RateLimitExceeded(OsuApiError):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationError(OsuApiError):
    """Raised when authentication fails"""
    pass


class NotFound(OsuApiError):
    """Raised when resource is not found"""
    pass


def handle_api_error(response_status: int, message: str = None):
    error_map = {
        401: AuthenticationError("Authentication failed"),
        404: NotFound("Resource not found"),
        429: RateLimitExceeded("Rate limit exceeded"),
    }

    if response_status in error_map:
        raise error_map[response_status]
    elif response_status >= 400:
        raise OsuApiError(f"API error: {message or 'Unknown error'}")