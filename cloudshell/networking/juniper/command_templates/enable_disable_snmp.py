from cloudshell.cli.command_template.command_template import CommandTemplate

ENTER_EDIT_SNMP = CommandTemplate('edit snmp', [], [])
EXIT_EDIT_SNMP = CommandTemplate('exit', [], [])
ENABLE_SNMP = CommandTemplate('set community "{}" authorization read-only', [r'.+'], ['Wrong community name'])
DISABLE_SNMP = CommandTemplate('delete snmp', [], [])
