from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from flights.models import Flight


class Command(BaseCommand):
    help = 'ساخت گروه‌های کاربری برای مدیریت پروازها'

    def handle(self, *args, **options):
        # ساخت گروه Flight Managers
        group, created = Group.objects.get_or_create(name='Flight Managers')
        
        # اختیارات مورد نیاز برای Flight Managers
        content_type = ContentType.objects.get_for_model(Flight)
        
        # اختیارات استاندارد
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=['add_flight', 'change_flight', 'delete_flight']
        )
        
        group.permissions.set(permissions)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ گروه "Flight Managers" با موفقیت ساخته شد'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠ گروه "Flight Managers" قبلاً وجود داشت'
                )
            )
