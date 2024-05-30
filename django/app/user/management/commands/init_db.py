from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Initialize database with required updates'

    def handle(self, *args, **kwargs):
        sql_commands = [
            "DELETE FROM pong_game WHERE finished = false;",
            "DELETE FROM pong_tournament_players WHERE tournament_id IN (SELECT id FROM pong_tournament WHERE finished = false);",
            "DELETE FROM pong_tournament WHERE finished = false;"
        ]

        with connection.cursor() as cursor:
            for command in sql_commands:
                cursor.execute(command)
                self.stdout.write(self.style.SUCCESS(f"Executed: {command}"))
