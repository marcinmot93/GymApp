from django.db import models
from django.contrib.auth.models import User
import datetime

DAYS = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
)

WEEKS = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
)

STATUS = (
    (1, 'active'),
    (2, 'to do'),
    (3, 'ended'),
)

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

class ThePupil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    starting_weight = models.FloatField()
    height = models.FloatField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)


class Exercise(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    movie_link = models.CharField(max_length=256, null=True)

class TrainingPlan(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    the_pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE)
    status = models.IntegerField(default=2, choices=STATUS)
    start_date = models.DateField()
    week_training_days = models.IntegerField(choices=WEEKS)
    exercises = models.ManyToManyField(Exercise, through="PlanExercises")

    def check_plan_expiration(self):
        now = datetime.datetime.now().date()
        if (now - self.start_date).days / 7 >= self.week_training_days:
            self.status = 2
            self.save()
            return False
        return True

    def check_days_left(self):
        now = datetime.datetime.now().date()
        days_passed = (now - self.start_date).days
        days_remaining = (self.week_training_days * 7) - days_passed
        return days_remaining

    def till_start_days(self):
        now = datetime.datetime.now().date()
        days_left = (self.start_date-now).days
        return days_left


class DayNumber(models.Model):
    name = models.CharField(max_length=128)
    number = models.IntegerField(choices=DAYS)

class PlanExercises(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    series = models.IntegerField()
    reps = models.IntegerField()
    training_day = models.ForeignKey(DayNumber, on_delete=models.CASCADE)

class ActualWeight(models.Model):
    actual_weight = models.FloatField()
    add_date = models.DateField()
    the_pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE)



