from django.core.management.base import BaseCommand
from accounts.ai_service import create_news_insights_for_all_users


class Command(BaseCommand):
    help = 'Fetch latest Google News (stocks/finance) and create AI Insights for users'

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, help='Search query for news')
        parser.add_argument('--max', type=int, default=8, help='Maximum news items to fetch')

    def handle(self, *args, **options):
        query = options.get('query')
        max_items = options.get('max')

        created = create_news_insights_for_all_users(query=query, max_items=max_items)
        self.stdout.write(self.style.SUCCESS(f'Created {created} news-based AI insight(s)'))
