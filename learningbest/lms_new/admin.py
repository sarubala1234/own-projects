from django.contrib import admin
from .models import UserProfile, CourseCategory, Course, Lesson, Enrollment, Quiz, Question, Certificate, LessonCompletion

admin.site.register(UserProfile)
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Certificate)
admin.site.register(LessonCompletion)
