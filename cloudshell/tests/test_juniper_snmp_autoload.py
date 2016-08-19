from unittest import TestCase

from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload
from mock import MagicMock as Mock


class TestJuniperSnmpAutoload(TestCase):
    def setUp(self):
        self._snmp_handler = Mock()
        self._logger = Mock()
        self._config = Mock()
        self._autoload_operations_instance = JuniperSnmpAutoload(snmp_handler=self._snmp_handler, logger=self._logger,
                                                                 config=self._config)

    def _mock_methods(self):
        self._autoload_operations_instance._is_valid_device_os = Mock()
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
