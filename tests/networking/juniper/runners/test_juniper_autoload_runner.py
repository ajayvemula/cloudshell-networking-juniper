from unittest import TestCase

from mock import Mock, patch, PropertyMock

from cloudshell.networking.juniper.runners.juniper_autoload_runner import JuniperAutoloadRunner


class TestJuniperAutoloadRunner(TestCase):
    def setUp(self):
        self._cli = Mock()
        self._logger = Mock()
        self._resource_config = Mock()
        self._api = Mock()
        self._instance = JuniperAutoloadRunner(self._cli, self._logger, self._resource_config, self._api)

    @patch('cloudshell.networking.juniper.runners.juniper_autoload_runner.AutoloadRunner.__init__')
    def test_init(self, autoload_runner_init):
        instance = JuniperAutoloadRunner(self._cli, self._logger, self._resource_config, self._api)
        autoload_runner_init.assert_called_once_with(self._resource_config)
        self.assertIs(instance._cli, self._cli)
        self.assertIs(instance._api, self._api)
        self.assertIs(instance._logger, self._logger)

    @patch('cloudshell.networking.juniper.runners.juniper_autoload_runner.JuniperSnmpHandler')
    def test_snmp_handler_prop(self, juniper_snmp_handler):
        result = Mock()
        juniper_snmp_handler.return_value = result
        self.assertIs(self._instance.snmp_handler, result)
        juniper_snmp_handler.assert_called_once_with(self._cli, self._resource_config, self._logger, self._api)

    @patch('cloudshell.networking.juniper.runners.juniper_autoload_runner.JuniperAutoloadRunner.snmp_handler',
           new_callable=PropertyMock)
    @patch('cloudshell.networking.juniper.runners.juniper_autoload_runner.JuniperSnmpAutoloadFlow')
    def test_autoload_flow_prop(self, juniper_snmp_autoload_flow, snmp_handler_prop):
        result = Mock()
        snmp_handler = Mock()
        snmp_handler_prop.return_value = snmp_handler
        juniper_snmp_autoload_flow.return_value = result
        self.assertIs(self._instance.autoload_flow, result)
        juniper_snmp_autoload_flow.assert_called_once_with(snmp_handler, self._logger)
