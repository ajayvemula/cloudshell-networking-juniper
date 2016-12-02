from collections import OrderedDict
from cloudshell.cli.command_mode import CommandMode


class CliCommandMode(CommandMode):
    PROMPT = r'%\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        self._context = context
        CommandMode.__init__(self, CliCommandMode.PROMPT, CliCommandMode.ENTER_COMMAND,
                             CliCommandMode.EXIT_COMMAND, enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_actions(self, cli_operations):
        pass

    def enter_action_map(self):
        return OrderedDict()

    def enter_error_map(self):
        return OrderedDict()

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()


class DefaultCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = 'cli'
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        self._context = context
        CommandMode.__init__(self, DefaultCommandMode.PROMPT,
                             DefaultCommandMode.ENTER_COMMAND,
                             DefaultCommandMode.EXIT_COMMAND, enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_actions(self, cli_operations):
        cli_operations.send_command('set cli screen-length 0')

    def enter_action_map(self):
        return OrderedDict()

    def enter_error_map(self):
        return OrderedDict()

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()


class ConfigCommandMode(CommandMode):
    PROMPT = r'#\s*$'
    ENTER_COMMAND = 'configure'
    EXIT_COMMAND = 'exit'

    def __init__(self, context):
        CommandMode.__init__(self, ConfigCommandMode.PROMPT,
                             ConfigCommandMode.ENTER_COMMAND,
                             ConfigCommandMode.EXIT_COMMAND, enter_action_map=self.enter_action_map(),
                             exit_action_map=self.exit_action_map(), enter_error_map=self.enter_error_map(),
                             exit_error_map=self.exit_error_map())

    def enter_action_map(self):
        return OrderedDict()

    def enter_error_map(self):
        return OrderedDict()

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()


CommandMode.RELATIONS_DICT = {
    CliCommandMode: {
        DefaultCommandMode: {
            ConfigCommandMode: {}
        }
    }
}
