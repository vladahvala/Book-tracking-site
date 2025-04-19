# ==== PATTERN COMMAND ====

class Command:
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")

class UpdateStatusCommand(Command):
    def __init__(self, user_book, status):
        self.user_book = user_book
        self.status = status

    def execute(self):
        if self.status == 'unread':
            self.user_book.delete()
        else:
            self.user_book.status = self.status
            self.user_book.save()



class UpdateRatingCommand(Command):
    def __init__(self, user_book, rating):
        self.user_book = user_book
        self.rating = rating

    def execute(self):
        self.user_book.rating = int(self.rating)
        self.user_book.save()


class UpdateReviewCommand(Command):
    def __init__(self, user_book, review):
        self.user_book = user_book
        self.review = review

    def execute(self):
        self.user_book.review = self.review
        self.user_book.save()


# CommandInvoker to execute commands
class CommandInvoker:
    def __init__(self):
        self._commands = []

    def add_command(self, command: Command):
        self._commands.append(command)

    def execute_commands(self):
        for command in self._commands:
            command.execute()
        self._commands.clear()  # Clear the commands list after execution
