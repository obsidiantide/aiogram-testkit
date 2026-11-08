from collections import deque
from typing import Any, AsyncGenerator, Deque, Dict, List, Optional, Type, TypeVar


from aiogram.client.bot import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType

T = TypeVar("T", bound=TelegramMethod[Any])


class MockedSession(BaseSession):
    """
    A mocked session for testing aiogram bots without making real network requests.
    Records all outgoing requests and allows mocking responses.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests: List[TelegramMethod[Any]] = []
        self.responses: Dict[str, Any] = {}
        self._queues: Dict[str, Deque[Any]] = {}

    def add_result(self, method_name: str, result: Any) -> None:
        """
        Mock the result for a specific API method (e.g. 'SendMessage').

        ``result`` may be:

        * a plain value, returned as is on every call;
        * an exception instance, raised on every call (useful for simulating
          Telegram API errors such as ``TelegramForbiddenError``);
        * a callable, invoked with the recorded method; its return value is
          used as the result, which allows building responses from the request.
        """
        self._queues.pop(method_name, None)
        self.responses[method_name] = result

    def add_results(self, method_name: str, *results: Any) -> None:
        """
        Queue several results for a method: the first call gets the first
        result, the second call the second one, and so on. Once only one result
        is left it is returned on every further call.

        Each item follows the same rules as in :meth:`add_result` (plain value,
        exception instance or callable).
        """
        if not results:
            raise ValueError("add_results() requires at least one result")
        self.responses.pop(method_name, None)
        self._queues[method_name] = deque(results)

    def get_request(self, method_type: Type[T]) -> Optional[T]:
        """
        Returns the first recorded request matching the specified TelegramMethod type.
        """
        for req in self.requests:
            if isinstance(req, method_type):
                return req
        return None

    def find_requests(self, method_type: Type[T]) -> List[T]:
        """
        Returns all recorded requests matching the specified TelegramMethod type.
        """
        return [req for req in self.requests if isinstance(req, method_type)]

    def has_request(self, method_type: Type[TelegramMethod[Any]]) -> bool:
        """
        Checks whether any request of the specified TelegramMethod type was made.
        """
        return any(isinstance(req, method_type) for req in self.requests)

    def count_requests(self, method_type: Optional[Type[TelegramMethod[Any]]] = None) -> int:
        """
        Returns the number of recorded requests, optionally filtered by method type.
        """
        if method_type is None:
            return len(self.requests)
        return sum(1 for req in self.requests if isinstance(req, method_type))

    @property
    def last_request(self) -> Optional[TelegramMethod[Any]]:
        """
        Returns the last recorded request or None if no requests have been made.
        """
        return self.requests[-1] if self.requests else None

    def reset(self) -> None:
        """
        Resets recorded requests and mocked responses.
        """
        self.requests.clear()
        self.responses.clear()
        self._queues.clear()

    async def close(self) -> None:
        pass

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = None,
    ) -> TelegramType:
        """
        Intercepts the request, records it, and returns the mocked response if available.
        """
        self.requests.append(method)
        method_name = type(method).__name__

        if method_name in self._queues:
            queue = self._queues[method_name]
            result = queue[0] if len(queue) == 1 else queue.popleft()
        elif method_name in self.responses:
            result = self.responses[method_name]
        else:
            return None

        if isinstance(result, BaseException):
            raise result
        if callable(result):
            return result(method)
        return result

    async def stream_content(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        yield b""
