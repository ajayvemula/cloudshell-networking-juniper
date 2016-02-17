import json
# Do not remove!
from cloudshell.networking.resource_driver.networking_generic_resource_dirver import networking_generic_resource_driver
from cloudshell.networking.networking_base import NetworkingBase, DriverFunction
from cloudshell.shell.core.handler_factory import HandlerFactory

from cloudshell.networking.platform_detector.hardware_platform_detector import HardwarePlatformDetector

class juniper_generic_resource_driver(networking_generic_resource_driver):
    ATTRIBUTE_MATRIX = {
        "resource": ["ResourceAddress", "User", "Password", "Enable Password", "Console Server IP Address",
                     "Console User", "Console Password", "Console Port", "CLI Connection Type",
                     "SNMP Version", "SNMP Read Community", "SNMP V3 User", "SNMP V3 Password",
                     "SNMP V3 Private Key"]}

    @staticmethod
    def create_snmp_helper(host, json_object_resource, logger):

        snmp_helper = HardwarePlatformDetector(host,
                                                 json_object_resource['SNMP V3 User'],
                                                 json_object_resource['SNMP V3 Password'],
                                                 json_object_resource['SNMP Read Community'],
                                                 json_object_resource['SNMP Version'],
                                                 json_object_resource['SNMP V3 Private Key'],
                                                 logger,
                                                 )
        return snmp_helper

    def __detect_hardware_platform(self, snmp_handler):
        if snmp_handler:
            self.temp_snmp_handler = snmp_handler.snmp
            return snmp_handler._detect_hardware_platform()
        return None

    def __check_for_attributes_changes(self, matrixJSON):
        """Verify if resource and/re reservation details changed, update handler accordingly

        :param matrixJSON:
        :return:
        """
        json_object = json.loads(matrixJSON)
        self._resource_handler._logger.info('Self MATRIX = {0}'.format(self._json_matrix))
        self._resource_handler._logger.info('NEW MATRIX = {0}'.format(json_object))

        handler_params = self.get_handler_parameters_from_json(json_object)

        for matrix_key in json_object.keys():
            matrix = json_object[matrix_key]
            for key, val in matrix.iteritems():
                if not key in self._json_matrix[matrix_key].keys():
                    # skip extra parameters, compare only existing keys
                    pass
                elif self._json_matrix[matrix_key][key] != matrix[key]:
                    if key in ['User', 'Password', 'ResourceAddress', 'CLI Connection Type', 'ReservationId']:
                        # Init handler again
                        self.Init(matrixJSON)
                        return

                    elif key in ['SNMP V3 User', 'SNMP V3 Password', 'SNMP Read Community', 'SNMP Version',
                                 'SNMP V3 Private Key']:
                        # create new SNMP handler
                        current_logger = self._resource_handler._logger
                        snmp_helper = juniper_generic_resource_driver.create_snmp_helper(handler_params['host'],
                                                                                         json_object['resource'],
                                                                                         current_logger)
                        self._resource_handler._snmp_handler = snmp_helper.snmp

    def get_handler_parameters_from_json(self, json_object):
        """ Assosiate json matrix parameters with required handler_params

        :param json_object:
        :return:
        """

        logger_params = {'handler_name': self.resource_name,
                         'reservation_details': json_object['reservation']}
        handler_params = {}
        handler_params['username'] = json_object['resource']['User'].encode('ascii', errors='backslashreplace')
        handler_params['password'] = json_object['resource']['Password'].encode('ascii', errors='backslashreplace')
        handler_params['logger_params'] = logger_params

        address_elements = json_object['resource']['ResourceAddress'].encode('ascii', errors='backslashreplace').split(
            ':')
        handler_params['host'] = address_elements[0]
        if len(address_elements) > 1:
            handler_params['port'] = int(address_elements[1])

        handler_params['enable_password'] = json_object['resource']['Enable Password'].encode('ascii',
                                                                                              errors='backslashreplace')
        handler_params['console_server_ip'] = json_object['resource']['Console Server IP Address'].encode('ascii',
                                                                                                          errors='backslashreplace')
        handler_params['console_server_user'] = json_object['resource']['Console User'].encode('ascii',
                                                                                               errors='backslashreplace')
        handler_params['console_server_password'] = json_object['resource']['Console Password'].encode('ascii',
                                                                                                       errors='backslashreplace')
        handler_params['console_port'] = json_object['resource']['Console Port'].encode('ascii',
                                                                                        errors='backslashreplace')
        handler_params['session_handler_name'] = json_object['resource']['CLI Connection Type'].encode('ascii',
                                                                                                       errors='backslashreplace')
        if len(handler_params['session_handler_name']) == 0:
            handler_params['session_handler_name'] = 'auto'

        return handler_params

    @DriverFunction(extraMatrixRows=ATTRIBUTE_MATRIX)
    def Init(self, matrixJSON):

        json_object = json.loads(matrixJSON)
        self._json_matrix = json_object
        self.resource_name = 'generic_resource'
        # self.handler_name = 'generic_driver'
        if not self.handler_name:
            self.handler_name = 'generic_driver'
        self.temp_snmp_handler = None

        # if not self.handler_name:
        #    #ToDo Decide sould we prohibid direct usage of this class
        #    self.handler_name = 'generic_driver'

        # set initial reservation ID to 'Autoload' will be used if not other provided.
        self.reservation_id = 'Autoload'

        if 'ResourceName' in json_object['resource'] and not json_object['resource']['ResourceName'] is None:
            self.resource_name = json_object['resource']['ResourceName']

        if 'reservation' in json_object:
            if 'ReservationId' in json_object['reservation'] and not json_object['reservation'][
                'ReservationId'] is None:
                self.reservation_id = json_object['reservation']['ReservationId']
        else:
            json_object['reservation'] = {}
            json_object['reservation']['ReservationId'] = self.reservation_id

        handler_params = self.get_handler_parameters_from_json(json_object)
        detected_platform_name = None
        if 'Filename' in json_object['resource'] and json_object['resource']['Filename'] != '':
            handler_params['session_handler_name'] = 'file'
            handler_params['filename'] = json_object['resource']['Filename']
            if 'HandlerName' in json_object['resource'] and json_object['resource']['HandlerName'] != '':
                detected_platform_name = json_object['resource']['HandlerName']
        else:
            driver_logger = HandlerFactory.get_logger(self.handler_name, logger_params=handler_params['logger_params'])
            handler_params['logger'] = driver_logger

            tmp_snmp_handler = juniper_generic_resource_driver.create_snmp_helper(handler_params['host'],
                                                                                  json_object['resource'],
                                                                                  driver_logger)
            detected_platform_name = self.__detect_hardware_platform(tmp_snmp_handler)

        if detected_platform_name:
            self.handler_name = detected_platform_name


        self._resource_handler = HandlerFactory.create_handler(self.handler_name, **handler_params)
        self._resource_handler._logger.info('Created resource handle {0}'.format(self.handler_name.upper()))

        self._resource_handler.set_parameters(json_object)

        if self.temp_snmp_handler:
            self._resource_handler._snmp_handler = self.temp_snmp_handler

        # return 'Log Path: {0}'.format(self._resource_handler._logger.handlers[0].baseFilename)

    @DriverFunction(alias='Get Inventory', extraMatrixRows=ATTRIBUTE_MATRIX)
    def GetInventory(self, matrixJSON):
        """
        Return device structure with all standard attributes
        :return: result
        :rtype: string
        """
        # result = self._resource_handler.discover_snmp()
        # return self._resource_handler.normalize_output(result)
        return self._resource_handler.discover_snmp()

    @DriverFunction(alias='Update Firmware', extraMatrixRows=ATTRIBUTE_MATRIX)
    def UpdateFirmware(self, matrixJSON, remote_host, file_path):
        """
        Upload and updates firmware on the resource
        :return: result
        :rtype: string
        """
        result_str = self._resource_handler.update_firmware(remote_host, file_path)
        self._resource_handler.disconnect()
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Save', extraMatrixRows=ATTRIBUTE_MATRIX)
    def Save(self, matrixJSON, destination_host, source_filename):
        """
        Backup configuration
       :return: success string with saved file name
        :rtype: string
        """
        result_str = self._resource_handler.backup_configuration(destination_host, source_filename)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Restore', extraMatrixRows=ATTRIBUTE_MATRIX)
    def Restore(self, matrixJSON, source_file, clear_config='no'):
        """
        Restore configuration
        :return: success string
        :rtype: string
        """
        result_str = self._resource_handler.restore_configuration(source_file, clear_config)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Send Command', extraMatrixRows=ATTRIBUTE_MATRIX)
    def SendCommand(self, matrixJSON, command):
        """
        Send custom command
        :return: result
        :rtype: string
        """
        self.__check_for_attributes_changes(matrixJSON)
        result_str = self._resource_handler.send_command(cmd=command)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Add Vlan', category='Hidden Commands', extraMatrixRows=ATTRIBUTE_MATRIX)
    def Add_VLAN(self, matrixJSON, ports, vlan_range, switchport_type, additional_info):
        """
        Assign vlan or vlan range to the certain interface
        :return: result
        :rtype: string
        """

        self.__check_for_attributes_changes(matrixJSON)
        result_str = self._resource_handler.configure_vlan(ports=ports,
                                                           vlan_range=vlan_range, switchport_type=switchport_type,
                                                           additional_info=additional_info, remove=False)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Remove Vlan', category='Hidden Commands', extraMatrixRows=ATTRIBUTE_MATRIX)
    def Remove_VLAN(self, matrixJSON, ports, vlan_range, switchport_type, additional_info):
        """
        Remove vlan or vlan range from the certain interface
        :return: result
        :rtype: string
        """
        self.__check_for_attributes_changes(matrixJSON)

        result_str = self._resource_handler.configure_vlan(ports=ports,
                                                           vlan_range=vlan_range, switchport_type=switchport_type,
                                                           additional_info=additional_info, remove=True)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Send Config Command', category='Hidden Commands', extraMatrixRows=ATTRIBUTE_MATRIX)
    def SendConfigCommand(self, matrixJSON, command):
        self.__check_for_attributes_changes(matrixJSON)

        result_str = self._resource_handler.sendConfigCommand(cmd=command)
        return self._resource_handler.normalize_output(result_str)

    @DriverFunction(alias='Reset Driver', extraMatrixRows=ATTRIBUTE_MATRIX)
    def ResetDriver(self, matrix_json):
        self.__check_for_attributes_changes(matrix_json)
        self.Init(matrix_json)
        return 'Driver reset completed'


if __name__ == '__main__':
    data_json = str("""{
            "resource" : {

                    "ResourceAddress": "192.168.42.217:2022",
                    "User": "quali",
                    "Password": "quali0033",
                    "CLI Connection Type": "auto",
                    "Console User": "",
                    "Console Password": "",
                    "Console Server IP Address": "",
                    "ResourceName" : "Juniper-2",
                    "ResourceFullName" : "Juniper-2",
                    "Enable Password": "",
                    "Console Port": "",
                    "SNMP Read Community": "sdnsdn",
                    "SNMP Version": "",
                    "SNMP V3 Password": "",
                    "SNMP V3 User": "",
                    "SNMP V3 Private Key": ""
                },
            "reservation" : {

                    "Username" : "admin",
                    "Password" : "admin",
                    "Domain" : "Global",
                    "AdminUsername" : "admin",
                    "AdminPassword" : "admin"}
            }""")
    # "ReservationId" : "94e31679-7262-4ad8-977e-cea2dbe2705e",

    # "ResourceAddress": "172.29.128.17",
    # "User": "klop",
    # "Password": "azsxdc",
    # "CLI Connection Type": "ssh ",


    resource_driver = juniper_generic_resource_driver('77', data_json)
    print resource_driver.GetInventory(data_json)
    print resource_driver.GetInventory(data_json)
    import sys;

    sys.exit()
    # print resource_driver.Remove_VLAN(data_json, '192.168.42.235/0/FE23', '', '', '')
    print resource_driver.Save(data_json, 'tftp://192.168.65.85', 'startup-config')
    data_json = str("""{
            "resource" : {

                    "ResourceAddress": "192.168.42.235",
                    "User": "root",
                    "Password": "Password1",
                    "CLI Connection Type": "ssh",
                    "Console User": "",
                    "Console Password": "",
                    "Console Server IP Address": "",
                    "ResourceName" : "Cisco-2950-Route",
                    "ResourceFullName" : "Cisco-2950-Router",
                    "Enable Password": "",
                    "Console Port": "",
                    "SNMP Read Community": "Cisco",
                    "SNMP Version": "",
                    "SNMP V3 Password": "",
                    "SNMP V3 User": "",
                    "SNMP V3 Private Key": ""
                },
            "reservation" : {
                    "ReservationId": "a1163c75-6427-44da-872d-c5857a67f6be",
                    "Username" : "admin",
                    "Password" : "admin",
                    "Domain" : "Global",
                    "AdminUsername" : "admin",
                    "AdminPassword" : "admin"}
            }""")

    print resource_driver.Save(data_json, 'tftp://192.168.65.85', 'startup-config')
