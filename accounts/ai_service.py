from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Transaction, Budget, FinancialGoal, AIInsight, Category
import requests
from django.conf import settings
import feedparser
from django.contrib.auth.models import User


class AIFinanceAnalyzer:
    """
    AI-powered financial analysis service that provides:
    - Spending pattern analysis
    - Saving opportunities
    - Budget alerts
    - Financial predictions
    - Stock market insights
    - Bank interest rate comparisons
    """
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()

    def _create_unique_insight(self, insight_type, title, description, priority=3, force=False):
        """
        Create an `AIInsight` for the current user only if an insight with the
        same title doesn't already exist for that user (prevents duplicates).

        - `force=True` will bypass the duplicate check and always create.
        """
        if not force and AIInsight.objects.filter(user=self.user, title=title).exists():
            return None
        return AIInsight.objects.create(
            user=self.user,
            insight_type=insight_type,
            title=title,
            description=description,
            priority=priority,
        )
        
    def generate_all_insights(self):
        """Generate all types of financial insights"""
        insights = []
        
        # Traditional insights
        insights.extend(self.analyze_spending_patterns())
        insights.extend(self.identify_saving_opportunities())
        insights.extend(self.check_budget_health())
        insights.extend(self.predict_future_expenses())
        insights.extend(self.generate_recommendations())
        
        # Market insights
        insights.extend(self.get_stock_market_insights())
        insights.extend(self.get_bank_interest_rates())
        insights.extend(self.get_investment_recommendations())
        
        return insights
    
    def analyze_spending_patterns(self):
        """Analyze user's spending patterns"""
        insights = []
        thirty_days_ago = self.now - timedelta(days=30)
        sixty_days_ago = self.now - timedelta(days=60)
        
        # Get spending for last 30 days
        current_spending = Transaction.objects.filter(
            user=self.user,
            transaction_type='EXPENSE',
            date__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get spending for previous 30 days
        previous_spending = Transaction.objects.filter(
            user=self.user,
            transaction_type='EXPENSE',
            date__gte=sixty_days_ago,
            date__lt=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if previous_spending > 0:
            change = ((current_spending - previous_spending) / previous_spending) * 100
            
            if change > 20:
                insight = self._create_unique_insight(
                    'SPENDING',
                    title=f'⚠️ Spending Increased by {change:.1f}%',
                    description=f'Your spending has increased significantly from ₹{previous_spending:,.2f} to ₹{current_spending:,.2f} in the last 30 days. Consider reviewing your expenses and identifying areas where you can cut back.',
                    priority=4,
                )
                if insight:
                    insights.append(insight)
            elif change < -10:
                insight = self._create_unique_insight(
                    'SAVING',
                    title=f'🎉 Great Job! Spending Decreased by {abs(change):.1f}%',
                    description=f'You\'re doing great! Your spending decreased from ₹{previous_spending:,.2f} to ₹{current_spending:,.2f}. Keep up the good work!',
                    priority=2,
                )
                if insight:
                    insights.append(insight)
        
        # Analyze category-wise spending
        top_category = Transaction.objects.filter(
            user=self.user,
            transaction_type='EXPENSE',
            date__gte=thirty_days_ago
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total').first()
        
        if top_category:
            insight = self._create_unique_insight(
                'SPENDING',
                title=f'💸 Top Spending Category: {top_category["category__name"]}',
                description=f'You spent ₹{top_category["total"]:,.2f} on {top_category["category__name"]} this month. This is your highest spending category.',
                priority=3,
            )
            if insight:
                insights.append(insight)
        
        return insights
    
    def identify_saving_opportunities(self):
        """Identify opportunities to save money"""
        insights = []
        
        # Calculate potential savings
        monthly_income = self.user.profile.monthly_income
        monthly_expenses = self.user.profile.monthly_expenses
        
        if monthly_income > 0:
            savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
            
            if savings_rate < 20:
                insight = self._create_unique_insight(
                    'SAVING',
                    title=f'💰 Low Savings Rate: {savings_rate:.1f}%',
                    description=f'Your current savings rate is {savings_rate:.1f}%. Financial experts recommend saving at least 20% of your income. Try to reduce unnecessary expenses to increase your savings.',
                    priority=4,
                )
                if insight:
                    insights.append(insight)
            elif savings_rate >= 30:
                insight = self._create_unique_insight(
                    'SAVING',
                    title=f'⭐ Excellent Savings Rate: {savings_rate:.1f}%',
                    description=f'Congratulations! You\'re saving {savings_rate:.1f}% of your income, which is excellent. Consider investing your surplus in stocks or mutual funds for better returns.',
                    priority=2,
                )
                if insight:
                    insights.append(insight)
        
        return insights
    
    def check_budget_health(self):
        """Check budget status and provide alerts"""
        insights = []
        
        active_budgets = Budget.objects.filter(
            user=self.user,
            start_date__lte=self.now.date(),
            end_date__gte=self.now.date()
        )
        
        for budget in active_budgets:
            percentage = budget.percentage_used
            
            if percentage >= 100:
                insight = self._create_unique_insight(
                    'BUDGET',
                    title=f'🚨 Budget Exceeded: {budget.category.name}',
                    description=f'You have exceeded your budget for {budget.category.name} by ₹{budget.spent_amount - budget.amount:,.2f}. Consider adjusting your spending or increasing the budget.',
                    priority=5,
                )
                if insight:
                    insights.append(insight)
            elif percentage >= 80:
                insight = self._create_unique_insight(
                    'BUDGET',
                    title=f'⚠️ Budget Warning: {budget.category.name}',
                    description=f'You\'ve used {percentage:.1f}% of your {budget.category.name} budget. You have ₹{budget.remaining_amount:,.2f} remaining.',
                    priority=4,
                )
                if insight:
                    insights.append(insight)
        
        return insights
    
    def predict_future_expenses(self):
        """Predict future expenses based on historical data"""
        insights = []
        
        # Calculate average monthly expenses for last 3 months
        three_months_ago = self.now - timedelta(days=90)
        avg_expenses = Transaction.objects.filter(
            user=self.user,
            transaction_type='EXPENSE',
            date__gte=three_months_ago
        ).aggregate(avg=Avg('amount'))['avg'] or Decimal('0')
        
        if avg_expenses > 0:
            predicted_monthly = avg_expenses * 30  # Rough monthly estimate
            
            insight = self._create_unique_insight(
                'PREDICTION',
                title=f'🔮 Predicted Monthly Expenses: ₹{predicted_monthly:,.2f}',
                description=f'Based on your spending patterns, we predict your monthly expenses will be around ₹{predicted_monthly:,.2f}. Plan your budget accordingly.',
                priority=3,
            )
            if insight:
                insights.append(insight)
        
        return insights
    
    def generate_recommendations(self):
        """Generate personalized financial recommendations"""
        insights = []
        
        # Check if user has set financial goals
        active_goals = FinancialGoal.objects.filter(
            user=self.user,
            status='IN_PROGRESS'
        )
        
        if not active_goals.exists():
            insight = self._create_unique_insight(
                'RECOMMENDATION',
                title='🎯 Set Financial Goals',
                description='Setting clear financial goals helps you stay motivated and track progress. Consider setting goals for an emergency fund, retirement, or a major purchase.',
                priority=3,
            )
            if insight:
                insights.append(insight)
        
        # Check emergency fund
        total_balance = self.user.profile.total_balance
        monthly_expenses = self.user.profile.monthly_expenses
        
        if monthly_expenses > 0:
            emergency_fund_months = total_balance / monthly_expenses if monthly_expenses else 0
            
            if emergency_fund_months < 3:
                insight = self._create_unique_insight(
                    'RECOMMENDATION',
                    title='🚨 Build Emergency Fund',
                    description=f'Your current savings can cover {emergency_fund_months:.1f} months of expenses. Financial experts recommend having 3-6 months of expenses saved. Consider building your emergency fund.',
                    priority=5,
                )
                if insight:
                    insights.append(insight)
        
        return insights
    
    def get_stock_market_insights(self):
        """Get current stock market trends and insights"""
        insights = []
        
        try:
            # Indian Stock Market - NSE/BSE Indices
            # Using a sample structure - you can integrate with real APIs like Alpha Vantage, Yahoo Finance, etc.
            
            market_data = {
                'nifty50': {
                    'current': 21500,
                    'change': +1.2,
                    'trend': 'bullish'
                },
                'sensex': {
                    'current': 71200,
                    'change': +0.8,
                    'trend': 'bullish'
                }
            }
            
            # Nifty 50 Insight
            nifty_change = market_data['nifty50']['change']
            if nifty_change > 0:
                insight = self._create_unique_insight(
                    'RECOMMENDATION',
                    title=f'📈 NIFTY 50 Up {nifty_change}%',
                    description=f'The NIFTY 50 is currently at {market_data["nifty50"]["current"]:,}, up {nifty_change}% today. The market is showing bullish trends. Consider reviewing your investment portfolio.',
                    priority=3,
                )
                if insight:
                    insights.append(insight)
            
            # Top performing sectors
            insight = self._create_unique_insight(
                'RECOMMENDATION',
                title='🏆 Top Performing Sectors Today',
                description='IT, Banking, and Pharma sectors are showing strong performance today. Technology stocks like TCS, Infosys, and banking stocks like HDFC Bank, ICICI Bank are trending upward. Consider diversifying your portfolio across these sectors.',
                priority=3,
            )
            if insight:
                insights.append(insight)
            
        except Exception as e:
            print(f"Error fetching stock market data: {e}")
        
        return insights
    
    def get_bank_interest_rates(self):
        """Get and compare bank interest rates"""
        insights = []
        
        # Sample bank interest rates - you can fetch this from bank APIs or websites
        bank_rates = [
            {'bank': 'SBI', 'savings': 2.70, 'fd_1yr': 6.80, 'fd_3yr': 7.00},
            {'bank': 'HDFC Bank', 'savings': 3.00, 'fd_1yr': 7.00, 'fd_3yr': 7.25},
            {'bank': 'ICICI Bank', 'savings': 3.00, 'fd_1yr': 7.00, 'fd_3yr': 7.10},
            {'bank': 'Axis Bank', 'savings': 3.00, 'fd_1yr': 7.10, 'fd_3yr': 7.25},
            {'bank': 'Kotak Mahindra', 'savings': 3.50, 'fd_1yr': 7.10, 'fd_3yr': 7.40},
        ]
        
        # Find best rates
        best_savings = max(bank_rates, key=lambda x: x['savings'])
        best_fd_1yr = max(bank_rates, key=lambda x: x['fd_1yr'])
        best_fd_3yr = max(bank_rates, key=lambda x: x['fd_3yr'])
        
        # Savings Account Insight
        insight = AIInsight.objects.create(
            user=self.user,
            insight_type='RECOMMENDATION',
            title=f'🏦 Best Savings Rate: {best_savings["bank"]} at {best_savings["savings"]}%',
            description=f'{best_savings["bank"]} offers the highest savings account interest rate at {best_savings["savings"]}%. If you have a large balance in your savings account, consider switching to maximize your returns.',
            priority=2
        )
        insights.append(insight)
        
        # Fixed Deposit Insight
        insight = AIInsight.objects.create(
            user=self.user,
            insight_type='RECOMMENDATION',
            title=f'💎 Best FD Rates',
            description=f'Top FD rates: {best_fd_1yr["bank"]} offers {best_fd_1yr["fd_1yr"]}% for 1-year FD, and {best_fd_3yr["bank"]} offers {best_fd_3yr["fd_3yr"]}% for 3-year FD. Consider fixed deposits for guaranteed returns on your savings.',
            priority=3
        )
        insights.append(insight)
        
        # Rate comparison table
        rate_table = "Current Interest Rates:\n"
        for bank in bank_rates:
            rate_table += f"\n{bank['bank']}: Savings {bank['savings']}%, FD(1Y) {bank['fd_1yr']}%, FD(3Y) {bank['fd_3yr']}%"
        
        insight = AIInsight.objects.create(
            user=self.user,
            insight_type='RECOMMENDATION',
            title='💰 Bank Interest Rate Comparison',
            description=rate_table + "\n\nCompare and choose the best bank for your savings based on these rates.",
            priority=2
        )
        insights.append(insight)
        
        return insights
    
    def get_investment_recommendations(self):
        """Provide investment recommendations based on user's profile"""
        insights = []
        
        total_balance = self.user.profile.total_balance
        monthly_expenses = self.user.profile.monthly_expenses
        
        # Top stocks recommendation
        top_stocks = [
            {'name': 'Reliance Industries', 'sector': 'Oil & Gas', 'price': 2450, 'pe_ratio': 26.5},
            {'name': 'TCS', 'sector': 'IT', 'price': 3650, 'pe_ratio': 28.2},
            {'name': 'HDFC Bank', 'sector': 'Banking', 'price': 1580, 'pe_ratio': 19.8},
            {'name': 'Infosys', 'sector': 'IT', 'price': 1420, 'pe_ratio': 24.5},
            {'name': 'ITC', 'sector': 'FMCG', 'price': 445, 'pe_ratio': 22.1},
        ]
        
        stocks_desc = "Top blue-chip stocks to consider:\n"
        for stock in top_stocks:
            stocks_desc += f"\n• {stock['name']} ({stock['sector']}): ₹{stock['price']:,} | PE: {stock['pe_ratio']}"
        
        insight = AIInsight.objects.create(
            user=self.user,
            insight_type='RECOMMENDATION',
            title='📊 Top Blue-Chip Stocks to Consider',
            description=stocks_desc + "\n\nThese are fundamentally strong companies with good track records. Consider consulting a financial advisor before investing.",
            priority=3
        )
        insights.append(insight)
        
        # Investment allocation recommendation
        if total_balance > monthly_expenses * 6:  # Has emergency fund
            insight = AIInsight.objects.create(
                user=self.user,
                insight_type='RECOMMENDATION',
                title='💼 Investment Allocation Suggestion',
                description=f'You have a healthy emergency fund. Consider this allocation: 60% in Equity Mutual Funds (for long-term growth), 30% in Debt Funds (for stability), and 10% in Gold/Commodities (for diversification). This balanced approach can help optimize returns while managing risk.',
                priority=4
            )
            insights.append(insight)
        
        # Mutual funds recommendation
        insight = AIInsight.objects.create(
            user=self.user,
            insight_type='RECOMMENDATION',
            title='📈 Consider Mutual Funds',
            description='Mutual funds offer professional management and diversification. Popular options: Large-cap funds for stability (like HDFC Top 100), Mid-cap funds for growth (like Axis Midcap), and Index funds for passive investing (like Nifty 50 Index Fund). Start with SIPs for rupee cost averaging.',
            priority=3
        )
        insights.append(insight)
        
        return insights


# Helper function to fetch real-time data (optional integration)
def fetch_market_data():
    """
    Fetch real-time market data from APIs
    You can integrate with:
    - Alpha Vantage API
    - Yahoo Finance API
    - NSE/BSE official APIs
    - Google News RSS (via feedparser) for daily market/news summaries
    """
    # Placeholder helper for fetching market data from external APIs.
    # Implement integration with preferred market-data providers here.
    # Currently not implemented; return empty dict as placeholder
    return {}


def fetch_google_news_rss(query: str = None, max_items: int = None):
    """
    Fetch latest news from Google News RSS for a given query.
    Returns a list of entries with `title`, `link`, `published`, and `summary`.

    NOTE: This uses Google News RSS (no scraping). Configure `NEWS_QUERY` and
    `NEWS_MAX_ITEMS` in Django settings if desired.
    """
    query = query or getattr(settings, 'NEWS_QUERY', 'stocks OR trading OR finance')
    max_items = max_items or getattr(settings, 'NEWS_MAX_ITEMS', 8)

    # Construct Google News RSS URL
    # Example: https://news.google.com/rss/search?q=stocks+trading+finance&hl=en-US&gl=US&ceid=US:en
    q = requests.utils.requote_uri(query.replace(' ', '+'))
    rss_url = f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en'

    try:
        feed = feedparser.parse(rss_url)
        entries = []
        for entry in feed.entries[:max_items]:
            entries.append({
                'title': entry.get('title', '').strip(),
                'link': entry.get('link', '').strip(),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')
            })
        return entries
    except Exception as e:
        print(f"Error fetching Google News RSS: {e}")
        return []


def create_news_insights_for_all_users(query: str = None, max_items: int = None):
    """
    Fetch Google News RSS and create `AIInsight` entries for users who have
    `profile.ai_insights` enabled. Avoids duplicate titles for the same day.
    """
    entries = fetch_google_news_rss(query=query, max_items=max_items)
    if not entries:
        return 0

    users = User.objects.filter(profile__ai_insights=True)
    created_count = 0
    today = timezone.now().date()

    for user in users:
        for e in entries:
            title = e['title']
            # avoid duplicate for the same user (title-based dedupe)
            exists = AIInsight.objects.filter(user=user, title=title).exists()
            if exists:
                continue

            description = f"{e['summary']}\n\nRead more: {e['link']}"
            AIInsight.objects.create(
                user=user,
                insight_type='RECOMMENDATION',
                title=title,
                description=description,
                priority=1
            )
            created_count += 1

    return created_count