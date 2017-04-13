from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.flows.juniper_disable_snmp_flow import JuniperDisableSnmpFlow
from cloudshell.networking.juniper.flows.juniper_enable_snmp_flow import JuniperEnableSnmpFlow
from cloudshell.devices.snmp_handler import SnmpHandler


class JuniperSnmpHandler(SnmpHandler):
    def __init__(self, cli, resource_config, logger, api):
        super(JuniperSnmpHandler, self).__init__(resource_config, logger, api)
        self._cli = cli
        self._api = api

    @property
    def juniper_cli_handler(self):
        return JuniperCliHandler(self._cli, self.resource_config, self._logger, self._api)

    def _create_enable_flow(self):
        return JuniperEnableSnmpFlow(self.juniper_cli_handler, self._logger)

    def _create_disable_flow(self):
        return JuniperDisableSnmpFlow(self.juniper_cli_handler,
                                      self._logger)
