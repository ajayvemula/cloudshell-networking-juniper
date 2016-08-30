from copy import copy

from cloudshell.cli.service.cli_exceptions import CommandExecutionException
from cloudshell.cli.service.cli_service import CliService
from cloudshell.configuration.cloudshell_cli_binding_keys import SESSION
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER
import cloudshell.networking.juniper.command_templates.commit_rollback as commit_rollback
import inject


class JuniperCliService(CliService):
    @inject.params(logger=LOGGER, session=SESSION)
    def send_config_command(self, command, expected_str=None, expected_map=None, error_map=None, logger=None,
                            session=None, **optional_args):
        """
        Overridden method, added rollback call for CommandExecutionException
        :param command:
        :param expected_str:
        :param expected_map:
        :param error_map:
        :param logger:
        :param session:
        :param optional_args:
        :return:
        """
        try:
            return super(JuniperCliService, self).send_config_command(command, expected_str, expected_map, error_map,
                                                                      logger, session, **optional_args)
        except CommandExecutionException:
            self.rollback()
            raise

    @inject.params(logger=LOGGER, session=SESSION)
    def commit(self, expected_map=None, logger=None, session=None):
        """
        Call commit command
        :param expected_map:
        :param logger:
        :param session:
        :return:
        """
        logger.debug('Commit called')
        error_map = copy(self._error_map)
        error_map[r'[Ee]rror|ERROR'] = 'Commit error, see logs for more details'
        try:
            self._send_command(commit_rollback.COMMIT.get_command(), expected_map=expected_map, error_map=error_map,
                               session=session)
        except CommandExecutionException:
            self.rollback()
            raise

    @inject.params(logger=LOGGER, session=SESSION)
    def rollback(self, expected_map=None, logger=None, session=None):
        """
        Call rollback command
        :param expected_map:
        :param logger:
        :param session:
        :return:
        """
        logger.debug('Rollback called')
        self._enter_configuration_mode(session)
        self._send_command(commit_rollback.ROLLBACK.get_command(), expected_map=expected_map, session=session)
