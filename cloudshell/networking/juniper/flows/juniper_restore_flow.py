from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.devices.flows.cli_action_flows import RestoreConfigurationFlow
from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions
from cloudshell.networking.juniper.command_actions.save_restore_actions import SaveRestoreActions
from cloudshell.networking.juniper.helpers.save_restore_helper import SaveRestoreHelper


class JuniperRestoreFlow(RestoreConfigurationFlow):
    def execute_flow(self, path, restore_method, configuration_type, vrf_management_name):
        """Restore configuration on device from provided configuration file

        Restore configuration from local file system or ftp/tftp server into 'running-config' or 'startup-config'.
        :param path: relative path to the file on the remote host tftp://server/sourcefile
        :param configuration_type: the configuration type to restore (StartUp or Running)
        :param restore_method: override current config or not
        :param vrf_management_name: Virtual Routing and Forwarding management name
        :return:
        """
        configuration_type = SaveRestoreHelper.validate_configuration_type(configuration_type)

        restore_method = restore_method or "override"
        restore_method = restore_method.lower()

        if restore_method == 'append':
            restore_type = 'merge'
        elif restore_method == 'override':
            restore_type = restore_method
        else:
            raise Exception(self.__class__.__name__,
                            "Restore method '{}' is wrong! Use 'Append' or 'Override'".format(restore_method))

        if not path:
            raise Exception(self.__class__.__name__, 'Config source cannot be empty')

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as cli_service:
            restore_actions = SaveRestoreActions(cli_service, self._logger)
            commit_rollback_actions = CommitRollbackActions(cli_service, self._logger)
            try:
                restore_actions.restore_running(restore_type, path)
                commit_rollback_actions.commit()
            except CommandExecutionException:
                commit_rollback_actions.rollback()
                raise
