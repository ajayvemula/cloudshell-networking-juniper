#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os

# from cloudshell.networking.devices.autoload.networking_attributes import RootAttributes, ChassisAttributes, \
#     PowerPortAttributes, \
#     ModuleAttributes, SubModuleAttributes, PortAttributes, PortChannelAttributes
from cloudshell.networking.devices.autoload.networking_model import RootElement, Chassis, Module, SubModule, Port, \
    PowerPort, \
    PortChannel

from cloudshell.networking.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.networking.standards.networking.autoload_structure import *

from cloudshell.networking.juniper.helpers.add_remove_vlan_helper import AddRemoveVlanHelper

from cloudshell.networking.juniper.utils import sort_elements_by_attributes


class JuniperGenericPort(object):
    """
    Collect information and build Port or PortChannel
    """
    PORTCHANNEL_DESCRIPTIONS = ['ae']
    PORT_NAME_CHAR_REPLACEMENT = {'/': '-'}

    AUTOLOAD_MAX_STRING_LENGTH = 100

    JUNIPER_IF_MIB = 'JUNIPER-IF-MIB'
    IF_MIB = 'IF-MIB'
    ETHERLIKE_MIB = 'EtherLike-MIB'

    def __init__(self, index, snmp_handler, shell_name, shell_type, resource_name):
        """
        Create GenericPort with index and snmp handler
        :param index:
        :param snmp_handler:
        :return:
        """
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.associated_port_names = []
        self.index = index
        self._snmp_handler = snmp_handler
        self._resource_name = resource_name

        self._port_phis_id = None
        self._port_description = None
        self._logical_unit = None
        self._fpc_id = None
        self._pic_id = None
        self._type = None

        self.ipv4_addresses = []
        self.ipv6_addresses = []
        if self.port_description[:2] in self.PORTCHANNEL_DESCRIPTIONS:
            self.is_portchannel = True
        else:
            self.is_portchannel = False

        self._port_name_char_replacement = self.PORT_NAME_CHAR_REPLACEMENT
        self._max_string_length = self.AUTOLOAD_MAX_STRING_LENGTH

    def _get_snmp_attribute(self, mib, snmp_attribute):
        return self._snmp_handler.get_property(mib, snmp_attribute, self.index)

    @property
    def port_phis_id(self):
        if not self._port_phis_id:
            self._port_phis_id = self._get_snmp_attribute(self.JUNIPER_IF_MIB, 'ifChassisPort')
        return self._port_phis_id

    @property
    def port_description(self):
        if not self._port_description:
            self._port_description = self._get_snmp_attribute(self.IF_MIB, 'ifDescr')
        return self._port_description

    @property
    def logical_unit(self):
        if not self._logical_unit:
            self._logical_unit = self._get_snmp_attribute(self.JUNIPER_IF_MIB, 'ifChassisLogicalUnit')
        return self._logical_unit

    @property
    def fpc_id(self):
        if not self._fpc_id:
            self._fpc_id = self._get_snmp_attribute(self.JUNIPER_IF_MIB, 'ifChassisFpc')
        return self._fpc_id

    @property
    def pic_id(self):
        if not self._pic_id:
            self._pic_id = self._get_snmp_attribute(self.JUNIPER_IF_MIB, 'ifChassisPic')
        return self._pic_id

    @property
    def type(self):
        if not self._type:
            self._type = self._get_snmp_attribute(self.IF_MIB, 'ifType').strip('\'')
        return self._type

    @property
    def name(self):
        return AddRemoveVlanHelper.convert_port_name(self.port_description)

    def _get_associated_ipv4_address(self):
        return self._validate_attribute_value(','.join(self.ipv4_addresses))

    def _get_associated_ipv6_address(self):
        return self._validate_attribute_value(','.join(self.ipv6_addresses))

    def _validate_attribute_value(self, attribute_value):
        if len(attribute_value) > self._max_string_length:
            attribute_value = attribute_value[:self._max_string_length] + '...'
        return attribute_value

    def _get_port_duplex(self):
        duplex = None
        snmp_result = self._get_snmp_attribute(self.ETHERLIKE_MIB, 'dot3StatsDuplexStatus')
        if snmp_result:
            port_duplex = snmp_result.strip('\'')
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
        """
        Build Port instance using collected information
        :return:
        """
        port = GenericPort(shell_name=self.shell_name,
                           name=self.name,
                           unique_id='{0}.{1}.{2}'.format(self._resource_name, 'port', self.index))

        port.port_description = self.port_description
        port.l2_protocol_type = self.type
        port.mac_address = self._get_snmp_attribute(self.IF_MIB, 'ifPhysAddress')
        port.mtu = self._get_snmp_attribute(self.IF_MIB, 'ifMtu')
        port.bandwidth = self._get_snmp_attribute(self.IF_MIB, 'ifSpeed')
        port.ipv4_address = self._get_associated_ipv4_address()
        port.ipv6_address = self._get_associated_ipv6_address()
        port.protocol_type = self._get_snmp_attribute(self.IF_MIB, 'protoType')
        port.duplex = self._get_port_duplex()
        port.auto_negotiation = self._get_port_autoneg()
        port.adjacent = self._get_port_adjacent()

        return port

    def get_portchannel(self):
        """
        Build PortChannel instance using collected information
        :return:
        """

        port_channel = GenericPortChannel(shell_name=self.shell_name,
                                          name=self.name,
                                          unique_id='{0}.{1}.{2}'.format(self._resource_name, 'port_channel', self.index))

        # port_channel = PortChannel(self.port_phis_id, self.name, unique_id=unique_id)

        port_channel.port_description = self.port_description
        port_channel.ipv4_address = self._get_associated_ipv4_address()
        port_channel.ipv6_address = self._get_associated_ipv6_address()
        port_channel.protocol_type = self._get_snmp_attribute(self.IF_MIB, 'protoType')
        port_channel.associated_ports = ','.join(self.associated_port_names)

        return port_channel


class JuniperSnmpAutoload(object):
    """
    Load inventory by snmp and build device elements and attributes
    """
    FILTER_PORTS_BY_DESCRIPTION = ['bme', 'vme', 'me', 'vlan', 'gr', 'vt', 'mt', 'mams', 'irb', 'lsi', 'tap', 'fxp']
    FILTER_PORTS_BY_TYPE = ['tunnel', 'other', 'pppMultilinkBundle', 'mplsTunnel', 'softwareLoopback']

    # SUPPORTED_OS = [r'[Jj]uniper']

    def __init__(self, snmp_handler, shell_name, shell_type, resource_name, logger):
        self.shell_name = shell_name
        self.shell_type = shell_type
        self._content_indexes = None
        self._if_indexes = None
        self._logger = logger
        self._snmp_handler = snmp_handler
        self._resource_name = resource_name
        self._initialize_snmp_handler()

        self.resource = GenericResource(shell_name=shell_name,
                                        shell_type=shell_type,
                                        name=resource_name,
                                        unique_id=resource_name)
        self._chassis = {}
        self._modules = {}
        self.sub_modules = {}
        self._ports = {}
        self._logical_generic_ports = {}
        self._physical_generic_ports = {}
        self._generic_physical_ports_by_description = None
        self._generic_logical_ports_by_description = None

        self._ipv4_table = None
        self._ipv6_table = None
        self._if_duplex_table = None
        self._autoneg = None

    @property
    def logger(self):
        return self._logger

    @property
    def snmp_handler(self):
        return self._snmp_handler

    @property
    def ipv4_table(self):
        if not self._ipv4_table:
            self._ipv4_table = sort_elements_by_attributes(
                self._snmp_handler.walk(('IP-MIB', 'ipAddrTable')), 'ipAdEntIfIndex')
        return self._ipv4_table

    @property
    def ipv6_table(self):
        if not self._ipv6_table:
            self._ipv6_table = sort_elements_by_attributes(
                self._snmp_handler.walk(('IPV6-MIB', 'ipv6AddrEntry')), 'ipAdEntIfIndex')
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

    def _initialize_snmp_handler(self):
        """
        Snmp settings and load specific mibs
        :return:
        """
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp_handler.update_mib_sources(path)
        self.logger.info("Loading mibs")
        self.snmp_handler.load_mib('JUNIPER-MIB')
        self.snmp_handler.load_mib('JUNIPER-IF-MIB')
        self.snmp_handler.load_mib('IF-MIB')
        self.snmp_handler.load_mib('JUNIPER-CHASSIS-DEFINES-MIB')
        self.snmp_handler.load_mib('IEEE8023-LAG-MIB')
        self.snmp_handler.load_mib('EtherLike-MIB')
        self.snmp_handler.load_mib('IP-MIB')
        self.snmp_handler.load_mib('IPV6-MIB')

    def _build_root(self):
        """
        Collect device root attributes
        :return:
        """
        self.logger.info("Building Root")
        vendor = ''
        model = ''
        os_version = ''
        sys_obj_id = self.snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', 0)
        model_search = re.search('^(?P<vendor>\w+)-\S+jnxProductName(?P<model>\S+)', sys_obj_id
                                 )
        if model_search:
            vendor = model_search.groupdict()['vendor'].capitalize()
            model = model_search.groupdict()['model']
        sys_descr = self.snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
        os_version_search = re.search('JUNOS \S+(,)?\s', sys_descr, re.IGNORECASE)
        if os_version_search:
            os_version = os_version_search.group(0).replace('JUNOS ', '').replace(',', '').strip(' \t\n\r')

        self.resource.contact_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.os_version = os_version
        self.resource.vendor = vendor
        self.resource.model = model

    def _get_content_indexes(self):
        container_indexes = self.snmp_handler.walk(('JUNIPER-MIB', 'jnxContentsContainerIndex'))
        content_indexes = {}
        for index, value in container_indexes.iteritems():
            ct_index = value['jnxContentsContainerIndex']
            if ct_index in content_indexes:
                content_indexes[ct_index].append(index)
            else:
                content_indexes[ct_index] = [index]
        return content_indexes

    @property
    def content_indexes(self):
        if not self._content_indexes:
            self._content_indexes = self._get_content_indexes()
        return self._content_indexes

    @property
    def if_indexes(self):
        if not self._if_indexes:
            self._if_indexes = self.snmp_handler.walk(('JUNIPER-IF-MIB', 'ifChassisPort')).keys()
        return self._if_indexes

    def _build_chassis(self):
        """
        Build Chassis resources and attributes
        :return:
        """
        self.logger.debug('Building Chassis')
        element_index = '1'
        chassis_snmp_attributes = {'jnxContentsModel': 'str', 'jnxContentsType': 'str', 'jnxContentsSerialNo': 'str',
                                   'jnxContentsChassisId': 'str'}
        if element_index in self.content_indexes:
            for index in self.content_indexes[element_index]:
                content_data = self.snmp_handler.get_properties('JUNIPER-MIB', index, chassis_snmp_attributes).get(
                    index)
                index1, index2, index3, index4 = index.split('.')[:4]
                chassis_id = index2

                chassis = GenericChassis(shell_name=self.shell_name,
                                         name="Chassis {}".format(chassis_id),
                                         unique_id="{0}.{1}.{2}".format(self._resource_name, "chassis", index))
                chassis.model = self._get_element_model(content_data)
                chassis.serial_number = content_data.get("jnxContentsSerialNo")

                self.resource.add_sub_resource(chassis_id, chassis)

                chassis_id_str = content_data.get("jnxContentsChassisId")
                if chassis_id_str:
                    self._chassis[chassis_id_str.strip("'")] = chassis

    def _build_power_modules(self):
        """
        Build Power modules resources and attributes
        :return:
        """
        self.logger.debug("Building PowerPorts")
        power_modules_snmp_attributes = {"jnxContentsModel": "str", "jnxContentsType": "str", "jnxContentsDescr": "str",
                                         "jnxContentsSerialNo": "str", "jnxContentsRevision": "str",
                                         "jnxContentsChassisId": "str"}
        element_index = "2"
        if element_index in self.content_indexes:
            for index in self.content_indexes[element_index]:
                content_data = self.snmp_handler.get_properties("JUNIPER-MIB", index,
                                                                power_modules_snmp_attributes).get(index)
                index1, index2, index3, index4 = index.split(".")[:4]
                power_port_id = index2

                power_port = GenericPowerPort(shell_name=self.shell_name,
                                              name="PP{}".format(power_port_id),
                                              unique_id="{0}.{1}.{2}".format(self._resource_name, "power_port", index))

                power_port.model = self._get_element_model(content_data)
                power_port.port_description = content_data.get("jnxContentsDescr")
                power_port.serial_number = content_data.get("jnxContentsSerialNo")
                power_port.version = content_data.get("jnxContentsRevision")

                chassis_id_str = content_data.get("jnxContentsChassisId")
                if chassis_id_str:
                    chassis = self._chassis.get(chassis_id_str.strip("'"))
                    if chassis:
                        chassis.add_sub_resource(power_port_id, power_port)

    def _build_modules(self):
        """
        Build Modules resources and attributes
        :return:
        """
        self.logger.debug("Building Modules")
        modules_snmp_attributes = {"jnxContentsModel": "str",
                                   "jnxContentsType": "str",
                                   "jnxContentsSerialNo": "str",
                                   "jnxContentsRevision": "str",
                                   "jnxContentsChassisId": "str"}
        element_index = "7"
        if element_index in self.content_indexes:
            for index in self.content_indexes[element_index]:
                content_data = self.snmp_handler.get_properties("JUNIPER-MIB", index,
                                                                modules_snmp_attributes).get(index)
                index1, index2, index3, index4 = index.split(".")[:4]
                module_id = index2

                module = GenericModule(shell_name=self.shell_name,
                                       name="Module {}".format(module_id),
                                       unique_id="{0}.{1}.{2}".format(self._resource_name, "module", index))

                module.model = self._get_element_model(content_data)
                module.serial_number = content_data.get("jnxContentsSerialNo")
                module.version = content_data.get("jnxContentsRevision")

                chassis_id_str = content_data.get("jnxContentsChassisId")
                if chassis_id_str:
                    chassis = self._chassis.get(chassis_id_str.strip("'"))
                    if chassis:
                        chassis.add_sub_resource(module_id, module)
                        self._modules[module_id] = module

    def _build_sub_modules(self):
        """
        Build SubModules resources and attributes
        :return:
        """
        self.logger.debug("Building Sub Modules")
        sub_modules_snmp_attributes = {"jnxContentsModel": "str",
                                       "jnxContentsType": "str",
                                       "jnxContentsSerialNo": "str",
                                       "jnxContentsRevision": "str"}

        element_index = "8"
        if element_index in self.content_indexes:
            for index in self.content_indexes[element_index]:
                content_data = self.snmp_handler.get_properties("JUNIPER-MIB", index,
                                                                sub_modules_snmp_attributes).get(index)
                index1, index2, index3, index4 = index.split(".")[:4]
                parent_id = index2
                sub_module_id = index3

                sub_module = GenericSubModule(shell_name=self.shell_name,
                                              name="SubModule {}".format(sub_module_id),
                                              unique_id="{0}.{1}.{2}".format(self._resource_name, "sub_module", index))

                sub_module.model = self._get_element_model(content_data)
                sub_module.serial_number = content_data.get("jnxContentsSerialNo")
                sub_module.version = content_data.get("jnxContentsRevision")

                if parent_id in self._modules:
                    self._modules[parent_id].add_sub_resource(sub_module_id, sub_module)
                    self.sub_modules[sub_module_id] = sub_module

    @staticmethod
    def _get_element_model(content_data):
        model_string = content_data.get('jnxContentsModel')
        if not model_string:
            model_string = content_data.get('jnxContentsType').split('::')[-1]
        return model_string

    def _build_generic_ports(self):
        """
        Build JuniperGenericPort instances
        :return:
        """
        self.logger.debug("Building generic ports")

        for index in self.if_indexes:
            index = int(index)
            generic_port = JuniperGenericPort(index, self.snmp_handler, self._resource_name)
            if not self._port_filtered_by_description(generic_port) and not self._port_filtered_by_type(generic_port):
                if generic_port.logical_unit == '0':
                    self._physical_generic_ports[index] = generic_port
                else:
                    self._logical_generic_ports[index] = generic_port

    def _associate_ipv4_addresses(self):
        """
        Associates ipv4 with generic port
        :return:
        """
        self.logger.debug("Associate ipv4")
        for index in self.ipv4_table:
            if int(index) in self._logical_generic_ports:
                logical_port = self._logical_generic_ports[int(index)]
                physical_port = self._get_associated_phisical_port_by_description(logical_port.port_description)
                ipv4_address = self.ipv4_table[index].get('ipAdEntAddr')
                if physical_port and ipv4_address:
                    physical_port.ipv4_addresses.append(ipv4_address)

    def _associate_ipv6_addresses(self):
        """
        Associate ipv6 with generic port
        :return:
        """
        self.logger.debug("Associate ipv6")
        for index in self.ipv6_table:
            if int(index) in self._logical_generic_ports:
                logical_port = self._logical_generic_ports[int(index)]
                physical_port = self._get_associated_phisical_port_by_description(logical_port.port_description)
                ipv6_address = self.ipv6_table[index].get('ipAdEntAddr')
                if ipv6_address:
                    physical_port.ipv6_addresses.append(ipv6_address)

    def _associate_portchannels(self):
        """
        Associate physical ports with the portchannel
        :return:
        """
        self.logger.debug("Associate portchannels")
        snmp_data = self._snmp_handler.walk(('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'))
        for port_index in snmp_data:
            port_index = int(port_index)
            if port_index in self._logical_generic_ports:
                associated_phisical_port = self._get_associated_phisical_port_by_description(
                    self._logical_generic_ports[port_index].port_description)
                logical_portchannel_index = snmp_data[port_index].get('dot3adAggPortAttachedAggID')
                if logical_portchannel_index and int(logical_portchannel_index) in self._logical_generic_ports:
                    associated_phisical_portchannel = self._get_associated_phisical_port_by_description(
                        self._logical_generic_ports[int(logical_portchannel_index)].port_description)
                    if associated_phisical_portchannel:
                        associated_phisical_portchannel.is_portchannel = True
                        if associated_phisical_port:
                            associated_phisical_portchannel.associated_port_names.append(associated_phisical_port.name)

    def _get_associated_phisical_port_by_description(self, description):
        """
        Associate physical port by description
        :param description:
        :return:
        """
        for port_description in self.generic_physical_ports_by_description:
            if port_description in description:
                return self.generic_physical_ports_by_description[port_description]
        return None

    def _port_filtered_by_description(self, port):
        """
        Filter ports by description
        :param port:
        :return:
        """
        for pattern in self.FILTER_PORTS_BY_DESCRIPTION:
            if re.search(pattern, port.port_description):
                return True
        return False

    def _port_filtered_by_type(self, port):
        """
        Filter ports by type
        :param port:
        :return:
        """
        if port.type in self.FILTER_PORTS_BY_TYPE:
            return True
        return False

    def _build_ports(self):
        """
        Associate ports with the structure resources and build Ports and PortChannels
        :return:
        """
        self.logger.debug("Building ports")
        self._build_generic_ports()
        self._associate_ipv4_addresses()
        self._associate_ipv6_addresses()
        self._associate_portchannels()
        for generic_port in self._physical_generic_ports.values():
            if generic_port.is_portchannel:
                self.resource.add_sub_resource(generic_port.port_phis_id, generic_port.get_portchannel())
                # self._root.port_channels.append(generic_port.get_portchannel())
            else:
                port = generic_port.get_port()
                if generic_port.fpc_id > 0 and generic_port.fpc_id in self._modules:
                    fpc = self._modules.get(generic_port.fpc_id)
                    if fpc and generic_port.pic_id > 0:
                        pic = self._get_pic_by_index(fpc, int(generic_port.pic_id))
                        if pic:
                            pic.add_sub_resource(generic_port.port_phis_id, port)
                            # pic.ports.append(port)
                        else:
                            self.logger.info('Port {} is not allowed'.format(port.name))
                    else:
                        fpc.add_sub_resource(generic_port.port_phis_id, port)
                        # fpc.ports.append(port)
                else:
                    chassis = self._chassis.values()[0]
                    chassis.add_sub_resource(generic_port.port_phis_id, port)
                    # chassis.ports.append(generic_port.get_port())

    def _get_pic_by_index(self, fpc, index):
        for pic in fpc.sub_modules:
            if pic.element_id == index:
                return pic
        return None

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp
            :return: True or False
        """

        system_description = self.snmp_handler.get_property('SNMPv2-MIB', 'sysDescr', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))
        result = re.search(r"({0})".format("|".join(supported_os)),
                           system_description,
                           flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for \'{0}\' operation system(s)'. \
                format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _log_autoload_details(self, autoload_details):
        """
        Logging autoload details
        :param autoload_details:
        :return:
        """
        self.logger.debug('-------------------- <RESOURCES> ----------------------')
        for resource in autoload_details.resources:
            self.logger.debug(
                '{0}, {1}, {2}'.format(resource.relative_address, resource.name, resource.unique_identifier))
        self.logger.debug('-------------------- </RESOURCES> ----------------------')

        self.logger.debug('-------------------- <ATTRIBUTES> ---------------------')
        for attribute in autoload_details.attributes:
            self.logger.debug('-- {0}, {1}, {2}'.format(attribute.relative_address, attribute.attribute_name,
                                                        attribute.attribute_value))
        self.logger.debug('-------------------- </ATTRIBUTES> ---------------------')

    def discover(self, supported_os):
        """
        Call methods in specific order to build resources and attributes
        :return:
        """

        if not self._is_valid_device_os(supported_os):
            raise Exception(self.__class__.__name__, 'Unsupported device OS')

        self._build_root()
        self._build_chassis()
        self._build_power_modules()
        self._build_modules()
        self._build_sub_modules()
        self._build_ports()
        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        # autoload_details = self._root.get_autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details
