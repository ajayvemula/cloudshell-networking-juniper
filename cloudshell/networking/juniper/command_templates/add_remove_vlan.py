from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = {}
ERROR_MAP = {}

CREATE_VLAN = CommandTemplate('set vlans {vlan_name} vlan-id {vlan_id}')
CONFIGURE_VLAN_QNQ = CommandTemplate('set vlans {vlan_name} dot1q-tunneling')
ASSIGN_VLAN_MEMBER = CommandTemplate(
    'set interfaces {port} unit 0 family ethernet-switching port-mode {mode} vlan members {vlan_name}')

ENABLE_INTERFACE = CommandTemplate('delete interfaces {0} disable')
DISABLE_INTERFACE = CommandTemplate('set interfaces {0} disable')

DELETE_VLAN_MEMBER = CommandTemplate(
    'delete interfaces {port} unit 0 family ethernet-switching vlan members {vlan_name}')

DELETE_PORT_MODE_ON_INTERFACE = CommandTemplate(
    'delete interfaces {port_name} unit 0 family ethernet-switching port-mode')

DELETE_VLAN = CommandTemplate('delete vlans {vlan_name}')

CREATE_VLAN_RANGE = CommandTemplate('set vlans {vlan_name} vlan-range {vlan_range}')

SHOW_VLAN_INTERFACES = CommandTemplate('show vlans {vlan_name}')
SHOW_INTERFACE = CommandTemplate('show interfaces {port_name}')
