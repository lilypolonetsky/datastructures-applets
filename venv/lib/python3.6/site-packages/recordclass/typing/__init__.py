from recordclass.record import recordclass
from typing import _type_check

import sys as _sys

_prohibited = ('__new__', '__init__', '__slots__', '__getnewargs__',
               '_fields', '_field_defaults', '_field_types',
               '_make', '_replace', '_asdict', '_source')

_special = ('__module__', '__name__', '__qualname__', '__annotations__')

def _make_recordclass(name, types):
    msg = "RecordClass('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    types = [(n, _type_check(t, msg)) for n, t in types]
    rec_cls = recordclass(name, [n for n, t in types])
    rec_cls.__annotations__ = rec_cls._field_types = dict(types)
    try:
        rec_cls.__module__ = _sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    return rec_cls

class RecordClassMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get('_root', False):
            return super().__new__(cls, typename, bases, ns)
        # if not _PY36:
        #     raise TypeError("Class syntax for RecordClass is only supported"
        #                     " in Python 3.6+")
        types = ns.get('__annotations__', {})
        nm_tpl = _make_recordclass(typename, types.items())

        defaults = []
        defaults_dict = {}
        for field_name in types:
            if field_name in ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value
            elif defaults:
                raise TypeError("Non-default recordclass field {field_name} cannot "
                                "follow default field(s) {default_names}"
                                .format(field_name=field_name,
                                        default_names=', '.join(defaults_dict.keys())))
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        # update from user namespace without overriding special recordclass attributes
        for key in ns:
            if key in _prohibited:
                raise AttributeError("Cannot overwrite RecordClass attribute " + key)
            elif key not in _special and key not in nm_tpl._fields:
                setattr(nm_tpl, key, ns[key])

        return nm_tpl


class RecordClass(metaclass=RecordClassMeta):
    _root = True

    def __new__(self, typename, fields=None, **kwargs):
        # if kwargs and not _PY36:
        #     raise TypeError("Keyword syntax for RecordClass is only supported"
        #                     " in Python 3.6+")
        if fields is None:
            fields = kwargs.items()
        elif kwargs:
            raise TypeError("Either list of fields or keywords"
                            " can be provided to RecordClass, not both")
        return _make_recordclass(typename, fields)
