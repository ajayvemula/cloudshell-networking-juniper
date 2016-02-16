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

def build_mib_dict(data, name):
    mib_dict = QualiMibTable(name)
    for key, val in data:
        mib_dict[key] = val
    return mib_dict