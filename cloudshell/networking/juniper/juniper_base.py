from abc import ABCMeta
from abc import abstractmethod

class JuniperBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def _send_command(self, command, expected_str=None, timeout=30):
        pass

    @abstractmethod
    def connect(self):
        pass