from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import Notification, Transaction, BankAccount

def financial_summary_processor(request):
    """Add global financial data to all templates (Highly Optimized)"""
    if not request.user.is_authenticated:
        return {
            'total_balance': 0, 
            'monthly_income': 0, 
            'monthly_expenses': 0,
            'net_savings': 0
        }
        
    now = timezone.now()
    # SINGLE QUERY for all monthly stats
    summary_data = Transaction.objects.filter(
        user=request.user,
        date__year=now.year,
        date__month=now.month
    ).values('transaction_type').annotate(total=Sum('amount'))
    
    # Map the results instantly
    monthly_income = Decimal('0')
    monthly_expenses = Decimal('0')
    for item in summary_data:
        if item['transaction_type'] == 'INCOME':
            monthly_income = item['total']
        elif item['transaction_type'] == 'EXPENSE':
            monthly_expenses = item['total']

    # Total balance across all accounts
    total_balance = BankAccount.objects.filter(user=request.user).aggregate(total=Sum('balance'))['total'] or Decimal('0')
    net_savings = monthly_income - monthly_expenses
    
    return {
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_savings': net_savings,
    }

def notifications_processor(request):
    """Add unread notifications count to all templates"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {
            'unread_notifications_count': unread_count,
        }
    return {
        'unread_notifications_count': 0,
    }