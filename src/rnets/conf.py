# -*- coding: utf-8 -*-
from enum import EnumType, Flag, auto
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
from types import UnionType
from functools import reduce


# TODO: maybe extract to some utils?
def error(exception: Exception | None = None) -> NoReturn:
    raise exception or ValueError()


@runtime_checkable
class NamedTupleProtocol(Protocol):
    _fields: list[str]
    _field_defaults: dict[str, Any]


# TODO: overengineering????
class NamedTupleMemberFlag(Flag):
    """Optional means that field can be omitted"""

    OPTIONAL = auto()


class NamedTupleMemberInfo[T](NamedTuple):
    """Metadata about named tuple member"""

    default: T
    check: Callable[[Any], bool] = lambda _: True
    transform: Callable[[Any], T] | None = None
    flags: NamedTupleMemberFlag = NamedTupleMemberFlag(0)


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

    def generator() -> (
        Generator[tuple[str, Any, type, NamedTupleMemberFlag], None, None]
    ):
        for k in named_tuple._fields:
            t = named_tuple.__annotations__.get(k, Any)
            v = None
            flags = NamedTupleMemberFlag(0)
            if k in named_tuple._field_defaults:
                v = named_tuple._field_defaults[k]
                flags |= NamedTupleMemberFlag.OPTIONAL

            yield (k, v, t, flags)

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
                    get_deeply_nested_type(
                        rest.__value__ if isinstance(rest, TypeAliasType) else rest,
                        ignore_type_modifiers=True,
                    )
                    for rest in typing.get_args(t)
                ),
            )

        return object

    def handle_special_types(t: type) -> NamedTupleMemberModifier | None:
        if isinstance(t, EnumType):
            # reveal_type(t) Type of "t" is "type" WHY, PYRIGHT, WHY?
            t = typing.cast(EnumType, t)
            return NamedTupleMemberModifier(
                lambda x: x in t.__members__, t.__members__.get
            )

        return

    def create_member(
        k: str, v: Any, t: type, fl: NamedTupleMemberFlag
    ) -> NamedTupleMemberInfo:
        dt = get_deeply_nested_type(t)
        check = lambda x: isinstance(x, dt)
        transform = None

        if dt in type_modifiers:
            # we cast because somewhy type checkers think about Literals of
            # type TypeAliasType as of type itself, but when it's a free
            # variable it's not
            check, transform = type_modifiers[typing.cast(type, dt)]
        elif not isinstance(dt, (UnionType, type)):
            raise ValueError(
                f"Something gone wrong in deeply nested type search\n"
                f"key: {k}\n"
                f"dt is of type {type(dt)}"
            )
        elif (
            isinstance(dt, type)
            and (special_modifier := handle_special_types(dt)) is not None
        ):
            check, transform = special_modifier

        return NamedTupleMemberInfo(v, check, transform, fl)

    def get_value(
        k: str, v: Any, t: type, fl: NamedTupleMemberFlag
    ) -> NamedTupleMemberInfo | NamedTupleInfo:
        return (
            get_named_tuple_members_mapping(t, type_modifiers=type_modifiers)
            if isinstance(t, NamedTupleProtocol)
            else create_member(k, v, t, fl)
        )

    return NamedTupleInfo(
        named_tuple, {k: get_value(k, v, t, fl) for k, v, t, fl in generator()}
    )


def create_named_tuple_from_mapping(
    info: NamedTupleInfo, d: dict[str, Any]
) -> NamedTupleProtocol:
    for k in d:
        if k not in info.members:
            raise ValueError(
                f"It seems you have supplied key {k}, which can't be found "
                f"in the context of {info.origin.__name__} section"
            )

    def check_and_return[
        T
    ](key: str, value: T | None, info: NamedTupleMemberInfo[T]) -> T:
        if value is None:
            if NamedTupleMemberFlag.OPTIONAL not in info.flags:
                raise ValueError(
                    f"It seems you haven't declared a required value of {key!r}"
                )
            return info.default

        if not info.check(value):
            raise ValueError(
                f"It seems {key} isn't passing check\nGot {value!r} while parsing"
            )

        return info.transform(value) if info.transform is not None else value

    return info.origin(
        **{
            k: create_named_tuple_from_mapping(v, d.get(k, {}))
            if isinstance(v, NamedTupleInfo)
            else check_and_return(k, d.get(k, None), v)
            for k, v in info.members.items()
        }
    )
