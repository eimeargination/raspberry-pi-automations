import abc

class BotBase(metaclass=abc.ABCMeta):

    def __init__(self, name, messenger, config=None):
        self.name = name
        self.messenger = messenger
        self.config = config or {}

    @abc.abstractmethod
    def prepare_message(self):
        """Generate message content to send"""
        pass

    def run(self):
        """Prepare + send message"""
        message = self.prepare_message()
        self.messenger.send(message, bot_name=self.name)
