from __future__ import division, absolute_import, print_function

import os
from distutils.msvc9compiler import MSVCCompiler as _MSVCCompiler


def _merge(old, new):
    """Concatenate two environment paths avoiding repeats.

    Here `old` is the environment string before the base class initialize
    function is called and `new` is the string after the call. The new string
    will be a fixed string if it is not obtained from the current enviroment,
    or the same as the old string if obtained from the same enviroment. The aim
    here is not to append the new string if it is already contained in the old
    string so as to limit the growth of the environment string.

    Parameters
    ----------
    old : string
        Previous enviroment string.
    new : string
        New environment string.

    Returns
    -------
    ret : string
        Updated environment string.

    """
    if new in old:
        return old
    if not old:
        return new

    # Neither new nor old is empty. Give old priority.
    return ';'.join([old, new])


class MSVCCompiler(_MSVCCompiler):
    def __init__(self, verbose=0, dry_run=0, force=0):
        _MSVCCompiler.__init__(self, verbose, dry_run, force)

    def initialize(self, plat_name=None):
        # The 'lib' and 'include' variables may be overwritten
        # by MSVCCompiler.initialize, so save them for later merge.
        environ_lib = os.getenv('lib')
        environ_include = os.getenv('include')
        _MSVCCompiler.initialize(self, plat_name)

        # Merge current and previous values of 'lib' and 'include'
        os.environ['lib'] = _merge(environ_lib, os.environ['lib'])
        os.environ['include'] = _merge(environ_include, os.environ['include'])

    def manifest_setup_ldargs(self, output_filename, build_temp, ld_args):
        ld_args.append('/MANIFEST')
        _MSVCCompiler.manifest_setup_ldargs(self, output_filename,
                                            build_temp, ld_args)
