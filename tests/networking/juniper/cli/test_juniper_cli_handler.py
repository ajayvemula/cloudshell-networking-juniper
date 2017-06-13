from unittest import TestCase

from mock import Mock, patch

from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.cli.junipr_command_modes import DefaultCommandMode, ConfigCommandMode


class TestJuniperCliHandler(TestCase):
    def setUp(self):
        self._cli = Mock()
        self._resource_config = Mock()
        self._logger = Mock()
        self._api = Mock()
        self._enable_mode = Mock()
        self._config_mode = Mock()
        self._command_modes = {DefaultCommandMode: self._enable_mode, ConfigCommandMode: self._config_mode}
        self._instance = self._create_instance()

    @patch('cloudshell.networking.juniper.cli.juniper_cli_handler.CommandModeHelper')
    def _create_instance(self, command_mode_helper):
        command_mode_helper.create_command_mode.return_value = self._command_modes
        instance = JuniperCliHandler(self._cli, self._resource_config, self._logger, self._api)
        command_mode_helper.create_command_mode.assert_called_once_with(self._resource_config, self._api)
        return instance

    def test_init(self):
        self.assertIs(self._instance.modes, self._command_modes)

    def test_enable_mode_prop(self):
        self.assertIs(self._instance.enable_mode, self._enable_mode)

    def test_config_mode_prop(self):
        self.assertIs(self._instance.config_mode, self._config_mode)

    def test_default_mode_service(self):
        self._instance.get_cli_service = Mock()
        result = Mock()
        self._instance.get_cli_service.return_value = result
        self.assertIs(self._instance.default_mode_service(), result)
        self._instance.get_cli_service.assert_called_once_with(self._enable_mode)

    def test_config_mode_service(self):
        self._instance.get_cli_service = Mock()
        result = Mock()
        self._instance.get_cli_service.return_value = result
        self.assertIs(self._instance.config_mode_service(), result)
        self._instance.get_cli_service.assert_called_once_with(self._config_mode)
