from cloudshell.cli.command_template.command_template import CommandTemplate

ACTION_MAP = {}
ERROR_MAP = {r'[Ee]rror:': 'Command error'}

SAVE = CommandTemplate('save {dst_path}', error_map=ERROR_MAP)
RESTORE = CommandTemplate('load {restore_type} {src_path}', error_map=ERROR_MAP)
