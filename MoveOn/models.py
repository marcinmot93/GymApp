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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

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

    def check_plan_expire(self):
        now = datetime.datetime.now().date()
        if (now - self.start_date).days / 7 >= self.week_training_days:
            self.status = 3
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
        days_left = (self.start_date - now).days
        return days_left

    def current_plan_day(self):
        now = datetime.datetime.now().date()
        current_day = now - self.start_date
        return current_day.days


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
    add_date = models.DateField(auto_now=True)
    the_pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('add_date', 'the_pupil')


class MyAchievements(models.Model):
    pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE)
    exercise = models.ForeignKey(PlanExercises, on_delete=models.CASCADE)
    which_series = models.IntegerField()
    reps = models.IntegerField()
    result = models.FloatField()
    date = models.DateField()
    add_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('which_series', 'exercise', 'date')


class IsMatched(models.Model):
    pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE, related_name='rating_one')
    rated_pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE, related_name='rated_one')
    decision = models.IntegerField(choices=(
        (1, 'Yes'),
        (2, 'No')
    ))

    class Meta:
        unique_together = ('pupil', 'rated_pupil')


class Post(models.Model):
    pupil = models.ForeignKey(ThePupil, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=True)
    image = models.ImageField()
    likes = models.IntegerField(default=0)
    comment = models.CharField(max_length=128)
