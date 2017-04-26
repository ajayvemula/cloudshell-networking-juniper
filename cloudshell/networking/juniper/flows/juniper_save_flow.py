from cloudshell.devices.flows.cli_action_flows import SaveConfigurationFlow
from cloudshell.networking.juniper.command_actions.save_restore_actions import SaveRestoreActions
from cloudshell.networking.juniper.helpers.save_restore_helper import SaveRestoreHelper


class JuniperSaveFlow(SaveConfigurationFlow):
    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """Backup 'startup-config' or 'running-config' from device to provided file_system [ftp|tftp]
        Also possible to backup config to localhost
         :param folder_path:  tftp/ftp server where file be saved
         :param configuration_type: type of configuration that will be saved (StartUp or Running)
         :param vrf_management_name: Virtual Routing and Forwarding management name
         :return: Saved configuration path
         """

        configuration_type = SaveRestoreHelper.validate_configuration_type(configuration_type)
        self._logger.info("Save configuration to file {0}".format(folder_path))
        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as cli_service:
            save_action = SaveRestoreActions(cli_service, self._logger)
            save_action.save_running(folder_path)
        return folder_path
