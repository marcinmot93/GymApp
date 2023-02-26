from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from MoveOn.forms import *
from MoveOn.models import *
import datetime


class Index(View):
    """Renders the appropriate main page based on the user's role."""

    def get(self, request):
        """Renders the appropriate template depending on user type."""
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
    """Handles user login functionality."""

    def get(self, request):
        """Renders the login page."""
        if request.user.is_authenticated:
            return redirect('/')
        form = LoginForm()

        return render(request, 'login.html', {'form': form})

    def post(self, request):
        """Logs in the user and redirects them to the appropriate page."""
        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            username = data.get('username')
            password = data.get('password')

            if not User.objects.filter(username=username):
                messages.error(request, 'User does not exist')
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
        return render(request, 'login.html', {'form': form})


class LogoutView(View):
    """Handles user logout functionality."""

    def get(self, request):
        """Logs out the user and redirects them to the homepage."""
        logout(request)

        return redirect('/')


class CreateUserView(View):
    """View responsible for creating new user accounts."""

    def get(self, request):
        """Handles GET requests to the view."""
        form = CreateUserForm()

        return render(request, 'create_account.html', {'form': form})

    def post(self, request):
        """Handles POST requests to the view."""
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
            return redirect('/create_account/')


class PupilDetailsView(View):
    """View responsible for showing and processing pupil details form."""

    def get(self, request, user_id):
        """Handles GET requests to the view."""
        if not request.user.is_authenticated:
            return redirect('/')
        if hasattr(request.user, 'thepupil') or hasattr(request.user, 'trainer'):
            return redirect('/')
        if not request.user.id == user_id:
            return redirect('/')
        user = get_object_or_404(User, id=user_id)
        initial_data = {
            'name': user.first_name,
            'last_name': user.last_name,
        }
        form = PupilDetailsForm(
            initial=initial_data
        )
        form.fields['trainer'].choices = [
            (trainer.id, f'{trainer.name}') for trainer in Trainer.objects.all()
        ]

        return render(request, 'pupil_details.html', {'form': form})

    def post(self, request, user_id):
        """Handles POST requests to the view."""
        form = PupilDetailsForm(request.POST)
        form.fields['trainer'].choices = [
            (trainer.id, f'{trainer.name}') for trainer in Trainer.objects.all()
        ]

        if form.is_valid():
            data = form.cleaned_data

            user = get_object_or_404(User, id=user_id)
            pupil = ThePupil.objects.create(
                user=user,
                first_name=data.get('name'),
                last_name=data.get('last_name'),
                starting_weight=data.get('starting_weight'),
                height=data.get('height'),
                trainer=Trainer.objects.get(id=int(data.get('trainer'))),
            )

            return redirect(f'/main/{pupil.id}/')
        print(form.errors)
        return redirect(f'/creating_details/{user_id}/')


class TrainerMainView(View):
    """A view for displaying the main page for a trainer with their pupils and training plans."""

    def get(self, request, trainer_id):
        """Handles GET requests. Renders the trainer main page with the trainer's pupils and training plans."""
        if request.user.is_authenticated:
            if hasattr(request.user, 'trainer') and request.user.trainer.id == trainer_id:
                trainer = get_object_or_404(Trainer, id=request.user.trainer.id)
                pupils = trainer.thepupil_set.all()
                context = {
                    'trainer': trainer,
                    'pupils': pupils,
                }

                return render(request, 'trainer_main.html', context)
            else:
                return redirect('/')
        else:
            return redirect('/')


class ThePupilMainView(View):
    """A view for displaying the main page for a pupil with their current training plan."""

    def get(self, request, pupil_id):
        """Handles GET requests. Renders the pupil main page with the current training plan."""
        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'thepupil'):
            return redirect('/')
        if not request.user.thepupil.id == pupil_id:
            return redirect('/')
        pupil = get_object_or_404(ThePupil, id=pupil_id)

        for plan in pupil.trainingplan_set.all():
            if plan.status == 1:
                training_plan = get_object_or_404(pupil.trainingplan_set.all(), status=1)
                if training_plan.check_plan_expire() is False:
                    messages.error(request, 'Your plan has ended')
                    return redirect(f'/main/{pupil_id}/')
                left_days = None
                till_start = None
                current_day = None
                if datetime.datetime.now().date() >= training_plan.start_date:
                    left_days = training_plan.check_days_left
                    current_day = training_plan.current_plan_day
                else:
                    till_start = training_plan.till_start_days
                days = training_plan.planexercises_set.all()
                mapping = {
                    1: 'first',
                    2: 'second',
                    3: 'third',
                    4: 'fourth',
                    5: 'fifth',
                    6: 'sixth',
                    7: 'seventh',
                }
                mapping2 = {
                    1: 'first1',
                    2: 'second2',
                    3: 'third3',
                    4: 'fourth4',
                    5: 'fifth5',
                    6: 'sixth6',
                    7: 'seventh7',
                }
                ctx = {mapping[day.training_day.id]: day.training_day for day in days}

                ctx2 = {mapping2[day.training_day.id]: days.filter(training_day=day.training_day.id) for day in days}

                context = {'pupil': pupil,
                           'training_plan': training_plan,
                           'days': days,
                           **ctx,
                           **ctx2,
                           }

                if left_days:
                    context['left_days'] = left_days
                    context['current_day'] = current_day
                if till_start:
                    context['till_start'] = till_start
                if not ActualWeight.objects.filter(the_pupil=pupil).first():
                    actual_weight_start = pupil.starting_weight
                    context['actual_weight_start'] = actual_weight_start
                else:
                    actual_weight = ActualWeight.objects.filter(the_pupil=pupil).latest('add_date')
                    context['actual_weight'] = actual_weight

                form = ActualWeightForm()
                context['form'] = form

                return render(request, 'pupil_main.html', context)
            else:
                return render(request, 'pupil_main_without_plan.html', {'pupil': pupil})
        else:
            return render(request, 'pupil_main_without_plan.html', {'pupil': pupil})

    def post(self, request, pupil_id):

        form = ActualWeightForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            actual_weight = data.get('actual_weight')
            pupil = get_object_or_404(ThePupil, id=pupil_id)
            date = datetime.date.today()
            if ActualWeight.objects.filter(the_pupil=pupil, add_date=date).exists():
                obj = ActualWeight.objects.get(the_pupil=pupil, add_date=date)
                obj.actual_weight = actual_weight
                obj.save()
            else:
                ActualWeight.objects.create(the_pupil=pupil, actual_weight=actual_weight)

            return redirect(f'/main/{pupil_id}')


class CreatePlanView(View):
    """A view for creating a new training plan for a pupil."""

    def get(self, request, trainer_id, pupil_id):
        """Handles GET requests. Renders the create plan page for the specified trainer and pupil."""
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

        return render(request, 'create_plan.html', {'trainer': trainer, 'pupil': pupil, 'form': form})

    def post(self, request, trainer_id, pupil_id):
        """Handles POST requests. Creates a new training plan for the specified pupil."""
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
    """A view for adding exercises to a training plan."""

    def get(self, request, trainer_id, pupil_id, plan_id):
        """Handles GET requests. Renders the create exercise plan page for the specified plan."""
        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'trainer'):
            return redirect('/')
        if not request.user.trainer.id == trainer_id:
            return redirect('/')
        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        plan = get_object_or_404(TrainingPlan, id=plan_id)
        plan_days = plan.planexercises_set.all()
        form = CreateExercisePlanForm()
        form.fields['exercise'].choices = [
            ('', 'Choose an exercise'),
            *[(ex.id, f'{ex.name}') for ex in trainer.exercise_set.all()]
        ]
        training_days = {
            1: 'first',
            2: 'second',
            3: 'third',
            4: 'fourth',
            5: 'fifth',
            6: 'sixth',
            7: 'seventh',
        }

        ctx = {training_days[day.training_day.id]: day.training_day for day in plan_days}

        context = {'trainer': trainer,
                   'pupil': pupil,
                   'plan': plan,
                   'plan_days': plan_days,
                   'form': form,
                   }

        context.update(ctx)

        return render(request, 'create_exercise_plan.html', context)

    def post(self, request, trainer_id, pupil_id, plan_id):
        """Handles POST requests. Adds a new exercise to the specified training plan."""
        form = CreateExercisePlanForm(request.POST)
        trainer = get_object_or_404(Trainer, id=trainer_id)
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        plan = get_object_or_404(TrainingPlan, id=plan_id)

        form.fields['exercise'].choices = [
            (ex.id, f'{ex.name}') for ex in trainer.exercise_set.all()
        ]

        if form.is_valid():
            data = form.cleaned_data
            exercise = data.get('exercise')
            exercise = get_object_or_404(Exercise, id=exercise)
            series = data.get('series')
            reps = data.get('reps')
            day = data.get('training_day')
            day = get_object_or_404(DayNumber, id=day)

            PlanExercises.objects.create(exercise=exercise, training_plan=plan, series=series, reps=reps,
                                         training_day=day)

            return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')
        else:
            return redirect(f'/exercise_plan/{trainer.id}/{pupil.id}/{plan.id}/')


class DeleteFromExercisePlan(View):
    """A view for deleting an exercise from a training plan."""

    def get(self, request, plan_exercise_id, pupil_id):
        """Handles GET requests to the view."""
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
    """Displays exercises for a given trainer and allows adding new exercises."""

    def get(self, request, trainer_id):
        """Handles GET requests to retrieve and display exercises for a trainer."""
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
        """Handles POST requests to add a new exercise for a trainer."""
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
    """Displays information about a trainer's pupil and their training plan."""

    def get(self, request, trainer_id, pupil_id):
        """Handles GET requests to retrieve and display information about a pupil's training plan."""
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
                training_days = {
                    1: 'first',
                    2: 'second',
                    3: 'third',
                    4: 'fourth',
                    5: 'fifth',
                    6: 'sixth',
                    7: 'seventh',
                }

                ctx = {training_days[day.training_day.id]: day.training_day for day in days}

                context = {'pupil': pupil,
                           'training_plan': training_plan,
                           'days': days,
                           'trainer': trainer,
                           **ctx,
                           }

                if left_days:
                    context['left_days'] = left_days
                if till_start:
                    context['till_start'] = till_start

                return render(request, 'trainer_pupil_main.html', context)
            else:
                return render(request, 'trainer_pupil_main.html', {'pupil': pupil})
        else:
            return render(request, 'trainer_pupil_main.html', {'pupil': pupil})


class DeleteExercise(View):
    """Deletes a given exercise and redirects to the exercises page for the exercise's trainer."""

    def get(self, request, ex_id):
        """Handles GET requests to delete a given exercise."""
        exercise = Exercise.objects.get(id=ex_id)
        del_id = exercise.trainer.id
        exercise.delete()

        return redirect(f'/exercises/{del_id}/')


class Achievements(View):
    def get(self, request, pupil_id, plan_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'thepupil'):
            return redirect('/')
        if not request.user.thepupil.id == pupil_id:
            return redirect('/')
        all_days = DayNumber.objects.all()
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        plan = get_object_or_404(TrainingPlan, id=plan_id)
        days = plan.planexercises_set.all().order_by('training_day_id')
        mapping = {
            1: 'first',
            2: 'second',
            3: 'third',
            4: 'fourth',
            5: 'fifth',
            6: 'sixth',
            7: 'seventh',
        }
        mapping2 = {
            1: 'first1',
            2: 'second2',
            3: 'third3',
            4: 'fourth4',
            5: 'fifth5',
            6: 'sixth6',
            7: 'seventh7',
        }
        ctx = {mapping[day.training_day.id]: day.training_day for day in days}

        ctx2 = {mapping2[day.training_day.id]: days.filter(training_day=day.training_day.id) for day in days}

        context = {'all_days': all_days, 'days': days, 'pupil': pupil, **ctx, **ctx2}
        if MyAchievements.objects.exists():
            last_date = MyAchievements.objects.latest('date')
            day_of_week = last_date.date.strftime("%A")
            context['last_date'] = last_date
            context['day_of_week'] = day_of_week
            latest_results = MyAchievements.objects.filter(date=last_date.date).order_by('exercise', 'which_series')
            context['last_result'] = latest_results
            context['exercises'] = latest_results.distinct('exercise')

        return render(request, 'achievements.html', context)


class MyResults(View):

    def get(self, request, plan_id, exercise_id):
        plan_exercise = get_object_or_404(PlanExercises, id=plan_id)
        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'thepupil'):
            return redirect('/')
        if not request.user.thepupil.id == plan_exercise.training_plan.the_pupil.id:
            return redirect('/')
        exercise = get_object_or_404(Exercise, id=exercise_id)
        date = datetime.date.today()
        initial_data = {'date': date}
        form = AddResultForm(
            initial=initial_data
        )
        form.fields['which_series'].choices = [(str(i), str(i)) for i in range(1, int(plan_exercise.series) + 1)]

        ctx = {'form': form,
               'plan': plan_exercise,
               'exercise': exercise}

        now = datetime.date.today()
        result = MyAchievements.objects.filter(exercise=plan_exercise, date=now).order_by('which_series')
        ctx['result'] = result
        return render(request, 'my_results.html', ctx)

    def post(self, request, plan_id, exercise_id):

        plan_exercise = get_object_or_404(PlanExercises, id=plan_id)
        training_plan = plan_exercise.training_plan
        form = AddResultForm(request.POST)
        form.fields['which_series'].choices = [(str(i), str(i)) for i in range(1, int(plan_exercise.series) + 1)]

        if form.is_valid():
            data = form.cleaned_data
            pupil = plan_exercise.training_plan.the_pupil
            exercise = plan_exercise
            which_series = data.get('which_series')
            reps = data.get('reps')
            result = data.get('weight')
            date = data.get('date')
            obj, created = MyAchievements.objects.update_or_create(
                exercise=exercise, which_series=which_series, date=date,
                defaults={'pupil': pupil, 'reps': reps, 'result': result, 'training_plan': training_plan}
            )

            if not created:
                obj.reps = reps
                obj.result = result
                obj.save()

            return redirect(f'/results/{plan_id}/{exercise_id}/')

        return redirect(f'/results/{plan_id}/{exercise_id}/')


class AllResults(View):

    def get(self, request, pupil_id, plan_id):

        if not request.user.is_authenticated:
            return redirect('/')
        if not hasattr(request.user, 'thepupil'):
            return redirect('/')
        if not request.user.thepupil.id == pupil_id:
            return redirect('/')
        training_plan = get_object_or_404(TrainingPlan, id=plan_id)
        all_dates = training_plan.myachievements_set.all().distinct('date').values_list('date', flat=True)
        formatted_dates = [d.strftime('%Y-%m-%d') for d in all_dates]
        pupil = get_object_or_404(ThePupil, id=pupil_id)
        selected_date = request.GET.get('selected_date')
        context = {'training_plan': training_plan,
                   'formatted_dates': formatted_dates,
                   'pupil': pupil}
        if selected_date:
            all_results = training_plan.myachievements_set.filter(date=selected_date).order_by('date')
            training_day = training_plan.myachievements_set.filter(date=selected_date).first()
            exercises = training_plan.myachievements_set.filter(date=selected_date).distinct('exercise')
            context['all_results'] = all_results
            context['selected_date'] = selected_date
            context['training_day'] = training_day
            context['exercises'] = exercises
        return render(request, 'all_results.html', context)

