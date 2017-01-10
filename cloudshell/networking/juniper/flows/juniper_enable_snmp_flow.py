from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters


class JuniperEnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
        Enable snmp flow
        :param cli_handler:
        :type cli_handler: JuniperCliHandler
        :param logger:
        :return:
        """
        super(JuniperEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters):
        if not isinstance(snmp_parameters, SNMPV2Parameters):
            message = 'Unsupported SNMP version'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        if not snmp_parameters.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        snmp_community = snmp_parameters.snmp_community
        with self._cli_handler.config_mode_service() as cli_service:
            snmp_actions = EnableDisableSnmpActions(cli_service, self._logger)
            commit_rollback = CommitRollbackActions(cli_service, self._logger)
            if not snmp_actions.configured(snmp_community):
                self._logger.debug('Configuring SNMP with community {}'.format(snmp_community))
                try:
                    output = snmp_actions.enable_snmp(snmp_community)
                    output += commit_rollback.commit()
                    return output
                except CommandExecutionException as exception:
                    commit_rollback.rollback()
                    self._logger.error(exception)
                    raise exception
