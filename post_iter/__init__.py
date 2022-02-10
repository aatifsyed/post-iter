from __future__ import annotations

from dataclasses import dataclass
from functools import reduce, wraps
from itertools import chain, groupby, islice, zip_longest
from typing import (
    TYPE_CHECKING,
    Callable,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparisonT, SupportsRichComparison

from more_itertools import unique_everseen

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


@dataclass
class PostIter(Generic[T], Iterator[T]):
    inner: Iterator[T]

    def __next__(self) -> T:
        return next(self.inner)

    def __iter__(self) -> Iterator[T]:
        return self

    @classmethod
    def from_iterable(cls, i: Iterable[T]) -> PostIter[T]:
        return PostIter(iter(i))

    @classmethod
    def empty(cls) -> PostIter[T]:
        return PostIter(iter(()))

    def all(self, f: Callable[[T], bool] = bool) -> bool:
        return all(f(t) for t in self)

    def any(self, f: Callable[[T], bool] = bool) -> bool:
        return any(f(t) for t in self)

    def chain(self, *i: Iterable[T]) -> PostIter[T]:
        return PostIter(chain(self, *i))

    def zip(self, other: Iterable[U]) -> PostIter[Tuple[T, U]]:
        return PostIter(zip(self, other))

    def zip_longest(
        self, other: Iterable[U], fill: V
    ) -> PostIter[Tuple[T, Union[U, V]]]:
        return PostIter(zip_longest(self, other, fillvalue=fill))

    def map(self, f: Callable[[T], U]) -> PostIter[U]:
        return PostIter(map(f, self))

    def filter(self, f: Callable[[T], bool]) -> PostIter[T]:
        return PostIter(filter(f, self))

    def enumerate(self) -> PostIter[Tuple[int, T]]:
        return PostIter(enumerate(self))

    def skip(self, n: int = 1) -> PostIter[T]:
        try:
            for _ in range(n):
                _ = next(self)
            return self
        except StopIteration:
            return PostIter.empty()

    @overload
    def sorted(
        self: PostIter[SupportsRichComparisonT],
        key: Literal[None] = ...,
        reverse: bool = ...,
    ) -> PostIter[SupportsRichComparisonT]:
        ...

    @overload
    def sorted(
        self: PostIter[T],
        key: Callable[[T], SupportsRichComparison] = ...,
        reverse: bool = ...,
    ) -> PostIter[T]:
        ...

    def sorted(
        self: Union[PostIter[T], PostIter[SupportsRichComparisonT]],
        key: Optional[Callable[[T], SupportsRichComparison]] = None,
        reverse: bool = False,
    ) -> Union[PostIter[T], PostIter[SupportsRichComparisonT]]:
        return PostIter.from_iterable(sorted(self, key=key, reverse=reverse))

    def reversed(self) -> PostIter[T]:
        return PostIter.from_iterable(reversed(list(self)))

    def next(self) -> Optional[T]:
        return next(self, None)

    def reduce(self, f: Callable[[T, T], T]) -> Optional[T]:
        try:
            return reduce(f, self)
        except TypeError:
            return None

    def fold(self, f: Callable[[U, T], U], initial: U) -> U:
        return reduce(f, self, initial)

    def take(self, n: int) -> PostIter[T]:
        return PostIter(islice(self, n))

    def flatten(self: PostIter[Iterable[T]]) -> PostIter[T]:
        return PostIter(chain.from_iterable(self))

    def inspect(self, f: Callable[[T], None]) -> PostIter[T]:
        def _inspect(t: T) -> T:
            f(t)
            return t

        return self.map(_inspect)

    def into(self, t: Callable[[Iterable[T]], U]) -> U:
        return t(self)

    def groupby(self, key: Callable[[T], U]) -> PostIter[Tuple[U, Iterator[T]]]:
        return PostIter(groupby(self, key))

    def unique(self) -> PostIter[T]:
        return PostIter(unique_everseen(self))

    def filter_none(self) -> PostIter[T]:
        return self.filter(lambda t: t is not None)

    def map_safe(self, f: Callable[[T], U]) -> PostIter[U]:
        def _safe() -> Generator[U, None, None]:
            for t in self:
                try:
                    yield f(t)
                except Exception:
                    pass

        return PostIter(_safe())

    def filter_safe(self, f: Callable[[T], bool]) -> PostIter[T]:
        @wraps(f)
        def _safe(t: T) -> bool:
            try:
                return f(t)
            except Exception:
                return False

        return self.filter(_safe)
