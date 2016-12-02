from cloudshell.networking.devices.flows.action_flows import AddVlanFlow


class JuniperAddVlanFlow(AddVlanFlow):
    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        pass
