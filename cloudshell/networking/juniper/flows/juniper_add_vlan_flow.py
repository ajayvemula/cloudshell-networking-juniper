from cloudshell.networking.devices.flows.action_flows import AddVlanFlow


class JuniperAddVlanFlow(AddVlanFlow):
    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        self._logger.debug(vlan_range)
        self._logger.debug(port_mode)
        self._logger.debug(port_name)
        self._logger.debug(qnq)
        self._logger.debug(c_tag)
