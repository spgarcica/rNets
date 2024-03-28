import doctest
import enum
import typing
import unittest
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import NamedTuple

from rnets import conf_type_checker as conf


class ConfTestCase(unittest.TestCase):
    """A test case for conf module"""

    def check_nm_proto(self, t: type) -> None:
        """Checks if a type has attributes of NamedTuple and fails if not"""
        if not isinstance(t, conf.NamedTupleProtocol):
            self.fail(f"Couldn't resolve type {t!r} as a NamedTuple heir")

    def test_builtin_simple(self):
        class Struct(NamedTuple):
            a: int
            b: str
            c: float

        data = {"a": 1, "b": "2", "c": 3.0}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)
        self.assertIsInstance(struct.a, int)
        self.assertIsInstance(struct.b, str)
        self.assertIsInstance(struct.c, float)
        self.assertEqual(struct, Struct(1, "2", 3.0))

    def test_builtin_simple_fail(self):
        class Struct(NamedTuple):
            a: int
            b: str

        data = {"a": 2.0, "b": "1"}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)

    def test_optional_fields(self):
        class Struct(NamedTuple):
            b: str
            a: Sequence[int] = [1, 3, 5, 7]

        data = {"b": "bbbb"}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        self.assertIn(conf.NamedTupleMemberFlag.OPTIONAL, mapping.members["a"])
        self.assertNotIn(conf.NamedTupleMemberFlag.OPTIONAL, mapping.members["b"])
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)
        # it needs to create Struct, because `Struct.a` is a property, not a
        # field, but in a instance it is
        # >>> type(Struct.a)
        # <class 'collections._tuplegetter'>
        # >>> type(Struct("").a)
        # <class 'list'>
        self.assertIs(struct.a, Struct("").a)

    def test_union_fields(self):
        class Struct(NamedTuple):
            a: int | str
            b: Sequence[int] | int

        data1 = {"a": "1", "b": [1, 3, 5]}
        data2 = {"a": 1, "b": 2}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct1 = conf.recreate_named_tuple(mapping, data1)
        struct2 = conf.recreate_named_tuple(mapping, data2)
        self.assertIsInstance(struct1, Struct)
        self.assertIsInstance(struct2, Struct)
        self.assertEqual(struct1, Struct("1", [1, 3, 5]))
        self.assertEqual(struct2, Struct(1, 2))

    def test_nested_nm(self):
        class NestedStruct(NamedTuple):
            a: int
            b: str

        class Struct(NamedTuple):
            a: NestedStruct
            b: str
            c: int

        data = {"a": {"a": 1, "b": "abc"}, "b": "def", "c": 2}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)
        self.assertEqual(struct, Struct(NestedStruct(1, "abc"), "def", 2))

    def test_enum_fields(self):
        class E(Enum):
            b = enum.auto()
            c = enum.auto()

        class Struct(NamedTuple):
            a: E
            b: E

        data = {"a": "c", "b": "b"}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertIs(E.c, struct.a)
        self.assertIs(E.b, struct.b)

    type TestAlias = int

    def test_simple_type_alias(self):
        class Struct(NamedTuple):
            a: ConfTestCase.TestAlias
            b: ConfTestCase.TestAlias

        data = {"a": 1, "b": 2}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct(1, 2))

    def test_simple_type_alias_fail(self):
        class Struct(NamedTuple):
            a: ConfTestCase.TestAlias
            b: ConfTestCase.TestAlias

        data = {"a": 1, "b": "2"}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)

    def test_empty_nested_structs(self):
        class NestedStruct(NamedTuple):
            a: int = 0
            b: str = "abc"

        class Struct(NamedTuple):
            a: NestedStruct = NestedStruct()
            b: float = 3.0

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, {})
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct())

    def test_type_modifiers(self):
        class Struct(NamedTuple):
            a: int = 0
            b: str = "123"

        data = {"a": "456", "b": "123"}
        type_modifiers: conf.TypeModifiersDict = {
            int: conf.NamedTupleMemberModifier(
                lambda x, **kwargs: isinstance(x, str) and x.isnumeric(),
                lambda x, **kwargs: int(x),
            )
        }

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct, type_modifiers=type_modifiers)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct(a=456))

    type TestAlias0 = int
    type TestAlias1 = tuple[int, int]

    def test_type_modifiers_type_alias(self):
        """
        The idea is that type statements create `TypeAliasType` types, which
        means they deviate from doing `TypeAlias: typing.TypeAlias = int`
        >>> d = {int: 1}
        >>> TA: typing.TypeAlias = int
        >>> d.get(TA)
        1
        but if we went with type statements
        >>> type TA = int
        >>> d.get(TA)
        None
        """

        class Struct(NamedTuple):
            a: ConfTestCase.TestAlias0
            b: ConfTestCase.TestAlias1
            c: int

        data = {"a": "1", "b": [2, 3], "c": ["4", "5", "6"]}
        type_modifiers: conf.TypeModifiersDict = {
            ConfTestCase.TestAlias0: conf.NamedTupleMemberModifier(
                lambda x, **kwargs: isinstance(x, str) and x.isnumeric(),
                lambda x, **kwargs: int(x),
            ),
            ConfTestCase.TestAlias1: conf.NamedTupleMemberModifier(
                lambda x, **kwargs: isinstance(x, Sequence)
                and len(x) == 2
                and all(isinstance(i, int) for i in x),
                lambda x, **kwargs: tuple(x),
            ),
            int: conf.NamedTupleMemberModifier(
                lambda x, **kwargs: isinstance(x, Sequence)
                and all(isinstance(i, str) and i.isnumeric() for i in x),
                lambda x, **kwargs: int("".join(x)),
            ),
        }

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct, type_modifiers=type_modifiers)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct(1, (2, 3), 456))

    def test_sequence(self):
        class Struct(NamedTuple):
            a: Sequence[int]

        data = {"a": [1, 3, 5]}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct([1, 3, 5]))

    def test_sequence_fail(self):
        class Struct(NamedTuple):
            a: Sequence[int]

        data = {"a": [1, "2", 3]}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)

    def test_sequence_union(self):
        class Struct(NamedTuple):
            a: Sequence[int | str]

        data = {"a": [1, "3", 5]}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct([1, "3", 5]))

    def test_mapping(self):
        class Struct(NamedTuple):
            a: Mapping[int, str]

        data = {"a": {1: "b", 9: "c"}}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct({1: "b", 9: "c"}))

    def test_mapping_fail(self):
        class Struct(NamedTuple):
            a: Mapping[int, str]

        data = {"a": {"a": 2, 3: 5}}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)

    def test_mapping_union(self):
        class Struct(NamedTuple):
            a: Mapping[int | str, int]

        data = {"a": {"a": 2, 3: 5}}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct({"a": 2, 3: 5}))

    def test_nested_sequence(self):
        class Struct(NamedTuple):
            a: Sequence[Sequence[int]]

        data = {"a": [[1], [2, 3]]}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct([[1], [2, 3]]))

    def test_mapping_sequence(self):
        class Struct(NamedTuple):
            a: Mapping[str, Sequence[Mapping[int, str]]]

        data = {"a": {"b": [{1: "c", 2: "d"}, {3: "e", 4: "f"}]}}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct({"b": [{1: "c", 2: "d"}, {3: "e", 4: "f"}]}))

    def test_tuple(self):
        class Struct(NamedTuple):
            a: tuple[int, str]

        data = {"a": (1, "2")}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct((1, "2")))

    def test_empty_tuple_fail(self):
        class Struct(NamedTuple):
            a: tuple[()]
            b: int

        data = {"a": (1, 2, 3), "b": 4}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)

    def test_tuple_sequence(self):
        class Struct(NamedTuple):
            a: tuple[int, ...]

        data = {"a": (1, 2, 3, 4)}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        struct = conf.recreate_named_tuple(mapping, data)
        self.assertIsInstance(struct, Struct)

        self.assertEqual(struct, Struct((1, 2, 3, 4)))

    def test_tuple_sequence_fail(self):
        class Struct(NamedTuple):
            a: tuple[int, ...]

        data = {"a": (1, 2, 3, "4")}

        self.check_nm_proto(Struct)
        mapping = conf.named_tuple_info(Struct)
        with self.assertRaises(ValueError):
            conf.recreate_named_tuple(mapping, data)


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, ignore: str):
    _ = (loader, ignore)  # discard so linter won't yell
    tests.addTests(doctest.DocTestSuite(conf))
    return tests


if __name__ == "__main__":
    unittest.main()
