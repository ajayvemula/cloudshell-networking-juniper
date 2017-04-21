from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

CREATE_VLAN = CommandTemplate('set vlans {vlan_name} vlan-id {vlan_id}', error_map=ERROR_MAP)
CONFIGURE_VLAN_QNQ = CommandTemplate('set vlans {vlan_name} dot1q-tunneling', error_map=ERROR_MAP)
ASSIGN_VLAN_MEMBER = CommandTemplate(
    'set interfaces {port} unit 0 family ethernet-switching port-mode {mode} vlan members {vlan_range}',
    error_map=ERROR_MAP)

ENABLE_INTERFACE = CommandTemplate('delete interfaces {0} disable', error_map=ERROR_MAP)
DISABLE_INTERFACE = CommandTemplate('set interfaces {0} disable', error_map=ERROR_MAP)

DELETE_VLAN_MEMBER = CommandTemplate(
    'delete interfaces {port} unit 0 family ethernet-switching vlan members {vlan_range}', error_map=ERROR_MAP)

DELETE_PORT_MODE_ON_INTERFACE = CommandTemplate(
    'delete interfaces {port_name} unit 0 family ethernet-switching port-mode', error_map=ERROR_MAP)

DELETE_VLAN = CommandTemplate('delete vlans {vlan_name}', error_map=ERROR_MAP)

CREATE_VLAN_RANGE = CommandTemplate('set vlans {vlan_name} vlan-range {vlan_range}', error_map=ERROR_MAP)

SHOW_VLAN_INTERFACES = CommandTemplate('run show vlans {vlan_name}', error_map=ERROR_MAP)
SHOW_INTERFACE = CommandTemplate('show interfaces {port_name}', error_map=ERROR_MAP)
SHOW_VLANS = CommandTemplate('show vlans', error_map=ERROR_MAP)
SHOW_SPECIFIC_VLAN = CommandTemplate('show vlans {vlan_name}', error_map=ERROR_MAP)
