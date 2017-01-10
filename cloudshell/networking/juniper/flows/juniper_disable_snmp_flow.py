from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions


class JuniperDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
          Enable snmp flow
          :param cli_handler:
          :type cli_handler: JuniperCliHandler
          :param logger:
          :return:
          """
        super(JuniperDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self):
        with self._cli_handler.config_mode_service() as cli_service:
            snmp_actions = EnableDisableSnmpActions(cli_service, self._logger)
            commit_rollback = CommitRollbackActions(cli_service, self._logger)
            try:
                self._logger.debug('Disable SNMP')
                snmp_actions.disable_snmp()
                commit_rollback.commit()
            except CommandExecutionException as exception:
                commit_rollback.rollback()
                self._logger.error(exception)
                raise exception
