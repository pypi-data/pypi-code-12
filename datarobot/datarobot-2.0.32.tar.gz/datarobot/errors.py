class AppPlatformError(Exception):
    """
    Raised by :meth:`Client.request()` for requests that:
      - Return a non-200 HTTP response, or
      - Connection refused/timeout or
      - Response timeout or
      - Malformed request
      - Have a malformed/missing header in the response.
    """


class InputNotUnderstoodError(Exception):
    """
    Raised if a method is called in a way that cannot be understood
    """


class AllRetriesFailedError(Exception):
    """Raised when the retry manager does not successfully make a request"""


class InvalidModelCategoryError(Exception):
    """
    Raised when method specific for model category was called from wrong model
    """


class AsyncTimeoutError(Exception):
    """
    Raised when an asynchronous operation did not successfully get resolved
    within a specified time limit
    """


class AsyncFailureError(Exception):
    """
    Raised when querying an asynchronous status resulted in an exceptional
    status code (not 200 and not 303)
    """


class AsyncProcessUnsuccessfulError(Exception):
    """
    Raised when querying an asynchronous status showed that async process
    was not successful
    """


class AsyncModelCreationError(Exception):
    """
    Raised when querying an asynchronous status showed that model creation
    was not successful
    """


class AsyncPredictionsGenerationError(Exception):
    """
    Raised when querying an asynchronous status showed that predictions
    generation was not successful
    """


class PendingJobFinished(Exception):
    """
    Raised when the server responds with a 303 for the pending creation of a
    resource.
    """


class JobNotFinished(Exception):
    """
    Raised when execution was trying to get a finished resource from a pending
    job, but the job is not finished
    """


class DuplicateFeaturesError(Exception):
    """
    Raised when trying to create featurelist with duplicating features
    """
