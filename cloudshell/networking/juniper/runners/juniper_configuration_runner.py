from cloudshell.networking.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.flows.juniper_restore_flow import JuniperRestoreFlow
from cloudshell.networking.juniper.flows.juniper_save_flow import JuniperSaveFlow


class JuniperConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli, logger, context, api):
        super(JuniperConfigurationRunner, self).__init__(logger, context, api)
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)
        self._save_flow = JuniperSaveFlow(self._cli_handler, self._logger)
        self._restore_flow = JuniperRestoreFlow(self._cli_handler, self._logger)
