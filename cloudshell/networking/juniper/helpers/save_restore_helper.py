class SaveRestoreHelper(object):
    @staticmethod
    def validate_configuration_type(configuration_type):
        """Validate configuration type, return it in lowercase
        :param configuration_type:
        :return: configuration type: "running"
        :raises Exception if configuration type is not "Running"
        """

        configuration_type = configuration_type or "running"
        configuration_type = configuration_type.lower()

        if configuration_type != "running":
            raise Exception(SaveRestoreHelper.__name__, 'Device support only "running" configuration type')
        return configuration_type
