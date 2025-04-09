from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TestReport
from django.core.cache import cache

@receiver([post_save, post_delete], sender=TestReport)
def invalidate_test_scores_cache(sender, instance, **kwargs):
    """
    Invalidate the cache for all test scores-related views whenever a TestReport is saved or deleted.
    """
    cache_keys = [
        'test_scores_list',  # Cache key for ListOfTestScores
        'test_scores_list_by_studyset_and_date'  # Cache key for ListOfTestScoresByStudySetAndDate
    ]
    for key in cache_keys:
        cache.delete(key)
        print(f"Cache invalidated for key: {key}")