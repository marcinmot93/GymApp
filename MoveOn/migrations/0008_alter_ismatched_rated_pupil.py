# Generated by Django 4.1.6 on 2023-02-20 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MoveOn', '0007_remove_ismatched_rated_pupil_ismatched_rated_pupil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismatched',
            name='rated_pupil',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rated_one', to='MoveOn.thepupil'),
        ),
    ]
