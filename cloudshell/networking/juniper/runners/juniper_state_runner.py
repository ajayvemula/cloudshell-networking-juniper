from cloudshell.networking.devices.runners.state_runner import StateRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler


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
