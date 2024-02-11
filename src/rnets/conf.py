# -*- coding: utf-8 -*-
from collections.abc import Sequence, Mapping, Callable, Generator
from enum import EnumType, Flag, auto
from types import UnionType
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
import inspect


def _id[T](x: T) -> T:
    return x


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
    transform: Callable[[Any], T] = _id
    flags: NamedTupleMemberFlag = NamedTupleMemberFlag(0)


type NamedTupleMembersMappingValue[T] = NamedTupleMemberInfo[T] | NamedTupleInfo


class NamedTupleInfo[T: type[NamedTupleProtocol]](NamedTuple):
    """Metadata about named tuple itself"""

    origin: T
    members: dict[str, NamedTupleMembersMappingValue]


class NamedTupleMemberModifier[T](NamedTuple):
    """Auxiliary named tuple to hold check and transform functions for type
    modifiers map
    """

    check: Callable[[Any], bool]
    transform: Callable[[Any], T] = _id


type TypeModifiersDict = Mapping[type | TypeAliasType, NamedTupleMemberModifier]


def __singular_modifier[T](
    t: type[T], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    if t in type_modifiers:
        return type_modifiers[t]

    return NamedTupleMemberModifier(lambda x: isinstance(x, t))


def __tuple_modifier[T: tuple](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    ocheck, otransform = resolve_type(origin, type_modifiers=type_modifiers)

    otransform = tuple if otransform is _id else otransform

    def check(x: Any) -> bool:
        return ocheck(x) and all(mod.check(i) for i, mod in zip(x, modifiers))

    def transform(x: Any) -> T:
        return typing.cast(
            T, otransform(mod.transform(i) for i, mod in zip(x, modifiers))
        )

    match args:
        case tuple() if len(args) == 0:
            return NamedTupleMemberModifier(
                check=lambda x: isinstance(x, origin) and len(x) == 0
            )

        case (t, el) if el is ...:
            return __sequence_modifier(origin, (t,), type_modifiers)

        case (*_,):
            modifiers = [resolve_type(at, type_modifiers=type_modifiers) for at in args]
            return NamedTupleMemberModifier(check=check, transform=transform)


def __sequence_modifier[T](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    (arg,) = args
    ocheck, otransform = resolve_type(origin, type_modifiers=type_modifiers)
    acheck, atransform = resolve_type(arg, type_modifiers=type_modifiers)
    otransform = (
        (list if inspect.isabstract(origin) else origin)
        if otransform is _id
        else otransform
    )

    def check(x: Any) -> bool:
        return ocheck(x) and all(acheck(i) for i in x)

    def transform(x: Any) -> T:
        return typing.cast(T, otransform(atransform(i) for i in x))

    return NamedTupleMemberModifier(check, transform)


def __mapping_modifier[T](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    (karg, varg) = args
    ocheck, otransform = resolve_type(origin, type_modifiers=type_modifiers)
    kcheck, ktransform = resolve_type(karg, type_modifiers=type_modifiers)
    vcheck, vtransform = resolve_type(varg, type_modifiers=type_modifiers)

    otransform = (
        (dict if inspect.isabstract(origin) else origin)
        if otransform is _id
        else otransform
    )

    def check(x: Any) -> bool:
        return ocheck(x) and all(kcheck(k) and vcheck(v) for k, v in x.items())

    def transform(x: Any) -> T:
        return typing.cast(
            T, otransform((ktransform(k), vtransform(v)) for k, v in x.items())
        )

    return NamedTupleMemberModifier(check, transform)


def __union_modifier[T](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    _ = origin
    modifiers = [resolve_type(at, type_modifiers=type_modifiers) for at in args]

    def check(x: Any) -> bool:
        return any(check(x) for check, _ in modifiers)

    def transform(x: Any) -> T:
        for check, trans in modifiers:
            if check(x):
                return trans(x)

        raise ValueError("It shouldn't pop, but if pops, then there is a problem")

    return NamedTupleMemberModifier(check, transform)


def resolve_type(
    t: type | TypeAliasType,
    *,
    type_modifiers: TypeModifiersDict,
) -> NamedTupleMemberModifier:
    while True:
        if type_modifiers is not None and t in type_modifiers:
            return type_modifiers[t]

        if not isinstance(t, TypeAliasType):
            break

        t = t.__value__

    if t is Any:
        return NamedTupleMemberModifier(lambda _: True)

    if t is float:
        # sincerely, python typing system is a mess, and in typing world
        # int is a subclass of float, but in real world it's not true, but
        # writing 3 instead of 3.0 is kinda fancy
        return NamedTupleMemberModifier(
            lambda x: isinstance(x, (int, float)), lambda x: float(x)
        )

    if isinstance(t, EnumType):
        return NamedTupleMemberModifier(lambda x: x in t.__members__, t.__members__.get)

    origin = typing.get_origin(t)
    args = typing.get_args(t)

    if origin is None:
        return __singular_modifier(t, type_modifiers)

    f = None

    if issubclass(origin, tuple):
        f = __tuple_modifier

    elif issubclass(origin, Sequence):
        f = __sequence_modifier

    elif issubclass(origin, Mapping):
        f = __mapping_modifier

    elif origin is UnionType or origin is Union:
        f = __union_modifier

    if f is None:
        # warning?
        raise ValueError("CAN'T GET WHAT YOU WANT")

    return f(
        origin,  # type: ignore
        args,
        type_modifiers,
    )


def named_tuple_info[T: type[NamedTupleProtocol]](
    named_tuple: T,
    *,
    type_modifiers: TypeModifiersDict | None = None,
) -> NamedTupleInfo[T]:
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

    def create_member(
        k: str, v: Any, t: type, fl: NamedTupleMemberFlag
    ) -> NamedTupleMemberInfo:
        _ = k
        check, transform = resolve_type(t, type_modifiers=type_modifiers)

        return NamedTupleMemberInfo(v, check, transform, fl)

    def get_value(
        k: str, v: Any, t: type, fl: NamedTupleMemberFlag
    ) -> NamedTupleMemberInfo | NamedTupleInfo:
        return (
            named_tuple_info(t, type_modifiers=type_modifiers)
            if isinstance(t, NamedTupleProtocol)
            else create_member(k, v, t, fl)
        )

    return NamedTupleInfo(
        named_tuple, {k: get_value(k, v, t, fl) for k, v, t, fl in generator()}
    )


def recreate_named_tuple[T: type[NamedTupleProtocol]](
    info: NamedTupleInfo[T], d: Mapping[str, Any]
) -> T:
    for k in d:
        if k not in info.members:
            raise ValueError(
                f"It seems you have supplied key {k}, which can't be found "
                f"in the context of {info.origin.__name__} section"
            )

    def check_and_return[K](
        key: str, value: K | None, info: NamedTupleMemberInfo[K]
    ) -> K:
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
            k: recreate_named_tuple(v, d.get(k, {}))
            if isinstance(v, NamedTupleInfo)
            else check_and_return(k, d.get(k, None), v)
            for k, v in info.members.items()
        }
    )
