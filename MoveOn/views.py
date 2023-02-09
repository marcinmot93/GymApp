from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.views.generic import FormView
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from MoveOn.forms import *
from MoveOn.models import *

class Index(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return render(request, 'main.html')

        if hasattr(request.user, 'trainer'):
            trainer = get_object_or_404(Trainer, id=request.user.trainer.id)
            return render(request, 'main_trainer.html', {'trainer': trainer})
        elif hasattr(request.user, 'thepupil'):
            pupil = get_object_or_404(ThePupil, id=request.user.thepupil.id)
            return render(request, 'main_pupil.html', {'pupil': pupil})
        else:
            return redirect(f'creating_details/{request.user.id}/')


class LoginView(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect('/')
        form = LoginForm()

        return render(request, 'login.html', {'form': form})

    def post(self, request):

        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            username = data.get('username')
            password = data.get('password')

            if not User.objects.filter(username=username):
                messages.error(request, 'Username does not exist')
                return redirect('/login/')

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                if hasattr(user, 'thepupil'):
                    pupil = user.thepupil.id
                    return redirect(f'/main/{pupil}/')
                elif hasattr(user, 'trainer'):
                    trainer = user.trainer.id
                    return redirect(f'/main/trainer/{trainer}/')
                else:
                    return redirect(f'/creating_details/{user.id}/')
            else:
                messages.error(request, 'Wrong password')
                return redirect('/login/')


class LogoutView(View):

    def get(self, request):

        logout(request)

        return redirect('/')


class CreateUserView(View):

    def get(self, request):

        form = CreateUserForm()

        return render(request, 'create_account.html', {'form': form})


    def post(self, request):

        form = CreateUserForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=data.get('login'),
                password=data.get('password'),
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
            )

            account_type = data.get('account_type')
            login(request, user)

            if account_type == '1':
                return redirect(f'/creating_details/{user.id}/')
            else:
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                trainer = Trainer.objects.create(user=user, first_name=first_name, last_name=last_name)

                return redirect(f'/main/trainer/{trainer.id}/')

        else:
            return render(request, 'create_account.html', {'form': form})


class PupilDetailsView(View):

    def get(self, request, user_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if hasattr(request.user, 'thepupil') or hasattr(request.user, 'trainer'):
            return redirect('/')
        user = User.objects.get(id=user_id)
        trainers = Trainer.objects.all()

        return render(request, 'pupil_details.html', {'user': user, 'trainers': trainers})

    def post(self, request, user_id):

        user = User.objects.get(id=user_id)
        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name')
        starting_weight = request.POST.get('starting_weight')
        height = request.POST.get('height')
        trainer = request.POST.get('trainer')
        trainer = Trainer.objects.get(id=int(trainer))
        pupil = ThePupil.objects.create(user=user, first_name=first_name, last_name=last_name, starting_weight=starting_weight, height=height, trainer=trainer)

        return redirect(f'/main/{pupil.id}')


class TrainerMainView(View):

    def get(self, request, trainer_id):

        if request.user.is_authenticated:
            if hasattr(request.user, 'trainer') and request.user.trainer.id == trainer_id:
                trainer = get_object_or_404(Trainer, id=request.user.trainer.id)
                pupils = trainer.thepupil_set.all()

                return render(request, 'trainer_main.html', {'trainer': trainer, 'pupils': pupils})

            else:
                return redirect('/')
        else:
            return redirect('/')


class ThePupilMainView(View):

    def get(self, request, pupil_id):

        if request.user.is_authenticated:
            if hasattr(request.user, 'thepupil') and request.user.thepupil.id == pupil_id:
                pupil = get_object_or_404(ThePupil, id=pupil_id)

                for plan in pupil.trainingplan_set.all():
                    if plan.status == 1:
                        training_plan = get_object_or_404(pupil.trainingplan_set.all(), status=1)
                        if training_plan.check_plan_expiration() is False:
                            messages.error(request, 'Your plan has ended')
                            return redirect(f'/main/{pupil_id}/')
                        left_days = None
                        till_start = None
                        if datetime.datetime.now().date() >= training_plan.start_date:
                            left_days = training_plan.check_days_left
                        else:
                            till_start = training_plan.till_start_days
                        days = training_plan.planexercises_set.all()
                        first = None
                        second = None
                        third = None
                        fourth = None
                        fifth = None
                        sixth = None
                        seventh = None
                        for i in days:
                            if i.training_day.id == 1:
                                first = i.training_day
                            if i.training_day.id == 2:
                                second = i.training_day
                            if i.training_day.id == 3:
                                third = i.training_day
                            if i.training_day.id == 4:
                                fourth = i.training_day
                            if i.training_day.id == 5:
                                fifth = i.training_day
                            if i.training_day.id == 6:
                                sixth = i.training_day
                            if i.training_day.id == 7:
                                seventh = i.training_day

                        context = {'pupil': pupil,
                                    'training_plan': training_plan,
                                    'days': days,
                                    }
                        if first:
                            context['first'] = first
                        if second:
                            context['second'] = second
                        if third:
                            context['third'] = third
                        if fourth:
                            context['fourth'] = fourth
                        if fifth:
                            context['fifth'] = fifth
                        if sixth:
                            context['sixth'] = sixth
                        if seventh:
                            context['seventh'] = seventh
                        if left_days:
                            context['left_days'] = left_days
                        if till_start:
                            context['till_start'] = till_start

                        return render(request, 'pupil_main.html', context)
                    else:
                        return render(request, 'pupil_main_without_plan.html', {'pupil': pupil})
                else:
                    return render(request, 'pupil_main_without_plan.html', {'pupil': pupil})
            else:
                return redirect('/')
        else:
            return redirect('/')


class CreatePlanView(View):

    def get(self, request, trainer_id, pupil_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'trainer'):
            return redirect('/')
        if not request.user.trainer.id == trainer_id:
            return redirect('/')
        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)

        if pupil not in trainer.thepupil_set.all():
            return redirect('/')

        form = AddTrainingPlanForm()

        return render(request, 'create_plan.html', {'trainer':trainer, 'pupil': pupil, 'form': form})


    def post(self, request, trainer_id, pupil_id ):

        form = AddTrainingPlanForm(request.POST)
        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)

        if form.is_valid():
            if pupil.trainingplan_set.filter(status=1).exists():
                messages.error(request, 'The Pupil has already active plan')
                return render(request, 'create_plan.html', {'trainer': trainer, 'pupil': pupil, 'form': form})
            data = form.cleaned_data
            name = data.get('name')
            description = data.get('description')
            start_date = data.get('start_date')
            week_training_days = data.get('week_training_days')

            plan = TrainingPlan.objects.create(
                name=name,
                description=description,
                trainer=trainer,
                status=1,
                the_pupil=pupil,
                start_date=start_date,
                week_training_days=week_training_days
            )

            return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')

        else:
            return render(request, 'create_plan.html', {'trainer': trainer, 'pupil': pupil, 'form': form})


class CreateExercisePlan(View):

    def get(self, request, trainer_id, pupil_id, plan_id):

        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        plan = get_object_or_404(TrainingPlan, id=plan_id)
        plan_days = plan.planexercises_set.all()
        first = None
        second = None
        third = None
        fourth = None
        fifth = None
        sixth = None
        seventh = None
        for i in plan_days:
            if i.training_day.id == 1:
                first = i.training_day
            if i.training_day.id == 2:
                second = i.training_day
            if i.training_day.id == 3:
                third = i.training_day
            if i.training_day.id == 4:
                fourth = i.training_day
            if i.training_day.id == 5:
                fifth = i.training_day
            if i.training_day.id == 6:
                sixth = i.training_day
            if i.training_day.id == 7:
                seventh = i.training_day

        context = {'trainer': trainer,
                   'pupil': pupil,
                   'days': DayNumber.objects.all(),
                   'exercises': trainer.exercise_set.all(),
                   'plan': plan,
                   'plan_days': plan_days,
                   }
        if first:
            context['first'] = first
        if second:
            context['second'] = second
        if third:
            context['third'] = third
        if fourth:
            context['fourth'] = fourth
        if fifth:
            context['fifth'] = fifth
        if sixth:
            context['sixth'] = sixth
        if seventh:
            context['seventh'] = seventh


        return render(request, 'create_exercise_plan.html', context)

    def post(self, request, trainer_id, pupil_id, plan_id):

        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        plan = get_object_or_404(TrainingPlan, id=plan_id)

        exercise = request.POST.get('exercise')
        exercise = get_object_or_404(Exercise, id=exercise)
        series = request.POST.get('series')
        if not series:
            messages.error(request, "Fields cannot be empty")
            return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')
        reps = request.POST.get('reps')
        if not reps:
            messages.error(request, "Fields cannot be empty")
            return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')
        day = request.POST.get('day')
        day = get_object_or_404(DayNumber, id=day)

        PlanExercises.objects.create(exercise=exercise, training_plan=plan, series=series, reps=reps, training_day=day)

        return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')


class DeleteFromExercisePlan(View):

    def get(self, request, plan_exercise_id, pupil_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'trainer'):
            return redirect('/')
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        trainer_id = pupil.trainer.id
        if not request.user.trainer.id == trainer_id:
            return redirect('/')
        plan = pupil.trainingplan_set.get(status=1).id
        plan_exercise = get_object_or_404(PlanExercises, id=plan_exercise_id)
        plan_exercise.delete()

        return redirect(f'/exercise_plan/{trainer_id}/{pupil_id}/{plan}/')


class ExercisesView(View):

    def get(self, request, trainer_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'trainer'):
            return redirect('/')
        if not request.user.trainer.id == trainer_id:
            return redirect('/')
        form = AddExerciseForm()
        trainer = get_object_or_404(Trainer, id=trainer_id)
        exercises = trainer.exercise_set.all()

        return render(request, 'exercises.html', {'form': form, 'exercises': exercises, 'trainer': trainer})

    def post(self, request, trainer_id):

        form = AddExerciseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            trainer = get_object_or_404(Trainer, id=trainer_id)
            name = data.get('name')
            description = data.get('description')
            movie_link = data.get('movie_link')
            exercise = Exercise.objects.filter(name__iexact=name)
            if not exercise:
                Exercise.objects.create(trainer=trainer, name=name, description=description, movie_link=movie_link)
                return redirect(f'/exercises/{trainer_id}/')

            else:
                messages.error(request, 'Name already exist')
                return redirect(f'/exercises/{trainer_id}/')


class TrainerPupilView(View):

    def get(self, request, trainer_id, pupil_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'trainer'):
            return redirect('/')
        if not request.user.trainer.id == trainer_id:
            return redirect('/')
        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        if pupil not in trainer.thepupil_set.all():
            return redirect('/')
        for plan in pupil.trainingplan_set.all():
            if plan.status == 1:
                training_plan = get_object_or_404(pupil.trainingplan_set.all(), status=1)
                left_days = None
                till_start = None
                if datetime.datetime.now().date() >= training_plan.start_date:
                    left_days = training_plan.check_days_left
                else:
                    till_start = training_plan.till_start_days
                days = training_plan.planexercises_set.all()
                first = None
                second = None
                third = None
                fourth = None
                fifth = None
                sixth = None
                seventh = None
                for i in days:
                    if i.training_day.id == 1:
                        first = i.training_day
                    if i.training_day.id == 2:
                        second = i.training_day
                    if i.training_day.id == 3:
                        third = i.training_day
                    if i.training_day.id == 4:
                        fourth = i.training_day
                    if i.training_day.id == 5:
                        fifth = i.training_day
                    if i.training_day.id == 6:
                        sixth = i.training_day
                    if i.training_day.id == 7:
                        seventh = i.training_day

                context = {'pupil': pupil,
                            'training_plan': training_plan,
                            'days': days,
                            'trainer': trainer
                            }
                if first:
                    context['first'] = first
                if second:
                    context['second'] = second
                if third:
                    context['third'] = third
                if fourth:
                    context['fourth'] = fourth
                if fifth:
                    context['fifth'] = fifth
                if sixth:
                    context['sixth'] = sixth
                if seventh:
                    context['seventh'] = seventh
                if left_days:
                    context['left_days'] = left_days
                if till_start:
                    context['till_start'] = till_start

                return render(request, 'trainer_pupil_main.html', context)
            else:
                return render(request, 'trainer_pupil_main.html', {'pupil': pupil})
        else:
            return render(request, 'trainer_pupil_main.html', {'pupil': pupil})

