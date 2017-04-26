import time
from cloudshell.devices.flows.cli_action_flows import LoadFirmwareFlow
from cloudshell.networking.juniper.command_actions.system_actions import SystemActions


class JuniperFirmwareFlow(LoadFirmwareFlow):
    def execute_flow(self, path, vrf, timeout):
        """Update firmware version on device by loading provided image, performs following steps:
            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf: VRF Name
        :return: status / exception
        """
        self._logger.info("Upgrading firmware")

        if not path:
            raise Exception(self.__class__.__name__, "Firmware file path cannot be empty")
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            system_actions = SystemActions(cli_service, self._logger)
            system_actions.load_firmware(path)
            waiting_time = 0
            try:
                system_actions.reboot(10)
                self._logger.debug('Waiting session down')
                waiting_time = self._wait_session_disconnect(cli_service, timeout)
            except:
                pass
            self._logger.debug('Waiting session up')
            cli_service.reconnect(timeout - waiting_time)

    def _wait_session_disconnect(self, cli_service, timeout):
        reboot_time = time.time()
        while True:
            rest_time = time.time() - reboot_time
            try:
                if rest_time > timeout:
                    raise Exception(self.__class__.__name__,
                                    'Session cannot start reboot after {} sec.'.format(timeout))
                cli_service.send_command('', timeout=10)
                time.sleep(1)
            except:
                self._logger.debug('Session disconnected')
                return rest_time
