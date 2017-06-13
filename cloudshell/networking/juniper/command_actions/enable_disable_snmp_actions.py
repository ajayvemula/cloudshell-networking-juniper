from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.juniper.cli.junipr_command_modes import EditSnmpCommandMode
from cloudshell.networking.juniper.command_templates import enable_disable_snmp as command_template


class EnableDisableSnmpActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def configured(self, snmp_community):
        """
        Check snmp community configured
        :param snmp_community:
        :return:
        """
        snmp_community_info = CommandTemplateExecutor(self._cli_service,
                                                      command_template.SHOW_SNMP_COMUNITY).execute_command(
            snmp_community=snmp_community)

        if "authorization read" in snmp_community_info:
            present = True
        else:
            present = False
        return present

    def enable_snmp(self, snmp_community):
        """
        Enable snmp on the device
        :return:
        """
        edit_snmp_mode = EditSnmpCommandMode()
        self._cli_service.command_mode.add_child_node(edit_snmp_mode)
        with self._cli_service.enter_mode(edit_snmp_mode) as edit_snmp_service:
            output = CommandTemplateExecutor(edit_snmp_service, command_template.ENABLE_SNMP).execute_command(
                snmp_community=snmp_community)
        return output

    def disable_snmp(self):
        """
        Disable SNMP
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.DISABLE_SNMP).execute_command()
        return output
