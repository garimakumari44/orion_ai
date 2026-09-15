from __future__ import annotations


class CompanyError(Exception):
    """
    Base exception for all company-related errors.
    """

    def __init__(self, message: str = "Company operation failed") -> None:
        super().__init__(message)


class CompanyNotFoundError(CompanyError):
    """
    Raised when a company cannot be found.
    """

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Company '{identifier}' was not found.")


class CompanyAlreadyExistsError(CompanyError):
    """
    Raised when attempting to create a company that already exists.
    """

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Company '{identifier}' already exists.")


class InvalidCompanyError(CompanyError):
    """
    Raised when company data fails validation.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid company data: {reason}")


class ProviderUnavailableError(CompanyError):
    """
    Raised when an external provider is unavailable.
    """

    def __init__(self, provider: str) -> None:
        super().__init__(f"Provider '{provider}' is currently unavailable.")


class CompanySearchError(CompanyError):
    """
    Raised when a company search fails.
    """

    def __init__(self, query: str) -> None:
        super().__init__(f"Failed to search for company '{query}'.")


class CompanySyncError(CompanyError):
    """
    Raised when synchronization fails.
    """

    def __init__(self, company: str) -> None:
        super().__init__(f"Failed to synchronize company '{company}'.")


class CompanyCacheError(CompanyError):
    """
    Raised when cache operations fail.
    """

    def __init__(self, operation: str) -> None:
        super().__init__(f"Cache operation failed: {operation}")


class CompanyRepositoryError(CompanyError):
    """
    Raised when repository operations fail.
    """

    def __init__(self, operation: str) -> None:
        super().__init__(f"Repository operation failed: {operation}")


class CompanyNormalizationError(CompanyError):
    """
    Raised when normalization fails.
    """

    def __init__(self, provider: str) -> None:
        super().__init__(
            f"Failed to normalize company data from provider '{provider}'."
        )


class CompanyValidationError(CompanyError):
    """
    Raised when validation fails.
    """

    def __init__(self, field: str) -> None:
        super().__init__(f"Validation failed for field '{field}'.")