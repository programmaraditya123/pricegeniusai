from fastapi import Query


def pagination_params(
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> tuple[int, int]:
    return page, size

