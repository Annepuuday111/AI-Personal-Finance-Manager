from django.contrib import admin
from .models import (
    UserProfile, Category, BankAccount, Transaction, 
    Budget, FinancialGoal, AIInsight, Notification, RecurringTransaction
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'currency', 'monthly_budget', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone_number']
    list_filter = ['currency', 'email_notifications', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'icon', 'color', 'budget_limit']
    list_filter = ['category_type', 'created_at']
    search_fields = ['name', 'user__email']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'user', 'balance', 'currency', 'is_active']
    list_filter = ['account_type', 'is_active', 'created_at']
    search_fields = ['name', 'user__email', 'account_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'transaction_type', 'amount', 'user', 'account', 'category', 'date']
    list_filter = ['transaction_type', 'is_recurring', 'date', 'created_at']
    search_fields = ['description', 'user__email', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'amount', 'period', 'start_date', 'end_date', 'alert_threshold']
    list_filter = ['period', 'start_date', 'created_at']
    search_fields = ['category__name', 'user__email']

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'current_amount', 'deadline', 'status']
    list_filter = ['status', 'deadline', 'created_at']
    search_fields = ['name', 'user__email', 'description']

@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'insight_type', 'user', 'priority', 'is_read', 'created_at']
    list_filter = ['insight_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'description', 'user__email']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'user', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']

@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'user', 'amount', 'frequency', 'next_occurrence', 'is_active']
    list_filter = ['frequency', 'is_active', 'transaction_type', 'created_at']
    search_fields = ['description', 'user__email']