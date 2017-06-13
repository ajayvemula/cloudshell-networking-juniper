from unittest import TestCase

from mock import Mock, patch

from cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions


class ContextManagerMock(object):
    def __init__(self, session):
        self._session = session

    def __enter__(self):
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestEnableDisableSnmpActions(TestCase):
    def setUp(self):
        self._cli_service = Mock()
        self._logger = Mock()
        self._instance = EnableDisableSnmpActions(self._cli_service, self._logger)

    def test_init(self):
        self.assertIs(self._instance._cli_service, self._cli_service)
        self.assertIs(self._instance._logger, self._logger)

    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.CommandTemplateExecutor')
    def test_configured_true(self, command_template_executor, command_template):
        snmp_community = Mock()
        output = 'authorization read'
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.configured(snmp_community), True)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.SHOW_SNMP_COMUNITY)
        execute_command.execute_command.assert_called_once_with(snmp_community=snmp_community)

    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.CommandTemplateExecutor')
    def test_configured_false(self, command_template_executor, command_template):
        snmp_community = Mock()
        output = 'test'
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.configured(snmp_community), False)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.SHOW_SNMP_COMUNITY)
        execute_command.execute_command.assert_called_once_with(snmp_community=snmp_community)

    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.EditSnmpCommandMode')
    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.CommandTemplateExecutor')
    def test_enable_snmp(self, command_template_executor, command_template, edit_snmp_comman_mode):
        snmp_community = Mock()
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        edit_snmp_mode = Mock()
        edit_snmp_session = Mock()
        context_manager_mock = ContextManagerMock(edit_snmp_session)
        self._cli_service.enter_mode.return_value = context_manager_mock
        edit_snmp_comman_mode.return_value = edit_snmp_mode
        self.assertIs(self._instance.enable_snmp(snmp_community), output)
        command_template_executor.assert_called_once_with(edit_snmp_session, command_template.ENABLE_SNMP)
        execute_command.execute_command.assert_called_once_with(snmp_community=snmp_community)

    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.enable_disable_snmp_actions.CommandTemplateExecutor')
    def test_disable_snmp(self, command_template_executor, command_template):
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.disable_snmp(), output)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.DISABLE_SNMP)
        execute_command.execute_command.assert_called_once_with()
