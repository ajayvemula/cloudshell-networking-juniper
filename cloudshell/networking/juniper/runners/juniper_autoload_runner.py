#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.networking.juniper.flows.juniper_autoload_flow import JuniperSnmpAutoloadFlow
from cloudshell.networking.juniper.snmp.juniper_snmp_handler import JuniperSnmpHandler


class JuniperAutoloadRunner(AutoloadRunner):
    def __init__(self, cli, logger, context, api, supported_os):
        super(JuniperAutoloadRunner, self).__init__(context, supported_os)
        self._cli = cli
        self._api = api
        self._logger = logger

    @property
    def snmp_handler(self):
        return JuniperSnmpHandler(self._cli, self._context, self._logger, self._api)

    @property
    def autoload_flow(self):
        return JuniperSnmpAutoloadFlow(self.snmp_handler, self._logger)
