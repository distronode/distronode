"""
These test cases verify distronode-test version constraints for pylint and its dependencies across Python versions.
The initial test cases were discovered while testing various Python versions against distronode/distronode.
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Python 3.8 fails with astroid 2.2.5 but works on 2.3.3
#   syntax-error: Cannot import 'string' due to syntax error 'invalid syntax (&lt;unknown&gt;, line 109)'
# Python 3.9 fails with astroid 2.2.5 but works on 2.3.3
#   syntax-error: Cannot import 'string' due to syntax error 'invalid syntax (&lt;unknown&gt;, line 104)'
import string  # pylint: disable=unused-import

# Python 3.9 fails with pylint 2.3.1 or 2.4.4 with astroid 2.3.3 but works with pylint 2.5.0 and astroid 2.4.0
#   'Call' object has no attribute 'value'
result = {None: None}[{}.get('something')]

foo = {}.keys()
