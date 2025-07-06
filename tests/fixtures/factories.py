"""
Factory classes for generating test data
"""
import factory
from factory import fuzzy
from datetime import datetime, timedelta
import random
from src.models import Paper, Summary


class PaperFactory(factory.Factory):
    """Factory for creating Paper instances"""
    class Meta:
        model = dict
    
    arxiv_id = factory.Sequence(lambda n: f"2401.{n:05d}")
    title = factory.Faker('sentence', nb_words=10)
    authors = factory.LazyFunction(
        lambda: [factory.Faker('name').generate() for _ in range(random.randint(1, 5))]
    )
    abstract = factory.Faker('text', max_nb_chars=1000)
    published_date = fuzzy.FuzzyDate(
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date()
    )
    categories = factory.LazyFunction(
        lambda: random.sample(['cs.CL', 'cs.AI', 'cs.LG', 'cs.CV'], k=random.randint(1, 3))
    )
    pdf_url = factory.LazyAttribute(lambda obj: f"https://arxiv.org/pdf/{obj.arxiv_id}.pdf")

class SummaryFactory(factory.Factory):
    """Factory for creating Summary instances"""
    class Meta:
        model = dict
    
    summary = factory.Faker('text', max_nb_chars=200)
    key_points = factory.LazyFunction(
        lambda: [factory.Faker('sentence').generate() for _ in range(random.randint(3, 5))]
    )
    relevance_score = fuzzy.FuzzyFloat(low=0.0, high=10.0)
    model_used = fuzzy.FuzzyChoice(['facebook/bart-large-cnn', 'google/pegasus-large', 't5-base'])


class LLMPaperFactory(PaperFactory):
    """Factory for creating LLM-specific papers"""
    title = factory.LazyFunction(
        lambda: f"{random.choice(['Advances in', 'Novel', 'Efficient'])} "
                f"{random.choice(['Large Language Models', 'Transformer Architecture', 'LLM Training'])}: "
                f"{factory.Faker('sentence', nb_words=5).generate()}"
    )
    abstract = factory.LazyFunction(
        lambda: f"This paper presents {random.choice(['novel', 'groundbreaking', 'efficient'])} "
                f"approaches to {random.choice(['LLM', 'language model', 'transformer'])} "
                f"{random.choice(['training', 'architecture', 'fine-tuning'])}. "
                f"{factory.Faker('text', max_nb_chars=500).generate()}"
    )
    categories = ['cs.CL', 'cs.AI']