from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.juniper.junipr_command_modes import DefaultCommandMode, ConfigCommandMode


class JuniperCliHandler(CliHandlerImpl):
    def __init__(self, cli, context, logger, api):
        super(JuniperCliHandler, self).__init__(cli, context, logger, api)
        modes = CommandModeHelper.create_command_mode(context)
        self.enable_mode = modes[DefaultCommandMode]
        self.config_mode = modes[ConfigCommandMode]
