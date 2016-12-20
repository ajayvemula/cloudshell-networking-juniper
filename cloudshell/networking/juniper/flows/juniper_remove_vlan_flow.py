from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.networking.devices.flows.action_flows import RemoveVlanFlow
from cloudshell.networking.juniper.command_actions.add_remove_vlan_actions import AddRemoveVlanActions
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.helpers.add_remove_vlan_helper import AddRemoveVlanHelper


class JuniperRemoveVlanFlow(RemoveVlanFlow):
    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        port = AddRemoveVlanHelper.extract_port_name(port_name, self._logger)
        vlan_name = "vlan-" + vlan_range
        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as cli_service:
            commit_rollback_actions = CommitRollbackActions(cli_service, self._logger)
            vlan_actions = AddRemoveVlanActions(cli_service, self._logger)
            try:
                vlan_actions.delete_member(port, vlan_name)
                commit_rollback_actions.commit()
                vlan_actions.delete_vlan(vlan_name)
                commit_rollback_actions.commit()
                return 'Success'
            except CommandExecutionException:
                commit_rollback_actions.rollback()
                raise
