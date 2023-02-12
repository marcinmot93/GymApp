"""TrainingApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MoveOn import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('create_account/', views.CreateUserView.as_view()),
    path('creating_details/<int:user_id>/', views.PupilDetailsView.as_view()),
    path('main/trainer/<int:trainer_id>/', views.TrainerMainView.as_view()),
    path('main/<int:pupil_id>/', views.ThePupilMainView.as_view()),
    path('create_plan/<int:trainer_id>/<int:pupil_id>/', views.CreatePlanView.as_view()),
    path('exercises/<int:trainer_id>/', views.ExercisesView.as_view()),
    path('exercise_plan/<int:trainer_id>/<int:pupil_id>/<int:plan_id>/', views.CreateExercisePlan.as_view()),
    path('details/trainer/<int:trainer_id>/<int:pupil_id>/', views.TrainerPupilView.as_view()),
    path('delete_from_plan/<int:pupil_id>/<int:plan_exercise_id>/', views.DeleteFromExercisePlan.as_view()),
    path('exercise/<int:ex_id>/delete/', views.DeleteExercise.as_view())

]
