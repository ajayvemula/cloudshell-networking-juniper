from cloudshell.cli.command_template.command_template import CommandTemplate

EDIT_SNMP = CommandTemplate('edit snmp', [], [])
ENABLE_SNMP = CommandTemplate('set community "{}" authorization read-only', [r'.+'], ['Wrong community name'])
DISABLE_SNMP = CommandTemplate('delete snmp', [], [])
