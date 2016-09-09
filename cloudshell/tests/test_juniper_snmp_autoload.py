from unittest import TestCase

from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload
from mock import MagicMock as Mock
import mock

class TestJuniperSnmpAutoload(TestCase):
    def setUp(self):
        self._snmp_handler = Mock()
        self._logger = Mock()
        self._config = Mock()
        self._cli_service = Mock()
        self._snmp_community = Mock()
        self._autoload_operations_instance = JuniperSnmpAutoload(snmp_handler=self._snmp_handler, logger=self._logger,
                                                                 config=self._config, cli_service=self._cli_service,
                                                                 snmp_community=self._snmp_community)

    def _mock_methods(self):
        self._autoload_operations_instance._is_valid_device_os = Mock()
        self._autoload_operations_instance.enable_snmp = Mock()
        self._autoload_operations_instance.disable_snmp = Mock()
        self._autoload_operations_instance._build_root = Mock()
        self._autoload_operations_instance._build_chassis = Mock()
        self._autoload_operations_instance._build_power_modules = Mock()
        self._autoload_operations_instance._build_modules = Mock()
        self._autoload_operations_instance._build_sub_modules = Mock()
        self._autoload_operations_instance._build_ports = Mock()
        self._autoload_operations_instance._root = Mock()

    def test_discover_is_valid_device_os_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._is_valid_device_os.assert_called_once_with()

    def test_discover_build_root_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_root.assert_called_once_with()

    def test_discover_build_chassis_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_chassis.assert_called_once_with()

    def test_discover_build_power_modules_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_power_modules.assert_called_once_with()

    def test_discover_build_modules_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_modules.assert_called_once_with()

    def test_discover_build_sub_modules_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_sub_modules.assert_called_once_with()

    def test_discover_build_ports_call(self):
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance._build_ports.assert_called_once_with()

    def test_enable_snmp_if_community_string_is_present(self):
        """Check that enable_snmp doesn't send command to add community string if such one is already on the device"""
        self._cli_service.send_config_command.return_value = "authorization read-only;"
        self._autoload_operations_instance.enable_snmp()
        self._cli_service.send_config_command.assert_called_once()
        self._cli_service.send_command_list.assert_not_called()
        self._cli_service.commit.assert_not_called()

    def test_enable_snmp_if_no_community_string(self):
        """Check that enable_snmp send commands to add community string if such one is not on the device"""
        self._cli_service.send_config_command.return_value = ""
        self._autoload_operations_instance.enable_snmp()
        self._cli_service.send_config_command.assert_called_once()
        self._cli_service.send_command_list.assert_called_once()
        self._cli_service.commit.assert_called_once()

    def test_disable_snmp(self):
        self._autoload_operations_instance.disable_snmp()
        self._cli_service.send_config_command.assert_called_once()
        self._cli_service.commit.assert_called_once()

    @mock.patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.get_attribute_by_name')
    def test_discover_calls_enable_snmp(self, get_attribute_by_name_func):
        """Check that discover method calls enable_snmp if 'Enable SNMP' attr is 'True'"""
        get_attribute_by_name_func.return_value = 'True'
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance.enable_snmp.assert_called_once()

    @mock.patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.get_attribute_by_name')
    def test_discover_doesnt_call_enable_snmp(self, get_attribute_by_name_func):
        """Check that discover method doesn't call enable_snmp if 'Enable SNMP' attr is 'False'"""
        get_attribute_by_name_func.return_value = 'False'
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance.enable_snmp.assert_not_called()

    @mock.patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.get_attribute_by_name')
    def test_discover_calls_disable_snmp(self, get_attribute_by_name_func):
        """Check that discover method calls disable_snmp if 'Disable SNMP' attr is 'True'"""
        get_attribute_by_name_func.return_value = 'True'
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance.disable_snmp.assert_called_once()

    @mock.patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.get_attribute_by_name')
    def test_discover_doesnt_call_disable_snmp(self, get_attribute_by_name_func):
        """Check that discover method doesn't call disable_snmp if 'Disable SNMP' attr is 'False'"""
        get_attribute_by_name_func.return_value = 'False'
        self._mock_methods()
        self._autoload_operations_instance.discover()
        self._autoload_operations_instance.disable_snmp.assert_not_called()
