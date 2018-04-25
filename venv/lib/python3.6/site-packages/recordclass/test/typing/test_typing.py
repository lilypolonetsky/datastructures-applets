"""Unit tests for recordclass.py."""
import unittest, doctest, operator
from recordclass import recordclass, memoryslots

try:
    from test import support
except:
    from test import test_support as support

import pickle
import typing
from recordclass import RecordClass

class CoolEmployee(RecordClass):
    name: str
    cool: int

class CoolEmployeeWithDefault(RecordClass):
    name: str
    cool: int = 0

class XMeth(RecordClass):
    x: int
    def double(self):
        return 2 * self.x

class XRepr(RecordClass):
    x: int
    y: int = 1
    def __str__(self):
        return f'{self.x} -> {self.y}'
    def __add__(self, other):
        return 0
        
class RecordClassTypingTest(unittest.TestCase):
    def test_typing(self):
        class A(RecordClass):
            a: int
            b: str
            c: typing.List[int]

        tmp = A(a=1, b='1', c=[1, 2, 3])
        self.assertEqual(repr(tmp), "A(a=1, b='1', c=[1, 2, 3])")
        self.assertEqual(tmp._field_types, {'a': int, 'b': str, 'c': typing.List[int]})

    def test_recordclass_basics(self):
        Emp = RecordClass('Emp', [('name', str), ('id', int)])
        #self.assertIsSubclass(Emp, memoryslots)
        joe = Emp('Joe', 42)
        jim = Emp(name='Jim', id=1)
        self.assertIsInstance(joe, Emp)
        self.assertIsInstance(joe, memoryslots)
        self.assertEqual(joe.name, 'Joe')
        self.assertEqual(joe.id, 42)
        self.assertEqual(jim.name, 'Jim')
        self.assertEqual(jim.id, 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp._fields, ('name', 'id'))
        self.assertEqual(Emp.__annotations__,
                         dict([('name', str), ('id', int)]))
        self.assertIs(Emp._field_types, Emp.__annotations__)

    # def test_namedtuple_pyversion(self):
    #     if sys.version_info[:2] < (3, 6):
    #         with self.assertRaises(TypeError):
    #             RecordClass('Name', one=int, other=str)
    #         with self.assertRaises(TypeError):
    #             class NotYet(NamedTuple):
    #                 whatever = 0

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage(self):
        tim = CoolEmployee('Tim', 9000)
        self.assertIsInstance(tim, CoolEmployee)
        self.assertIsInstance(tim, memoryslots)
        self.assertEqual(tim.name, 'Tim')
        self.assertEqual(tim.cool, 9000)
        self.assertEqual(CoolEmployee.__name__, 'CoolEmployee')
        self.assertEqual(CoolEmployee._fields, ('name', 'cool'))
        self.assertEqual(CoolEmployee.__annotations__,
                         dict(name=str, cool=int))
        self.assertIs(CoolEmployee._field_types, CoolEmployee.__annotations__)

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage_with_default(self):
        jelle = CoolEmployeeWithDefault('Jelle')
        self.assertIsInstance(jelle, CoolEmployeeWithDefault)
        self.assertIsInstance(jelle, memoryslots)
        self.assertEqual(jelle.name, 'Jelle')
        self.assertEqual(jelle.cool, 0)
        cooler_employee = CoolEmployeeWithDefault('Sjoerd', 1)
        self.assertEqual(cooler_employee.cool, 1)

        self.assertEqual(CoolEmployeeWithDefault.__name__, 'CoolEmployeeWithDefault')
        self.assertEqual(CoolEmployeeWithDefault._fields, ('name', 'cool'))
        self.assertEqual(CoolEmployeeWithDefault._field_types, dict(name=str, cool=int))
        self.assertEqual(CoolEmployeeWithDefault._field_defaults, dict(cool=0))

        with self.assertRaises(TypeError):
            exec("""
class NonDefaultAfterDefault(RecordClass):
    x: int = 3
    y: int
""")

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage_with_methods(self):
        self.assertEqual(XMeth(1).double(), 2)
        self.assertEqual(XMeth(42).x, XMeth(42)[0])
        self.assertEqual(str(XRepr(42)), '42 -> 1')
        self.assertEqual(XRepr(1, 2) + XRepr(3), 0)

        with self.assertRaises(AttributeError):
            exec("""
class XMethBad(RecordClass):
    x: int
    def _fields(self):
        return 'no chance for this'
""")

        with self.assertRaises(AttributeError):
            exec("""
class XMethBad2(RecordClass):
    x: int
    def _source(self):
        return 'no chance for this as well'
""")

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_recordclass_keyword_usage(self):
        LocalEmployee = RecordClass("LocalEmployee", name=str, age=int)
        nick = LocalEmployee('Nick', 25)
        self.assertIsInstance(nick, memoryslots)
        self.assertEqual(nick.name, 'Nick')
        self.assertEqual(LocalEmployee.__name__, 'LocalEmployee')
        self.assertEqual(LocalEmployee._fields, ('name', 'age'))
        self.assertEqual(LocalEmployee.__annotations__, dict(name=str, age=int))
        self.assertIs(LocalEmployee._field_types, LocalEmployee.__annotations__)
        with self.assertRaises(TypeError):
            RecordClass('Name', [('x', int)], y=str)
        with self.assertRaises(TypeError):
            RecordClass('Name', x=1, y='a')

    def test_pickle(self):
        global Emp  # pickle wants to reference the class by name
        Emp = RecordClass('Emp', [('name', str), ('id', int)])
        jane = Emp('jane', 37)
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RecordClassTypingTest))
    return suite
