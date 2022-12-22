from django.core.management import BaseCommand
from fruitshop import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username='joker').exists():
            User.objects.create(username='joker', email='joker_joker@email.com')
            self.stdout.write("JOKER CREATED")
        else:
            self.stdout.write("JOKER EXISS")
        if not User.objects.filter(username="anonim").exists():
            User.objects.create(username='anonim', email='anonim@email.com')
            self.stdout.write("ANONI< CREATED")

        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create(username='admin', email='anonim@email.com')
            admin.set_password("qwerty40Req!")
            admin.save()
            personal_account = models.PersonalAccount.objects.create(user=admin)
            self.stdout.write("ADMON CREATED")
        else:
            self.stdout.write("ADMIN EXIRX")


