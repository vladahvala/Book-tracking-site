# ==== PATTERN STATE ====

class BookState:
    def update_status(self, user_book, status):
        raise NotImplementedError("Each state must implement this method.")

    def add_review(self, user_book, review):
        raise NotImplementedError("Each state must implement this method.")
        
    def add_rating(self, user_book, rating):
        raise NotImplementedError("Each state must implement this method.")


class UnreadState(BookState):
    def update_status(self, user_book, status):
        user_book.status = status
        user_book.save()

class PlanningState(BookState):
    def update_status(self, user_book, status):
        user_book.status = status
        user_book.save()

class ReadingState(BookState):
    def update_status(self, user_book, status):
        user_book.status = status
        user_book.save()


class ReadState(BookState):
    def update_status(self, user_book, status):
        user_book.status = status
        user_book.save()

    def add_review(self, user_book, review):
        user_book.review = review
        user_book.save()

    def add_rating(self, user_book, rating):
        user_book.rating = rating
        user_book.save()
