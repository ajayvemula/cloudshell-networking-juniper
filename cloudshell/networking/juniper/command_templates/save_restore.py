from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict(
    [(r'[Ee]rror:', 'Command error'), (r'[Ee]rror\ssaving\sconfiguration', 'Error saving configuration')])

SAVE = CommandTemplate('save "{dst_path}"', error_map=ERROR_MAP)
RESTORE = CommandTemplate('load {restore_type} "{src_path}"', error_map=ERROR_MAP)
