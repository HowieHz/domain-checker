from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Ok(Generic[T, E]):
    value: T


@dataclass
class Err(Generic[T, E]):
    error: E


Result = Union[Ok[T, E], Err[T, E]]
