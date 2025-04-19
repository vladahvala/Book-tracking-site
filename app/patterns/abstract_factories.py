# ==== PATTERN ABSTRACT FACTORY ==== 
# Creational 

from abc import ABC, abstractmethod
from app.models import Book  # імпортуємо модель Book

# Абстрактна фабрика
class AbstractFactory(ABC):
    @abstractmethod
    def create_categories(self):
        pass
    
    @abstractmethod
    def create_books_by_subcategory(self):
        pass

# Конкретна фабрика для категорії Business Literature
class BusinessLiteratureFactory(AbstractFactory):
    def create_categories(self):
        return ['Business Literature', 'Career & HR', 'Marketing & PR', 'Finance', 'Economics']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Detectives & Thrillers
class DetectivesAndThrillersFactory(AbstractFactory):
    def create_categories(self):
        return ['Action', 'Detectives', 'Humorous & Women\'s Detectives', 'Historical Detective', 
                'Classic Detective', 'Crime Detective', 'Hard-Boiled Detective', 'Political Detective', 
                'Police Detective', 'Maniac Stories', 'Soviet Detective', 'Thriller', 'Espionage Detective']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Nonfiction Literature
class NonfictionLiteratureFactory(AbstractFactory):
    def create_categories(self):
        return ['Biographies & Memoirs', 'Military Documentary & Analysis', 'Military Science', 
                'Geography & Travel Notes', 'General Nonfiction', 'Journalism & Publicism']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Home & Family
class HomeAndFamilyFactory(AbstractFactory):
    def create_categories(self):
        return ['Cars & Traffic Rules', 'Martial Arts & Sports', 'Pets', 'Home Economics', 'Health', 'Cooking', 'Entertainment']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Art, Art Studies & Design
class ArtAndDesignFactory(AbstractFactory):
    def create_categories(self):
        return ['Painting, Albums, Illustrated Catalogs', 'Art & Design', 'Art Criticism', 'Cinema & Film', 
                'Music', 'Theatre', 'Sculpture & Architecture']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Computers & Internet
class ComputersAndInternetFactory(AbstractFactory):
    def create_categories(self):
        return ['Foreign Computer Literature', 'Computer Hardware & Digital Signal Processing', 
                'Operating Systems, Networks & Internet', 'Programming, Software & Databases', 
                'Computer Tutorials & Guides']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Children’s Literature
class ChildrensLiteratureFactory(AbstractFactory):
    def create_categories(self):
        return ['General Children\'s Literature', 'Educational Literature for Children', 
                'Thrilling Literature for Children', 'Games & Exercises for Children', 'World Folk Tales']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Romance Novels
class RomanceNovelsFactory(AbstractFactory):
    def create_categories(self):
        return ['Historical Romance', 'Short Romance Stories', 'Romantic Fantasy', 'Romantic Thrillers', 'Contemporary Romance']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Science & Education
class ScienceAndEducationFactory(AbstractFactory):
    def create_categories(self):
        return ['Alternative Medicine', 'Alternative Sciences & Theories', 'Biology, Biophysics & Biochemistry', 
                'Military History', 'Law & Government']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Poetry
class PoetryFactory(AbstractFactory):
    def create_categories(self):
        return ['Classical foreign poetry', 'Song lyrics poetry', 'Modern foreign poetry']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Adventure
class AdventureFactory(AbstractFactory):
    def create_categories(self):
        return ['Adventure novel', 'Adventures', 'Modern world adventures', 'Nature and animals', 'Maritime adventures']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Prose
class ProseFactory(AbstractFactory):
    def create_categories(self):
        return ['Gothic novel', 'Classical prose of the 19th century', 'War prose', 'Phantasmagoria, absurdist prose', 'Epistolary prose']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Science Fiction and Fantasy
class SciFiAndFantasyFactory(AbstractFactory):
    def create_categories(self):
        return ['Heroic fantasy', 'Cyberpunk', 'Mythological fantasy', 'Post-apocalypse', 'Slavic fantasy', 
                'Horror', 'Steampunk', 'Fantasy', 'Epic science fiction', 'Modern fairy tale']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')

# Конкретна фабрика для категорії Humor
class HumorFactory(AbstractFactory):
    def create_categories(self):
        return ['Jokes', 'Satire', 'Humor']
    
    def create_books_by_subcategory(self):
        return Book.objects.filter(genre__in=self.create_categories()).values('id', 'book_title', 'author')
