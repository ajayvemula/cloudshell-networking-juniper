#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.flows.juniper_firmware_flow import JuniperFirmwareFlow


class JuniperFirmwareRunner(FirmwareRunner):
    def __init__(self, cli, logger, resource_config, api):
        super(JuniperFirmwareRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.resource_config = resource_config

    @property
    def cli_handler(self):
        return JuniperCliHandler(self.cli, self.resource_config, self._logger, self.api)

    @property
    def load_firmware_flow(self):
        return JuniperFirmwareFlow(self.cli_handler, self._logger)
