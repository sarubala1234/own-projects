from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegistrationForm, LoginForm, UserForm, UserProfileForm, CourseForm, LessonForm, QuizForm, QuestionForm, AnnouncementForm, CommentForm, MessageForm
from .models import UserProfile, Course, Lesson, Enrollment, LessonCompletion, CourseCategory, Quiz, Question, Announcement, Comment, Message
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from django.db import models

# Helper to get categories with courses
def get_categories_with_courses():
    categories = CourseCategory.objects.all().prefetch_related('course_set')
    for cat in categories:
        cat.courses = cat.course_set.all()
    return categories

# Home page
def home(request):
    context = {
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    }
    return render(request, 'lms_new/home.html', context)

# Course list page
def course_list(request):
    courses = Course.objects.filter(is_approved=True)
    category_id = request.GET.get('category')
    current_category_id = int(category_id) if category_id else None
    context = {
        'courses': courses,
        'categories': get_categories_with_courses(),
        'current_category_id': current_category_id,
        'current_course_id': None,
    }
    return render(request, 'lms_new/course_list.html', context)

# Course detail page
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    enrolled = False
    progress = 0
    completed_lesson_ids = []
    comments = Comment.objects.filter(course=course, lesson__isnull=True).order_by('-created_at')
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        if enrollment:
            enrolled = True
            progress = enrollment.progress
            completed_lesson_ids = list(
                LessonCompletion.objects.filter(
                    student=request.user, 
                    lesson__course=course
                ).values_list('lesson_id', flat=True)
            )
        if request.method == 'POST' and not enrolled:
            Enrollment.objects.create(student=request.user, course=course)
            return redirect('course_detail', course_id=course.id)
        # Handle comment form
        if request.method == 'POST' and enrolled:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.course = course
                comment.save()
                return redirect('course_detail', course_id=course.id)
        else:
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        'course': course,
        'lessons': lessons,
        'enrolled': enrolled,
        'progress': progress,
        'completed_lesson_ids': completed_lesson_ids,
        'categories': get_categories_with_courses(),
        'current_category_id': course.category.id if course.category else None,
        'current_course_id': course.id,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'lms_new/course_detail.html', context)

# Registration page
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    }
    return render(request, 'lms_new/register.html', context)

# Login page
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on role
                try:
                    role = user.userprofile.role
                    if role == 'student':
                        return redirect('student_dashboard')
                    elif role == 'instructor':
                        return redirect('instructor_dashboard')
                    else:
                        return redirect('home')
                except UserProfile.DoesNotExist:
                    return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    context = {
        'form': form,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    }
    return render(request, 'lms_new/login.html', context)

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')

# Dashboard redirect based on user role
@login_required
def dashboard_redirect(request):
    try:
        role = request.user.userprofile.role
        if role == 'student':
            return redirect('student_dashboard')
        elif role == 'instructor':
            return redirect('instructor_dashboard')
        else:
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')

# Student dashboard
@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    course_ids = enrollments.values_list('course_id', flat=True)
    announcements = Announcement.objects.filter(course_id__in=course_ids).order_by('-created_at')[:10]
    # Analytics: progress per course
    progress_data = []
    for enrollment in enrollments:
        lessons_count = enrollment.course.lessons.count()
        completed = LessonCompletion.objects.filter(student=request.user, lesson__course=enrollment.course).count()
        progress_data.append({
            'course': enrollment.course,
            'progress': enrollment.progress,
            'completed': completed,
            'total': lessons_count,
        })
    context = {
        'enrollments': enrollments,
        'announcements': announcements,
        'progress_data': progress_data,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    }
    return render(request, 'lms_new/student_dashboard.html', context)

# Instructor dashboard
@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    course_ids = courses.values_list('id', flat=True)
    announcements = Announcement.objects.filter(course_id__in=course_ids).order_by('-created_at')[:10]
    # Analytics: enrollment and quiz stats
    analytics = []
    for course in courses:
        enroll_count = Enrollment.objects.filter(course=course).count()
        avg_progress = Enrollment.objects.filter(course=course).aggregate(models.Avg('progress'))['progress__avg'] or 0
        quiz_count = Quiz.objects.filter(lesson__course=course).count()
        analytics.append({
            'course': course,
            'enroll_count': enroll_count,
            'avg_progress': round(avg_progress, 1),
            'quiz_count': quiz_count,
        })
    context = {
        'courses': courses,
        'announcements': announcements,
        'analytics': analytics,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    }
    return render(request, 'lms_new/instructor_dashboard.html', context)

# Lesson viewing
@login_required
def lesson_view(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        return redirect('course_detail', course_id=course.id)
    is_completed = LessonCompletion.objects.filter(student=request.user, lesson=lesson).exists()
    comments = Comment.objects.filter(lesson=lesson).order_by('-created_at')
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.lesson = lesson
            comment.save()
            return redirect('lesson_view', course_id=course.id, lesson_id=lesson.id)
    else:
        comment_form = CommentForm()
    context = {
        'course': course,
        'lesson': lesson,
        'is_completed': is_completed,
        'categories': get_categories_with_courses(),
        'current_category_id': course.category.id if course.category else None,
        'current_course_id': course.id,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'lms_new/lesson_view.html', context)

# Mark lesson as complete
@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled in the course
    enrollment = Enrollment.objects.filter(student=request.user, course=lesson.course).first()
    if not enrollment:
        return redirect('course_detail', course_id=lesson.course.id)
    
    # Mark lesson as complete
    LessonCompletion.objects.get_or_create(student=request.user, lesson=lesson)
    
    # Update progress
    total_lessons = lesson.course.lessons.count()
    completed_lessons = LessonCompletion.objects.filter(student=request.user, lesson__course=lesson.course).count()
    progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    enrollment.progress = progress
    enrollment.save()
    
    return redirect('lesson_view', course_id=lesson.course.id, lesson_id=lesson.id)

@login_required
def profile_view(request):
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'lms_new/profile_view.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'view_only': True,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_view')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'lms_new/profile_view.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'view_only': False,
        'categories': get_categories_with_courses(),
        'current_category_id': None,
        'current_course_id': None,
    })

def is_instructor(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'instructor'

@login_required
def instructor_course_list(request):
    if not is_instructor(request.user):
        return redirect('home')
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'lms_new/instructor_course_list.html', {'courses': courses})

@login_required
def course_create(request):
    if not is_instructor(request.user):
        return redirect('home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('instructor_course_list')
    else:
        form = CourseForm()
    return render(request, 'lms_new/course_form.html', {'form': form, 'create': True})

@login_required
def course_edit(request, course_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('instructor_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'lms_new/course_form.html', {'form': form, 'create': False})

@login_required
def course_delete(request, course_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('instructor_course_list')
    return render(request, 'lms_new/course_confirm_delete.html', {'course': course})

# LESSON MANAGEMENT
@login_required
def lesson_list(request, course_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'lms_new/lesson_list.html', {'course': course, 'lessons': lessons})

@login_required
def lesson_create(request, course_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Lesson created successfully.')
            return redirect('lesson_list', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'lms_new/lesson_form.html', {'form': form, 'course': course, 'create': True})

@login_required
def lesson_edit(request, course_id, lesson_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('lesson_list', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'lms_new/lesson_form.html', {'form': form, 'course': course, 'create': False})

@login_required
def lesson_delete(request, course_id, lesson_id):
    if not is_instructor(request.user):
        return redirect('home')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('lesson_list', course_id=course.id)
    return render(request, 'lms_new/lesson_confirm_delete.html', {'lesson': lesson, 'course': course})

# QUIZ MANAGEMENT
@login_required
def quiz_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quizzes = lesson.quizzes.all()
    return render(request, 'lms_new/quiz_list.html', {'lesson': lesson, 'quizzes': quizzes})

@login_required
def quiz_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            messages.success(request, 'Quiz created successfully.')
            return redirect('quiz_list', lesson_id=lesson.id)
    else:
        form = QuizForm()
    return render(request, 'lms_new/quiz_form.html', {'form': form, 'lesson': lesson, 'create': True})

@login_required
def quiz_edit(request, lesson_id, quiz_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully.')
            return redirect('quiz_list', lesson_id=lesson.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'lms_new/quiz_form.html', {'form': form, 'lesson': lesson, 'create': False})

@login_required
def quiz_delete(request, lesson_id, quiz_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        return redirect('quiz_list', lesson_id=lesson.id)
    return render(request, 'lms_new/quiz_confirm_delete.html', {'quiz': quiz, 'lesson': lesson})

# QUESTION MANAGEMENT
@login_required
def question_list(request, lesson_id, quiz_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    questions = quiz.questions.all()
    return render(request, 'lms_new/question_list.html', {'quiz': quiz, 'lesson': lesson, 'questions': questions})

@login_required
def question_create(request, lesson_id, quiz_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question created successfully.')
            return redirect('question_list', lesson_id=lesson.id, quiz_id=quiz.id)
    else:
        form = QuestionForm()
    return render(request, 'lms_new/question_form.html', {'form': form, 'quiz': quiz, 'lesson': lesson, 'create': True})

@login_required
def question_edit(request, lesson_id, quiz_id, question_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully.')
            return redirect('question_list', lesson_id=lesson.id, quiz_id=quiz.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'lms_new/question_form.html', {'form': form, 'quiz': quiz, 'lesson': lesson, 'create': False})

@login_required
def question_delete(request, lesson_id, quiz_id, question_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=lesson)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('question_list', lesson_id=lesson.id, quiz_id=quiz.id)
    return render(request, 'lms_new/question_confirm_delete.html', {'question': question, 'quiz': quiz, 'lesson': lesson})

# STUDENT QUIZ TAKING
@login_required
def take_quiz(request, lesson_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson_id=lesson_id)
    questions = quiz.questions.all()
    if request.method == 'POST':
        score = 0
        total = questions.count()
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected == question.correct_option:
                score += 1
        percent = int((score / total) * 100) if total > 0 else 0
        return render(request, 'lms_new/quiz_result.html', {'quiz': quiz, 'score': score, 'total': total, 'percent': percent})
    return render(request, 'lms_new/take_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def announcement_list(request):
    if not is_instructor(request.user):
        return redirect('home')
    announcements = Announcement.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'lms_new/announcement_list.html', {'announcements': announcements})

@login_required
def announcement_create(request):
    if not is_instructor(request.user):
        return redirect('home')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'lms_new/announcement_form.html', {'form': form, 'create': True})

@login_required
def announcement_edit(request, announcement_id):
    if not is_instructor(request.user):
        return redirect('home')
    announcement = get_object_or_404(Announcement, id=announcement_id, author=request.user)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'lms_new/announcement_form.html', {'form': form, 'create': False})

@login_required
def announcement_delete(request, announcement_id):
    if not is_instructor(request.user):
        return redirect('home')
    announcement = get_object_or_404(Announcement, id=announcement_id, author=request.user)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
        return redirect('announcement_list')
    return render(request, 'lms_new/announcement_confirm_delete.html', {'announcement': announcement})

@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Check if the user completed the course
    total_lessons = course.lessons.count()
    completed_lessons = LessonCompletion.objects.filter(student=request.user, lesson__course=course).count()
    if total_lessons == 0 or completed_lessons < total_lessons:
        return HttpResponse('You must complete all lessons to download the certificate.', status=403)
    # Generate PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont('Helvetica-Bold', 24)
    p.drawCentredString(300, 700, 'Certificate of Completion')
    p.setFont('Helvetica', 16)
    p.drawCentredString(300, 650, f'Awarded to: {request.user.get_full_name() or request.user.username}')
    p.drawCentredString(300, 600, f'For successfully completing the course:')
    p.setFont('Helvetica-Bold', 18)
    p.drawCentredString(300, 570, course.title)
    p.setFont('Helvetica', 14)
    from datetime import date
    p.drawCentredString(300, 520, f'Date: {date.today().strftime("%B %d, %Y")}')
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'certificate_{course.title}.pdf')

@user_passes_test(lambda u: u.is_superuser)
def admin_analytics(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_lessons = Lesson.objects.count()
    # Most popular courses by enrollment
    popular_courses = Course.objects.annotate(enroll_count=models.Count('enrollments')).order_by('-enroll_count')[:5]
    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'popular_courses': popular_courses,
    }
    return render(request, 'lms_new/admin_analytics.html', context)

@login_required
def inbox(request):
    messages_in = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'lms_new/inbox.html', {'messages_in': messages_in})

@login_required
def sent_messages(request):
    messages_out = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'lms_new/sent_messages.html', {'messages_out': messages_out})

@login_required
def compose_message(request):
    to_id = request.GET.get('to')
    initial = {}
    if to_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            initial['recipient'] = User.objects.get(id=to_id)
        except User.DoesNotExist:
            pass
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            return redirect('sent_messages')
    else:
        form = MessageForm(initial=initial)
        form.fields['recipient'].queryset = User.objects.exclude(id=request.user.id)
    return render(request, 'lms_new/compose_message.html', {'form': form})

@login_required
def read_message(request, message_id):
    msg = Message.objects.get(id=message_id, recipient=request.user)
    msg.is_read = True
    msg.save()
    return render(request, 'lms_new/read_message.html', {'msg': msg})
