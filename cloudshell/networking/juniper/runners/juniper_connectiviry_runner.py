from cloudshell.networking.devices.runners.connectivity_runner import ConnectivityRunner
from cloudshell.networking.juniper.flows.juniper_add_vlan_flow import JuniperAddVlanFlow
from cloudshell.networking.juniper.flows.juniper_remove_vlan_flow import JuniperRemoveVlanFlow
from cloudshell.networking.juniper.juniper_cli_handler import JuniperCliHandler


class JuniperConnectivityRunner(ConnectivityRunner):
    def __init__(self, cli, logger, api, context):
        """
            Handle add/remove vlan flows

            :param cli:
            :param logger:
            :param api:
            :param context:
            :param supported_os:
            """
        super(JuniperConnectivityRunner, self).__init__(logger)
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)
        self.add_vlan_flow = JuniperAddVlanFlow(self._cli_handler, logger)
        self.remove_vlan_flow = JuniperRemoveVlanFlow(self._cli_handler, logger)
