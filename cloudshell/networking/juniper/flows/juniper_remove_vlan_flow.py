from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import RemoveVlanFlow
from cloudshell.networking.juniper.command_actions.add_remove_vlan_actions import AddRemoveVlanActions
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.helpers.add_remove_vlan_helper import AddRemoveVlanHelper, VlanRangeOperations, \
    VlanRange


class JuniperRemoveVlanFlow(RemoveVlanFlow):
    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        port = AddRemoveVlanHelper.extract_port_name(port_name)
        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as cli_service:
            commit_rollback_actions = CommitRollbackActions(cli_service, self._logger)
            vlan_actions = AddRemoveVlanActions(cli_service, self._logger)
            try:
                existing_ranges = VlanRangeOperations.create_from_dict(vlan_actions.get_vlans())
                range_instance = VlanRange(VlanRange.range_from_string(vlan_range))
                range_intersection = VlanRangeOperations.find_intersection([range_instance], existing_ranges)

                vlan_actions.delete_member(port, vlan_range)
                commit_rollback_actions.commit()
                for _range in range_intersection:
                    vlan_actions.delete_vlan(_range.name)
                commit_rollback_actions.commit()
                return 'Success'
            except CommandExecutionException:
                commit_rollback_actions.rollback()
                raise
