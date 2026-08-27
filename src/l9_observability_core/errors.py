"""Domain exceptions for canonical observability contracts."""


class ObservabilityError(ValueError):
    """Base error for invalid canonical observability data."""


class CanonicalizationError(ObservabilityError):
    """Raised when a value cannot be represented canonically."""


class UnknownSchemaError(ObservabilityError):
    """Raised when an event schema is not registered."""
