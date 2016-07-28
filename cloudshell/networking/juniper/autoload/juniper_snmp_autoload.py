from copy import deepcopy
import cPickle as pickle

from cloudshell.networking.autoload.networking_attributes import RootAttributes, ChassisAttributes, PowerPortAttributes, \
    ModuleAttributes, SubModuleAttributes, PortAttributes
from cloudshell.networking.autoload.networking_model import RootElement, Chassis, Module, SubModule, Port, PowerPort
from cloudshell.networking.operations.interfaces.autoload_operations_interface import AutoloadOperationsInterface
from cloudshell.shell.core.driver_context import AutoLoadDetails
import inject
import re
import os
from cloudshell.networking.juniper.utils import sort_elements_by_attributes, sort_objects_by_attributes
from cloudshell.configuration.cloudshell_snmp_binding_keys import SNMP_HANDLER
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER

ATTRIBUTE_MAPPING = {"PORT": {'ifType': 'L2 Protocol Type', 'ifPhysAddress': 'MAC Address', 'ifMtu': 'MTU',
                              'ifSpeed': 'Bandwidth', 'ifDescr': "Port Description", "ipAdEntAddr": "IPv4 Address",
                              "protoType": "Protocol Type", "dot3StatsDuplexStatus": "Duplex",
                              "autoNegotiation": "Auto Negotiation",
                              },
                     "PORT_CHANNEL": {'associatedPorts': 'Associated Ports',
                                      "protoType": "Protocol Type", "ipAdEntAddr": "IPv4 Address",
                                      'ifDescr': "Port Description"},
                     "CHASSIS": {"jnxContainersType": "Model", "jnxContentsSerialNo": "Serial Number"},
                     "MODULE": {"jnxContentsType": "Model", "jnxContentsRevision": "Version",
                                "jnxContentsSerialNo": "Serial Number"},
                     "SUB_MODULE": {"jnxContentsType": "Model", "jnxContentsRevision": "Version",
                                    "jnxContentsSerialNo": "Serial Number"},
                     "POWER_MODULE": {"jnxContentsType": "Model", "jnxContentsSerialNo": "Serial Number",
                                      "jnxContentsDescr": "Port Description", "jnxContentsRevision": "Version"},
                     }

ATTRIBUTE_PERMANENT_VALUES = {"PORT": {'protoType': 'Transparent', "autoNegotiation": "True"},
                              "PORT_CHANNEL": {'protoType': 'Transparent'}}

RESOURCE_TEMPLATE = '{0}^{1}^{2}^{3}|'
RESOURCE_ATTRIBUTE_TEMPLATE = '{0}^{1}^{2}|'

RESOURCES_MATRIX_HEADERS = ['Model', 'Name', 'Relative Address', 'Unique Identifier']

ATTRIBUTES_MATRIX_HEADERS = ['Relative Address', 'Attribute Name', 'Attribute Value']

DATAMODEL_ASSOCIATION = {"CHASSIS": ["Generic Chassis", "Chassis"], "MODULE": ["Generic Module", "Module"],
                         "SUB_MODULE": ["Generic Sub Module", "SubModule"],
                         "POWER_MODULE": ["Generic Power Port", "PowerPort"], "PORT": ["Generic Port"],
                         "PORT_CHANNEL": ["Generic Port Channel"]}

ATTRIBUTE_DESCRIPTION = {"CHASSIS": "jnxContentsDescr", "MODULE": "jnxContainersDescr",
                         "SUB_MODULE": "jnxContainersDescr", "POWER_MODULE": "jnxContainersDescr", "PORT": "ifDescr",
                         "PORT_CHANNEL": "ifDescr"}

ELEMENT_DEFINITION = {"1": "CHASSIS", "7": "MODULE", "8": "SUB_MODULE", "2": "POWER_MODULE"}

# PORT_DEFINITION = {"ethernetCsmacd": "PORT", "ieee8023adLag": "PORT_CHANNEL"}
# PORT_DEFINITION = {"ethernetCsmacd": "PORT", 'ieee8023adLag': 'PORT_CHANNEL', 'propVirtual': 'PORT', 'fibreChannel': 'PORT'}
PORTCHANNEL_TYPES = ['ieee8023adLag']

FILTER_PORTS_BY_DESCRIPTION = [r'bme', r'vme', r'me', r'vlan']
FILTER_PORTS_BY_TYPE = ['tunnel', 'other', 'pppMultilinkBundle']

OUTPUT_TABLE = {r"'": lambda val: val.strip("'"), r'.+::.+': lambda val: val.split('::')[1],
                r'fullDuplex': lambda val: 'Full', r'halfDuplex': lambda val: 'Half'}


# class Element:
#     CONTAINER_ATTRIBUTES = {"container_type": "jnxContainersType", "container_description": "jnxContainersDescr",
#                             "container_parent_index": "jnxContainersWithin", "container_level": "jnxContainersLevel"}
#
#     CONTENT_ATTRIBUTES = {"content_type": "jnxContentsType", "content_description": "jnxContentsDescr",
#                           "content_partno": "jnxContentsRevision", "type": "jnxContentsContainerIndex",
#                           "content_serialno": "jnxContentsSerialNo", "chassis_id": "jnxContentsChassisId"}
#
#     def __init__(self):
#         self.type = None
#         self.type_string = None
#         self.chassis_id = None
#         self.container_level = None
#         self.container_type = "Generic"
#         self.content_type = "Generic"
#         self.container_description = None
#         self.content_description = None
#         self.content_index = None
#         self.relative_path = None
#         self.attributes = {}
#         self.content_partno = None
#         self.content_serialno = None
#         self.container_parent_index = None
#
#     def __str__(self):
#         return "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(self.content_index, self.content_type, self.container_type,
#                                                           self.content_description,
#                                                           self.content_description,
#                                                           self.container_parent_index, self.container_level)


# class Port:
#     ATTRIBUTES_MAP = {"pic": "ifChassisPic", "fpc": "ifChassisFpc", "logical_unit": "ifChassisLogicalUnit",
#                       "type": "ifType", "name": "ifDescr", 'physical_id': 'ifChassisPort'}
#
#     def __init__(self):
#         self.index = None
#         self.pic = None
#         self.type = None
#         self.type_string = None
#         self.fpc = None
#         self.logical_unit = None
#         self.relative_path = None
#         self.name = None
#         self.attributes = {}
#         self.physical_id = None
#
#     def __str__(self):
#         return "{0}, {1}, {2}, {3}".format(self.index, self.fpc, self.pic, self.relative_path)


class JuniperSnmpAutoload(AutoloadOperationsInterface):
    CONTENT_INDEXES = {Chassis: '1', Module: '7', SubModule: '8', PowerPort: '2'}

    FILTER_PORTS_BY_DESCRIPTION = [r'bme', r'vme', r'me', r'vlan']
    FILTER_PORTS_BY_TYPE = ['tunnel', 'other', 'pppMultilinkBundle']

    def __init__(self, snmp_handler=None, logger=None):
        self._ports = {}
        self.sub_modules = {}
        self._modules = {}
        self._chassis = {}
        self._root = RootElement()
        try:
            with open('/tmp/_snmp_cache', 'rb') as ff:
                self._snmp_cache = pickle.load(ff)
        except:
            self._snmp_cache = {}
        self._cache_changed = False
        self._snmp_handler = None
        self.snmp_handler = snmp_handler

        self._ipv4_table = None
        self._ipv6_table = None
        self._if_duplex_table = None
        self._autoneg = None


        # path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        # self._snmp_handler.update_mib_sources(path)
        self._logger = logger
        self.elements = {}
        self.ports = {}
        self.chassis = {}
        self.index_table = {}
        self.snmp_data = {}
        self._chassis_elements_methods_by_index = {'1': self._build_chassis, '2': self._build_power_modules,
                                                   '7': self._build_modules}

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
            self._snmp_handler = snmp_handler
            self._initialize_snmp_handler()

    def _initialize_snmp_handler(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self._snmp_handler.update_mib_sources(path)
        self.logger.info("Loading mibs")
        self.snmp_handler.load_mib('JUNIPER-MIB')
        self.snmp_handler.load_mib('JUNIPER-SMI')
        self.snmp_handler.load_mib('JUNIPER-IF-MIB')
        self.snmp_handler.load_mib('IF-MIB')
        self.snmp_handler.load_mib('JUNIPER-CHASSIS-DEFINES-MIB')
        self.snmp_handler.load_mib('IEEE8023-LAG-MIB')
        self.snmp_handler.load_mib('EtherLike-MIB')
        # self.snmp_handler.load_mib('SNMPv2-MIB')
        self.snmp_handler.load_mib('IP-MIB')
        self.snmp_handler.load_mib('IPV6-MIB')

        # self.logger.info('Start loading MIB tables:')

        # self.snmp_data["system"] = self.snmp_handler.walk(('SNMPv2-MIB', 'system'))
        # self.logger.info('General System information loaded')

        # self.snmp_data["jnxContainersTable"] = self._snmp_handler.walk(('JUNIPER-MIB', 'jnxContainersTable'))
        # self._logger.info('Containers information loaded')
        #
        # self.snmp_data["jnxContentsTable"] = self._snmp_handler.walk(('JUNIPER-MIB', 'jnxContentsTable'))
        # self._logger.info('Contents information loaded')
        #
        # self.snmp_data["ifChassisTable"] = self._snmp_handler.walk(('JUNIPER-IF-MIB', 'ifChassisTable'))
        # self._logger.info('Juniper interfaces chassis information loaded')
        #
        # self.snmp_data["interfaces"] = self._snmp_handler.walk(('IF-MIB', 'interfaces'))
        # self._logger.info('Interfaces information loaded')
        #
        # self.snmp_data["ipAddrTable"] = self._snmp_handler.walk(('IP-MIB', 'ipAddrTable'))
        # self._logger.info('ip v4 address table loaded')
        #
        # self.snmp_data["dot3StatsDuplexStatus"] = self._snmp_handler.walk(('EtherLike-MIB', 'dot3StatsDuplexStatus'))
        # self._logger.info("Duplex table loaded")
        #
        # self.snmp_data["dot3adAggPortTable"] = self._snmp_handler.walk(
        #     ('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'))
        # self._logger.info("Aggregation ports table loaded")

        # with open(os.path.join(os.path.dirname(__file__), 'autoload_debug_file.txt'), 'w') as debug_file:
        #     debug_file.write(str(self.snmp_data))

        # self.ip_v6_table = self.snmp.walk(('IPV6-MIB', 'ipv6AddrEntry'))
        # self._logger.info('ip v6 address table loaded')

        # 'EtherLike-MIB', 'dot3StatsTable'

    def _build_root(self):
        self.logger.info("Building Root")
        vendor = ''
        model = ''
        os_version = ''
        sys_obj_id = self._snmp_request(('SNMPv2-MIB', 'sysObjectID', '0'))
        model_search = re.search('^(?P<vendor>\w+)-\S+jnxProductName(?P<model>\S+)', sys_obj_id
                                 )
        if model_search:
            vendor = model_search.groupdict()['vendor'].capitalize()
            model = model_search.groupdict()['model']
        sys_descr = self._snmp_request(('SNMPv2-MIB', 'sysDescr', '0'))
        os_version_search = re.search('JUNOS \S+(,)?\s', sys_descr, re.IGNORECASE)
        if os_version_search:
            os_version = os_version_search.group(0).replace('JUNOS ', '').replace(',', '').strip(' \t\n\r')
        root_attributes = dict()
        root_attributes[RootAttributes.CONTACT_NAME] = self._snmp_request(('SNMPv2-MIB', 'sysContact', '0'))
        root_attributes[RootAttributes.SYSTEM_NAME] = self._snmp_request(('SNMPv2-MIB', 'sysName', '0'))
        root_attributes[RootAttributes.LOCATION] = self._snmp_request(('SNMPv2-MIB', 'sysLocation', '0'))
        root_attributes[RootAttributes.OS_VERSION] = os_version
        root_attributes[RootAttributes.VENDOR] = vendor
        root_attributes[RootAttributes.MODEL] = model
        self._root.build_attributes(root_attributes)

    def _build_chassis(self):
        self.logger.debug('Building Chassis')
        element_index = '1'
        content_table = self._snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        container_table = self._snmp_request(('JUNIPER-MIB', 'jnxContainersTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == element_index:
                content_data = content_table[key]
                chassis_id = index2
                chassis = Chassis(chassis_id)

                chassis_attributes = dict()
                model_string = self._get_from_table('jnxContainersType', container_table[int(index1)])
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    chassis_attributes[ChassisAttributes.MODEL] = model_list[1]
                else:
                    chassis_attributes[ChassisAttributes.MODEL] = model_string
                chassis_attributes[ChassisAttributes.SERIAL_NUMBER] = self._get_from_table('jnxContentsSerialNo',
                                                                                           content_data)
                chassis.build_attributes(chassis_attributes)
                self._root.chassis.append(chassis)
                self._chassis[self._get_from_table('jnxContentsChassisId', content_data)] = chassis

    def _build_power_modules(self):
        self.logger.debug('Building PowerPorts')
        element_index = '2'
        content_table = self._snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        container_table = self._snmp_request(('JUNIPER-MIB', 'jnxContainersTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == element_index:
                content_data = content_table[key]
                element_id = index2
                element = PowerPort(element_id)

                element_attributes = dict()
                model_string = self._get_from_table('jnxContainersType', container_table[int(index1)])
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[PowerPortAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[PowerPortAttributes.MODEL] = model_string
                element_attributes[PowerPortAttributes.PORT_DESCRIPTION] = self._get_from_table('jnxContentsDescr',
                                                                                                content_data)
                element_attributes[PowerPortAttributes.SERIAL_NUMBER] = self._get_from_table('jnxContentsSerialNo',
                                                                                             content_data)
                element_attributes[PowerPortAttributes.VERSION] = self._get_from_table('jnxContentsRevision',
                                                                                       content_data)
                element.build_attributes(element_attributes)
                chassis_id = self._get_from_table('jnxContentsChassisId', content_data)
                if chassis_id in self._chassis:
                    chassis = self._chassis[chassis_id]
                    chassis.power_ports.append(element)

    def _build_modules(self):
        self.logger.debug('Building Modules')
        element_index = '7'
        content_table = self._snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        container_table = self._snmp_request(('JUNIPER-MIB', 'jnxContainersTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == str(element_index):
                content_data = content_table[key]
                element_id = index2
                element = Module(element_id)

                element_attributes = dict()
                model_string = self._get_from_table('jnxContainersType', container_table[int(index1)])
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[ModuleAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[ModuleAttributes.MODEL] = model_string
                element_attributes[ModuleAttributes.SERIAL_NUMBER] = self._get_from_table('jnxContentsSerialNo',
                                                                                          content_data)
                element_attributes[ModuleAttributes.VERSION] = self._get_from_table('jnxContentsRevision',
                                                                                    content_data)
                element.build_attributes(element_attributes)
                chassis_id = self._get_from_table('jnxContentsChassisId', content_data)
                if chassis_id in self._chassis:
                    chassis = self._chassis[chassis_id]
                    chassis.modules.append(element)
                    self._modules[element_id] = element

    def _build_sub_modules(self):
        self.logger.debug('Building Sub Modules')
        element_index = '8'
        content_table = self._snmp_request(('JUNIPER-MIB', 'jnxContentsTable'))
        container_table = self._snmp_request(('JUNIPER-MIB', 'jnxContainersTable'))
        for key in content_table:
            index1, index2, index3, index = key.split('.')
            if index1 == str(element_index):
                content_data = content_table[key]
                parent_id = index2
                element_id = index3
                element = SubModule(element_id)
                element_attributes = dict()
                model_string = self._get_from_table('jnxContainersType', container_table[int(index1)])
                model_list = model_string.split('::')
                if len(model_list) == 2:
                    element_attributes[SubModuleAttributes.MODEL] = model_list[1]
                else:
                    element_attributes[SubModuleAttributes.MODEL] = model_string
                element_attributes[SubModuleAttributes.SERIAL_NUMBER] = self._get_from_table('jnxContentsSerialNo',
                                                                                             content_data)
                element_attributes[SubModuleAttributes.VERSION] = self._get_from_table('jnxContentsRevision',
                                                                                       content_data)
                element.build_attributes(element_attributes)
                if parent_id in self._modules:
                    self._modules[parent_id].sub_modules.append(element)
                    self.sub_modules[element_id] = element

    def _build_ports(self):
        self.logger.info("Building ports")
        if_chassis_table = self._snmp_request(('JUNIPER-IF-MIB', 'ifChassisTable'))
        if_mib_table = self._snmp_request(('IF-MIB', 'interfaces'))
        # print('dsds')
        # ip_addr_data = sort_elements_by_attributes(self.snmp_data["ipAddrTable"], "ipAdEntIfIndex")
        # juniper_if_mib_data = self.snmp_data["ifChassisTable"]
        # if_mib_data = self.snmp_data["interfaces"]
        # duplex_table = self.snmp_data["dot3StatsDuplexStatus"]

        for index in if_chassis_table:
            if_chassis_data = if_chassis_table[index]
            if_mib_data = if_mib_table[index]
            port_phis_id = self._get_from_table('ifChassisPort', if_chassis_data)
            port_descr = self._get_from_table('ifDescr', if_mib_data)
            port = Port(port_phis_id, self._convert_port_name(port_descr))
            port.logical_unit = self._get_from_table('ifChassisLogicalUnit', if_chassis_data)
            port_attributes = dict()
            port_attributes[PortAttributes.PORT_DESCRIPTION] = self._get_from_table('ifDescr', if_mib_data)
            port_type = self._get_from_table('ifType', if_mib_data)
            port_attributes[PortAttributes.L2_PROTOCOL_TYPE] = port_type
            port.type = port_type
            port_attributes[PortAttributes.MAC_ADDRESS] = self._get_from_table('ifPhysAddress', if_mib_data)
            port_attributes[PortAttributes.MTU] = self._get_from_table('ifMtu', if_mib_data)
            port_attributes[PortAttributes.BANDWIDTH] = self._get_from_table('ifSpeed', if_mib_data)
            port_attributes[PortAttributes.IPV4_ADDRESS] = self._get_associated_port_ipv4_address(index)
            port_attributes[PortAttributes.IPV6_ADDRESS] = self._get_associated_port_ipv6_address(index)
            port_attributes[PortAttributes.PROTOCOL_TYPE] = self._get_from_table('protoType', if_mib_data)
            port_attributes[PortAttributes.DUPLEX] = self._get_port_duplex(index)
            port_attributes[PortAttributes.AUTO_NEGOTIATION] = self._get_port_autoneg(index)
            port_attributes[PortAttributes.ADJACENT] = self._get_port_adjacent(index)
            port.build_attributes(port_attributes)
            self._ports[index] = port
            if not self._port_filtered(port):
                fpc_id = self._get_from_table('ifChassisFpc', if_chassis_data)
                pic_id = self._get_from_table('ifChassisPic', if_chassis_data)
                if fpc_id > 0 and pic_id > 0:
                    if fpc_id in self._modules:
                        fpc = self._modules[fpc_id]
                        pic = self._get_pic_by_index(fpc, pic_id)
                        if pic:
                            pic.ports.append(port)

    def _get_associated_port_ipv4_address(self, port_index):
        if not self._ipv4_table:
            self._ipv4_table = sort_elements_by_attributes(self._snmp_request(('IP-MIB', 'ipAddrTable')),
                                                           'ipAdEntIfIndex')
        ipv4_address = None
        if port_index in self._ipv4_table:
            ipv4_address = self._get_from_table('ipAdEntAddr', self._ipv4_table[port_index])
        return ipv4_address

    def _get_associated_port_ipv6_address(self, port_index):
        if not self._ipv6_table:
            self._ipv6_table = sort_elements_by_attributes(self._snmp_request(('IPV6-MIB', 'ipv6AddrEntry')),
                                                           'ipAdEntIfIndex')
        ipv6_address = None
        if port_index in self._ipv6_table:
            ipv6_address = self._get_from_table('ipAdEntAddr', self._ipv6_table[port_index])
        return ipv6_address

    def _get_port_duplex(self, port_index):
        if not self._if_duplex_table:
            self._if_duplex_table = self._snmp_request(('EtherLike-MIB', 'dot3StatsDuplexStatus'))

        port_duplex = None
        if port_index in self._if_duplex_table:
            port_duplex = self._if_duplex_table[port_index]
        return port_duplex

    def _get_port_autoneg(self, port_index):
        # auto_negotiation = self._snmp_request(('MAU-MIB', 'ifMauAutoNegAdminStatus'))
        # return auto_negotiation
        return None

    def _get_port_adjacent(self, port_index):
        return None

    def _port_filtered(self, port):
        for pattern in self.FILTER_PORTS_BY_DESCRIPTION:
            if re.search(pattern, port.name):
                return True

        if hasattr(port, 'type') and port.type in self.FILTER_PORTS_BY_TYPE:
            return True
        return False






            #     print(index)
        # port = Port()
        # port.index = index
        # port_attributes = deepcopy(juniper_if_mib_data[index])
        # port_attributes.update(if_mib_data[index])
        # if index in duplex_table:
        #     port_attributes.update(duplex_table[index])
        # if index in ip_addr_data:
        #     port_attributes.update(ip_addr_data[index])
        # self._map_attributes(port, Port.ATTRIBUTES_MAP, port_attributes)
        # port.type = port.type.strip("'")
        # if not self._port_filtered(port):
        #     # port.type_string = PORT_DEFINITION[port.type]
        #     if port.type in PORTCHANNEL_TYPES:
        #         port.type_string = 'PORT_CHANNEL'
        #     else:
        #         port.type_string = 'PORT'
        #     self.ports[index] = port

    def _get_pic_by_index(self, fpc, index):
        for pic in fpc.sub_modules:
            if pic.element_id == index:
                return pic
        return None

    # def _build_chassis_elements(self):
    #     self._logger.info("Building chassis elements")
    #     container_data = self.snmp_data["jnxContainersTable"]
    #     content_data = self.snmp_data["jnxContentsTable"]
    #     elements = {}
    #     for index in content_data:
    #         element = Element()
    #         element.content_index = index
    #         elements[index] = element
    #         self._map_attributes(element, Element.CONTENT_ATTRIBUTES, content_data[index])
    #         self._map_attributes(element, Element.CONTAINER_ATTRIBUTES, container_data[int(element.type)])
    #         if element.type in ELEMENT_DEFINITION:
    #             element.type_string = ELEMENT_DEFINITION[element.type]
    #     self.elements = elements

    @staticmethod
    def _convert_port_name(port_name):
        port_name_converted = port_name.replace("/", "-")
        return port_name_converted

    def _build_elements_relative_path(self):
        self._logger.info("Generating relative path for chassis elements")
        # for element in elements:
        level_map = self._sort_by_level(self.elements)
        # for index in sorted([int(key.split('.')[0]) for key in elements.keys()]):
        for level in sorted(level_map):
            for element in level_map[level]:
                self._path_by_content_index(element)

    def _path_by_content_index(self, element):
        if element.type in ELEMENT_DEFINITION:
            index_list = element.content_index.split('.')
            element_index = index_list.pop(0)
            level = element.container_level
            if level is "0":
                element.relative_path = self._get_sutable_relative_path(None)
                self.chassis[element.chassis_id] = element
            elif level is "1":
                chassis_relative_path = self.chassis[element.chassis_id].relative_path
                element.relative_path = self._get_sutable_relative_path(chassis_relative_path)
            else:
                zero_list = []
                for index in reversed(index_list):
                    if index is "0":
                        index_list.pop(-1)
                        zero_list.append("0")
                    else:
                        break
                element_id = index_list.pop(-1)
                zero_list.append("0")
                parent_index = "{0}.{1}".format(element.container_parent_index, ".".join(index_list + zero_list))
                parent_element_relative_path = self.elements[parent_index].relative_path
                element.relative_path = self._get_sutable_relative_path(parent_element_relative_path)

    def _get_suitable_index(self, parent_path):
        if parent_path is None:
            curent_position = self.index_table
        else:
            curent_position = self.index_table
            for path_index in parent_path.split("/"):
                curent_position = curent_position[int(path_index)]
        index = max(curent_position) if curent_position else None
        if index is None:
            index = 0
        else:
            index += 1
        curent_position[index] = {}
        return index

    def _get_sutable_relative_path(self, parent_path):
        index = self._get_suitable_index(parent_path)
        if parent_path is None:
            path = "{0}".format(str(index))
        else:
            path = "{0}/{1}".format(parent_path, str(index))
        return path

    def _is_relative_path_used(self, relative_path):
        is_used = True
        position = self.index_table
        for index in relative_path.split('/'):
            if int(index) in position:
                position = position[int(index)]
            else:
                is_used = False
        return is_used

    def _add_relative_path(self, relative_path):
        position = self.index_table
        path_elements = relative_path.split('/')
        element_index = 0
        for index in range(0, len(path_elements)):
            if int(path_elements[index]) in position:
                position = position[int(path_elements[index])]
            else:
                element_index = index
                break
        for index in range(element_index, len(path_elements)):
            position[int(path_elements[index])] = {}
            position = position[int(path_elements[index])]

    def _get_element_by_relative_path(self, relative_path):
        sorted_by_path = sort_objects_by_attributes(self.elements.values(), 'relative_path')
        return sorted_by_path[relative_path]

    def _sort_by_level(self, elements):
        level_map = {}
        for key in elements:
            if elements[key].container_level in level_map.keys():
                level_map[elements[key].container_level].append(elements[key])
            else:
                level_map[elements[key].container_level] = [elements[key]]
        return level_map

    def build_ports(self):
        self._logger.info("Building ports")
        ip_addr_data = sort_elements_by_attributes(self.snmp_data["ipAddrTable"], "ipAdEntIfIndex")
        juniper_if_mib_data = self.snmp_data["ifChassisTable"]
        if_mib_data = self.snmp_data["interfaces"]
        duplex_table = self.snmp_data["dot3StatsDuplexStatus"]

        for index in juniper_if_mib_data:
            port = Port()
            port.index = index
            port_attributes = deepcopy(juniper_if_mib_data[index])
            port_attributes.update(if_mib_data[index])
            if index in duplex_table:
                port_attributes.update(duplex_table[index])
            if index in ip_addr_data:
                port_attributes.update(ip_addr_data[index])
            self._map_attributes(port, Port.ATTRIBUTES_MAP, port_attributes)
            port.type = port.type.strip("'")
            if not self._port_filtered(port):
                # port.type_string = PORT_DEFINITION[port.type]
                if port.type in PORTCHANNEL_TYPES:
                    port.type_string = 'PORT_CHANNEL'
                else:
                    port.type_string = 'PORT'
                self.ports[index] = port



    def associate_portchannels(self):
        snmp_data = self.snmp_data['dot3adAggPortTable']
        for port_index in snmp_data:
            associated_phisical_port = self._get_associated_phisical_port_by_name(self.ports[int(port_index)].name)
            logical_portchannel_index = snmp_data[port_index]['dot3adAggPortAttachedAggID']
            if logical_portchannel_index and int(logical_portchannel_index) > 0:
                associated_phisical_portchannel = self._get_associated_phisical_port_by_name(
                    self.ports[int(logical_portchannel_index)].name)
                if associated_phisical_portchannel:
                    if associated_phisical_portchannel.type_string != 'PORT_CHANNEL':
                        associated_phisical_portchannel.type_string = 'PORT_CHANNEL'
                    if associated_phisical_port:
                        if 'associatedPorts' in associated_phisical_portchannel.attributes:
                            associated_phisical_portchannel.attributes['associatedPorts'] = '{0},{1}'.format(
                                associated_phisical_portchannel.attributes['associatedPorts'],
                                associated_phisical_port.name.replace("/", "-"))
                        else:
                            associated_phisical_portchannel.attributes['associatedPorts'] = \
                                associated_phisical_port.name.replace("/", "-")

    def _get_associated_phisical_port_by_name(self, name):
        for port in self.ports.values():
            if port.name in name and port.logical_unit is '0':
                return port
        return None

    def _remove_logical_ports(self):
        physical_ports = {}
        for port_index, port in self.ports.iteritems():
            if port.type_string == 'PORT_CHANNEL' or port.physical_id != '0':
                physical_ports[port_index] = port
        self.ports = physical_ports

    def build_ports_relative_path(self):
        self._logger.info("Generating relative path for ports")
        fpc_pic_map = self.sort_elements_by_fpc_pic()
        for port in [p for p in self.ports.values() if p.logical_unit is '0']:
            if port.type_string == 'PORT_CHANNEL':
                pc_id = re.findall(r'\d+', port.name)
                if len(pc_id) > 0:
                    port.relative_path = 'PC' + pc_id[0]
                else:
                    port.relative_path = port.name
            else:
                index = "{0}.{1}".format(port.fpc, port.pic)
                if index in fpc_pic_map:
                    parent_path = fpc_pic_map[index].relative_path
                else:
                    parent_path = self.chassis[self.chassis.keys()[0]].relative_path

                if port.physical_id is not None:
                    port_relative_path = '{0}/{1}'.format(parent_path, port.physical_id)
                else:
                    port_relative_path = self._get_sutable_relative_path(parent_path)
                port.relative_path = port_relative_path
                if self._is_relative_path_used(port_relative_path):
                    element = self._get_element_by_relative_path(port_relative_path)
                    element_n = len(self.ports)
                    suitable_path = '{0}/{1}'.format(parent_path, element_n)
                    while True:
                        if self._is_relative_path_used(suitable_path):
                            element_n += 1
                            suitable_path = '{0}/{1}'.format(parent_path, element_n)
                        else:
                            break
                    element.relative_path = suitable_path
                    self._add_relative_path(suitable_path)
                else:
                    self._add_relative_path(port_relative_path)

    def sort_elements_by_fpc_pic(self):
        elements = {}
        for index in [index for index in self.elements if index.startswith("7") or index.startswith("8")]:
            index_list = index.split('.')
            elements["{0}.{1}".format(index_list[1], index_list[2])] = self.elements[index]
        return elements

    def _map_attributes(self, element, attribute_map, data):
        for attribute in attribute_map:
            setattr(element, attribute, data[attribute_map[attribute]])
        element.attributes.update(deepcopy(data))

    def _generate_description_string(self):
        self._logger.info("Generate description string")
        description_string = RESOURCE_TEMPLATE.format(*RESOURCES_MATRIX_HEADERS)
        for element in [el for el in self.elements.values() if el.type in ELEMENT_DEFINITION]:
            if len(DATAMODEL_ASSOCIATION[element.type_string]) == 2:
                name = "{0} {1}".format(DATAMODEL_ASSOCIATION[element.type_string][1],
                                        element.relative_path.split("/")[-1])
            else:
                name = element.content_description
            description_string += RESOURCE_TEMPLATE.format(DATAMODEL_ASSOCIATION[element.type_string][0],
                                                           name, element.relative_path, "")
        for port in [p for p in self.ports.values() if p.logical_unit is '0']:
            description_string += RESOURCE_TEMPLATE.format(DATAMODEL_ASSOCIATION[port.type_string][0],
                                                           str(port.name).replace("/", "-"), port.relative_path, "")
        return description_string

    def _generate_attribute_string(self):
        self._logger.info("Generate attribute string")
        attribute_string = ""
        for element in [el for el in self.elements.values() if el.type in ELEMENT_DEFINITION]:
            attribute_string += self._get_attribute_string_for_element(element)

        for port in [p for p in self.ports.values() if p.logical_unit is '0']:
            attribute_string += self._get_attribute_string_for_element(port)
        return attribute_string

    def _get_attribute_string_for_element(self, element):
        attribute_string = ""
        attripute_map = ATTRIBUTE_MAPPING[element.type_string]
        for attribute in attripute_map:
            attribute_name = attripute_map[attribute]
            if element.type_string in ATTRIBUTE_PERMANENT_VALUES and attribute in ATTRIBUTE_PERMANENT_VALUES[
                element.type_string]:
                attribute_value = ATTRIBUTE_PERMANENT_VALUES[element.type_string][attribute]
            else:
                attribute_value = element.attributes[attribute] if attribute in element.attributes else None
            if attribute_name and attribute_value:
                attribute_string += RESOURCE_ATTRIBUTE_TEMPLATE.format(element.relative_path, attribute_name,
                                                                       self._cleaning_output(attribute_value))
        return attribute_string

    def _cleaning_output(self, value):
        for pattern in OUTPUT_TABLE:
            if re.search(pattern, value):
                value = OUTPUT_TABLE[pattern](value)
        return value

    def _snmp_request(self, request_data):
        if isinstance(request_data, tuple):
            if request_data in self._snmp_cache:
                result = self._snmp_cache[request_data]
            else:
                if len(request_data) == 2:
                    result = self.snmp_handler.walk(request_data)
                elif len(request_data) > 2:
                    result = self.snmp_handler.get_property(*request_data)
                else:
                    raise Exception('_snmp_request', 'Request tuple len has to be 2 or 3')
                self._snmp_cache[request_data] = result
                self._cache_changed = True
        else:
            raise Exception('_snmp_request', 'Has to be tuple')
        return result

    def _get_from_table(self, key, table):
        if key in table:
            return table[key]
        else:
            return None

            # def discover(self):

            # self._load_tables()
            #
            # self._build_chassis_elements()
            # self._build_elements_relative_path()
            #
            # self.build_ports()
            # self.associate_portchannels()
            # self._remove_logical_ports()
            # self.build_ports_relative_path()
            #
            # result = "{0}${1}{2}".format(self._generate_description_string(), self._get_device_details(),
            #                              self._generate_attribute_string())
            # self._logger.info('*******************************************')
            # self._logger.info('Resource details:')
            #
            # for table in result.split('$'):
            #     self._logger.info('------------------------------')
            #     for line in table.split('|'):
            #         self._logger.info(line.replace('^', '\t\t'))
            #
            # self._logger.info('*******************************************')
            # return result

    def _save_cache(self):
        # count = 0
        # for key in self._snmp_cache:
        #     with open('/tmp/snmp_cache/key_{}'.format(count), 'wb') as ff:
        #         pickle.dump(key, ff, pickle.HIGHEST_PROTOCOL)
        #     with open('/tmp/snmp_cache/value_{}'.format(count), 'wb') as ff:
        #         pickle.dump(self., ff, pickle.HIGHEST_PROTOCOL)
        if self._cache_changed:
            with open('/tmp/_snmp_cache', 'wb') as ff:
                pickle.dump(self._snmp_cache, ff, pickle.HIGHEST_PROTOCOL)

    def discover(self):
        self._build_root()
        self._build_chassis()
        self._build_power_modules()
        self._build_modules()
        self._build_sub_modules()
        self._build_ports()
        # self._build_chassis_elements()
        # self._build_ports()
        # self._build_port_channels()
        # self._root.build_relative_path()
        self._root.build_relative_path()
        self._save_cache()
        autoload_details = AutoLoadDetails(self._root.get_resources(), self._root.get_attributes())
        return autoload_details
