__doc__ = '''
Utilities for managing Python function/method signatures
'''

from inspect import getfullargspec

def keywordParameters(
      func: 'User defined Python function or method'
) -> 'List of parameter names that can be specified by keyword':
   spec = getfullargspec(func)
   return spec.args[len(spec.args) - 
                    (len(spec.defaults) if spec.defaults else 0):] + list(
                       spec.kwonlyargs or ())
