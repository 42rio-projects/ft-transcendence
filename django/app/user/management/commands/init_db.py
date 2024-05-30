from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Initialize database with required updates'

    def handle(self, *args, **kwargs):
        sql_commands = [
            "UPDATE pong_game SET finished = true;",
            "UPDATE pong_tournament SET finished = true;"
        ]

        with connection.cursor() as cursor:
            for command in sql_commands:
                cursor.execute(command)
                self.stdout.write(self.style.SUCCESS(f"Executed: {command}"))
