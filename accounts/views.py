from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal  # ADD THIS IMPORT
from .models import (
    UserProfile, BankAccount, Transaction, Category, 
    Budget, FinancialGoal, AIInsight, Notification, RecurringTransaction
)
from .ai_service import AIFinanceAnalyzer
from .forms import (
    UserProfileForm, UserUpdateForm, BankAccountForm, TransactionForm,
    CategoryForm, BudgetForm, FinancialGoalForm
)

# ==================== DASHBOARD ====================

def landing_page(request):
    """Landing page for non-authenticated users"""
    # Redirect authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    return render(request, 'account/landing.html')

@login_required
def dashboard(request):
    """Main dashboard with overview"""
    profile = request.user.profile
    now = timezone.now()
    
    # Get financial summary
    total_balance = profile.total_balance
    monthly_income = profile.monthly_income
    monthly_expenses = profile.monthly_expenses
    net_savings = monthly_income - monthly_expenses
    
    # Get recent transactions - PROPERLY SELECT RELATED FIELDS
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category', 'account').order_by('-date', '-created_at')[:10]
    
    # Debug: Print transaction count
    print(f"Found {recent_transactions.count()} transactions for user {request.user.email}")
    
    # Get active budgets
    active_budgets_qs = Budget.objects.filter(
        user=request.user,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    ).select_related('category')[:5]
    
    # Create a list of budget dictionaries with calculated values
    active_budgets = []
    for budget in active_budgets_qs:
        # Calculate spent amount for this budget
        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='EXPENSE',
            date__gte=budget.start_date,
            date__lte=budget.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Calculate percentage
        percentage = min((spent / budget.amount * 100) if budget.amount > 0 else 0, 100)
        
        # Create a dictionary with budget data and calculated values
        active_budgets.append({
            'category': budget.category,
            'amount': budget.amount,
            'spent_amount': spent,
            'percentage_used': float(percentage),
            'start_date': budget.start_date,
            'end_date': budget.end_date,
        })
    
    # Get financial goals
    financial_goals_qs = FinancialGoal.objects.filter(
        user=request.user,
        status='IN_PROGRESS'
    ).order_by('-created_at')[:5]
    
    # Create a list of goal dictionaries with calculated values
    financial_goals = []
    for goal in financial_goals_qs:
        progress = min(
            (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0,
            100
        )
        
        financial_goals.append({
            'name': goal.name,
            'icon': goal.icon,
            'target_amount': goal.target_amount,
            'current_amount': goal.current_amount,
            'progress_percentage': float(progress),
            'deadline': goal.deadline,
        })
    
    # Get AI insights
    ai_insights = AIInsight.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-priority', '-created_at')[:5]
    
    # Get unread notifications count
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    # Get recent notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Get spending by category (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    category_spending = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE',
        date__gte=thirty_days_ago
    ).values('category__name', 'category__icon', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:6]
    
    context = {
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_savings': net_savings,
        'recent_transactions': recent_transactions,  # Already model objects, works perfectly!
        'active_budgets': active_budgets,  # List of dictionaries
        'financial_goals': financial_goals,  # List of dictionaries
        'ai_insights': ai_insights,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'category_spending': category_spending,
    }
    
    return render(request, 'accounts/dashboard.html', context)

# ==================== PROFILE ====================
@login_required
def profile(request):
    """User profile page"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    # Get unread notifications count for sidebar
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'accounts/profile.html', context)


# ==================== BANK ACCOUNTS ====================
@login_required
def bank_accounts(request):
    """List all bank accounts"""
    accounts = BankAccount.objects.filter(user=request.user)
    total_balance = sum(acc.balance for acc in accounts)
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
    }
    
    return render(request, 'accounts/bank_accounts.html', context)


@login_required
def add_bank_account(request):
    """Add new bank account"""
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, 'Bank account added successfully!')
            return redirect('accounts:bank_accounts')
    else:
        form = BankAccountForm()
    
    return render(request, 'accounts/add_bank_account.html', {'form': form})


# ==================== TRANSACTIONS ====================
@login_required
def transactions(request):
    transactions_qs = Transaction.objects.filter(user=request.user).order_by('-date')

    selected_type = request.GET.get('type', '')
    if selected_type:
        transactions_qs = transactions_qs.filter(transaction_type=selected_type)

    date_from = request.GET.get('date_from')
    if date_from:
        transactions_qs = transactions_qs.filter(date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        transactions_qs = transactions_qs.filter(date__lte=date_to)

    total_income = (
        transactions_qs.filter(transaction_type='INCOME')
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    total_expenses = (
        transactions_qs.filter(transaction_type='EXPENSE')
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    context = {
        'transactions': transactions_qs,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'selected_type': selected_type,
    }

    return render(request, 'accounts/transactions.html', context)


@login_required
def add_transaction(request):
    """Add new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            
            # Update account balance
            account = transaction.account
            if transaction.transaction_type == 'INCOME':
                account.balance += transaction.amount
            else:
                account.balance -= transaction.amount
            account.save()
            
            # Check budget alerts after adding expense
            if transaction.transaction_type == 'EXPENSE':
                check_budget_alerts(request.user)
            
            messages.success(request, 'Transaction added successfully!')
            return redirect('accounts:transactions')
    else:
        form = TransactionForm(user=request.user)
    
    # Get unread notifications count for sidebar
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'form': form,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'accounts/add_transaction.html', context)


# ==================== BUDGETS ====================
@login_required
def budgets(request):
    """List all budgets"""
    active_budgets = Budget.objects.filter(
        user=request.user,
        end_date__gte=timezone.now().date()
    )
    
    budget_data = []
    for budget in active_budgets:
        budget_data.append({
            'budget': budget,
            'spent': budget.spent_amount,
            'remaining': budget.remaining_amount,
            'percentage': budget.percentage_used,
        })
    
    # Get unread notifications count
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'budget_data': budget_data,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'accounts/budgets.html', context)


@login_required
def add_budget(request):
    """Add new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('accounts:budgets')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'accounts/add_budget.html', {'form': form})


# ==================== FINANCIAL GOALS ====================
@login_required
def financial_goals(request):
    """List all financial goals"""
    goals = FinancialGoal.objects.filter(user=request.user)
    
    # Calculate totals
    total_target = sum(goal.target_amount for goal in goals)
    total_saved = sum(goal.current_amount for goal in goals)
    in_progress_count = goals.filter(status='IN_PROGRESS').count()
    
    context = {
        'goals': goals,
        'total_target': total_target,
        'total_saved': total_saved,
        'in_progress_count': in_progress_count,
    }
    
    return render(request, 'accounts/financial_goals.html', context)


@login_required
def add_financial_goal(request):
    """Add new financial goal"""
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Financial goal created successfully!')
            return redirect('accounts:financial_goals')
    else:
        form = FinancialGoalForm()
    
    return render(request, 'accounts/add_financial_goal.html', {'form': form})


@login_required
def update_goal_progress(request, goal_id):
    """Update progress of a financial goal"""
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount_decimal = Decimal(str(amount))
                goal.current_amount += amount_decimal
                if goal.current_amount >= goal.target_amount:
                    goal.status = 'COMPLETED'
                    messages.success(request, f'🎉 Congratulations! You\'ve achieved your goal: {goal.name}!')
                else:
                    messages.success(request, f'✅ Added ₹{amount_decimal:,.2f} to {goal.name}. Keep going!')
                goal.save()
            except (ValueError, TypeError) as e:
                messages.error(request, 'Invalid amount entered. Please enter a valid number.')
        else:
            messages.error(request, 'Please enter an amount.')
    return redirect('accounts:financial_goals')

# ==================== AI INSIGHTS ====================
@login_required
def ai_insights(request):
    """View all AI insights"""
    insights = AIInsight.objects.filter(user=request.user).order_by('-priority', '-created_at')
    
    context = {
        'insights': insights,
    }
    
    return render(request, 'accounts/ai_insights.html', context)


@login_required
def generate_insights(request):
    """Generate new AI insights"""
    analyzer = AIFinanceAnalyzer(request.user)
    insights = analyzer.generate_all_insights()
    
    messages.success(request, f'Generated {len(insights)} new insights!')
    return redirect('accounts:ai_insights')


@login_required
def mark_insight_read(request, insight_id):
    """Mark an insight as read"""
    insight = get_object_or_404(AIInsight, id=insight_id, user=request.user)
    insight.is_read = True
    insight.save()
    
    return JsonResponse({'status': 'success'})


# ==================== NOTIFICATIONS ====================
@login_required
def notifications(request):
    """View all notifications"""
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = all_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': all_notifications,
        'unread_notifications_count': unread_count,
    }
    
    return render(request, 'accounts/notifications.html', context)


def check_budget_alerts(user):
    """Check all active budgets and create notifications for exceeded/warning budgets"""
    now = timezone.now()
    active_budgets = Budget.objects.filter(
        user=user,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    )
    
    for budget in active_budgets:
        spent = budget.spent_amount
        percentage = budget.percentage_used
        
        # Check if notification already exists for this budget period
        existing_notification = Notification.objects.filter(
            user=user,
            notification_type='BUDGET_ALERT',
            title__icontains=budget.category.name,
            created_at__gte=budget.start_date,
            created_at__date=now.date()
        ).exists()
        
        if existing_notification:
            continue
            
        # Create notification if budget exceeded
        if percentage >= 100:
            Notification.objects.create(
                user=user,
                notification_type='BUDGET_ALERT',
                title=f'🚨 Budget Exceeded: {budget.category.name}',
                message=f'You have exceeded your {budget.get_period_display().lower()} budget for {budget.category.name}. Spent: ₹{spent:.2f} / ₹{budget.amount:.2f} ({percentage:.0f}%)',
                is_read=False
            )
        # Create warning notification at threshold
        elif percentage >= budget.alert_threshold:
            Notification.objects.create(
                user=user,
                notification_type='BUDGET_ALERT',
                title=f'⚠️ Budget Warning: {budget.category.name}',
                message=f'You have used {percentage:.0f}% of your {budget.get_period_display().lower()} budget for {budget.category.name}. Spent: ₹{spent:.2f} / ₹{budget.amount:.2f}',
                is_read=False
            )


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Notification marked as read!')
    return redirect('accounts:notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    messages.success(request, 'All notifications marked as read!')
    return redirect('accounts:notifications')


# ==================== ANALYTICS ====================
@login_required
def analytics(request):
    """Financial analytics with dynamic period selection"""
    
    # Get period from query parameter (default to 'month')
    period = request.GET.get('period', 'month')
    now = timezone.now()
    
    # Calculate date range based on period
    if period == 'week':
        start_date = now - timedelta(days=7)
        period_name = "Last 7 Days"
        data_points = 7
        group_by = 'day'
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
        period_name = "Last Quarter"
        data_points = 3
        group_by = 'month'
    elif period == 'year':
        start_date = now - timedelta(days=365)
        period_name = "Last Year"
        data_points = 12
        group_by = 'month'
    else:  # Default to month
        start_date = now - timedelta(days=30)
        period_name = "Last 30 Days"
        data_points = 30
        group_by = 'day'
    
    # Get all transactions for the period
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date.date(),
        date__lte=now.date()
    )
    
    # Calculate totals
    total_income = transactions.filter(
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    total_expenses = transactions.filter(
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    net_savings = total_income - total_expenses
    
    # Calculate savings rate
    if total_income > 0:
        savings_rate = (net_savings / total_income) * 100
    else:
        savings_rate = 0
    
    # Prepare report data
    report = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'period_name': period_name,
    }
    
    # Generate time-series data based on group_by
    monthly_data = []
    
    if group_by == 'day':
        # Daily breakdown
        for i in range(data_points - 1, -1, -1):
            date = now.date() - timedelta(days=i)
            
            day_income = transactions.filter(
                transaction_type='INCOME',
                date=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            day_expenses = transactions.filter(
                transaction_type='EXPENSE',
                date=date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': date.strftime('%b %d'),
                'income': float(day_income),
                'expenses': float(day_expenses)
            })
    
    else:  # group_by == 'month'
        # Monthly breakdown
        months_to_show = 12 if period == 'year' else 6
        for i in range(months_to_show - 1, -1, -1):
            # Calculate month start and end
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            
            # Get last day of month
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            month_income = transactions.filter(
                transaction_type='INCOME',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expenses = transactions.filter(
                transaction_type='EXPENSE',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'income': float(month_income),
                'expenses': float(month_expenses)
            })
    
    # Get category-wise spending (top 6 categories)
    category_spending = transactions.filter(
        transaction_type='EXPENSE'
    ).values(
        'category__name', 'category__icon', 'category__color'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:6]
    
    # Format category data for chart
    category_data = {
        'labels': [cat['category__name'] or 'Uncategorized' for cat in category_spending],
        'values': [float(cat['total']) for cat in category_spending],
        'colors': [cat['category__color'] or '#667eea' for cat in category_spending]
    }
    
    # Get unread notifications count
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'report': report,
        'monthly_data': monthly_data,
        'category_data': category_data,
        'current_period': period,
        'unread_notifications_count': unread_notifications_count,
    }
    
    return render(request, 'accounts/analytics.html', context)


# ==================== CATEGORIES ====================
@login_required
def categories(request):
    """Manage categories"""
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'accounts/categories.html', context)


@login_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('accounts:categories')
    else:
        form = CategoryForm()
    
    return render(request, 'accounts/add_category.html', {'form': form})