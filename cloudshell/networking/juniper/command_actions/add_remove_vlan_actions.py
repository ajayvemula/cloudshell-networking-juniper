from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
import re
from cloudshell.networking.juniper.command_templates import add_remove_vlan as command_template
from cloudshell.cli.cli_service import CliService


class AddRemoveVlanActions(object):
    def __init__(self, cli_service, logger):
        """
        Add remove vlan
        :param cli_service: config mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def get_vlan_ports(self, vlan_name):
        """
        Return list of interfaces assigned on vlan
        :param vlan_name:
        :return: List of interfaces
        :rtype: list
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_VLAN_INTERFACES).execute_command(
            vlan_name=vlan_name)
        ports = re.findall(r'[a-zA-Z]+-(?:\d+/)+\d+|ae\d+', re.sub(r'\n|\r', '', output))
        return [port.strip() for port in set(ports)]

    def create_qnq_vlan(self, vlan_name, vlan_range):
        """
        Create qnq vlan
        :param vlan_name:
        :type vlan_name: str
        :param vlan_range:
        :type vlan_range: str
        :return:
        """

        output = self.create_vlan(vlan_name, vlan_range)

        output += CommandTemplateExecutor(self._cli_service, command_template.CONFIGURE_VLAN_QNQ).execute_command(
            vlan_name=vlan_name)
        self._logger.debug('Set qnq tag for {0}'.format(vlan_name))
        return output

    def create_vlan(self, vlan_name, vlan_range):
        """
        Create vlan or vlan range
        :param vlan_name:
        :param vlan_range:
        :return:
        """
        if re.match(r'\d+-\d+', vlan_range):
            output = CommandTemplateExecutor(self._cli_service, command_template.CREATE_VLAN_RANGE).execute_command(
                vlan_name=vlan_name, vlan_range=vlan_range)
            self._logger.debug('Created vlan range {0}, ids {1}'.format(vlan_name, vlan_range))
        else:
            output = CommandTemplateExecutor(self._cli_service, command_template.CREATE_VLAN).execute_command(
                vlan_name=vlan_name, vlan_id=vlan_range)
            self._logger.debug('Created vlan {0}, id {1}'.format(vlan_name, vlan_range))
        return output

    def delete_vlan(self, vlan_name):
        """
        Delete vlan
        :param vlan_name:
        :return:
        """
        output = ''
        if len(self.get_vlan_ports(vlan_name)) == 0:
            output = CommandTemplateExecutor(self._cli_service, command_template.DELETE_VLAN).execute_command(
                vlan_name=vlan_name)
        return output

    def assign_member(self, port, vlan_range, mode):
        """
        Assign interface to the vlan members
        :param port:
        :param vlan_name:
        :param mode:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.ASSIGN_VLAN_MEMBER).execute_command(
            port=port,
            vlan_range=vlan_range,
            mode=mode)
        return output

    def delete_member(self, port, vlan_range):
        """
        Delete interface from vlan members
        :param port:
        :param vlan_name:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.DELETE_VLAN_MEMBER).execute_command(
            port=port,
            vlan_range=vlan_range)
        return output

    def get_vlans_for_port(self, port):
        """
        Return list of assigned vlans
        :param port:
        :return:
        """
        output = CommandTemplateExecutor(self._cli_service, command_template.SHOW_INTERFACE).execute_command(
            port_name=port)
        found_list = re.findall(r'vlan\s*\{\s*members\s*\[*\s*((?:[\w\d-]+\s*)+)\s*\]*\s*;\s*\}',
                                re.sub(r'\n|\r', '', output))
        if len(found_list) > 0:
            return [vlan.strip() for vlan in found_list[0].split()]
        return []

    def remove_port_mode_on_interface(self, port):
        output = CommandTemplateExecutor(self._cli_service,
                                         command_template.DELETE_PORT_MODE_ON_INTERFACE).execute_command(port_name=port)

        self._logger.info("Port mode removed for {0}".format(port))
        return output

    def clean_port(self, port):
        """
        Remove port from all vlans
        :param port:
        :return:
        """
        vlans = self.get_vlans_for_port(port)
        for vlan_name in vlans:
            self.delete_member(port, vlan_name)
        self.remove_port_mode_on_interface(port)
        self._logger.info("Cleaning port {0}, vlans, {1}".format(port, ", ".join(vlans)))

    def get_vlans(self):
        """
        Get vlans info
        :return:
        """
        vlan_dict = {}
        out = CommandTemplateExecutor(self._cli_service, command_template.SHOW_VLANS).execute_command()
        pattern = '(?P<vlan_name>.+)\s+{\s+vlan-(id|range)\s+(?P<vlan_id>\d+(-\d+)?);'
        iterator = re.finditer(pattern, out, flags=re.MULTILINE | re.IGNORECASE)
        for match in iterator:
            match_dict = match.groupdict()
            vlan_dict[match_dict['vlan_name'].strip()] = match_dict['vlan_id'].strip()
        return vlan_dict

    def check_vlan_qnq(self, vlan_name):
        """
        Check if vlan qnq
        :param vlan_name:
        :return:
        """
        pattern = r'dot1q-tunneling;'
        out = CommandTemplateExecutor(self._cli_service, command_template.SHOW_SPECIFIC_VLAN).execute_command(vlan_name=vlan_name)
        if re.search(pattern, out, flags=re.MULTILINE | re.IGNORECASE):
            return True
        else:
            return False
