# -*- coding: utf-8 -*-
import inspect
import typing
from collections.abc import Callable, Generator, Mapping, Sequence
from enum import EnumType, Flag, auto
from types import UnionType
from typing import (
    Any,
    NamedTuple,
    NotRequired,
    TypeGuard,
    Protocol,
    Self,
    TypeAliasType,
    TypedDict,
    Union,
    Unpack,
    runtime_checkable,
)


def _id[T](x: T, **kwargs) -> T:
    _ = kwargs
    return x


@runtime_checkable
class NamedTupleProtocol(Protocol):
    _fields: tuple[str, ...]
    _field_defaults: dict[str, Any]


# TODO: overengineering????
class NamedTupleMemberFlag(Flag):
    """Some additional metadata, that is neatly packed in flag enum"""

    OPTIONAL = auto()


class NamedTupleMemberModifierKwargs[T](TypedDict):
    key: NotRequired[str]
    default: NotRequired[T]


# TODO: change it to callable, to accept different names
# Here we use protocols to make use of Unpack[TypedDict],
# even if mypy supports it in Callable, pyright doesn't
class NamedTupleMemberModifierCheckCallback[T](Protocol):
    def __call__(
        self: Self, x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs[T]]
    ) -> bool: ...


# see NamedTupleMemberModifierCheckCallback
class NamedTupleMemberModifierTransformCallback[T](Protocol):
    def __call__(
        self: Self, x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs[T]]
    ) -> T: ...


class NamedTupleMemberInfo[T](NamedTuple):
    """Metadata about named tuple member"""

    default: T
    check: NamedTupleMemberModifierCheckCallback[T] = lambda x, **kwargs: True
    transform: NamedTupleMemberModifierTransformCallback[T] = _id
    flags: NamedTupleMemberFlag = NamedTupleMemberFlag(0)


type NamedTupleMembersMappingValue[T] = NamedTupleMemberInfo[T] | NamedTupleInfo


class NamedTupleInfo[T: NamedTupleProtocol](NamedTuple):
    """Metadata about named tuple itself"""

    origin: type[T]
    members: dict[str, NamedTupleMembersMappingValue]


class NamedTupleMemberModifier[T](NamedTuple):
    """Auxiliary named tuple to hold check and transform functions for type
    modifiers map
    """

    check: NamedTupleMemberModifierCheckCallback[T]
    transform: NamedTupleMemberModifierTransformCallback[T] = _id


type TypeModifiersDict = Mapping[
    type | TypeAliasType | UnionType, NamedTupleMemberModifier
]


def __singular_modifier[T](
    t: type[T], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    if t in type_modifiers:
        return type_modifiers[t]

    return NamedTupleMemberModifier(lambda x, **kwargs: isinstance(x, t))


def __tuple_modifier[T: tuple](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    ocheck, otransform = resolve_type(origin, type_modifiers=type_modifiers)

    if otransform is _id:
        otransform = lambda x, **kwargs: tuple(x)

    def check(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> bool:
        return ocheck(x, **kwargs) and all(mod.check(i) for i, mod in zip(x, modifiers))

    def transform(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> T:
        return typing.cast(
            T, otransform((mod.transform(i) for i, mod in zip(x, modifiers)), **kwargs)
        )

    match args:
        case tuple() if len(args) == 0:
            return NamedTupleMemberModifier(
                check=lambda x, **kwargs: isinstance(x, origin) and len(x) == 0
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
    if otransform is _id:
        output_origin = list if inspect.isabstract(origin) else origin
        otransform = lambda x, **kwargs: output_origin(x)

    def check(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> bool:
        return ocheck(x) and all(acheck(i) for i in x)

    def transform(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> T:
        return typing.cast(T, otransform(atransform(i) for i in x))

    return NamedTupleMemberModifier(check, transform)


def __mapping_modifier[T](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    (karg, varg) = args
    ocheck, otransform = resolve_type(origin, type_modifiers=type_modifiers)
    kcheck, ktransform = resolve_type(karg, type_modifiers=type_modifiers)
    vcheck, vtransform = resolve_type(varg, type_modifiers=type_modifiers)

    if otransform is _id:
        output_origin = dict if inspect.isabstract(origin) else origin
        otransform = lambda x, **kwargs: output_origin(x)

    def check(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> bool:
        return ocheck(x, **kwargs) and all(
            kcheck(k) and vcheck(v) for k, v in x.items()
        )

    def transform(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> T:
        return typing.cast(
            T,
            otransform(
                ((ktransform(k), vtransform(v)) for k, v in x.items()), **kwargs
            ),
        )

    return NamedTupleMemberModifier(check, transform)


def __union_modifier[T](
    origin: type[T], args: tuple[type, ...], type_modifiers: TypeModifiersDict
) -> NamedTupleMemberModifier[T]:
    _ = origin
    modifiers = [resolve_type(at, type_modifiers=type_modifiers) for at in args]

    def check(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> bool:
        return any(check(x, **kwargs) for check, _ in modifiers)

    def transform(x: Any, **kwargs: Unpack[NamedTupleMemberModifierKwargs]) -> T:
        for check, trans in modifiers:
            if check(x, **kwargs):
                return trans(x, **kwargs)

        raise ValueError("It shouldn't pop, but if pops, then there is a problem")

    return NamedTupleMemberModifier(check, transform)


class TypeNotSupportedError(Exception):
    def __init__(
        self: Self, t: type | TypeAliasType | UnionType, msg: str | None = None
    ) -> None:
        self.t, self.msg = t, msg or f"Type {t!r} is not supported"

    def __str__(self) -> str:
        return self.msg


def resolve_type(
    t: type | TypeAliasType | UnionType,
    *,
    type_modifiers: TypeModifiersDict,
) -> NamedTupleMemberModifier:
    """Returns a member modifier for a given type"""
    ogt = t
    while True:
        if type_modifiers is not None and t in type_modifiers:
            return type_modifiers[t]

        if not isinstance(t, TypeAliasType):
            break

        t = t.__value__

    if t is Any:
        return NamedTupleMemberModifier(lambda x, **kwargs: True)

    if t is float:
        # sincerely, python typing system is a mess, and in typing world
        # int is a subclass of float, but in real world it's not true, but
        # writing 3 instead of 3.0 is kinda fancy
        return NamedTupleMemberModifier(
            lambda x, **kwargs: isinstance(x, (int, float)),
            lambda x, **kwargs: float(x),
        )

    if isinstance(t, EnumType):
        return NamedTupleMemberModifier(
            lambda x, **kwargs: x in t.__members__,
            lambda x, **kwargs: t.__members__.get(x),
        )

    origin = typing.get_origin(t)
    args = typing.get_args(t)

    if origin is None:
        assert not isinstance(t, UnionType)
        if is_named_tuple_type(t):
            info = named_tuple_info(t, type_modifiers=type_modifiers)
            return NamedTupleMemberModifier(
                lambda x, **kwargs: isinstance(x, Mapping),
                lambda x, **kwargs: recreate_named_tuple(info, x),
            )

        return __singular_modifier(t, type_modifiers)

    f = None

    if issubclass(origin, tuple):
        f = __tuple_modifier

    elif issubclass(origin, Sequence):
        f = __sequence_modifier

    elif issubclass(origin, Mapping):
        f = __mapping_modifier

    if origin is UnionType or origin is Union:
        f = __union_modifier

    if f is None:
        raise TypeNotSupportedError(ogt)

    return f(
        origin,  # type: ignore
        args,
        type_modifiers,
    )


def is_named_tuple_type(t: type) -> TypeGuard[type[NamedTupleProtocol]]:
    if isinstance(t, NamedTupleProtocol):
        return True

    return False


def named_tuple_info[T: NamedTupleProtocol](
    named_tuple: type[T],
    *,
    type_modifiers: TypeModifiersDict | None = None,
) -> NamedTupleInfo[T]:
    """Returns metadata about named tuple"""
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
            if (t not in type_modifiers and is_named_tuple_type(t))
            else create_member(k, v, t, fl)
        )

    return NamedTupleInfo(
        named_tuple, {k: get_value(k, v, t, fl) for k, v, t, fl in generator()}
    )


class RedundantFieldError(Exception):
    def __init__(
        self: Self, nm: type[NamedTupleProtocol], key: str, msg: str | None = None
    ) -> None:
        self.nm, self.key, self.msg = (
            nm,
            key,
            msg
            or (
                f"It seems you have supplied field {key}, which can't be found "
                f"in the context of {nm.__name__} section"
            ),
        )

    def __str__(self: Self) -> str:
        return self.msg


class EmptyFieldError(Exception):
    def __init__(self: Self, key: str, msg: str | None = None) -> None:
        self.key, self.msg = (
            key,
            msg or (f"It seems you haven't declared a required value of {key!r}"),
        )

    def __str__(self: Self) -> str:
        return self.msg


def recreate_named_tuple[T: NamedTupleProtocol](
    info: NamedTupleInfo[T], d: Mapping[str, Any]
) -> T:
    """From a given metadata and data recreate a NamedTuple"""
    for k in d:
        if k not in info.members:
            raise RedundantFieldError(info.origin, k)

    def check_and_return[K](
        key: str, value: K | None, info: NamedTupleMemberInfo[K]
    ) -> K:
        if value is None:
            if NamedTupleMemberFlag.OPTIONAL not in info.flags:
                raise EmptyFieldError(key)
            return info.default

        kwargs = {
            "key": key,
            "default": info.default,
        }
        if not info.check(value, **kwargs):
            raise ValueError(
                f"It seems {key} isn't passing check\nGot {value!r} while parsing"
            )

        if info.transform is None:
            return value

        return info.transform(value, **kwargs)

    return info.origin(
        **{
            k: recreate_named_tuple(v, d.get(k, {}))
            if isinstance(v, NamedTupleInfo)
            else check_and_return(k, d.get(k, None), v)
            for k, v in info.members.items()
        }
    )
