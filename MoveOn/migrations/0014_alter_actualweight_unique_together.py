# Generated by Django 4.1.6 on 2023-02-21 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MoveOn', '0013_alter_actualweight_add_date_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='actualweight',
            unique_together={('add_date', 'the_pupil')},
        ),
    ]
