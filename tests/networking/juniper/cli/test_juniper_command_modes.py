from collections import OrderedDict
from unittest import TestCase, skip

from mock import Mock, patch

from cloudshell.networking.juniper.cli.junipr_command_modes import DefaultCommandMode, CliCommandMode, \
    ConfigCommandMode, EditSnmpCommandMode
from cloudshell.cli.command_mode import CommandMode


class TestJuniperCliCommandMode(TestCase):
    def setUp(self):
        self._resource_config = Mock()
        self._api = Mock()
        self._instance = self.create_instance()

    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CommandMode.__init__')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CliCommandMode.enter_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CliCommandMode.exit_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CliCommandMode.enter_error_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CliCommandMode.exit_error_map')
    def create_instance(self, exit_error_map, enter_error_map, exit_action_map, enter_action_map, command_mode_init):
        enter_action_map_result = Mock()
        enter_action_map.return_value = enter_action_map_result
        exit_action_map_result = Mock()
        exit_action_map.return_value = exit_action_map_result
        enter_error_map_result = Mock()
        enter_error_map.return_value = enter_error_map_result
        exit_error_map_result = Mock()
        exit_error_map.return_value = exit_error_map_result

        instance = CliCommandMode(self._resource_config, self._api)
        command_mode_init.assert_called_once_with(instance, CliCommandMode.PROMPT,
                                                  CliCommandMode.ENTER_COMMAND,
                                                  CliCommandMode.EXIT_COMMAND,
                                                  enter_action_map=enter_action_map_result,
                                                  exit_action_map=exit_action_map_result,
                                                  enter_error_map=enter_error_map_result,
                                                  exit_error_map=exit_error_map_result)
        return instance

    def test_init(self):
        self.assertIs(self._instance.resource_config, self._resource_config)
        self.assertIs(self._instance._api, self._api)

    def test_enter_action(self):
        cli_operations = Mock()
        self.assertIsNone(self._instance.enter_actions(cli_operations))

    def test_enter_action_map(self):
        self.assertEqual(self._instance.enter_action_map(), OrderedDict())

    def test_enter_error_map(self):
        self.assertEqual(self._instance.enter_error_map(), OrderedDict())

    def test_exit_action_map(self):
        self.assertEqual(self._instance.exit_action_map(), OrderedDict())

    def test_exit_error_map(self):
        self.assertEqual(self._instance.exit_error_map(), OrderedDict())


class TestJuniperDefaultCommandMode(TestCase):
    def setUp(self):
        self._resource_config = Mock()
        self._api = Mock()
        self._instance = self.create_instance()

    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CommandMode.__init__')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.DefaultCommandMode.enter_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.DefaultCommandMode.exit_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.DefaultCommandMode.enter_error_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.DefaultCommandMode.exit_error_map')
    def create_instance(self, exit_error_map, enter_error_map, exit_action_map, enter_action_map, command_mode_init):
        enter_action_map_result = Mock()
        enter_action_map.return_value = enter_action_map_result
        exit_action_map_result = Mock()
        exit_action_map.return_value = exit_action_map_result
        enter_error_map_result = Mock()
        enter_error_map.return_value = enter_error_map_result
        exit_error_map_result = Mock()
        exit_error_map.return_value = exit_error_map_result

        instance = DefaultCommandMode(self._resource_config, self._api)
        command_mode_init.assert_called_once_with(instance, DefaultCommandMode.PROMPT,
                                                  DefaultCommandMode.ENTER_COMMAND,
                                                  DefaultCommandMode.EXIT_COMMAND,
                                                  enter_action_map=enter_action_map_result,
                                                  exit_action_map=exit_action_map_result,
                                                  enter_error_map=enter_error_map_result,
                                                  exit_error_map=exit_error_map_result)
        return instance

    def test_init(self):
        self.assertIs(self._instance.resource_config, self._resource_config)
        self.assertIs(self._instance._api, self._api)

    def test_enter_action(self):
        cli_operations = Mock()
        self._instance.enter_actions(cli_operations)
        cli_operations.send_command.assert_called_once_with('set cli screen-length 0')

    def test_enter_action_map(self):
        self.assertEqual(self._instance.enter_action_map(), OrderedDict())

    def test_enter_error_map(self):
        self.assertEqual(self._instance.enter_error_map(), OrderedDict([(r'[Ee]rror:', 'Command error')]))

    def test_exit_action_map(self):
        self.assertEqual(self._instance.exit_action_map(), OrderedDict())

    def test_exit_error_map(self):
        self.assertEqual(self._instance.exit_error_map(), OrderedDict([(r'[Ee]rror:', 'Command error')]))


class TestJuniperConfigCommandMode(TestCase):
    def setUp(self):
        self._resource_config = Mock()
        self._api = Mock()
        self._instance = self.create_instance()

    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CommandMode.__init__')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.ConfigCommandMode.enter_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.ConfigCommandMode.exit_action_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.ConfigCommandMode.enter_error_map')
    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.ConfigCommandMode.exit_error_map')
    def create_instance(self, exit_error_map, enter_error_map, exit_action_map, enter_action_map, command_mode_init):
        enter_action_map_result = Mock()
        enter_action_map.return_value = enter_action_map_result
        exit_action_map_result = Mock()
        exit_action_map.return_value = exit_action_map_result
        enter_error_map_result = Mock()
        enter_error_map.return_value = enter_error_map_result
        exit_error_map_result = Mock()
        exit_error_map.return_value = exit_error_map_result

        instance = ConfigCommandMode(self._resource_config, self._api)
        command_mode_init.assert_called_once_with(instance, ConfigCommandMode.PROMPT,
                                                  ConfigCommandMode.ENTER_COMMAND,
                                                  ConfigCommandMode.EXIT_COMMAND,
                                                  enter_action_map=enter_action_map_result,
                                                  exit_action_map=exit_action_map_result,
                                                  enter_error_map=enter_error_map_result,
                                                  exit_error_map=exit_error_map_result)
        return instance

    def test_init(self):
        self.assertIs(self._instance.resource_config, self._resource_config)
        self.assertIs(self._instance._api, self._api)

    def test_enter_action_map(self):
        pass

    def test_enter_error_map(self):
        self.assertEqual(self._instance.enter_error_map(), OrderedDict([(r'[Ee]rror:', 'Command error')]))

    def test_exit_action_map(self):
        self.assertEqual(self._instance.exit_action_map(), OrderedDict())

    def test_exit_error_map(self):
        self.assertEqual(self._instance.exit_error_map(), OrderedDict([(r'[Ee]rror:', 'Command error')]))


class TestCommandModeRelations(TestCase):
    def setUp(self):
        pass

    def test_relations(self):
        self.assertEqual(CommandMode.RELATIONS_DICT, {
            CliCommandMode: {
                DefaultCommandMode: {
                    ConfigCommandMode: {}
                }
            }
        })


class TestEditSnmpCommandMode(TestCase):
    def setUp(self):
        pass

    @patch('cloudshell.networking.juniper.cli.junipr_command_modes.CommandMode.__init__')
    def test_init(self, command_mode_init):
        instance = EditSnmpCommandMode()
        command_mode_init.assert_called_once_with(instance, EditSnmpCommandMode.PROMPT,
                                                  EditSnmpCommandMode.ENTER_COMMAND,
                                                  EditSnmpCommandMode.EXIT_COMMAND)
