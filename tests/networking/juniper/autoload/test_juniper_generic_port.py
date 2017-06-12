from unittest import TestCase

from mock import Mock, PropertyMock, patch

from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperGenericPort


class TestJuniperGenericPort(TestCase):
    def setUp(self):
        self._index = '20'
        self._snmp_handler = Mock()
        self._shell_name = Mock()
        self._shell_type = Mock()
        self._resource_name = 'test_resource'

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_name',
           new_callable=PropertyMock)
    def _create_port_instance(self, port_name):
        port_name.return_value = 'port'
        return JuniperGenericPort(self._index, self._snmp_handler, self._shell_name, self._shell_type,
                                  self._resource_name)

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_name',
           new_callable=PropertyMock)
    def _create_portchannel_instance(self, port_name):
        port_name.return_value = 'ae1'
        return JuniperGenericPort(self._index, self._snmp_handler, self._shell_name, self._shell_type,
                                  self._resource_name)

    def test_init_port(self):
        instance = self._create_port_instance()
        self.assertIs(instance.index, self._index)
        self.assertIs(instance._snmp_handler, self._snmp_handler)
        self.assertIs(instance.shell_name, self._shell_name)
        self.assertIs(instance.shell_type, self._shell_type)
        self.assertIs(instance._resource_name, self._resource_name)
        self.assertIsNone(instance._port_phis_id)
        self.assertIsNone(instance._port_name)
        self.assertIsNone(instance._logical_unit)
        self.assertIsNone(instance._fpc_id)
        self.assertIsNone(instance._pic_id)
        self.assertIsNone(instance._type)

        self.assertEqual(instance.ipv4_addresses, [])
        self.assertEqual(instance.ipv6_addresses, [])
        self.assertIsNone(instance.port_adjacent)
        self.assertFalse(instance.is_portchannel)
        self.assertEqual(instance._max_string_length, JuniperGenericPort.AUTOLOAD_MAX_STRING_LENGTH)

    def test_init_portchannel(self):
        instance = self._create_portchannel_instance()
        self.assertIs(instance.index, self._index)
        self.assertIs(instance._snmp_handler, self._snmp_handler)
        self.assertIs(instance.shell_name, self._shell_name)
        self.assertIs(instance.shell_type, self._shell_type)
        self.assertIs(instance._resource_name, self._resource_name)
        self.assertIsNone(instance._port_phis_id)
        self.assertIsNone(instance._port_name)
        self.assertIsNone(instance._logical_unit)
        self.assertIsNone(instance._fpc_id)
        self.assertIsNone(instance._pic_id)
        self.assertIsNone(instance._type)

        self.assertEqual(instance.ipv4_addresses, [])
        self.assertEqual(instance.ipv6_addresses, [])
        self.assertIsNone(instance.port_adjacent)
        self.assertTrue(instance.is_portchannel)
        self.assertEqual(instance._max_string_length, JuniperGenericPort.AUTOLOAD_MAX_STRING_LENGTH)

    def test_get_snmp_attribute(self):
        mib = Mock()
        snmp_attribute = Mock()
        result = Mock()
        self._snmp_handler.get_property.return_value = result
        instance = self._create_port_instance()
        self.assertIs(instance._get_snmp_attribute(mib, snmp_attribute), result)
        self._snmp_handler.get_property.assert_called_once_with(mib, snmp_attribute, self._index)

    def test_port_phis_id_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.port_phis_id, value)
        self.assertIs(instance.port_phis_id, value)
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.JUNIPER_IF_MIB, 'ifChassisPort')

    def test_port_description_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.port_description, value)
        instance._get_snmp_attribute.assert_called_once_with('IF-MIB', 'ifAlias')

    def test_logical_unit_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.logical_unit, value)
        self.assertIs(instance.logical_unit, value)
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.JUNIPER_IF_MIB, 'ifChassisLogicalUnit')

    def test_fpc_id_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.fpc_id, value)
        self.assertIs(instance.fpc_id, value)
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.JUNIPER_IF_MIB, 'ifChassisFpc')

    def test_pic_id_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.pic_id, value)
        self.assertIs(instance.pic_id, value)
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.JUNIPER_IF_MIB, 'ifChassisPic')

    def test_type_prop(self):
        value = "'test'"
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertEqual(instance.type, value.strip('\''))
        self.assertEqual(instance.type, value.strip('\''))
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.IF_MIB, 'ifType')

    def test_port_name_prop(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertIs(instance.port_name, value)
        self.assertIs(instance.port_name, value)
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.IF_MIB, 'ifDescr')

    def test_get_associated_ipv4_address(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._validate_attribute_value = Mock()
        instance._validate_attribute_value.return_value = value
        instance.ipv4_addresses = ['10.0.1.1', '10.0.1.2']
        self.assertIs(instance._get_associated_ipv4_address(), value)
        instance._validate_attribute_value.assert_called_once_with(','.join(instance.ipv4_addresses))

    def test_get_associated_ipv6_address(self):
        value = Mock()
        instance = self._create_port_instance()
        instance._validate_attribute_value = Mock()
        instance._validate_attribute_value.return_value = value
        instance.ipv6_addresses = ['10.0.1.1', '10.0.1.2']
        self.assertIs(instance._get_associated_ipv6_address(), value)
        instance._validate_attribute_value.assert_called_once_with(','.join(instance.ipv6_addresses))

    def test_validate_attribute_value_short(self):
        instance = self._create_port_instance()
        instance._max_string_length = 20
        attribute_value = 'test_test'
        self.assertEqual(instance._validate_attribute_value(attribute_value), attribute_value)

    def test_validate_attribute_value_long(self):
        instance = self._create_port_instance()
        instance._max_string_length = 10
        attribute_value = 'test_test_test'
        self.assertEqual(instance._validate_attribute_value(attribute_value),
                         attribute_value[:instance._max_string_length] + '...')

    def test_get_port_duplex_full(self):
        value = 'full duplex'
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertEqual(instance._get_port_duplex(), 'Full')
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.ETHERLIKE_MIB, 'dot3StatsDuplexStatus')

    def test_get_port_duplex_half(self):
        value = 'test duplex'
        instance = self._create_port_instance()
        instance._get_snmp_attribute = Mock()
        instance._get_snmp_attribute.return_value = value
        self.assertEqual(instance._get_port_duplex(), 'Half')
        instance._get_snmp_attribute.assert_called_once_with(JuniperGenericPort.ETHERLIKE_MIB, 'dot3StatsDuplexStatus')

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_name',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.type',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_description',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.GenericPort')
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.AddRemoveVlanHelper')
    def test_get_port(self, add_remove_vlan_helper, generic_port_class, port_description_prop, port_type_prop,
                      port_name_prop):
        instance = self._create_port_instance()
        port_instance = Mock()
        generic_port_class.return_value = port_instance
        name = Mock()
        add_remove_vlan_helper.convert_port_name.return_value = name
        description = Mock()
        port_description_prop.return_value = description
        port_type = Mock()
        port_type_prop.return_value = port_type
        port_name = Mock()
        port_name_prop.return_value = port_name
        port_adjacent = Mock()
        instance.port_adjacent = port_adjacent
        mackaddress = Mock()
        mtu = Mock()
        bandwith = Mock()
        instance._get_snmp_attribute = Mock(side_effect=[mackaddress, mtu, bandwith])
        ipv4 = Mock()
        instance._get_associated_ipv4_address = Mock(return_value=ipv4)
        ipv6 = Mock()
        instance._get_associated_ipv6_address = Mock(return_value=ipv6)
        duplex = Mock()
        instance._get_port_duplex = Mock(return_value=duplex)
        autoneg = Mock()
        instance._get_port_autoneg = Mock(return_value=autoneg)
        port = instance.get_port()
        self.assertIs(port, port_instance)
        generic_port_class.assert_called_once_with(shell_name=self._shell_name, name=name,
                                                   unique_id='{0}.{1}.{2}'.format(self._resource_name, 'port',
                                                                                  self._index))
        self.assertIs(port.port_description, description)
        self.assertIs(port.l2_protocol_type, port_type)
        self.assertIs(port.mac_address, mackaddress)
        self.assertIs(port.mtu, mtu)
        self.assertIs(port.bandwidth, bandwith)
        self.assertIs(port.ipv4_address, ipv4)
        self.assertIs(port.ipv6_address, ipv6)
        self.assertIs(port.duplex, duplex)
        self.assertIs(port.auto_negotiation, autoneg)
        self.assertIs(port.adjacent, port_adjacent)
        add_remove_vlan_helper.convert_port_name.assert_called_once_with(port_name)

    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_name',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.type',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.JuniperGenericPort.port_description',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.GenericPortChannel')
    @patch('cloudshell.networking.juniper.autoload.juniper_snmp_autoload.AddRemoveVlanHelper')
    def test_get_portchannel(self, add_remove_vlan_helper, generic_portchannel_class, port_description_prop,
                             port_type_prop,
                             port_name_prop):
        instance = self._create_port_instance()
        port_instance = Mock()
        generic_portchannel_class.return_value = port_instance
        name = Mock()
        add_remove_vlan_helper.convert_port_name.return_value = name
        description = Mock()
        port_description_prop.return_value = description

        port_name = Mock()
        port_name_prop.return_value = port_name
        ipv4 = Mock()
        instance._get_associated_ipv4_address = Mock(return_value=ipv4)
        ipv6 = Mock()
        instance._get_associated_ipv6_address = Mock(return_value=ipv6)
        associated_ports = ['10.0.1.1', '10.0.1.2']
        instance.associated_port_names = associated_ports
        portchannel = instance.get_portchannel()
        self.assertIs(portchannel, port_instance)
        generic_portchannel_class.assert_called_once_with(shell_name=self._shell_name, name=name,
                                                          unique_id='{0}.{1}.{2}'.format(self._resource_name, 'port_channel',
                                                                                         self._index))
        self.assertIs(portchannel.port_description, description)
        self.assertIs(portchannel.ipv4_address, ipv4)
        self.assertIs(portchannel.ipv6_address, ipv6)
        self.assertEqual(portchannel.associated_ports, ','.join(associated_ports))
        add_remove_vlan_helper.convert_port_name.assert_called_once_with(port_name)
