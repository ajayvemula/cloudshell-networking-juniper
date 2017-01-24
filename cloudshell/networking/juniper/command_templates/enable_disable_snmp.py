from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

ENABLE_SNMP = CommandTemplate('set community {snmp_community} authorization read-only', action_map=ACTION_MAP,
                              error_map=ERROR_MAP)
DISABLE_SNMP = CommandTemplate('delete snmp', action_map=ACTION_MAP, error_map=ERROR_MAP)

SHOW_SNMP_COMUNITY = CommandTemplate('show snmp community {snmp_community}', action_map=ACTION_MAP, error_map=ERROR_MAP)
