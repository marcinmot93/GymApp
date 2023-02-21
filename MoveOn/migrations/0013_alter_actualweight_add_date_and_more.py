# Generated by Django 4.1.6 on 2023-02-21 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MoveOn', '0012_alter_ismatched_decision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualweight',
            name='add_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterUniqueTogether(
            name='actualweight',
            unique_together={('add_date', 'actual_weight')},
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=256)),
                ('image', models.ImageField(upload_to='')),
                ('likes', models.IntegerField(default=0)),
                ('comment', models.CharField(max_length=128)),
                ('pupil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MoveOn.thepupil')),
            ],
        ),
    ]
