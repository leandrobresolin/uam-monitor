from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial fixtures"

    def handle(self, *args, **options):

        fixtures = [
            "aircraft_types.json",
            "aircrafts.json",
            "vertiports.json",
            "routes.json",
            "routes_return.json",
            "waypoints_cgh_gru.json",
            "waypoints_gru_cgh.json",
        ]

        for fixture in fixtures:
            self.stdout.write(f"Loading fixture: {fixture}")
            call_command("loaddata", fixture)

        self.stdout.write(self.style.SUCCESS("All fixtures loaded."))
