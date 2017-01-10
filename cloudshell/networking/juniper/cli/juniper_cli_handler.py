#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.devices.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.juniper.cli.junipr_command_modes import DefaultCommandMode, ConfigCommandMode


class JuniperCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        super(JuniperCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode(resource_config, api)

    @property
    def enable_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    def default_mode_service(self):
        """
        Default mode session
        :return:
        """
        return self.get_cli_service(self.enable_mode)

    def config_mode_service(self):
        """
        Config mode session
        :return:
        """
        return self.get_cli_service(self.config_mode)
