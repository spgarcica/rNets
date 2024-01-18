# -*- coding: utf-8 -*-
import typing
from typing import (
    Any,
    NamedTuple,
    NoReturn,
    Protocol,
    TypeAliasType,
    Union,
    runtime_checkable,
)
from collections.abc import Sequence, Mapping, Callable, Generator
from types import NoneType, UnionType
from functools import reduce


# TODO: maybe extract to some utils?
def error(exception: Exception | None = None) -> NoReturn:
    raise exception or ValueError()


@runtime_checkable
class NamedTupleProtocol(Protocol):
    _fields: list[str]
    _field_defaults: dict[str, Any]


class NamedTupleMemberInfo[T](NamedTuple):
    """Metadata about named tuple member"""

    default: T
    check: Callable[[Any], bool] = lambda _: True
    transform: Callable[[Any], T] | None = None


type NamedTupleMembersMappingValue[T] = NamedTupleMemberInfo[T] | NamedTupleInfo


class NamedTupleInfo(NamedTuple):
    """Metadata about named tuple itself"""

    origin: type[NamedTupleProtocol]
    members: dict[str, NamedTupleMembersMappingValue]


class NamedTupleMemberModifier[T](NamedTuple):
    """Auxiliary named tuple to hold check and transform functions for type
    modifiers map
    """

    check: Callable[[Any], bool]
    transform: Callable[[Any], T]


def get_named_tuple_members_mapping(
    named_tuple: type[NamedTupleProtocol],
    *,
    type_modifiers: Mapping[type, NamedTupleMemberModifier] | None = None,
) -> NamedTupleInfo:
    if type_modifiers is None:
        type_modifiers = {}

    def generator() -> Generator[tuple[str, Any, type], None, None]:
        for k in named_tuple._fields:
            t = named_tuple.__annotations__.get(k, Any)
            v: Any = named_tuple._field_defaults.get(k)
            if (
                v is None
                # we do this because int | bool is not the same as Union[int, bool]
                and not typing.get_origin(t) is UnionType
                and not typing.get_origin(t) is Union
                and not NoneType in typing.get_args(t)
            ):
                # TODO: maybe there is a better solution to this?
                try:
                    v = typing.get_origin(t)()
                except Exception:
                    pass
            yield (k, v, t)

    def get_deeply_nested_type(
        t: type, *, ignore_type_modifiers: bool = False
    ) -> UnionType | type:
        while True:
            if not ignore_type_modifiers and t in type_modifiers:
                return t

            if isinstance(t, TypeAliasType):
                t = t.__value__
            else:
                break

        origin = typing.get_origin(t)

        if origin is None:
            return t

        if not ignore_type_modifiers and origin in type_modifiers:
            return origin

        if issubclass(origin, (Mapping, Sequence)):
            return origin

        if origin is UnionType or origin is Union:

            def reduce_fn(x: type | UnionType, y: type | UnionType) -> UnionType:
                return x | y

            return reduce(
                reduce_fn,
                (
                    get_deeply_nested_type(rest.__value__, ignore_type_modifiers=True)
                    if isinstance(rest, TypeAliasType)
                    else rest
                    for rest in typing.get_args(t)
                ),
            )

        return object

    def create_member(k: str, v: Any, t: type) -> NamedTupleMemberInfo:
        dt = get_deeply_nested_type(t)

        if dt in type_modifiers:
            # we cast because somewhy type checkers think about Literals of
            # type TypeAliasType as of type itself, but when it's a free
            # variable it's not
            check, transform = type_modifiers[typing.cast(type, dt)]
            return NamedTupleMemberInfo(v, check, transform)

        if not isinstance(dt, (UnionType, type)):
            raise ValueError(
                f"Something gone wrong in deeply nested type search\nkey: {k}\ndt is of type {type(dt)}"
            )

        return NamedTupleMemberInfo(v, lambda x: isinstance(x, dt))

    def get_value(k: str, v: Any, t: type) -> NamedTupleMemberInfo | NamedTupleInfo:
        return (
            get_named_tuple_members_mapping(t, type_modifiers=type_modifiers)
            if isinstance(t, NamedTupleProtocol)
            else create_member(k, v, t)
        )

    return NamedTupleInfo(
        named_tuple, {k: get_value(k, v, t) for k, v, t in generator()}
    )


def create_named_tuple_from_mapping(
    info: NamedTupleInfo, d: dict[Any, Any]
) -> NamedTupleProtocol:
    if not all(k in info.members for k in d):
        error()

    def check_and_return[T](value: T | None, info: NamedTupleMemberInfo[T]) -> T:
        if value is not None and not info.check(value):
            print(value)
            print(info)
            error()

        res = value or info.default
        if info.transform is not None:
            res = info.transform(res)

        return typing.cast(T, res)

    return info.origin(
        **{
            k: create_named_tuple_from_mapping(v, d[k])
            if isinstance(v, NamedTupleInfo)
            else check_and_return(d.get(k, None), v)
            for k, v in info.members.items()
        }
    )
