from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create initial users: 2 conveners, 3 reviewers, and 1 sample author'

    def handle(self, *args, **options):
        DEFAULT_PASSWORD = 'Portal@2024'

        users = [
            # Conveners
            {'email': 'navyabhanothi@gmail.com', 'full_name': 'Dr. Priya Sharma', 'role': 'convener'},
            {'email': 'bharath11062004@gmail.com', 'full_name': 'Dr. Ravi Kumar',   'role': 'convener'},
            # Reviewers
            {'email': 'bhavyasuseela05@gmail.com', 'full_name': 'Prof. Anita Nair',    'role': 'reviewer'},
            {'email': 'vupadhayayulab@gmail.com', 'full_name': 'Dr. Suresh Reddy',    'role': 'reviewer'},
            {'email': 'ramyanavya02@gmail.com', 'full_name': 'Dr. Meena Iyer',      'role': 'reviewer'},
            # Sample author
            {'email': 'bhanothiveeradevi@gmail.com',   'full_name': 'Arjun Patel',         'role': 'author'},
        ]

        for u in users:
            if User.objects.filter(email=u['email']).exists():
                self.stdout.write(f"  SKIP  {u['email']} (already exists)")
                continue
            user = User.objects.create_user(
                email=u['email'],
                password=DEFAULT_PASSWORD,
                full_name=u['full_name'],
                role=u['role'],
            )
            self.stdout.write(self.style.SUCCESS(f"  CREATED  {user.role:<10} {user.email}"))

        self.stdout.write(self.style.SUCCESS(
            f'\nAll users created. Default password: {DEFAULT_PASSWORD}'
        ))
        self.stdout.write('IMPORTANT: Change these passwords and emails before going to production!\n')
