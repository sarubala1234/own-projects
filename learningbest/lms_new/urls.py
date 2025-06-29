from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('mark-lesson-complete/<int:lesson_id>/', views.mark_lesson_complete, name='mark_lesson_complete'),

    # Profile management
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='lms_new/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='lms_new/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='lms_new/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='lms_new/password_reset_complete.html'), name='password_reset_complete'),

    # Password change URLs (for logged-in users)
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='lms_new/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='lms_new/password_change_done.html'), name='password_change_done'),

    # Quiz management
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/create/', views.quiz_create, name='quiz_create'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),

    # Question management
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/questions/', views.question_list, name='question_list'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/questions/create/', views.question_create, name='question_create'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    # Student quiz taking
    path('courses/<int:course_id>/lesson/<int:lesson_id>/quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),

    # Announcement management
    path('instructor/announcements/', views.announcement_list, name='announcement_list'),
    path('instructor/announcements/create/', views.announcement_create, name='announcement_create'),
    path('instructor/announcements/<int:announcement_id>/edit/', views.announcement_edit, name='announcement_edit'),
    path('instructor/announcements/<int:announcement_id>/delete/', views.announcement_delete, name='announcement_delete'),

    # Certificate download
    path('courses/<int:course_id>/certificate/', views.download_certificate, name='download_certificate'),

    # Admin analytics
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),

    # Messaging URLs
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/', views.compose_message, name='compose_message'),
    path('messages/read/<int:message_id>/', views.read_message, name='read_message'),
] 