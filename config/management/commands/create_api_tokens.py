"""
Django management command to create API tokens for all users.
Executed during deployment to ensure tokens exist.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create API tokens for all users'

    def handle(self, *args, **options):
        """Create tokens for all users that don't have one."""
        users = User.objects.all()
        created_count = 0

        for user in users:
            token, created = Token.objects.get_or_create(user=user)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Token created for user: {user.username}')
                )
                self.stdout.write(f'  Token: {token.key}')
                created_count += 1
            else:
                self.stdout.write(f'✓ Token already exists for user: {user.username}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total tokens created: {created_count}')
        )
