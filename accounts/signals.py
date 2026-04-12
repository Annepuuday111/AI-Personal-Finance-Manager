"""
Signal handlers for automatic notification generation
Add this to your models.py file or create a separate signals.py
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Category
from .notification_service import NotificationService


@receiver(post_save, sender=User)
def create_user_profile_and_welcome(sender, instance, created, **kwargs):
    """Create profile and send welcome notification for new users"""
    if created:
        # Create profile
        UserProfile.objects.create(user=instance)
        
        # Create default categories
        default_income_categories = [
            ('💼', 'Salary', 'INCOME', '#10b981'),
            ('💰', 'Business', 'INCOME', '#3b82f6'),
            ('🎁', 'Gifts', 'INCOME', '#8b5cf6'),
            ('📈', 'Investments', 'INCOME', '#06b6d4'),
        ]
        
        default_expense_categories = [
            ('🏠', 'Housing', 'EXPENSE', '#ef4444'),
            ('🍔', 'Food', 'EXPENSE', '#f59e0b'),
            ('🚗', 'Transportation', 'EXPENSE', '#6366f1'),
            ('💊', 'Healthcare', 'EXPENSE', '#ec4899'),
            ('🎬', 'Entertainment', 'EXPENSE', '#14b8a6'),
            ('🛍️', 'Shopping', 'EXPENSE', '#f43f5e'),
            ('📚', 'Education', 'EXPENSE', '#8b5cf6'),
            ('💳', 'Bills', 'EXPENSE', '#64748b'),
        ]
        
        for icon, name, cat_type, color in default_income_categories + default_expense_categories:
            Category.objects.create(
                user=instance,
                name=name,
                category_type=cat_type,
                icon=icon,
                color=color
            )
        
        # Send welcome notification
        NotificationService.send_welcome_notification(instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()