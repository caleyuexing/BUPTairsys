from django.core.management.base import BaseCommand
from Aircons.models import Group
from Users.models import Users_possess
from django_q.models import Schedule

class Command(BaseCommand):
    help = 'Clears the aircon_info table'

    def handle(self, *args, **kwargs):
        Group.objects.all().delete()
        Users_possess.objects.all().delete()
        Schedule.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared aircon_info table'))