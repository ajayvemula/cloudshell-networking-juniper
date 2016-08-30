from cloudshell.snmp.quali_snmp import QualiMibTable


def sort_elements_by_attributes(elements, *attributes):
    sorted_map = {}
    template = ".".join(["{%s}" % x for x in range(0, len(attributes))])
    for value_map in elements.values():
        index_values = [value_map[key] for key in attributes if key in value_map]
        if len(attributes) == len(index_values):
            index = template.format(*index_values)
            sorted_map[index] = value_map
    return sorted_map


def sort_objects_by_attributes(object_list, *attributes):
    sorted_map = {}
    template = ".".join(["{%s}" % x for x in range(0, len(attributes))])
    for obj in object_list:
        index_values = [getattr(obj, key) for key in attributes if hasattr(obj, key) and getattr(obj, key) is not None]
        if len(attributes) == len(index_values):
            index = template.format(*index_values)
            sorted_map[index] = obj
    return sorted_map


def build_mib_dict(data, name):
    mib_dict = QualiMibTable(name)
    for key, val in data:
        mib_dict[key] = val
    return mib_dict


class FakeSnmpHandler:
    def __init__(self, mib_data_map):
        self._mib_data_map = mib_data_map

    def walk(self, request_tuple):
        requested_data = '{0}::{1}'.format(*request_tuple)
        return build_mib_dict(self._mib_data_map[requested_data], requested_data)

    def load_mib(self, mib):
        pass

    def update_mib_sources(self, path):
        pass

    def load_data(self, mib, data):
        self._mib_data_map[mib]=data