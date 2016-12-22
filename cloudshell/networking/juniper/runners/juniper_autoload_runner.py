from cloudshell.networking.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler


class JuniperAutoloadRunner(AutoloadRunner):
    def __init__(self, cli, logger, api, context, supported_os):
        super(JuniperAutoloadRunner, self).__init__(cli, logger, context, supported_os)
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)
        self._logger = logger
        self._autoload_flow = CiscoAutoloadFlow(cli_handler=self._cli_handler,
                                                autoload_class=CiscoIOSAutoload,
                                                logger=logger,
                                                resource_name=self._resource_name)