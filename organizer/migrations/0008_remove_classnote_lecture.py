# Generated by Django 3.2.9 on 2024-04-14 03:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizer', '0007_classnote_lecture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classnote',
            name='lecture',
        ),
    ]
