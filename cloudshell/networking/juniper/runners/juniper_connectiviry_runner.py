#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.devices.runners.connectivity_runner import ConnectivityRunner
from cloudshell.networking.juniper.flows.juniper_add_vlan_flow import JuniperAddVlanFlow
from cloudshell.networking.juniper.flows.juniper_remove_vlan_flow import JuniperRemoveVlanFlow
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler


class JuniperConnectivityRunner(ConnectivityRunner):
    def __init__(self, cli, logger, api, context):
        """
            Handle add/remove vlan flows

            :param cli:
            :param logger:
            :param api:
            :param context:
            :param supported_os:
            """
        super(JuniperConnectivityRunner, self).__init__(logger)
        self.cli = cli
        self.api = api
        self.context = context

    @property
    def cli_handler(self):
        return JuniperCliHandler(self.cli, self.context, self._logger, self.api)

    @property
    def remove_vlan_flow(self):
        return JuniperRemoveVlanFlow(self.cli_handler, self._logger)

    @property
    def add_vlan_flow(self):
        return JuniperAddVlanFlow(self.cli_handler, self._logger)
