# Generated by Django 4.1.6 on 2023-02-20 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MoveOn', '0011_alter_ismatched_pupil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismatched',
            name='decision',
            field=models.IntegerField(choices=[(1, 'Yes'), (2, 'No')]),
        ),
    ]