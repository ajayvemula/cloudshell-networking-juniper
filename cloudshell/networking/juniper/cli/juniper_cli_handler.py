from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.juniper.cli.junipr_command_modes import DefaultCommandMode, ConfigCommandMode, \
    EditSnmpCommandMode


class JuniperCliHandler(CliHandlerImpl):
    def __init__(self, cli, context, logger, api):
        super(JuniperCliHandler, self).__init__(cli, context, logger, api)
        modes = CommandModeHelper.create_command_mode(context, api)
        self.enable_mode = modes[DefaultCommandMode]
        self.config_mode = modes[ConfigCommandMode]

    def default_mode_service(self):
        """
        Default mode session
        :return:
        """
        return self.get_cli_service(self.enable_mode)

    def config_mode_service(self):
        """
        Config mode session
        :return:
        """
        return self.get_cli_service(self.config_mode)
