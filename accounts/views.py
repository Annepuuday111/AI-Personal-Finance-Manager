from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal
from .models import (
    UserProfile, BankAccount, Transaction, Category, 
    Budget, FinancialGoal, AIInsight, Notification, RecurringTransaction
)
from .ai_service import AIFinanceAnalyzer
from .forms import (
    UserProfileForm, UserUpdateForm, BankAccountForm, TransactionForm,
    CategoryForm, BudgetForm, FinancialGoalForm
)
from .notification_service import NotificationService
import random
from django.core.mail import send_mail
from django.conf import settings
from allauth.account.views import LoginView, SignupView
from django.contrib.auth import login as auth_login
from .models import EmailOTP
import threading

# ==================== DASHBOARD ====================

def landing_page(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    return render(request, 'account/landing.html')

@login_required
def dashboard(request):
    """Main dashboard with overview"""
    now = timezone.now()
    
    # Financial summary is now handled globally by financial_summary_processor
    # We only need specific dashboard data here
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category', 'account').order_by('-date', '-created_at')[:10]
    
    # Get active budgets with optimized spent calculation
    active_budgets_qs = Budget.objects.filter(
        user=request.user,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    ).select_related('category')[:5]
    
    # Pre-calculate spent amounts for all active budget categories in one trip
    budget_categories = [b.category_id for b in active_budgets_qs]
    if budget_categories:
        all_spent = Transaction.objects.filter(
            user=request.user,
            category_id__in=budget_categories,
            transaction_type='EXPENSE',
            date__gte=min(b.start_date for b in active_budgets_qs),
            date__lte=max(b.end_date for b in active_budgets_qs)
        ).values('category_id').annotate(total=Sum('amount'))
        spent_map = {item['category_id']: item['total'] for item in all_spent}
    else:
        spent_map = {}

    active_budgets = []
    for budget in active_budgets_qs:
        # Note: This is an approximation if multiple budgets have same category, 
        # but for a single user dashboard it's much faster.
        spent = spent_map.get(budget.category_id, Decimal('0'))
        percentage = min((spent / budget.amount * 100) if budget.amount > 0 else 0, 100)
        
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
        'recent_transactions': recent_transactions,
        'active_budgets': active_budgets,
        'financial_goals': financial_goals,
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
            
            # Send notification
            NotificationService.create_notification(
                user=request.user,
                notification_type='PROFILE_UPDATED',
                title='Profile Updated',
                message='Your profile has been successfully updated with the latest information.'
            )
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
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
            
            # Send notification
            NotificationService.notify_account_created(account)
            
            messages.success(request, 'Bank account added successfully!')
            return redirect('accounts:bank_accounts')
    else:
        form = BankAccountForm()
    
    return render(request, 'accounts/add_bank_account.html', {'form': form})


# ==================== TRANSACTIONS ====================
@login_required
def transactions(request):
    # Optimized: Fetch category and account names in the same query trip
    transactions_qs = Transaction.objects.filter(user=request.user).select_related('category', 'account').order_by('-date')

    selected_type = request.GET.get('type', '')
    if selected_type:
        transactions_qs = transactions_qs.filter(transaction_type=selected_type)

    date_from = request.GET.get('date_from')
    if date_from:
        transactions_qs = transactions_qs.filter(date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        transactions_qs = transactions_qs.filter(date__lte=date_to)

    # Optimized: Fetch both totals in ONE aggregation trip
    totals = transactions_qs.aggregate(
        income=Sum('amount', filter=models.Q(transaction_type='INCOME')),
        expenses=Sum('amount', filter=models.Q(transaction_type='EXPENSE'))
    )
    
    total_income = totals['income'] or Decimal('0')
    total_expenses = totals['expenses'] or Decimal('0')

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
            
            # Send transaction notification
            NotificationService.notify_transaction_added(transaction)
            
            # Check budget alerts
            if transaction.transaction_type == 'EXPENSE':
                NotificationService.check_budget_alerts(request.user)
            
            # Check low balance
            NotificationService.check_low_balance(account)
            
            # Check savings milestone
            NotificationService.notify_savings_milestone(request.user)
            
            messages.success(request, 'Transaction added successfully!')
            return redirect('accounts:transactions')
    else:
        form = TransactionForm(user=request.user)
    
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
            
            # Send notification
            NotificationService.create_notification(
                user=request.user,
                notification_type='BUDGET_ALERT',
                title=f'Budget Created: {budget.category.name}',
                message=f'You have created a new {budget.get_period_display().lower()} budget for '
                       f'{budget.category.name}: ₹{budget.amount:,.2f}. '
                       f'Period: {budget.start_date.strftime("%b %d")} - {budget.end_date.strftime("%b %d, %Y")}. '
                       f'You will receive alerts when you reach {budget.alert_threshold}% of this budget.'
            )
            
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
            
            # Send notification
            NotificationService.notify_goal_created(goal)
            
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
                
                goal.save()
                
                # Send notification
                NotificationService.notify_goal_progress(goal, amount_decimal)
                
                if goal.status == 'COMPLETED':
                    messages.success(request, f'🎉 Congratulations! You\'ve achieved your goal: {goal.name}!')
                else:
                    messages.success(request, f'✅ Added ₹{amount_decimal:,.2f} to {goal.name}. Keep going!')
                    
            except (ValueError, TypeError):
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
    
    # Also run spending pattern analysis
    NotificationService.analyze_spending_patterns(request.user)
    
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
    
    period = request.GET.get('period', 'month')
    now = timezone.now()
    
    # Default values to ensure variables are always defined
    start_date = now - timedelta(days=30)
    period_name = "Last 30 Days"
    data_points = 30
    group_by = 'day'
    
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
    
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date.date(),
        date__lte=now.date()
    )
    
    total_income = transactions.filter(
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    total_expenses = transactions.filter(
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    net_savings = total_income - total_expenses
    
    if total_income > 0:
        savings_rate = (net_savings / total_income) * 100
    else:
        savings_rate = 0
    
    report = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'period_name': period_name,
    }
    
    from django.db.models.functions import TruncDay, TruncMonth
    
    monthly_data = []
    if group_by == 'day':
        # Optimized daily grouping using TruncDay (Only 1 query instead of 60!)
        daily_stats = (
            transactions.filter(date__gte=now.date() - timedelta(days=data_points))
            .annotate(day=TruncDay('date'))
            .values('day', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )
        
        # Build a rapid-access map
        stats_map = {}
        for entry in daily_stats:
            d = entry['day'].date() if hasattr(entry['day'], 'date') else entry['day']
            if d not in stats_map:
                stats_map[d] = {'INCOME': 0, 'EXPENSE': 0}
            stats_map[d][entry['transaction_type']] = entry['total']

        for i in reversed(range(data_points)):
            date = now.date() - timedelta(days=i)
            day_income = stats_map.get(date, {}).get('INCOME', 0)
            day_expenses = stats_map.get(date, {}).get('EXPENSE', 0)
            
            monthly_data.append({
                'month': date.strftime('%b %d'),
                'income': float(day_income),
                'expenses': float(day_expenses)
            })
    
    else:
        # Optimized monthly grouping
        months_to_show = 12 if period == 'year' else 6
        start_period = now - timedelta(days=30 * months_to_show)
        
        monthly_stats = (
            transactions.filter(date__gte=start_period.date())
            .annotate(month=TruncMonth('date'))
            .values('month', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        
        stats_map = {}
        for entry in monthly_stats:
            m = entry['month'].date() if hasattr(entry['month'], 'date') else entry['month']
            m_key = m.strftime('%Y-%m')
            if m_key not in stats_map:
                stats_map[m_key] = {'INCOME': 0, 'EXPENSE': 0}
            stats_map[m_key][entry['transaction_type']] = entry['total']

        for i in reversed(range(months_to_show)):
            month_date = now - timedelta(days=30 * i)
            m_key = month_date.strftime('%Y-%m')
            
            day_income = stats_map.get(m_key, {}).get('INCOME', 0)
            day_expenses = stats_map.get(m_key, {}).get('EXPENSE', 0)
            
            monthly_data.append({
                'month': month_date.strftime('%b %Y'),
                'income': float(day_income),
                'expenses': float(day_expenses)
            })
    
    category_spending = transactions.filter(
        transaction_type='EXPENSE'
    ).values(
        'category__name', 'category__icon', 'category__color'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:6]
    
    category_data = {
        'labels': [cat['category__name'] or 'Uncategorized' for cat in category_spending],
        'values': [float(cat['total']) for cat in category_spending],
        'colors': [cat['category__color'] or '#667eea' for cat in category_spending]
    }
    
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
            
            # Send notification
            NotificationService.create_notification(
                user=request.user,
                notification_type='CATEGORY_CREATED',
                title=f'Category Created: {category.name}',
                message=f'You have created a new {category.get_category_type_display().lower()} category: '
                       f'{category.icon} {category.name}. You can now use this category when adding transactions.'
            )
            
            messages.success(request, 'Category created successfully!')
            return redirect('accounts:categories')
    else:
        form = CategoryForm()
    
    return render(request, 'accounts/add_category.html', {'form': form})
# ==================== OTP AUTHENTICATION ====================

class CustomLoginView(LoginView):
    template_name = 'account/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('otp_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                context['show_otp'] = True
                context['otp_email'] = user.email
            except User.DoesNotExist:
                del self.request.session['otp_user_id']
        return context

    def post(self, request, *args, **kwargs):
        # Check if we are in OTP verification step
        user_id = request.session.get('otp_user_id')
        if user_id and 'otp' in request.POST:
            return self.verify_otp(request, user_id)
        
        # Otherwise, proceed with normal login (password check)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # This is called when the password is correct
        self.user = form.user
        
        # Generate OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Save OTP to database
        otp_obj, created = EmailOTP.objects.get_or_create(user=self.user)
        otp_obj.otp = otp_code
        otp_obj.created_at = timezone.now()
        otp_obj.is_verified = False
        otp_obj.save()
        
        # Send OTP via email (Using threading for fast response)
        try:
            subject = 'Your Secure Login OTP'
            html_message = render_to_string('account/email_otp.html', {
                'otp': otp_code,
                'title': 'Login Verification Code'
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [self.user.email]
            
            # Send in background thread for speed
            threading.Thread(
                target=send_mail, 
                args=(subject, plain_message, from_email, recipient_list),
                kwargs={'html_message': html_message}
            ).start()
            
            # Store user ID in session for verification
            self.request.session['otp_user_id'] = self.user.id
            
            messages.info(self.request, f'An OTP has been sent to {self.user.email}. Please enter it below.')
            return redirect('account_login')
        except Exception as e:
            messages.error(self.request, f'Error sending OTP: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))

    def verify_otp(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        otp_entered = request.POST.get('otp')
        
        try:
            otp_obj = EmailOTP.objects.get(user=user)
            
            if otp_obj.otp == otp_entered and not otp_obj.is_expired():
                # Success!
                otp_obj.is_verified = True
                otp_obj.save()
                
                # Log the user in
                auth_login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                
                # Cleanup session
                if 'otp_user_id' in request.session:
                    del request.session['otp_user_id']
                
                messages.success(request, f'Welcome back, {user.username or user.email}!')
                return redirect('accounts:dashboard')
            elif otp_obj.is_expired():
                messages.error(request, 'OTP has expired. Please try again.')
                del request.session['otp_user_id']
                return redirect('account_login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('account_login')
        except EmailOTP.DoesNotExist:
            messages.error(request, 'OTP verification failed. Please login again.')
            del request.session['otp_user_id']
            return redirect('account_login')

def reset_login(request):
    """Clear OTP session and return to login"""
    if 'otp_user_id' in request.session:
        del request.session['otp_user_id']
    return redirect('account_login')

# ==================== SIGNUP OTP VERIFICATION ====================

class CustomSignupView(SignupView):
    def form_valid(self, form):
        print(f"DEBUG: Signup form_valid called for {form.cleaned_data.get('email')}")
        # Store cleaned data in session
        signup_data = form.cleaned_data.copy()
        
        # Use password1 as per signup.html
        signup_data['password'] = self.request.POST.get('password1')
        
        self.request.session['signup_data'] = signup_data
        email = signup_data.get('email')
        
        # Generate OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Save OTP to database (using email, not user yet)
        otp_obj, created = EmailOTP.objects.get_or_create(email=email)
        otp_obj.otp = otp_code
        otp_obj.created_at = timezone.now()
        otp_obj.is_verified = False
        otp_obj.save()
        # Send OTP via email (Using threading for fast response)
        try:
            subject = 'Verify Your Email - FinanceAI'
            html_message = render_to_string('account/email_otp.html', {
                'otp': otp_code,
                'title': 'Registration Verification Code'
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            # Send in background thread for speed
            threading.Thread(
                target=send_mail, 
                args=(subject, plain_message, from_email, recipient_list),
                kwargs={'html_message': html_message}
            ).start()
            
            print(f"DEBUG: Signup OTP {otp_code} sent to {email}")
            
            self.request.session['otp_email'] = email
            messages.info(self.request, f'An OTP has been sent to {email}. Please enter it to complete your registration.')
            return redirect('accounts:verify_signup_otp')
        except Exception as e:
            messages.error(self.request, f'Error sending OTP: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))

def verify_signup_otp(request):
    email = request.session.get('otp_email')
    signup_data = request.session.get('signup_data')
    
    if not email or not signup_data:
        messages.error(request, 'Registration session expired. Please start over.')
        return redirect('account_signup')
        
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        try:
            otp_obj = EmailOTP.objects.get(email=email)
            
            if otp_obj.otp == otp_entered and not otp_obj.is_expired():
                # OTP Verified!
                otp_obj.delete() # Cleanup
                
                # Now create the user manually
                user = User.objects.create_user(
                    username=signup_data.get('email'), # Use email as username for consistency
                    email=signup_data.get('email'),
                    password=signup_data.get('password'),
                    first_name=signup_data.get('first_name', ''),
                    last_name=signup_data.get('last_name', '')
                )
                
                # Update phone number
                if signup_data.get('phone_number'):
                    if hasattr(user, 'profile'):
                        user.profile.phone_number = signup_data['phone_number']
                        user.profile.save()
                
                # Log the user in
                auth_login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                
                # Cleanup session
                del request.session['otp_email']
                del request.session['signup_data']
                
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
        except EmailOTP.DoesNotExist:
            messages.error(request, 'OTP verification failed. Please start over.')
            return redirect('account_signup')
            
    return render(request, 'account/signup_otp.html', {'email': email})
