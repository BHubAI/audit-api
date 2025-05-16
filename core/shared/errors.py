class ConflictingParametersError(Exception):
    """
    Matches the Http 409 - Conflict.
    By definition the 409 status indicates a request conflict with the target resource.
    It is supposed to be retryable by the request sender.

    Examples:
        - When some process is blocked by the current state of a resource
        - When registering a resource with an existing unique attribute in the db
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail

    def __str__(self):
        return self.detail


class InvalidParametersError(Exception):
    """
    Matches the Http 422 - Unprocessable Entity.
    By definition the 422 status indicates that the server understand the request,
    but it is unable to process it due to invalid data.
    It is supposed to be retryable by the request sender, which can try again.

    Examples:
        - When the server tries to process an uploaded file with absent/invalid data
        - When the user sends an invalid uuid as a parameter
        - When the request contains required values as None
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail

    def __str__(self):
        return self.detail


class ResourceNotFoundError(Exception):
    """
    Matches the Http 404 - Not Found.
    By definition the 404 status indicates the resource requested by the client
    can't be found. It is supposed to be retryable by the request sender.

    Examples:
        - When the user tries to access an invalid/wrong url
        - When the user tries to load an inexistent resource
        - When we are loading related resources (a child) and can't find it,
        when processing something else
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail

    def __str__(self):
        return self.detail
