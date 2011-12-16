from django.core.management.base import BaseCommand
from lizard_shape.models import Shape


class Command(BaseCommand):
    args = ''
    help = ('Re-saves all Shape models (1.17). '
            'This updates the Shape.prj field.')

    def handle(self, *args, **options):
        for s in Shape.objects.all():
            print 'Updating shape %s...' % s
            s.save()
