from collections import OrderedDict


class AddRemoveVlanHelper(object):
    PORT_NAME_CHAR_REPLACEMENT = OrderedDict([(':', '--'), ('/', '-')])

    @staticmethod
    def convert_port_name(port_name):
        for char, replacement in AddRemoveVlanHelper.PORT_NAME_CHAR_REPLACEMENT.iteritems():
            port_name = port_name.replace(char, replacement)
        return port_name

    @staticmethod
    def revert_port_name(port_name):
        port_name_splitted = port_name.split('/')[-1].split('-', 1)
        if len(port_name_splitted) == 2:
            port_suffix, port_location = port_name_splitted
            for replacement, value in AddRemoveVlanHelper.PORT_NAME_CHAR_REPLACEMENT.iteritems():
                port_location = port_location.replace(value, replacement)
            port_name = "{0}-{1}".format(port_suffix, port_location)
        elif len(port_name_splitted) == 1:
            port_name = port_name_splitted[0]
        else:
            raise Exception(AddRemoveVlanHelper.__class__.__name__, 'Incorrect port description format')
        return port_name

    @staticmethod
    def extract_port_name(port):
        """Get port name from port resource full address

        :param port: port resource full address (192.168.1.1/0/34)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """

        port_name = port.split('/')[-1]
        temp_port_name = AddRemoveVlanHelper.revert_port_name(port_name)
        return temp_port_name


class VlanRange(object):
    def __init__(self, vlan_range, name=None):
        """
        Vlan range
        :param name:
        :type name: str
        :param vlan_range:
        :type vlan_range: tuple
        """
        self.first_element = int(vlan_range[0])
        self.last_element = int(vlan_range[1])
        if self.first_element > self.last_element:
            raise Exception(self.__class__.__name__, 'Incorrect range')
        if name:
            self.name = name
        else:
            self.name = 'range-{0}-{1}'.format(self.first_element, self.last_element)

    def intersect(self, other):
        """
        Check for intersection
        :param other:
        :type other: VlanRange
        :return:
        """
        return self.first_element <= other.first_element <= self.last_element or self.first_element <= other.last_element <= self.last_element

    def cutoff(self, other):
        """
        Cut other range if intersect
        :param other:
        :type other: VlanRange
        :return:
        :rtype: list
        """
        result = []
        if self.intersect(other):
            if other.first_element <= self.first_element and self.last_element <= other.last_element:
                pass
            elif other.first_element <= self.first_element and other.last_element < self.last_element:
                first = other.last_element + 1
                last = self.last_element
                result.append(VlanRange((first, last)))
            elif self.first_element < other.first_element and self.last_element <= other.last_element:
                first = self.first_element
                last = other.first_element - 1
                result.append(VlanRange((first, last)))
            elif self.first_element < other.first_element and other.last_element < self.last_element:
                first1 = self.first_element
                last1 = other.first_element - 1
                first2 = other.last_element + 1
                last2 = self.last_element
                result.append(VlanRange((first1, last1)))
                result.append(VlanRange((first2, last2)))
        else:
            result.append(self)
        return result

    @staticmethod
    def range_from_string(range_str):
        """
        Range from string
        :param range_str:
        :return:
        """
        _range = range_str.split('-')
        if 1 <= len(_range) <= 2:
            return _range[0], _range[-1]
        else:
            raise Exception(VlanRange.__class__.__name__, 'Incorrect range string')

    def to_string(self):
        """
        Range to string
        :return:
        """
        return '{0}-{1}'.format(self.first_element, self.last_element)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other):
        return self.first_element == other.first_element and self.last_element == other.last_element


class VlanRangeOperations(object):
    @staticmethod
    def create_from_dict(range_dict):
        """
        Create list of ranges from dict
        :param range_dict:
        :return:
        """
        range_list = []
        for name, vlan_range in range_dict.iteritems():
            range_list.append(VlanRange(VlanRange.range_from_string(vlan_range), name=name))
        return range_list

    @staticmethod
    def cutoff_intersection(target_list, source_list):
        """
        Cut intersection
        :param target_list:
        :param source_list:
        :return:
        :rtype: list
        """
        for source_range in source_list:
            new_target_list = []
            for target_range in target_list:
                new_target_list.extend(target_range.cutoff(source_range))
            target_list = new_target_list
        return target_list

    @staticmethod
    def find_intersection(target_list, source_list):
        """
        Find ranges from source which are intersecting with target ranges
        :param target_list:
        :param source_list:
        :return:
        """
        intersection_list = []
        for source_range in source_list:
            for target_range in target_list:
                if target_range.intersect(source_range):
                    intersection_list.append(source_range)
        return intersection_list
