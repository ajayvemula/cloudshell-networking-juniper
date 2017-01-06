from cloudshell.networking.devices.runners.state_runner import StateRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.flows.juniper_shutdown_flow import JuniperShutdownFlow


class JuniperStateRunner(StateRunner):
    def __init__(self, cli, logger, api, context):
        """
        :param cli:
        :param logger:
        :param api:
        :param context:
        """

        super(JuniperStateRunner, self).__init__(logger, api, context)
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)

    @property
    def shutdown_flow(self):
        return JuniperShutdownFlow(self._cli_handler, self._logger)


