# ==== PATTERN STATE ====
# Behavioral

class BookState:
    def update_status(self, user_book, status):
        self._default_update_status(user_book, status)

    def _default_update_status(self, user_book, status):
        user_book.status = status
        user_book.save()

    def add_review(self, user_book, review):
        raise NotImplementedError("This state does not support adding a review.")

    def add_rating(self, user_book, rating):
        raise NotImplementedError("This state does not support adding a rating.")


class UnreadState(BookState):
    pass


class PlanningState(BookState):
    pass


class ReadingState(BookState):
    pass


class ReadState(BookState):
    def add_review(self, user_book, review):
        user_book.review = review
        user_book.save()

    def add_rating(self, user_book, rating):
        user_book.rating = rating
        user_book.save()

