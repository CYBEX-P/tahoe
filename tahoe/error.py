class DependencyError(Exception):
    """Raised when deleteing an attribute referred by others."""

class BackendError(Exception):
    """Raised when Backend is unreachable or wrongly configured"""
