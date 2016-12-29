#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.devices.runners.run_command_runner import RunCommandRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler


class JuniperRunCommandRunner(RunCommandRunner):
    def __init__(self, cli, context, logger, api):
        """
        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        super(JuniperRunCommandRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.context = context

    @property
    def cli_handler(self):
        return JuniperCliHandler(self.cli, self.context, self._logger, self.api)
