from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

# ==================== USER PROFILE ====================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # Financial preferences
    currency = models.CharField(max_length=3, default='USD')
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    savings_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    ai_insights = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

    @property
    def total_balance(self):
        accounts = self.user.bank_accounts.all()
        return sum(acc.balance for acc in accounts)

    @property
    def monthly_expenses(self):
        from django.db.models import Sum
        now = timezone.now()
        return self.user.transactions.filter(
            transaction_type='EXPENSE',
            date__year=now.year,
            date__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    @property
    def monthly_income(self):
        from django.db.models import Sum
        now = timezone.now()
        return self.user.transactions.filter(
            transaction_type='INCOME',
            date__year=now.year,
            date__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# ==================== CATEGORIES ====================
class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='💰')
    color = models.CharField(max_length=7, default='#667eea')
    budget_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category_type})"

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['user', 'name', 'category_type']


# ==================== BANK ACCOUNTS ====================
class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('CHECKING', 'Checking Account'),
        ('SAVINGS', 'Savings Account'),
        ('CREDIT', 'Credit Card'),
        ('INVESTMENT', 'Investment Account'),
        ('CASH', 'Cash'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=50, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_account_type_display()}"

    class Meta:
        ordering = ['-created_at']


# ==================== TRANSACTIONS ====================
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    
    # For recurring transactions
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(max_length=20, blank=True, null=True)  # DAILY, WEEKLY, MONTHLY, YEARLY
    
    # Tags for better organization
    tags = models.CharField(max_length=255, blank=True)
    
    # Receipt attachment
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.description}"

    class Meta:
        ordering = ['-date', '-created_at']


# ==================== BUDGETS ====================
class Budget(models.Model):
    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='MONTHLY')
    start_date = models.DateField()
    end_date = models.DateField()
    alert_threshold = models.IntegerField(default=80)  # Alert at 80% spent
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Budget: {self.category.name} - {self.amount}"

    @property
    def spent_amount(self):
        from django.db.models import Sum
        return self.category.transactions.filter(
            user=self.user,
            transaction_type='EXPENSE',
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    @property
    def remaining_amount(self):
        return self.amount - self.spent_amount

    @property
    def percentage_used(self):
        if self.amount > 0:
            return (self.spent_amount / self.amount) * 100
        return 0

    class Meta:
        ordering = ['-created_at']


# ==================== FINANCIAL GOALS ====================
class FinancialGoal(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    icon = models.CharField(max_length=50, default='🎯')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.target_amount}"

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, 0)

    class Meta:
        ordering = ['-created_at']


# ==================== AI INSIGHTS ====================
class AIInsight(models.Model):
    INSIGHT_TYPES = [
        ('SPENDING', 'Spending Pattern'),
        ('SAVING', 'Saving Opportunity'),
        ('BUDGET', 'Budget Alert'),
        ('PREDICTION', 'Financial Prediction'),
        ('RECOMMENDATION', 'Recommendation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.IntegerField(default=1)  # 1-5, 5 being highest
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_insight_type_display()} - {self.title}"

    class Meta:
        ordering = ['-priority', '-created_at']


# ==================== NOTIFICATIONS ====================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('BUDGET_ALERT', 'Budget Alert'),
        ('BILL_REMINDER', 'Bill Reminder'),
        ('GOAL_PROGRESS', 'Goal Progress'),
        ('AI_INSIGHT', 'AI Insight'),
        ('TRANSACTION', 'Transaction Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

    class Meta:
        ordering = ['-created_at']


# ==================== RECURRING TRANSACTIONS ====================
class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_transactions')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_occurrence = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.frequency}"

    class Meta:
        ordering = ['next_occurrence']


# ==================== SIGNALS ====================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
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

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()