from cloudshell.networking.autoload.networking_attributes import RootAttributes, ChassisAttributes, PowerPortAttributes, \
    ModuleAttributes, SubModuleAttributes, PortAttributes, PortChannelAttributes
from cloudshell.networking.autoload.networking_model import RootElement, Chassis, Module, SubModule, Port, PowerPort, \
    PortChannel
from cloudshell.networking.operations.interfaces.autoload_operations_interface import AutoloadOperationsInterface
import inject
import re
import os
from cloudshell.networking.juniper.utils import sort_elements_by_attributes
from cloudshell.configuration.cloudshell_snmp_binding_keys import SNMP_HANDLER
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER


def _get_from_table(key, table):
    if key in table:
        return table[key]
    else:
        return None


class GenericPort(object):
    PORTCHANNEL_DESCRIPTIONS = ['ae']
    _IF_CHASSIS_TABLE = None
    _IF_MIB_TABLE = None

    def __init__(self, index, snmp_handler):
        self.associated_port_names = []
        self._if_chassis_data = None
        self._if_mib_data = None
        self.index = index
        self._snmp_handler = snmp_handler

        self._ipv4_table = None
        self._ipv6_table = None
        self._if_duplex_table = None

        self.ipv4_addresses = []
        self.ipv6_addresses = []
        if self.port_description[:2] in self.PORTCHANNEL_DESCRIPTIONS:
            self.is_portchannel = True
        else:
            self.is_portchannel = False

    @property
    def if_chassis_table(self):
        if not GenericPort._IF_CHASSIS_TABLE:
            GenericPort._IF_CHASSIS_TABLE = self._snmp_handler.snmp_request(('JUNIPER-IF-MIB', 'ifChassisTable'))
        return GenericPort._IF_CHASSIS_TABLE

    @property
    def if_mib_table(self):
        if not GenericPort._IF_MIB_TABLE:
            GenericPort._IF_MIB_TABLE = self._snmp_handler.snmp_request(('IF-MIB', 'interfaces'))
        return GenericPort._IF_MIB_TABLE

    @property
    def if_chassis_data(self):
        if not self._if_chassis_data:
            self._if_chassis_data = self.if_chassis_table[self.index]
        return self._if_chassis_data

    @property
    def if_mib_data(self):
        if not self._if_mib_data:
            self._if_mib_data = self.if_mib_table[self.index]
        return self._if_mib_data

    @property
    def if_duplex_table(self):
        if not self._if_duplex_table:
            self._if_duplex_table = self._snmp_handler.snmp_request(('EtherLike-MIB', 'dot3StatsDuplexStatus'))
        return self._if_duplex_table

    @property
    def port_phis_id(self):
        return _get_from_table('ifChassisPort', self.if_chassis_data)

    @property
    def port_description(self):
        return _get_from_table('ifDescr', self.if_mib_data)

    @property
    def logical_unit(self):
        return _get_from_table('ifChassisLogicalUnit', self.if_chassis_data)

    @property
    def fpc_id(self):
        return _get_from_table('ifChassisFpc', self.if_chassis_data)

    @property
    def pic_id(self):
        return _get_from_table('ifChassisPic', self.if_chassis_data)

    @property
    def type(self):
        return _get_from_table('ifType', self.if_mib_data)

    @property
    def name(self):
        return self._convert_port_name(self.port_description)

    @staticmethod
    def _convert_port_name(port_name):
        port_name_converted = port_name.replace("/", "-")
        return port_name_converted

    def _get_associated_ipv4_address(self):
        if len(self.ipv4_addresses) > 0:
            return ','.join(self.ipv4_addresses)

    def _get_associated_ipv6_address(self):
        if len(self.ipv6_addresses) > 0:
            return ','.join(self.ipv6_addresses)

    def _get_port_duplex(self):
        duplex = None
        if self.index in self.if_duplex_table:
            port_duplex = self.if_duplex_table[self.index]['dot3StatsDuplexStatus'].strip('\'')
            if re.search(r'[Ff]ull', port_duplex):
                duplex = 'Full'
            else:
                duplex = 'Half'
        return duplex

    def _get_port_autoneg(self):
        # auto_negotiation = self.snmp_handler.snmp_request(('MAU-MIB', 'ifMauAutoNegAdminStatus'))
        # return auto_negotiation
        return None

    def _get_port_adjacent(self):
        return None

    def get_port(self):
        port = Port(self.port_phis_id, self.name)
        port_attributes = dict()
        port_attributes[PortAttributes.PORT_DESCRIPTION] = _get_from_table('ifDescr', self.if_mib_data)
        port_attributes[PortAttributes.L2_PROTOCOL_TYPE] = self.type.strip('\'')
        port_attributes[PortAttributes.MAC_ADDRESS] = _get_from_table('ifPhysAddress', self.if_mib_data)
        port_attributes[PortAttributes.MTU] = _get_from_table('ifMtu', self.if_mib_data)
        port_attributes[PortAttributes.BANDWIDTH] = _get_from_table('ifSpeed', self.if_mib_data)
        port_attributes[PortAttributes.IPV4_ADDRESS] = self._get_associated_ipv4_address()
        port_attributes[PortAttributes.IPV6_ADDRESS] = self._get_associated_ipv6_address()
        port_attributes[PortAttributes.PROTOCOL_TYPE] = _get_from_table('protoType', self.if_mib_data)
        port_attributes[PortAttributes.DUPLEX] = self._get_port_duplex()
        port_attributes[PortAttributes.AUTO_NEGOTIATION] = self._get_port_autoneg()
        port_attributes[PortAttributes.ADJACENT] = self._get_port_adjacent()
        port.build_attributes(port_attributes)
        return port

    def get_portchannel(self):
        port_channel = PortChannel(self.port_phis_id, self.name)
        port_channel_attributes = dict()
        port_channel_attributes[PortChannelAttributes.PORT_DESCRIPTION] = self.port_description
        port_channel_attributes[PortChannelAttributes.IPV4_ADDRESS] = self._get_associated_ipv4_address()
        port_channel_attributes[PortChannelAttributes.IPV6_ADDRESS] = self._get_associated_ipv6_address()
        port_channel_attributes[PortChannelAttributes.PROTOCOL_TYPE] = _get_from_table('protoType', self.if_mib_data)
        port_channel_attributes[PortChannelAttributes.ASSOCIATED_PORTS] = ','.join(self.associated_port_names)
        port_channel.build_attributes(port_channel_attributes)
        return port_channel


class JuniperSnmpAutoload(AutoloadOperationsInterface):
    FILTER_PORTS_BY_DESCRIPTION = [r'bme', r'vme', r'me', r'vlan', r'gr', r'vt', r'mt', r'mams']
    FILTER_PORTS_BY_TYPE = ['tunnel', 'other', 'pppMultilinkBundle']

    def __init__(self, snmp_handler=None, logger=None):
        self._logical_generic_ports = {}
        self._physical_generic_ports = {}
        self._generic_physical_ports_by_description = None
        self._generic_logical_ports_by_description = None
        self._ports = {}
        self.sub_modules = {}
        self._modules = {}
        self._chassis = {}
        self._root = RootElement()

        self._snmp_handler = None
        self.snmp_handler = snmp_handler

        self._ipv4_table = None
        self._ipv6_table = None
        self._if_duplex_table = None
        self._autoneg = None

        self._logger = logger

    @property
    def logger(self):
        if self._logger is not None:
            return self._logger
        return inject.instance(LOGGER)

    @property
    def snmp_handler(self):
        if self._snmp_handler is None:
            self.snmp_handler = inject.instance(SNMP_HANDLER)
        return self._snmp_handler

    @snmp_handler.setter
    def snmp_handler(self, snmp_handler):
        if snmp_handler:
            snmp_handler.snmp_request = self.snmp_request
            self._snmp_handler = snmp_handler
            self._initialize_snmp_handler()

    @property
    def ipv4_table(self):
        if not self._ipv4_table:
            self._ipv4_table = sort_elements_by_attributes(
                self._snmp_handler.snmp_request(('IP-MIB', 'ipAddrTable')), 'ipAdEntIfIndex')
        return self._ipv4_table

    @property
    def ipv6_table(self):
        if not self._ipv6_table:
            self._ipv6_table = sort_elements_by_attributes(
                self._snmp_handler.snmp_request(('IPV6-MIB', 'ipv6AddrEntry')), 'ipAdEntIfIndex')
        return self._ipv6_table

    @property
    def generic_physical_ports_by_description(self):
        if not self._generic_physical_ports_by_description:
            self._generic_physical_ports_by_description = {}
            for index, generic_port in self._physical_generic_ports.iteritems():
                self._generic_physical_ports_by_description[generic_port.port_description] = generic_port
        return self._generic_physical_ports_by_description

    @property
    def generic_logical_ports_by_description(self):
        if not self._generic_logical_ports_by_description:
            self._generic_logical_ports_by_description = {}
            for index, generic_port in self._logical_generic_ports.iteritems():
                self._generic_logical_ports_by_description[generic_port.port_description] = generic_port
        return self._generic_logical_ports_by_description

    def snmp_request(self, request_data):
        if len(request_data) == 2:
            result = self.snmp_handler.walk(request_data)
        elif len(request_data) > 2:
            result = self.snmp_handler.get_property(*request_data)
        else:
            raise Exception('_snmp_request', 'Request tuple len has to be 2 or more')
        return result

    def _initialize_snmp_handler(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp_handler.update_mib_sources(path)
        self.logger.info("Loading mibs")
        self.snmp_handler.load_mib('JUNIPER-MIB')
        self.snmp_handler.load_mib('JUNIPER-SMI')
        self.snmp_handler.load_mib('JUNIPER-IF-MIB')
        self.snmp_handler.load_mib('IF-MIB')
        self.snmp_handler.load_mib('JUNIPER-CHASSIS-DEFINES-MIB')
        self.snmp_handler.load_mib('IEEE8023-LAG-MIB')
        self.snmp_handler.load_mib('EtherLike-MIB')
        self.snmp_handler.load_mib('IP-MIB')
        self.snmp_handler.load_mib('IPV6-MIB')

    def _build_root(self):
        self.logger.info("Building Root")
        vendor = ''
        model = ''
        os_version = ''
        sys_obj_id = self.snmp_handler.snmp_request(('SNMPv2-MIB', 'sysObjectID', 0))
        model_search = re.search('^(?P<vendor>\w+)-\S+jnxProductName(?P<model>\S+)', sys_obj_id
                                 )
        if model_search:
            vendor = model_search.groupdict()['vendor'].capitalize()
            model = model_search.groupdict()['model']
        sys_descr = self.snmp_handler.snmp_request(('SNMPv2-MIB', 'sysDescr', '0'))
        os_version_search = re.search('JUNOS \S+(,)?\s', sys_descr, re.IGNORECASE)
        if os_version_search:
            os_version = os_version_search.group(0).replace('JUNOS ', '').replace(',', '').strip(' \t\n\r')
        root_attributes = dict()
        root_attributes[RootAttributes.CONTACT_NAME] = self.snmp_handler.snmp_request(('SNMPv2-MIB', 'sysContact', '0'))
        root_attributes[RootAttributes.SYSTEM_NAME] = self.snmp_handler.snmp_request(('SNMPv2-MIB', 'sysName', '0'))
        root_attributes[RootAttributes.LOCATION] = self.snmp_handler.snmp_request(('SNMPv2-MIB', 'sysLocation', '0'))
        root_attributes[RootAttributes.OS_VERSION] = os_version
        root_attributes[RootAttributes.VENDOR] = vendor
        root_attributes[RootAttributes.MODEL] = model
        self._root.build_attributes(root_attributes)

    def _build_chassis(self):
        self.logger.debug('Building Chassis')
        element_index = '1'
        content_table = self.snmp_handler.snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        container_table = self.snmp_handler.snmp_request(('JUNIPER-MIB', 'jnxContainersTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == element_index:
                content_data = content_table[key]
                chassis_id = index2
                chassis = Chassis(chassis_id)

                chassis_attributes = dict()
                model_string = _get_from_table('jnxContainersType', container_table[int(index1)])
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    chassis_attributes[ChassisAttributes.MODEL] = model_list[1]
                else:
                    chassis_attributes[ChassisAttributes.MODEL] = model_string
                chassis_attributes[ChassisAttributes.SERIAL_NUMBER] = _get_from_table('jnxContentsSerialNo',
                                                                                      content_data)
                chassis.build_attributes(chassis_attributes)
                self._root.chassis.append(chassis)
                self._chassis[_get_from_table('jnxContentsChassisId', content_data)] = chassis

    def _build_power_modules(self):
        self.logger.debug('Building PowerPorts')
        element_index = '2'
        content_table = self.snmp_handler.snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == element_index:
                content_data = content_table[key]
                element_id = index2
                element = PowerPort(element_id)

                element_attributes = dict()
                model_string = _get_from_table('jnxContentsType', content_data)
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[PowerPortAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[PowerPortAttributes.MODEL] = model_string
                element_attributes[PowerPortAttributes.PORT_DESCRIPTION] = _get_from_table('jnxContentsDescr',
                                                                                           content_data)
                element_attributes[PowerPortAttributes.SERIAL_NUMBER] = _get_from_table('jnxContentsSerialNo',
                                                                                        content_data)
                element_attributes[PowerPortAttributes.VERSION] = _get_from_table('jnxContentsRevision',
                                                                                  content_data)
                element.build_attributes(element_attributes)
                chassis_id = _get_from_table('jnxContentsChassisId', content_data)
                if chassis_id in self._chassis:
                    chassis = self._chassis[chassis_id]
                    chassis.power_ports.append(element)

    def _build_modules(self):
        self.logger.debug('Building Modules')
        element_index = '7'
        content_table = self.snmp_handler.snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == str(element_index):
                content_data = content_table[key]
                element_id = index2
                element = Module(element_id)

                element_attributes = dict()
                model_string = _get_from_table('jnxContentsType', content_data)
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[ModuleAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[ModuleAttributes.MODEL] = model_string
                element_attributes[ModuleAttributes.SERIAL_NUMBER] = _get_from_table('jnxContentsSerialNo',
                                                                                     content_data)
                element_attributes[ModuleAttributes.VERSION] = _get_from_table('jnxContentsRevision',
                                                                               content_data)
                element.build_attributes(element_attributes)
                chassis_id = _get_from_table('jnxContentsChassisId', content_data)
                if chassis_id in self._chassis:
                    chassis = self._chassis[chassis_id]
                    chassis.modules.append(element)
                    self._modules[element_id] = element

    def _build_sub_modules(self):
        self.logger.debug('Building Sub Modules')
        element_index = '8'
        content_table = self.snmp_handler.snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == str(element_index):
                content_data = content_table[key]
                parent_id = index2
                element_id = index3
                element = SubModule(element_id)
                element_attributes = dict()
                model_string = _get_from_table('jnxContentsType', content_data)
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[SubModuleAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[SubModuleAttributes.MODEL] = model_string
                element_attributes[SubModuleAttributes.SERIAL_NUMBER] = _get_from_table('jnxContentsSerialNo',
                                                                                        content_data)
                element_attributes[SubModuleAttributes.VERSION] = _get_from_table('jnxContentsRevision',
                                                                                  content_data)
                element.build_attributes(element_attributes)
                if parent_id in self._modules:
                    self._modules[parent_id].sub_modules.append(element)
                    self.sub_modules[element_id] = element

    def _build_generic_ports(self):
        self.logger.debug("Building ports")
        if_chassis_table = self.snmp_handler.snmp_request(('JUNIPER-IF-MIB', 'ifChassisTable'))

        for index in if_chassis_table:
            generic_port = GenericPort(index, self.snmp_handler)
            if not self._port_filtered_by_description(generic_port) and not self._port_filtered_by_type(generic_port):
                if generic_port.logical_unit == '0':
                    self._physical_generic_ports[index] = generic_port
                else:
                    self._logical_generic_ports[index] = generic_port

    def _associate_ipv4_addresses(self):
        for index in self.ipv4_table:
            if int(index) in self._logical_generic_ports:
                logical_port = self._logical_generic_ports[int(index)]
                physical_port = self._get_associated_phisical_port_by_description(logical_port.port_description)
                ipv4_address = _get_from_table('ipAdEntAddr', self.ipv4_table[index])
                if ipv4_address:
                    physical_port.ipv4_addresses.append(ipv4_address)

    def _associate_ipv6_addresses(self):
        for index in self.ipv6_table:
            if int(index) in self._logical_generic_ports:
                logical_port = self._logical_generic_ports[int(index)]
                physical_port = self._get_associated_phisical_port_by_description(logical_port.port_description)
                ipv6_address = _get_from_table('ipAdEntAddr', self.ipv6_table[index])
                if ipv6_address:
                    physical_port.ipv6_addresses.append(ipv6_address)

    def _associate_portchannels(self):
        snmp_data = self._snmp_handler.snmp_request(('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'))
        for port_index in snmp_data:
            # self.logger.debug(port_index)
            associated_phisical_port = self._get_associated_phisical_port_by_description(
                self._logical_generic_ports[port_index].port_description)
            logical_portchannel_index = _get_from_table('dot3adAggPortAttachedAggID', snmp_data[port_index])
            if logical_portchannel_index and int(logical_portchannel_index) > 0:
                associated_phisical_portchannel = self._get_associated_phisical_port_by_description(
                    self._logical_generic_ports[port_index].port_description)
                if associated_phisical_portchannel:
                    associated_phisical_portchannel.is_portchannel = True
                    if associated_phisical_port:
                        associated_phisical_portchannel.associated_port_names.append(associated_phisical_port.name)

    def _get_associated_phisical_port_by_description(self, description):
        for port_description in self.generic_physical_ports_by_description:
            if port_description in description:
                return self.generic_physical_ports_by_description[port_description]
        return None

    def _port_filtered_by_description(self, port):
        for pattern in self.FILTER_PORTS_BY_DESCRIPTION:
            if re.search(pattern, port.port_description):
                return True
        return False

    def _port_filtered_by_type(self, port):
        if port.type in self.FILTER_PORTS_BY_TYPE:
            return True
        return False

    def _build_ports(self):
        self._build_generic_ports()
        self._associate_ipv4_addresses()
        self._associate_ipv6_addresses()
        self._associate_portchannels()
        for generic_port in self._physical_generic_ports.values():
            if generic_port.is_portchannel:
                self._root.port_channels.append(generic_port.get_portchannel())
            else:
                port = generic_port.get_port()
                if generic_port.fpc_id > 0 and generic_port.fpc_id in self._modules:
                    fpc = self._modules.get(generic_port.fpc_id)
                    if fpc and generic_port.pic_id > 0:
                        pic = self._get_pic_by_index(fpc, generic_port.pic_id)
                        if pic:
                            pic.ports.append(port)
                        else:
                            self.logger.info('Port {} is not allowed'.format(port.name))
                    else:
                        fpc.ports.append(port)
                else:
                    chassis = self._chassis.values()[0]
                    chassis.ports.append(generic_port.get_port())

    def _get_pic_by_index(self, fpc, index):
        for pic in fpc.sub_modules:
            if pic.element_id == index:
                return pic
        return None

    def _log_autoload_details(self, autoload_details):
        self.logger.debug('-------------------- <RESOURCES> ----------------------')
        for resource in autoload_details.resources:
            self.logger.debug('{0}, {1}'.format(resource.relative_address, resource.name))
        self.logger.debug('-------------------- </RESOURCES> ----------------------')

        self.logger.debug('-------------------- <ATTRIBUTES> ---------------------')
        for attribute in autoload_details.attributes:
            self.logger.debug('-- {0}, {1}, {2}'.format(attribute.relative_address, attribute.attribute_name,
                                                        attribute.attribute_value))
        self.logger.debug('-------------------- </ATTRIBUTES> ---------------------')

    def discover(self):
        self._build_root()
        self._build_chassis()
        self._build_power_modules()
        self._build_modules()
        self._build_sub_modules()
        self._build_ports()
        autoload_details = self._root.get_autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details
