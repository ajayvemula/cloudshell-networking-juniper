from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

COMMIT = CommandTemplate('commit', error_map=ERROR_MAP)
ROLLBACK = CommandTemplate('rollback', error_map=ERROR_MAP)
