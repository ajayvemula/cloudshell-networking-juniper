#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.state_runner import StateRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler


class JuniperStateRunner(StateRunner):
    def __init__(self, cli, logger, api, resource_config):
        """
        :param cli:
        :param logger:
        :param api:
        :param resource_config:
        """

        super(JuniperStateRunner, self).__init__(logger, api, resource_config)
        self.cli = cli
        self.api = api

    @property
    def cli_handler(self):
        return JuniperCliHandler(self.cli, self.resource_config, self._logger, self.api)
