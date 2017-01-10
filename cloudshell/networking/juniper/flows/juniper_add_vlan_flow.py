from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import AddVlanFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.command_actions.add_remove_vlan_actions import AddRemoveVlanActions
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.helpers.add_remove_vlan_helper import AddRemoveVlanHelper


class JuniperAddVlanFlow(AddVlanFlow):
    def __init__(self, cli_handler, logger):
        """
        :param cli_handler:
        :type cli_handler: JuniperCliHandler
        :param logger:
        :return:
        """
        super(JuniperAddVlanFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        port = AddRemoveVlanHelper.extract_port_name(port_name)
        vlan_name = "vlan-" + vlan_range
        with self._cli_handler.config_mode_service() as cli_service:
            commit_rollback_actions = CommitRollbackActions(cli_service, self._logger)
            vlan_actions = AddRemoveVlanActions(cli_service, self._logger)
            try:
                if qnq:
                    vlan_actions.create_qnq_vlan(vlan_name, vlan_range)
                else:
                    vlan_actions.create_vlan(vlan_name, vlan_range)

                vlan_actions.clean_port(port)
                vlan_actions.assign_member(port, vlan_name, port_mode)
                commit_rollback_actions.commit()
                return 'Success'
            except CommandExecutionException:
                commit_rollback_actions.rollback()
                raise
