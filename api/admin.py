from django.contrib import admin

from .models import (
    Class,
    ClassTeaching,
    PlacementCompany,
    Subject,
    ExamResult,
    Exam,
    PlacementProfile,
    PlacementApplication,
    Teacher
)

admin.site.register(Class)
admin.site.register(ClassTeaching)
admin.site.register(Subject)
admin.site.register(ExamResult)
admin.site.register(Exam)
admin.site.register(PlacementProfile)
admin.site.register(PlacementCompany)
admin.site.register(PlacementApplication)
admin.site.register(Teacher)
