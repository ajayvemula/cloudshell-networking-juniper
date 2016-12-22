from cloudshell.networking.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.networking.juniper.cli.juniper_cli_handler import JuniperCliHandler
from cloudshell.networking.juniper.flows.juniper_firmware_flow import JuniperFirmwareFlow


class JuniperFirmwareRunner(FirmwareRunner):
    def __init__(self, cli, logger, context, api):
        super(JuniperFirmwareRunner, self).__init__(logger)
        self._cli_handler = JuniperCliHandler(cli, context, logger, api)
        self._load_firmware_flow = JuniperFirmwareFlow(self._cli_handler, self._logger)
