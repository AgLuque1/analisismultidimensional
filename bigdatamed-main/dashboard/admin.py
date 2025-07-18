from dashboard.models import Profile,Category,Experiment,DataBaseSystem, ProblemSelection
from django.contrib import admin

# Register your models here.
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(ProblemSelection)
admin.site.register(Experiment)
admin.site.register(DataBaseSystem)

