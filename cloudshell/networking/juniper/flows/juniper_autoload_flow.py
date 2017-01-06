from cloudshell.networking.devices.flows.snmp_action_flows import AutoloadFlow
from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload


class JuniperSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, resource_name):
        with self._snmp_handler.get_snmp_service() as snpm_service:
            juniper_snmp_autoload = JuniperSnmpAutoload(snpm_service, resource_name, self._logger)
            return juniper_snmp_autoload.discover(supported_os)