from cloudshell.cli.service.cli_exceptions import CommandExecutionException
from cloudshell.cli.service.cli_service import CliService
from cloudshell.configuration.cloudshell_cli_binding_keys import SESSION
from cloudshell.configuration.cloudshell_shell_core_binding_keys import LOGGER
from cloudshell.networking.juniper.command_templates.commit_rollback import JUNIPER_COMMIT, JUNIPER_ROLLBACK
import inject


class JuniperCliService(CliService):

    @inject.params(logger=LOGGER, session=SESSION)
    def send_config_command(self, command, expected_str=None, expected_map=None, error_map=None, logger=None,
                            session=None, **optional_args):
        try:
            return super(JuniperCliService, self).send_config_command(command, expected_str, expected_map, error_map,
                                                                      logger, session, **optional_args)
        except CommandExecutionException:
            self.rollback()

    @inject.params(logger=LOGGER, session=SESSION)
    def commit(self, expected_map=None, logger=None, session=None):
        logger.debug('Commit called')
        try:
            self._send_command(JUNIPER_COMMIT.get_command(), expected_map=expected_map)
        except CommandExecutionException:
            self.rollback()
            raise

    @inject.params(logger=LOGGER, session=SESSION)
    def rollback(self, expected_map=None, logger=None, session=None):
        logger.debug('Rollback called')
        self._send_command(JUNIPER_ROLLBACK.get_command(), expected_map=expected_map, session=session)
