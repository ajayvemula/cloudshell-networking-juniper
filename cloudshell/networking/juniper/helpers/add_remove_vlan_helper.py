from collections import OrderedDict


class AddRemoveVlanHelper(object):
    PORT_NAME_CHAR_REPLACEMENT = OrderedDict([(':', '--'), ('/', '-')])

    @staticmethod
    def convert_port_name(port_name, logger):
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
    def extract_port_name(port, logger):
        """Get port name from port resource full address

        :param port: port resource full address (192.168.1.1/0/34)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """

        port_name = port.split('/')[-1]
        temp_port_name = AddRemoveVlanHelper.convert_port_name(port_name, logger)
        return temp_port_name
