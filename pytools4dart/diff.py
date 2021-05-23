from difflib import unified_diff
try:
    from colorama import Fore, Back, Style, init
    init()
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''
    Fore = Back = Style = ColorFallback()

from .simulation import get_simu_name
from .core_ui.utils import core_diff

def color_diff(diff):
    for line in diff:
        if line.startswith('+'):
            yield Fore.GREEN + line + Fore.RESET
        elif line.startswith('-'):
            yield Fore.RED + line + Fore.RESET
        elif line.startswith('^'):
            yield Fore.BLUE + line + Fore.RESET
        else:
            yield line

def diff(object1, object2):

    if type(object1) != type(object2):
        raise IOError('Inputs have different classes.')

    if 'pytools4dart.core' in str(type(object1)):
        os1, os2 = core_diff(object1, object2)
        os1 = list(dict.fromkeys(os1)) # remove multiple None.build_ while keeping order
        os2 = list(dict.fromkeys(os2))
        os1 = ('\n\n'.join(os1)+'\n').splitlines(keepends=True)
        os2 = ('\n\n'.join(os2)+'\n').splitlines(keepends=True)
        name1 = 'object1'
        name2 = 'object2'
    else:
        os1 = object1.__str__().splitlines(keepends=True)
        os2 = object2.__str__().splitlines(keepends=True)
        os1[-1] += '\n'
        os2[-1] += '\n'
        name1 = get_simu_name(object1, 'object1')
        name2 = get_simu_name(object2, 'object2')

    diff_gen = unified_diff(os1, os2, name1, name2)
    diff_gen = color_diff(diff_gen)
    print(''.join([l for l in diff_gen if not l.startswith('@@')]))
