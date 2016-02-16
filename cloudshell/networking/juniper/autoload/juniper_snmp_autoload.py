from copy import deepcopy

import re
from cloudshell.networking.juniper.utils import sort_elements_by_attributes
from cloudshell.core.logger import qs_logger

ATTRIBUTE_MAPPING = {"PORT": {'ifType': 'L2 Protocol Type', 'ifPhysAddress': 'MAC Address', 'ifMtu': 'MTU',
                              'ifSpeed': 'Bandwidth', 'ifDescr': "Port Description", "ipAdEntAddr": "IPv4 Address",
                              "protoType": "Protocol Type", "dot3StatsDuplexStatus": "Duplex",
                              "autoNegotiation": "Auto Negotiation",
                              },
                     "PORT_CHANNEL": {'ifType': 'L2 Protocol Type', 'ifPhysAddress': 'MAC Address', 'ifMtu': 'MTU',
                                      'ifSpeed': 'Bandwidth'},
                     "CHASSIS": {"jnxContainersType": "Model", "jnxContentsSerialNo": "Serial Number"},
                     "MODULE": {"jnxContentsType": "Model", "jnxContentsRevision": "Version",
                                "jnxContentsSerialNo": "Serial Number"},
                     "SUB_MODULE": {"jnxContentsType": "Model", "jnxContentsRevision": "Version",
                                    "jnxContentsSerialNo": "Serial Number"},
                     "POWER_MODULE": {"jnxContentsType": "Model", "jnxContentsSerialNo": "Serial Number",
                                      "jnxContentsDescr": "Port Description", "jnxContentsPartNo": "Version"},
                     }

ATTRIBUTE_PERMANENT_VALUES = {"PORT": {'protoType': 'Transparent', "autoNegotiation": "True",
                                       "dot3StatsDuplexStatus": "Full"}}

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
PORT_DEFINITION = {"ethernetCsmacd": "PORT"}


class Element:
    CONTAINER_ATTRIBUTES = {"container_type": "jnxContainersType", "container_description": "jnxContainersDescr",
                            "container_parent_index": "jnxContainersWithin", "container_level": "jnxContainersLevel"}

    CONTENT_ATTRIBUTES = {"content_type": "jnxContentsType", "content_description": "jnxContentsDescr",
                          "content_partno": "jnxContentsPartNo", "type": "jnxContentsContainerIndex",
                          "content_serialno": "jnxContentsSerialNo", "chassis_id": "jnxContentsChassisId"}

    def __init__(self):
        self.type = None
        self.type_string = None
        self.chassis_id = None
        self.container_level = None
        self.container_type = "Generic"
        self.content_type = "Generic"
        self.container_description = None
        self.content_description = None
        self.content_index = None
        self.relative_path = None
        self.attributes = {}
        self.content_partno = None
        self.content_serialno = None
        self.container_parent_index = None

    def __str__(self):
        return "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(self.content_index, self.content_type, self.container_type,
                                                          self.content_description,
                                                          self.content_description,
                                                          self.container_parent_index, self.container_level)


class Port:
    ATTRIBUTES_MAP = {"pic": "ifChassisPic", "fpc": "ifChassisFpc", "logical_unit": "ifChassisLogicalUnit",
                      "type": "ifType"}

    def __init__(self):
        self.index = None
        self.pic = None
        self.type = None
        self.type_string = None
        self.fpc = None
        self.logical_unit = None
        self.relative_path = None
        self.attributes = {}

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.index, self.fpc, self.pic, self.relative_path)


class JuniperSnmpAutoload:
    def __init__(self, snmp_handler, logger=None):
        self._snmp_handler = snmp_handler
        self._logger = logger or qs_logger.getQSLogger()
        self.elements = {}
        self.ports = {}
        self.chassis = {}
        self.index_table = {}
        self.snmp_data = {}

    def _load_tables(self):
        self._logger.info("Loading mibs")
        self._snmp_handler.load_mib('JUNIPER-MIB')
        self._snmp_handler.load_mib('JUNIPER-SMI')
        self._snmp_handler.load_mib('JUNIPER-IF-MIB')
        self._snmp_handler.load_mib('IF-MIB')
        self._snmp_handler.load_mib('JUNIPER-CHASSIS-DEFINES-MIB')
        self._snmp_handler.load_mib('IEEE8023-LAG-MIB')

        self._logger.info('Start loading MIB tables:')

        self.snmp_data["system"] = self._snmp_handler.walk(('SNMPv2-MIB', 'system'))
        self._logger.info('General System information loaded')

        self.snmp_data["jnxContainersTable"] = self._snmp_handler.walk(('JUNIPER-MIB', 'jnxContainersTable'))
        self._logger.info('Containers information loaded')

        self.snmp_data["jnxContentsTable"] = self._snmp_handler.walk(('JUNIPER-MIB', 'jnxContentsTable'))
        self._logger.info('Contents information loaded')

        self.snmp_data["ifChassisTable"] = self._snmp_handler.walk(('JUNIPER-IF-MIB', 'ifChassisTable'))
        self._logger.info('Juniper interfaces chassis information loaded')

        self.snmp_data["interfaces"] = self._snmp_handler.walk(('IF-MIB', 'interfaces'))
        self._logger.info('Interfaces information loaded')

        self.snmp_data["ipAddrTable"] = self._snmp_handler.walk(('IP-MIB', 'ipAddrTable'))
        self._logger.info('ip v4 address table loaded')

        # self.ip_v6_table = self.snmp.walk(('IPV6-MIB', 'ipv6AddrEntry'))
        # self._logger.info('ip v6 address table loaded')

        # 'EtherLike-MIB', 'dot3StatsTable'

    def _build_chassis_elements(self):
        self._logger.info("Building chassis elements")
        container_data = self.snmp_data["jnxContainersTable"]
        content_data = self.snmp_data["jnxContentsTable"]
        elements = {}
        for index in content_data:
            element = Element()
            element.content_index = index
            elements[index] = element
            self._map_attributes(element, Element.CONTENT_ATTRIBUTES, content_data[index])
            self._map_attributes(element, Element.CONTAINER_ATTRIBUTES, container_data[int(element.type)])
            if element.type in ELEMENT_DEFINITION:
                element.type_string = ELEMENT_DEFINITION[element.type]
        self.elements = elements

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
        ports = {}
        for index in juniper_if_mib_data:
            port = Port()
            port.index = index
            port_attributes = deepcopy(juniper_if_mib_data[index])
            port_attributes.update(if_mib_data[index])
            if index in ip_addr_data:
                port_attributes.update(ip_addr_data[index])
            self._map_attributes(port, Port.ATTRIBUTES_MAP, port_attributes)
            if port.type.strip("'") in PORT_DEFINITION and port.logical_unit is "0":
                port.type_string = PORT_DEFINITION[port.type.strip("'")]
                ports[index] = port
        return ports

    def build_ports_relative_path(self):
        self._logger.info("Generating relative path for ports")
        fpc_pic_map = self.sort_elements_by_fpc_pic()
        for port in self.ports.values():
            index = "{0}.{1}".format(port.fpc, port.pic)
            if index in fpc_pic_map:
                parent_path = fpc_pic_map[index].relative_path
                port.relative_path = self._get_sutable_relative_path(parent_path)
            else:
                parent_path = self.chassis[self.chassis.keys()[0]].relative_path
                port.relative_path = self._get_sutable_relative_path(parent_path)

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
        for port in self.ports.values():
            description_string += RESOURCE_TEMPLATE.format(DATAMODEL_ASSOCIATION[port.type_string][0],
                                                           str(port.attributes[
                                                                   ATTRIBUTE_DESCRIPTION[port.type_string]]).replace(
                                                               "/", "-"),
                                                           port.relative_path, "")
        return description_string

    def _generate_attribute_string(self):
        self._logger.info("Generate attribute string")
        attribute_string = ""
        for element in [el for el in self.elements.values() if el.type in ELEMENT_DEFINITION] + \
                [port for port in self.ports.values()]:
            attribute_string += self._get_attribute_string_for_element(element)
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
            attribute_string += RESOURCE_ATTRIBUTE_TEMPLATE.format(element.relative_path, attribute_name,
                                                                   attribute_value)
        return attribute_string

    def _get_device_details(self):
        self._logger.info("Generate device details string")
        details_string = ""
        vendor = ''
        model = ''
        os_version = ''
        # self._logger.info('Start loading Switch Attributes')
        # result = self.snmp_data["system"][0]["sysDescr"]
        model_search = re.search('^(?P<vendor>\w+)-\S+jnxProductName(?P<model>\S+)',
                                 self.snmp_data["system"][0]["sysObjectID"])
        if model_search:
            vendor = model_search.groupdict()['vendor'].capitalize()
            model = model_search.groupdict()['model']
        os_version_search = re.search('JUNOS \S+(,)?\s', self.snmp_data["system"][0]["sysDescr"], re.IGNORECASE)
        if os_version_search:
            os_version = os_version_search.group(0).replace('JUNOS ', '').replace(',', '').strip(' \t\n\r')

        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "System Name", self.snmp_data["system"][0]["sysName"])
        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "Contact Name",
                                                             self.snmp_data["system"][0]["sysContact"])
        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "OS Version", os_version)
        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "Vendor", vendor)
        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "Location", self.snmp_data["system"][0]["sysLocation"])
        details_string += RESOURCE_ATTRIBUTE_TEMPLATE.format("", "Model", model)
        return details_string

    def get_inventory(self):

        self._load_tables()

        self._build_chassis_elements()
        self._build_elements_relative_path()

        self.ports = self.build_ports()
        self.build_ports_relative_path()

        result = "{0}${1}{2}".format(self._generate_description_string(), self._get_device_details(),
                                     self._generate_attribute_string())
        self._logger.info('*******************************************')
        self._logger.info('Resource details:')

        for table in result.split('$'):
            self._logger.info('------------------------------')
            for line in table.split('|'):
                self._logger.info(line.replace('^', '\t\t'))

        self._logger.info('*******************************************')
        return result


if __name__ == '__main__':
    from cloudshell.networking.juniper.utils import FakeSnmpHandler
    from cloudshell.networking.juniper.examples.autoload_test_data import MIB_DATA_MAP

    fake_smp_handler = FakeSnmpHandler(MIB_DATA_MAP)
    snmp_autoload = JuniperSnmpAutoload(fake_smp_handler)
    print(snmp_autoload.get_inventory())
    # print(snmp_autoload._get_device_details())


    # print(snmp_autoload._generate_description_string())



    # print(snmp_autoload.elements)
    # snmp_autoload.add_ports_if_attributes(build_mib_dict(NTT_IF_MIB, "if attrs"), build_mib_dict(NTT_JUNIPER_IF_MIB, "if mmm"))

    # print('\n'.join(map(str, [element.relative_path for element in snmp_autoload.elements.values()])))
    # print('\n'.join(map(str, [port.attributes["ifDescr"] for port in snmp_autoload.ports.values() if port.relative_path is None and port.logical_unit is "0"])))
    # print('\n'.join(map(str, [
    #     "{0}, {1}, {2}, {3}".format(port.attributes["ifDescr"], port.attributes["ifType"], port.relative_path,
    #                                 port.index) for port in
    #     snmp_autoload.ports.values()])))
    # print(snmp_autoload.ports[534].attributes)
    # mm={}
    # for key in Port.ATTRIBUTE_NAMES:
    #     if key in snmp_autoload.ports[520].attributes:
    #         mm[key]=Port.ATTRIBUTE_NAMES[key]
    # print(mm)
