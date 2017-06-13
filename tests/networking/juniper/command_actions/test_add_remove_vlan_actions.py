from unittest import TestCase

from mock import Mock, patch

from cloudshell.networking.juniper.command_actions.add_remove_vlan_actions import AddRemoveVlanActions


class TestAddRemoveVlanActions(TestCase):
    def setUp(self):
        self._cli_service = Mock()
        self._logger = Mock()
        self._instance = AddRemoveVlanActions(self._cli_service, self._logger)

    def test_init(self):
        self.assertIs(self._instance._cli_service, self._cli_service)
        self.assertIs(self._instance._logger, self._logger)

    @patch('cloudshell.networking.juniper.command_actions.add_remove_vlan_actions.re')
    @patch('cloudshell.networking.juniper.command_actions.add_remove_vlan_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.add_remove_vlan_actions.CommandTemplateExecutor')
    def test_get_vlan_ports(self, command_template_executor, command_template, re):
        vlan_name = Mock()
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        port = Mock()
        port_result = Mock()
        port.strip.return_value = port_result
        re_findall_result = [port]
        re.findall.return_value = re_findall_result
        re_sub_result = Mock()
        re.sub.return_value = re_sub_result
        self.assertEqual(self._instance.get_vlan_ports(vlan_name), [port_result])
        command_template_executor.assert_called_once_with(self._cli_service, command_template.SHOW_VLAN_INTERFACES)
        execute_command.execute_command.assert_called_once_with(vlan_name=vlan_name)
        re.sub.assert_called_once_with(r'\n|\r', '', output)
        re.findall.assert_called_once_with(r'[a-zA-Z]+-(?:\d+/)+\d+|ae\d+', re_sub_result)
        port.strip.assert_called_once_with()

    @patch('cloudshell.networking.juniper.command_actions.add_remove_vlan_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.add_remove_vlan_actions.CommandTemplateExecutor')
    def test_create_qnq_vlan(self, command_template_executor, command_template):
        self._instance.create_vlan = Mock()
        create_vlan_out = 'create_vlan'
        self._instance.create_vlan.return_value = create_vlan_out
        exec_out = 'exec_out'
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = exec_out
        vlan_name = Mock()
        vlan_range = Mock()
        self.assertEqual(self._instance.create_qnq_vlan(vlan_name, vlan_range), create_vlan_out + exec_out)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.CONFIGURE_VLAN_QNQ)
        execute_command.execute_command.assert_called_once_with(vlan_name=vlan_name)
