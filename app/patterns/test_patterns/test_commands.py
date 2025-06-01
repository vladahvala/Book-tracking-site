import unittest
from app.patterns.commands import (
    CommandInvoker,
    UpdateStatusCommand,
    UpdateRatingCommand,
    UpdateReviewCommand
)

class MockState:
    def __init__(self):
        self.log = []

    def update_status(self, user_book, status):
        self.log.append(f"status:{status}")
        user_book.status = status

    def add_rating(self, user_book, rating):
        self.log.append(f"rating:{rating}")
        user_book.rating = rating

    def add_review(self, user_book, review):
        self.log.append(f"review:{review}")
        user_book.review = review

class MockUserBook:
    def __init__(self):
        self.status = None
        self.rating = None
        self.review = None
        self._state = MockState()

    def get_state(self):
        return self._state


class TestCommandPattern(unittest.TestCase):

    def test_update_status_command(self):
        user_book = MockUserBook()
        cmd = UpdateStatusCommand(user_book, "in progress")
        cmd.execute()
        self.assertEqual(user_book.status, "in progress")

    def test_update_rating_command(self):
        user_book = MockUserBook()
        cmd = UpdateRatingCommand(user_book, 4)
        cmd.execute()
        self.assertEqual(user_book.rating, 4)

    def test_update_review_command(self):
        user_book = MockUserBook()
        cmd = UpdateReviewCommand(user_book, "Great book!")
        cmd.execute()
        self.assertEqual(user_book.review, "Great book!")

    def test_command_invoker(self):
        user_book = MockUserBook()
        invoker = CommandInvoker()
        invoker.add_command(UpdateStatusCommand(user_book, "done"))
        invoker.add_command(UpdateRatingCommand(user_book, 5))
        invoker.add_command(UpdateReviewCommand(user_book, "Loved it!"))
        invoker.execute_commands()

        self.assertEqual(user_book.status, "done")
        self.assertEqual(user_book.rating, 5)
        self.assertEqual(user_book.review, "Loved it!")

if __name__ == '__main__':
    unittest.main()
