from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.juniper.command_templates import system_commands


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def reboot(self, timeout=None):
        """
        Reboot the system
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, system_commands.REBOOT, timeout=timeout).execute_command()
        return output

    def shutdown(self):
        """
        Shutdown the system
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, system_commands.SHUTDOWN).execute_command()
        return output

    def load_firmware(self, src_path):
        """
        Ubgrade firmware
        :param src_path:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, system_commands.FIRMWARE_UPGRADE).execute_command(
            src_path=src_path)
        return output
