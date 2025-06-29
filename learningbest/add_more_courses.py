#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningbest.settings')
django.setup()

from django.contrib.auth.models import User
from lms_new.models import UserProfile, CourseCategory, Course, Lesson

def add_more_courses():
    print("Adding more IT courses...")
    
    # Get existing categories or create new ones
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
    
    cybersecurity = CourseCategory.objects.get_or_create(
        name="Cybersecurity",
        description="Learn about network security, ethical hacking, and digital forensics"
    )[0]
    
    cloud_computing = CourseCategory.objects.get_or_create(
        name="Cloud Computing",
        description="Master AWS, Azure, Google Cloud, and cloud architecture"
    )[0]
    
    mobile_dev = CourseCategory.objects.get_or_create(
        name="Mobile Development",
        description="Build iOS and Android applications"
    )[0]
    
    database = CourseCategory.objects.get_or_create(
        name="Database Management",
        description="Learn SQL, NoSQL, and database design"
    )[0]
    
    # Get existing instructor or create new one
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
    
    # Create additional courses
    courses_data = [
        # Programming Languages
        {
            'title': "Java Programming",
            'description': "Learn Java from basics to advanced concepts including OOP, collections, and multithreading.",
            'category': programming,
            'instructor': instructor,
            'lessons': [
                ("Introduction to Java", "Understanding Java basics, JVM, and development environment setup.", 1),
                ("Object-Oriented Programming", "Classes, objects, inheritance, polymorphism, and encapsulation.", 2),
                ("Java Collections Framework", "Working with lists, sets, maps, and other data structures.", 3),
                ("Exception Handling", "Try-catch blocks, custom exceptions, and best practices.", 4),
                ("Multithreading", "Concurrent programming with threads and synchronization.", 5),
            ]
        },
        {
            'title': "C++ Programming",
            'description': "Master C++ programming with memory management, templates, and STL.",
            'category': programming,
            'instructor': instructor,
            'lessons': [
                ("C++ Basics", "Variables, data types, control structures, and functions.", 1),
                ("Pointers and References", "Memory management, pointers, and reference variables.", 2),
                ("Classes and Objects", "Object-oriented programming in C++.", 3),
                ("Templates", "Generic programming with function and class templates.", 4),
                ("STL (Standard Template Library)", "Containers, algorithms, and iterators.", 5),
            ]
        },
        
        # Web Development
        {
            'title': "React.js Development",
            'description': "Build modern web applications with React.js, hooks, and state management.",
            'category': web_dev,
            'instructor': instructor,
            'lessons': [
                ("React Fundamentals", "Components, JSX, and React basics.", 1),
                ("State and Props", "Managing component state and passing data.", 2),
                ("Hooks", "useState, useEffect, and custom hooks.", 3),
                ("Routing", "React Router for navigation.", 4),
                ("State Management", "Context API and Redux basics.", 5),
            ]
        },
        {
            'title': "Node.js Backend Development",
            'description': "Build scalable backend applications with Node.js and Express.",
            'category': web_dev,
            'instructor': instructor,
            'lessons': [
                ("Node.js Basics", "Event-driven programming and asynchronous operations.", 1),
                ("Express.js Framework", "Building RESTful APIs with Express.", 2),
                ("Database Integration", "Connecting to MongoDB and MySQL.", 3),
                ("Authentication", "JWT tokens and user authentication.", 4),
                ("Deployment", "Deploying Node.js applications to production.", 5),
            ]
        },
        
        # Cybersecurity
        {
            'title': "Ethical Hacking",
            'description': "Learn penetration testing, vulnerability assessment, and security tools.",
            'category': cybersecurity,
            'instructor': instructor,
            'lessons': [
                ("Security Fundamentals", "Basic security concepts and terminology.", 1),
                ("Reconnaissance", "Information gathering and footprinting techniques.", 2),
                ("Scanning and Enumeration", "Network scanning and service enumeration.", 3),
                ("Exploitation", "Common attack vectors and exploitation techniques.", 4),
                ("Post-Exploitation", "Maintaining access and covering tracks.", 5),
            ]
        },
        {
            'title': "Network Security",
            'description': "Secure network infrastructure and protect against cyber threats.",
            'category': cybersecurity,
            'instructor': instructor,
            'lessons': [
                ("Network Protocols", "Understanding TCP/IP and common protocols.", 1),
                ("Firewalls and IDS", "Network security devices and monitoring.", 2),
                ("VPN and Encryption", "Secure communication and data protection.", 3),
                ("Wireless Security", "Securing wireless networks and protocols.", 4),
                ("Incident Response", "Handling security incidents and breaches.", 5),
            ]
        },
        
        # Cloud Computing
        {
            'title': "AWS Cloud Practitioner",
            'description': "Get certified in AWS fundamentals and cloud services.",
            'category': cloud_computing,
            'instructor': instructor,
            'lessons': [
                ("Cloud Computing Basics", "Understanding cloud models and AWS global infrastructure.", 1),
                ("AWS Core Services", "EC2, S3, VPC, and other essential services.", 2),
                ("Security and Compliance", "AWS security best practices and compliance.", 3),
                ("Pricing and Billing", "Understanding AWS pricing models and cost optimization.", 4),
                ("Architecture Best Practices", "Well-architected framework and design principles.", 5),
            ]
        },
        {
            'title': "Docker and Kubernetes",
            'description': "Master containerization and orchestration with Docker and Kubernetes.",
            'category': cloud_computing,
            'instructor': instructor,
            'lessons': [
                ("Container Basics", "Understanding containers and Docker fundamentals.", 1),
                ("Docker Images and Containers", "Creating and managing Docker images.", 2),
                ("Docker Compose", "Multi-container applications with Docker Compose.", 3),
                ("Kubernetes Basics", "Introduction to Kubernetes and its components.", 4),
                ("Kubernetes Deployment", "Deploying and managing applications on Kubernetes.", 5),
            ]
        },
        
        # Mobile Development
        {
            'title': "React Native Development",
            'description': "Build cross-platform mobile apps with React Native.",
            'category': mobile_dev,
            'instructor': instructor,
            'lessons': [
                ("React Native Setup", "Development environment and project setup.", 1),
                ("Components and Navigation", "Building UI components and navigation.", 2),
                ("State Management", "Managing app state with Redux and Context.", 3),
                ("Native Modules", "Integrating native functionality and APIs.", 4),
                ("Testing and Deployment", "Testing strategies and app store deployment.", 5),
            ]
        },
        {
            'title': "Flutter Development",
            'description': "Create beautiful mobile apps with Flutter and Dart.",
            'category': mobile_dev,
            'instructor': instructor,
            'lessons': [
                ("Flutter Basics", "Introduction to Flutter and Dart programming.", 1),
                ("Widgets and UI", "Building user interfaces with Flutter widgets.", 2),
                ("State Management", "Managing state with Provider and Bloc.", 3),
                ("Navigation and Routing", "App navigation and deep linking.", 4),
                ("Testing and Publishing", "Testing Flutter apps and publishing to stores.", 5),
            ]
        },
        
        # Database Management
        {
            'title': "SQL Database Design",
            'description': "Learn database design, SQL queries, and optimization.",
            'category': database,
            'instructor': instructor,
            'lessons': [
                ("Database Fundamentals", "Understanding databases and data modeling.", 1),
                ("SQL Basics", "SELECT, INSERT, UPDATE, DELETE operations.", 2),
                ("Advanced SQL", "JOINs, subqueries, and complex queries.", 3),
                ("Database Design", "Normalization and ER diagrams.", 4),
                ("Performance Optimization", "Indexing, query optimization, and tuning.", 5),
            ]
        },
        {
            'title': "MongoDB NoSQL Database",
            'description': "Master document-based database with MongoDB.",
            'category': database,
            'instructor': instructor,
            'lessons': [
                ("NoSQL Concepts", "Understanding document databases and MongoDB.", 1),
                ("MongoDB CRUD", "Create, read, update, and delete operations.", 2),
                ("Aggregation Framework", "Advanced querying and data aggregation.", 3),
                ("Indexing and Performance", "Optimizing MongoDB performance.", 4),
                ("MongoDB Atlas", "Cloud database management and deployment.", 5),
            ]
        },
        
        # Data Science
        {
            'title': "Data Analysis with Pandas",
            'description': "Master data manipulation and analysis with Python Pandas.",
            'category': data_science,
            'instructor': instructor,
            'lessons': [
                ("Pandas Basics", "Introduction to DataFrames and Series.", 1),
                ("Data Cleaning", "Handling missing data and data preprocessing.", 2),
                ("Data Manipulation", "Filtering, grouping, and transforming data.", 3),
                ("Data Visualization", "Creating charts and plots with Pandas.", 4),
                ("Advanced Analysis", "Statistical analysis and data insights.", 5),
            ]
        },
        {
            'title': "Deep Learning with TensorFlow",
            'description': "Build neural networks and deep learning models.",
            'category': data_science,
            'instructor': instructor,
            'lessons': [
                ("Neural Network Basics", "Understanding artificial neural networks.", 1),
                ("TensorFlow Fundamentals", "Building models with TensorFlow/Keras.", 2),
                ("Convolutional Neural Networks", "Image classification and computer vision.", 3),
                ("Recurrent Neural Networks", "Sequence modeling and time series.", 4),
                ("Model Deployment", "Deploying deep learning models to production.", 5),
            ]
        },
    ]
    
    # Create courses and lessons
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'description': course_data['description'],
                'category': course_data['category'],
                'instructor': course_data['instructor'],
                'is_approved': True
            }
        )
        
        if created:
            print(f"Created course: {course.title}")
            
            # Create lessons for this course
            for lesson_title, lesson_content, order in course_data['lessons']:
                lesson, lesson_created = Lesson.objects.get_or_create(
                    course=course,
                    title=lesson_title,
                    defaults={
                        'content': lesson_content,
                        'order': order
                    }
                )
                if lesson_created:
                    print(f"  - Created lesson: {lesson.title}")
    
    print(f"\nSuccessfully added {len(courses_data)} new courses!")
    print("Total courses now available: ", Course.objects.count())
    print("Total lessons now available: ", Lesson.objects.count())

if __name__ == '__main__':
    add_more_courses() 