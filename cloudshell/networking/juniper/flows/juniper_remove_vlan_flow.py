from cloudshell.networking.devices.flows.action_flows import RemoveVlanFlow


class JuniperRemoveVlanFlow(RemoveVlanFlow):
    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        pass
