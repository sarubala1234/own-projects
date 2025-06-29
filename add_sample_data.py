#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningbest.settings')
django.setup()

from django.contrib.auth.models import User
from lms_new.models import UserProfile, CourseCategory, Course, Lesson

def create_sample_data():
    print("Creating sample data...")
    
    # Create categories
    web_dev = CourseCategory.objects.get_or_create(
        name="Web Development",
        description="Learn HTML, CSS, JavaScript, and modern web frameworks"
    )[0]
    
    data_science = CourseCategory.objects.get_or_create(
        name="Data Science", 
        description="Master Python, statistics, and machine learning"
    )[0]
    
    programming = CourseCategory.objects.get_or_create(
        name="Programming Languages",
        description="Learn various programming languages from beginner to advanced"
    )[0]
    
    # Create instructor
    instructor, created = User.objects.get_or_create(
        username='instructor1',
        defaults={
            'email': 'instructor@example.com',
            'first_name': 'John',
            'last_name': 'Instructor'
        }
    )
    if created:
        instructor.set_password('password123')
        instructor.save()
        UserProfile.objects.create(user=instructor, role='instructor')
        print(f"Created instructor: {instructor.username}")
    
    # Create student
    student, created = User.objects.get_or_create(
        username='student1',
        defaults={
            'email': 'student@example.com',
            'first_name': 'Jane',
            'last_name': 'Student'
        }
    )
    if created:
        student.set_password('password123')
        student.save()
        UserProfile.objects.create(user=student, role='student')
        print(f"Created student: {student.username}")
    
    # Create courses
    python_course, created = Course.objects.get_or_create(
        title="Python for Beginners",
        defaults={
            'description': "Start your programming journey with Python. Learn variables, loops, functions, and object-oriented programming.",
            'category': programming,
            'instructor': instructor,
            'is_approved': True
        }
    )
    if created:
        print(f"Created course: {python_course.title}")
    
    web_course, created = Course.objects.get_or_create(
        title="Full Stack Web Development",
        defaults={
            'description': "Learn HTML, CSS, JavaScript, and Django to build complete web applications.",
            'category': web_dev,
            'instructor': instructor,
            'is_approved': True
        }
    )
    if created:
        print(f"Created course: {web_course.title}")
    
    ml_course, created = Course.objects.get_or_create(
        title="Machine Learning Basics",
        defaults={
            'description': "Get started with data science and machine learning using Python and popular libraries.",
            'category': data_science,
            'instructor': instructor,
            'is_approved': True
        }
    )
    if created:
        print(f"Created course: {ml_course.title}")
    
    # Create lessons for Python course
    lessons_data = [
        (python_course, "Introduction to Python", "Learn what Python is and why it's popular.", 1),
        (python_course, "Variables and Data Types", "Understanding variables, strings, numbers, and booleans.", 2),
        (python_course, "Control Flow", "Learn about if statements, loops, and conditional logic.", 3),
        (web_course, "HTML Basics", "Learn the fundamentals of HTML markup.", 1),
        (web_course, "CSS Styling", "Make your websites beautiful with CSS.", 2),
        (web_course, "JavaScript Fundamentals", "Add interactivity to your websites.", 3),
        (ml_course, "Introduction to Data Science", "Understanding the data science workflow.", 1),
        (ml_course, "Python for Data Analysis", "Using pandas and numpy for data manipulation.", 2),
        (ml_course, "Machine Learning Algorithms", "Understanding supervised and unsupervised learning.", 3),
    ]
    
    for course, title, content, order in lessons_data:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=title,
            defaults={
                'content': content,
                'order': order
            }
        )
        if created:
            print(f"Created lesson: {lesson.title} for {course.title}")
    
    print("\nSample data created successfully!")
    print("\nTest accounts:")
    print("Instructor: username=instructor1, password=password123")
    print("Student: username=student1, password=password123")
    print("\nAccess admin at: http://127.0.0.1:8000/admin/")
    print("Access website at: http://127.0.0.1:8000/")

if __name__ == '__main__':
    create_sample_data() 