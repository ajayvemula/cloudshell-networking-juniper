from unittest import TestCase

from mock import Mock, patch

from cloudshell.networking.juniper.command_actions.commit_rollback_actions import CommitRollbackActions


class TestCommitRollbackActions(TestCase):
    def setUp(self):
        self._cli_service = Mock()
        self._logger = Mock()
        self._instance = CommitRollbackActions(self._cli_service, self._logger)

    def test_init(self):
        self.assertIs(self._instance._cli_service, self._cli_service)
        self.assertIs(self._instance._logger, self._logger)

    @patch('cloudshell.networking.juniper.command_actions.commit_rollback_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.commit_rollback_actions.CommandTemplateExecutor')
    def test_commit(self, command_template_executor, command_template):
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.commit(), output)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.COMMIT)
        execute_command.execute_command.assert_called_once_with()

    @patch('cloudshell.networking.juniper.command_actions.commit_rollback_actions.command_template')
    @patch('cloudshell.networking.juniper.command_actions.commit_rollback_actions.CommandTemplateExecutor')
    def test_rollback(self, command_template_executor, command_template):
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.rollback(), output)
        command_template_executor.assert_called_once_with(self._cli_service, command_template.ROLLBACK)
        execute_command.execute_command.assert_called_once_with()
