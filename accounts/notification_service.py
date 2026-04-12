"""
Enhanced Notification Service for FinanceAI
Generates notifications for all major events with proper descriptions, icons, and context
"""

from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta


class NotificationService:
    """
    Centralized notification service for creating contextual notifications
    across the entire application
    """
    
    NOTIFICATION_TYPES = {
        'BUDGET_ALERT': {
            'icon': '⚠️',
            'color': '#f59e0b',
            'priority': 'high'
        },
        'BUDGET_WARNING': {
            'icon': '⚡',
            'color': '#d97706',
            'priority': 'medium'
        },
        'BUDGET_EXCEEDED': {
            'icon': '🚨',
            'color': '#ef4444',
            'priority': 'critical'
        },
        'BILL_REMINDER': {
            'icon': '📅',
            'color': '#ef4444',
            'priority': 'high'
        },
        'GOAL_PROGRESS': {
            'icon': '🎯',
            'color': '#10b981',
            'priority': 'medium'
        },
        'GOAL_COMPLETED': {
            'icon': '🎉',
            'color': '#059669',
            'priority': 'high'
        },
        'GOAL_MILESTONE': {
            'icon': '🏆',
            'color': '#16a34a',
            'priority': 'medium'
        },
        'AI_INSIGHT': {
            'icon': '🤖',
            'color': '#667eea',
            'priority': 'low'
        },
        'TRANSACTION_ADDED': {
            'icon': '💸',
            'color': '#06b6d4',
            'priority': 'low'
        },
        'TRANSACTION_LARGE': {
            'icon': '💰',
            'color': '#0891b2',
            'priority': 'medium'
        },
        'INCOME_RECEIVED': {
            'icon': '💵',
            'color': '#10b981',
            'priority': 'medium'
        },
        'ACCOUNT_CREATED': {
            'icon': '🏦',
            'color': '#3b82f6',
            'priority': 'low'
        },
        'ACCOUNT_LOW_BALANCE': {
            'icon': '⚠️',
            'color': '#f59e0b',
            'priority': 'high'
        },
        'SAVINGS_MILESTONE': {
            'icon': '💎',
            'color': '#7c3aed',
            'priority': 'medium'
        },
        'MONTHLY_REPORT': {
            'icon': '📊',
            'color': '#6366f1',
            'priority': 'medium'
        },
        'CATEGORY_CREATED': {
            'icon': '📑',
            'color': '#8b5cf6',
            'priority': 'low'
        },
        'PROFILE_UPDATED': {
            'icon': '👤',
            'color': '#64748b',
            'priority': 'low'
        },
        'WELCOME': {
            'icon': '👋',
            'color': '#667eea',
            'priority': 'high'
        },
        'SPENDING_SPIKE': {
            'icon': '📈',
            'color': '#ef4444',
            'priority': 'high'
        },
        'SAVING_OPPORTUNITY': {
            'icon': '💡',
            'color': '#10b981',
            'priority': 'medium'
        }
    }
    
    @staticmethod
    def create_notification(user, notification_type, title, message, metadata=None):
        """
        Create a notification with proper formatting
        
        Args:
            user: User object
            notification_type: Type of notification (from NOTIFICATION_TYPES)
            title: Notification title
            message: Detailed message
            metadata: Optional dictionary with additional data
        """
        from .models import Notification
        
        # Get notification config
        config = NotificationService.NOTIFICATION_TYPES.get(
            notification_type, 
            NotificationService.NOTIFICATION_TYPES['AI_INSIGHT']
        )
        
        # Format title with icon
        formatted_title = f"{config['icon']} {title}"
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=formatted_title,
            message=message,
            is_read=False
        )
        
        return notification
    
    # ==================== TRANSACTION NOTIFICATIONS ====================
    
    @staticmethod
    def notify_transaction_added(transaction):
        """Notify when a transaction is added"""
        if transaction.transaction_type == 'INCOME':
            NotificationService.create_notification(
                user=transaction.user,
                notification_type='INCOME_RECEIVED',
                title=f'Income Received: ₹{transaction.amount:,.2f}',
                message=f'You received ₹{transaction.amount:,.2f} from {transaction.description}. '
                       f'Account: {transaction.account.name}. Date: {transaction.date.strftime("%B %d, %Y")}.'
            )
        elif transaction.transaction_type == 'EXPENSE':
            # Check if it's a large expense
            if transaction.amount > 5000:  # Configurable threshold
                NotificationService.create_notification(
                    user=transaction.user,
                    notification_type='TRANSACTION_LARGE',
                    title=f'Large Expense: ₹{transaction.amount:,.2f}',
                    message=f'You spent ₹{transaction.amount:,.2f} on {transaction.description}. '
                           f'Category: {transaction.category.name if transaction.category else "Uncategorized"}. '
                           f'This is a significant transaction. Make sure it aligns with your budget.'
                )
            else:
                NotificationService.create_notification(
                    user=transaction.user,
                    notification_type='TRANSACTION_ADDED',
                    title=f'Expense Recorded: ₹{transaction.amount:,.2f}',
                    message=f'You spent ₹{transaction.amount:,.2f} on {transaction.description}. '
                           f'Category: {transaction.category.name if transaction.category else "Uncategorized"}.'
                )
    
    # ==================== BUDGET NOTIFICATIONS ====================
    
    @staticmethod
    def check_budget_alerts(user):
        """Check all budgets and create appropriate notifications"""
        from .models import Budget, Transaction
        
        now = timezone.now()
        active_budgets = Budget.objects.filter(
            user=user,
            start_date__lte=now.date(),
            end_date__gte=now.date()
        )
        
        for budget in active_budgets:
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_type='EXPENSE',
                date__gte=budget.start_date,
                date__lte=budget.end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
            remaining = budget.amount - spent
            
            # Check if notification already exists today
            from .models import Notification
            existing = Notification.objects.filter(
                user=user,
                title__icontains=budget.category.name,
                created_at__date=now.date()
            ).exists()
            
            if existing:
                continue
            
            # Critical: Budget exceeded
            if percentage >= 100:
                overspent = spent - budget.amount
                NotificationService.create_notification(
                    user=user,
                    notification_type='BUDGET_EXCEEDED',
                    title=f'Budget Exceeded: {budget.category.name}',
                    message=f'You have exceeded your {budget.get_period_display().lower()} budget for '
                           f'{budget.category.name} by ₹{overspent:,.2f}. '
                           f'Spent: ₹{spent:,.2f} / Budget: ₹{budget.amount:,.2f} ({percentage:.0f}%). '
                           f'Consider reviewing your expenses in this category or adjusting your budget.'
                )
            
            # High: Near budget limit (80-99%)
            elif percentage >= 80:
                NotificationService.create_notification(
                    user=user,
                    notification_type='BUDGET_WARNING',
                    title=f'Budget Alert: {budget.category.name}',
                    message=f'You have used {percentage:.0f}% of your {budget.get_period_display().lower()} '
                           f'budget for {budget.category.name}. '
                           f'Remaining: ₹{remaining:,.2f} out of ₹{budget.amount:,.2f}. '
                           f'Try to limit spending in this category for the rest of the period.'
                )
            
            # Medium: Halfway point (50-79%)
            elif percentage >= 50 and percentage < 80:
                # Only notify at 50%, 60%, 70%
                milestone = int(percentage / 10) * 10
                if milestone in [50, 60, 70]:
                    NotificationService.create_notification(
                        user=user,
                        notification_type='BUDGET_ALERT',
                        title=f'Budget Update: {budget.category.name}',
                        message=f'You have used {percentage:.0f}% of your {budget.category.name} budget. '
                               f'Spent: ₹{spent:,.2f} / Budget: ₹{budget.amount:,.2f}. '
                               f'You\'re on track. Keep monitoring your spending.'
                    )
    
    # ==================== GOAL NOTIFICATIONS ====================
    
    @staticmethod
    def notify_goal_progress(goal, amount_added):
        """Notify when progress is made on a financial goal"""
        progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining = goal.target_amount - goal.current_amount
        
        if goal.status == 'COMPLETED':
            NotificationService.create_notification(
                user=goal.user,
                notification_type='GOAL_COMPLETED',
                title=f'Goal Achieved: {goal.name}',
                message=f'Congratulations! You have successfully achieved your financial goal: {goal.name}. '
                       f'Target: ₹{goal.target_amount:,.2f}. '
                       f'You\'re building great financial habits. Consider setting a new goal to keep the momentum going!'
            )
        else:
            # Check for milestone achievements (25%, 50%, 75%)
            milestones = [25, 50, 75, 90]
            for milestone in milestones:
                if progress_percentage >= milestone and (progress_percentage - (amount_added / goal.target_amount * 100)) < milestone:
                    NotificationService.create_notification(
                        user=goal.user,
                        notification_type='GOAL_MILESTONE',
                        title=f'Milestone Reached: {goal.name}',
                        message=f'Great progress! You\'ve reached {milestone}% of your goal "{goal.name}". '
                               f'Current: ₹{goal.current_amount:,.2f} / Target: ₹{goal.target_amount:,.2f}. '
                               f'Only ₹{remaining:,.2f} more to go. Keep up the excellent work!'
                    )
                    return
            
            # Regular progress update
            NotificationService.create_notification(
                user=goal.user,
                notification_type='GOAL_PROGRESS',
                title=f'Progress Update: {goal.name}',
                message=f'Added ₹{amount_added:,.2f} to your goal "{goal.name}". '
                       f'Progress: ₹{goal.current_amount:,.2f} / ₹{goal.target_amount:,.2f} ({progress_percentage:.1f}%). '
                       f'Remaining: ₹{remaining:,.2f}. You\'re doing great!'
            )
    
    @staticmethod
    def notify_goal_created(goal):
        """Notify when a new financial goal is created"""
        days_until_deadline = (goal.deadline - timezone.now().date()).days
        
        NotificationService.create_notification(
            user=goal.user,
            notification_type='GOAL_PROGRESS',
            title=f'New Goal Created: {goal.name}',
            message=f'You\'ve set a new financial goal: {goal.name}. '
                   f'Target: ₹{goal.target_amount:,.2f}. '
                   f'Deadline: {goal.deadline.strftime("%B %d, %Y")} ({days_until_deadline} days). '
                   f'Start saving regularly to achieve your goal on time!'
        )
    
    # ==================== ACCOUNT NOTIFICATIONS ====================
    
    @staticmethod
    def notify_account_created(account):
        """Notify when a new bank account is added"""
        NotificationService.create_notification(
            user=account.user,
            notification_type='ACCOUNT_CREATED',
            title=f'Bank Account Added: {account.name}',
            message=f'You have successfully added a new {account.get_account_type_display()}: {account.name}. '
                   f'Current Balance: ₹{account.balance:,.2f}. '
                   f'You can now track transactions for this account.'
        )
    
    @staticmethod
    def check_low_balance(account):
        """Check if account balance is low and notify"""
        # Define low balance threshold (e.g., 10% of average balance or fixed amount)
        low_balance_threshold = 1000  # ₹1000 or make it configurable
        
        if account.balance < low_balance_threshold and account.balance > 0:
            from .models import Notification
            
            # Check if already notified today
            existing = Notification.objects.filter(
                user=account.user,
                title__icontains=account.name,
                created_at__date=timezone.now().date()
            ).exists()
            
            if not existing:
                NotificationService.create_notification(
                    user=account.user,
                    notification_type='ACCOUNT_LOW_BALANCE',
                    title=f'Low Balance: {account.name}',
                    message=f'Your account "{account.name}" has a low balance of ₹{account.balance:,.2f}. '
                           f'Consider transferring funds to avoid any issues.'
                )
    
    # ==================== SAVINGS NOTIFICATIONS ====================
    
    @staticmethod
    def notify_savings_milestone(user):
        """Notify when user reaches savings milestones"""
        total_balance = user.profile.total_balance
        milestones = [10000, 25000, 50000, 100000, 250000, 500000, 1000000]
        
        for milestone in milestones:
            if total_balance >= milestone:
                from .models import Notification
                
                # Check if milestone already celebrated
                existing = Notification.objects.filter(
                    user=user,
                    title__icontains=f'₹{milestone:,}',
                    notification_type='SAVINGS_MILESTONE'
                ).exists()
                
                if not existing:
                    NotificationService.create_notification(
                        user=user,
                        notification_type='SAVINGS_MILESTONE',
                        title=f'Savings Milestone: ₹{milestone:,}',
                        message=f'Congratulations! Your total savings have reached ₹{total_balance:,.2f}. '
                               f'You\'ve crossed the ₹{milestone:,} milestone! '
                               f'This is a significant achievement. Keep up the great work!'
                    )
                    break  # Only notify for the highest achieved milestone
    
    # ==================== MONTHLY REPORT NOTIFICATION ====================
    
    @staticmethod
    def generate_monthly_report(user):
        """Generate end-of-month financial report notification"""
        from .models import Transaction
        from datetime import datetime
        
        now = timezone.now()
        first_day = now.replace(day=1).date()
        
        # Calculate monthly statistics
        monthly_income = Transaction.objects.filter(
            user=user,
            transaction_type='INCOME',
            date__gte=first_day
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        monthly_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='EXPENSE',
            date__gte=first_day
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        net_savings = monthly_income - monthly_expenses
        savings_rate = (net_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # Get top spending category
        from django.db.models import Count
        top_category = Transaction.objects.filter(
            user=user,
            transaction_type='EXPENSE',
            date__gte=first_day
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total').first()
        
        message = f'Here\'s your financial summary for {now.strftime("%B %Y")}:\n\n'
        message += f'💰 Total Income: ₹{monthly_income:,.2f}\n'
        message += f'💸 Total Expenses: ₹{monthly_expenses:,.2f}\n'
        message += f'💎 Net Savings: ₹{net_savings:,.2f}\n'
        message += f'📊 Savings Rate: {savings_rate:.1f}%\n\n'
        
        if top_category:
            message += f'🔝 Top Spending: {top_category["category__name"]} (₹{top_category["total"]:,.2f})\n\n'
        
        if savings_rate >= 20:
            message += '🎉 Excellent savings rate! You\'re doing great!'
        elif savings_rate >= 10:
            message += '👍 Good savings rate. Keep it up!'
        else:
            message += '💡 Try to increase your savings rate to 20% or more for better financial health.'
        
        NotificationService.create_notification(
            user=user,
            notification_type='MONTHLY_REPORT',
            title=f'Monthly Report: {now.strftime("%B %Y")}',
            message=message
        )
    
    # ==================== WELCOME NOTIFICATION ====================
    
    @staticmethod
    def send_welcome_notification(user):
        """Send welcome notification to new users"""
        NotificationService.create_notification(
            user=user,
            notification_type='WELCOME',
            title='Welcome to FinanceAI!',
            message=f'Hi {user.first_name or user.email}! Welcome to FinanceAI - Your intelligent financial companion. '
                   f'We\'re excited to help you manage your finances smarter. '
                   f'Get started by adding your first bank account and recording transactions. '
                   f'Our AI will provide personalized insights to help you save more and spend wisely!'
        )
    
    # ==================== SPENDING ANALYSIS NOTIFICATIONS ====================
    
    @staticmethod
    def analyze_spending_patterns(user):
        """Analyze spending patterns and notify unusual activity"""
        from .models import Transaction
        
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        prev_7_days = now - timedelta(days=14)
        
        # Compare last 7 days with previous 7 days
        current_spending = Transaction.objects.filter(
            user=user,
            transaction_type='EXPENSE',
            date__gte=last_7_days.date()
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        previous_spending = Transaction.objects.filter(
            user=user,
            transaction_type='EXPENSE',
            date__gte=prev_7_days.date(),
            date__lt=last_7_days.date()
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if previous_spending > 0:
            change_percentage = ((current_spending - previous_spending) / previous_spending) * 100
            
            # Notify if spending increased significantly
            if change_percentage > 30:
                NotificationService.create_notification(
                    user=user,
                    notification_type='SPENDING_SPIKE',
                    title='Spending Alert: Unusual Activity',
                    message=f'Your spending has increased by {change_percentage:.0f}% in the last week. '
                           f'Last week: ₹{previous_spending:,.2f}, This week: ₹{current_spending:,.2f}. '
                           f'Review your recent transactions to ensure everything is on track.'
                )
            
            # Notify if spending decreased significantly (positive!)
            elif change_percentage < -20:
                NotificationService.create_notification(
                    user=user,
                    notification_type='SAVING_OPPORTUNITY',
                    title='Great News: Lower Spending',
                    message=f'Excellent job! Your spending decreased by {abs(change_percentage):.0f}% this week. '
                           f'Last week: ₹{previous_spending:,.2f}, This week: ₹{current_spending:,.2f}. '
                           f'You saved ₹{previous_spending - current_spending:,.2f}. Keep it up!'
                )