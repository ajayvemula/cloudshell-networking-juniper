from collections import OrderedDict
from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])
ACTION_MAP = OrderedDict([(r'\[[Yy]es,[Nn]o\]', lambda session, logger: session.send_line('yes', logger))])

FIRMWARE_UPGRADE = CommandTemplate('request system software add "{src_path}"', action_map=ACTION_MAP, error_map=ERROR_MAP)
SHUTDOWN = CommandTemplate('request system power-off')
REBOOT = CommandTemplate('request system reboot', error_map=ERROR_MAP, action_map=ACTION_MAP)
