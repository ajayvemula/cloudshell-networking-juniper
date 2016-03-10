from cloudshell.networking.juniper.autoload.juniper_snmp_autoload import JuniperSnmpAutoload
from cloudshell.networking.juniper.utils import FakeSnmpHandler
from cloudshell.networking.juniper.examples.autoload_test_data import MIB_DATA_MAP
# from cloudshell.networking.juniper.examples.autoload_srx220h_data import MIB_DATA_MAP
from cloudshell.snmp.quali_snmp import QualiSnmp


# from cloudshell.snmp.quali_snmp import QualiSnmp
#
# ip = "192.168.28.150"
# community = "public"
# snmp_handler = QualiSnmp(ip, community=community)
#

snmp_handler = FakeSnmpHandler(MIB_DATA_MAP)

snmp_autoload = JuniperSnmpAutoload(snmp_handler)
print(snmp_autoload.discover_snmp())
# print(snmp_autoload._get_device_details())
# print(snmp_autoload.ports[599].attributes)

# print(snmp_autoload._generate_description_string())



# print(snmp_autoload.elements)
# snmp_autoload.add_ports_if_attributes(build_mib_dict(NTT_IF_MIB, "if attrs"), build_mib_dict(NTT_JUNIPER_IF_MIB, "if mmm"))

# print('\n'.join(map(str, ['{0}, {1}'.format(element.relative_path, element.type_string) for element in snmp_autoload.elements.values() if element.type in ELEMENT_DEFINITION])))
# print('\n'.join(map(str, [port.attributes["ifDescr"] for port in snmp_autoload.ports.values() if port.relative_path is None and port.logical_unit is "0"])))
# print('\n'.join(map(str, [
#     "{0}, {1}, {2}, {3}".format(port.attributes["ifDescr"], port.attributes["ifType"], port.relative_path,
#                                 port.index) for port in
#     snmp_autoload.ports.values()])))
# print(snmp_autoload.ports[534].attributes)RF159832267CN
# mm={}
# for key in Port.ATTRIBUTE_NAMES:
#     if key in snmp_autoload.ports[520].attributes:
#         mm[key]=Port.ATTRIBUTE_NAMES[key]
# print(mm)
