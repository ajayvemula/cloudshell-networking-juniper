from unittest import TestCase, skip

from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload
from mock import MagicMock as Mock
import mock


class TestJuniperSnmpAutoload(TestCase):
    def setUp(self):
        self._snmp_handler = Mock()
        self._shell_name = Mock()
        self._shell_type = Mock()
        self._resource_name = Mock()
        self._logger = Mock()
        self._supported_os = Mock()
        # self._cli_service = Mock()
        # self._snmp_community = Mock()
        self._resource = Mock()
        self._autoload_operations_instance = self._create_instance()

    @mock.patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.GenericResource')
    @mock.patch(
        'cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperSnmpAutoload._initialize_snmp_handler')
    def _create_instance(self, initialize_snmp, generic_resource):
        generic_resource.return_value = self._resource
        instance = JuniperSnmpAutoload(self._snmp_handler, self._shell_name, self._shell_type,
                                       self._resource_name, self._logger)
        generic_resource.assert_called_once_with(shell_name=self._shell_name,
                                                 shell_type=self._shell_type,
                                                 name=self._resource_name,
                                                 unique_id=self._resource_name)
        initialize_snmp.assert_called_once_with()
        return instance

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

    def test_init(self):
        self.assertIs(self._autoload_operations_instance.shell_name, self._shell_name)
        self.assertIs(self._autoload_operations_instance.shell_type, self._shell_type)
        self.assertIsNone(self._autoload_operations_instance._content_indexes)
        self.assertIsNone(self._autoload_operations_instance._if_indexes)
        self.assertIs(self._autoload_operations_instance._logger, self._logger)
        self.assertIs(self._autoload_operations_instance._snmp_handler, self._snmp_handler)
        self.assertIs(self._autoload_operations_instance._resource_name, self._resource_name)
        self.assertIs(self._autoload_operations_instance.resource, self._resource)
        self.assertEqual(self._autoload_operations_instance._chassis, {})
        self.assertEqual(self._autoload_operations_instance._modules, {})
        self.assertEqual(self._autoload_operations_instance.sub_modules, {})
        self.assertEqual(self._autoload_operations_instance._ports, {})
        self.assertEqual(self._autoload_operations_instance._logical_generic_ports, {})
        self.assertEqual(self._autoload_operations_instance._physical_generic_ports, {})
        self.assertIsNone(self._autoload_operations_instance._generic_physical_ports_by_name)
        self.assertIsNone(self._autoload_operations_instance._generic_logical_ports_by_name)
        self.assertIsNone(self._autoload_operations_instance._ipv4_table)
        self.assertIsNone(self._autoload_operations_instance._ipv6_table)
        self.assertIsNone(self._autoload_operations_instance._if_duplex_table)
        self.assertIsNone(self._autoload_operations_instance._autoneg)
        self.assertIsNone(self._autoload_operations_instance._lldp_keys)

    def test_discover_call_methods(self):
        self._mock_methods()
        self._autoload_operations_instance.discover(self._supported_os)
        self._autoload_operations_instance._is_valid_device_os.assert_called_once_with(self._supported_os)
        self._autoload_operations_instance._build_root.assert_called_once_with()
        self._autoload_operations_instance._build_chassis.assert_called_once_with()
        self._autoload_operations_instance._build_power_modules.assert_called_once_with()
        self._autoload_operations_instance._build_modules.assert_called_once_with()
        self._autoload_operations_instance._build_sub_modules.assert_called_once_with()
        self._autoload_operations_instance._build_ports.assert_called_once_with()
