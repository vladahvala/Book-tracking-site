# ==== PATTERN COMMAND ====
# Behavioral

class Command:
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method")

class UpdateStatusCommand(Command):
    def __init__(self, user_book, status):
        self.user_book = user_book
        self.status = status

    def execute(self):
        current_state = self.user_book.get_state()  # Отримуємо поточний стан
        current_state.update_status(self.user_book, self.status)  # Викликаємо метод стану для оновлення статусу

class UpdateRatingCommand(Command):
    def __init__(self, user_book, rating):
        self.user_book = user_book
        self.rating = rating

    def execute(self):
        current_state = self.user_book.get_state()  # Отримуємо поточний стан
        current_state.add_rating(self.user_book, self.rating)  # Викликаємо метод стану для додавання рейтингу

class UpdateReviewCommand(Command):
    def __init__(self, user_book, review):
        self.user_book = user_book
        self.review = review

    def execute(self):
        current_state = self.user_book.get_state()  # Отримуємо поточний стан
        current_state.add_review(self.user_book, self.review)  # Викликаємо метод стану для додавання відгуку

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
