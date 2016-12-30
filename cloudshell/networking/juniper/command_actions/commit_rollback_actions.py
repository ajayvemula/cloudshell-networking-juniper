from cloudshell.cli.cli_service import CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.juniper.command_templates import commit_rollback as command_template


class CommitRollbackActions(object):
    def __init__(self, cli_service, logger):
        """
        Add remove vlan
        :param cli_service: config mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def commit(self):
        output = CommandTemplateExecutor(self._cli_service, command_template.COMMIT).execute_command()
        return output

    def rollback(self):
        output = CommandTemplateExecutor(self._cli_service, command_template.ROLLBACK).execute_command()
        return output
