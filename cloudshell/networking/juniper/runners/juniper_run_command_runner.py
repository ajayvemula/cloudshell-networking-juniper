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
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)
