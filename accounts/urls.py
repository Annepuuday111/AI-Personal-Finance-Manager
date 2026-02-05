from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Bank Accounts
    path('bank-accounts/', views.bank_accounts, name='bank_accounts'),
    path('bank-accounts/add/', views.add_bank_account, name='add_bank_account'),
    
    # Transactions
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    
    # Budgets
    path('budgets/', views.budgets, name='budgets'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    
    # Financial Goals
    path('goals/', views.financial_goals, name='financial_goals'),
    path('goals/add/', views.add_financial_goal, name='add_financial_goal'),
    path('goals/<int:goal_id>/update/', views.update_goal_progress, name='update_goal_progress'),
    
    # AI Insights
    path('insights/', views.ai_insights, name='ai_insights'),
    path('insights/generate/', views.generate_insights, name='generate_insights'),
    path('insights/<int:insight_id>/read/', views.mark_insight_read, name='mark_insight_read'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # Categories
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
]