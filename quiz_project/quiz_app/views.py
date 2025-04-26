from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm
from .models import Quiz, Question, QuizResult, UserProfile, ContactMessage
import json
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Avg, Sum, Count
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            # If form is invalid, render the page with form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check for staff
            if user.is_staff:
                messages.success(request, 'Staff logged in successfully')
                return redirect('staff_dashboard')
            else:
                messages.success(request, 'User logged in successfully')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'login.html')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user profile
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    
    # Get all available quizzes, filtered by search if present
    available_quizzes = Quiz.objects.all() # Start with all quizzes
    if search_query:
        available_quizzes = available_quizzes.filter(
            Q(title__icontains=search_query) | Q(created_by__username__icontains=search_query)
        ).distinct()
    
    # Get recent quiz results for the user
    recent_results = QuizResult.objects.filter(user=request.user).order_by('-completed_at')[:5]
    
    # Get attempt counts for each quiz
    attempt_counts = {}
    for quiz in available_quizzes:
        user_attempts = QuizResult.objects.filter(user=request.user, quiz=quiz).count()
        attempt_counts[quiz.id] = user_attempts
    
    # Format the results for the template
    recent_quizzes = []
    for result in recent_results:
        recent_quizzes.append({
            'title': result.quiz.title,
            'date': result.completed_at.strftime('%B %d, %Y'),
            'score': result.score
        })
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'recent_quizzes': recent_quizzes,
        'total_quizzes': user_profile.total_quizzes,
        'average_score': user_profile.average_score,
        'completed_quizzes': user_profile.completed_quizzes,
        'available_quizzes': available_quizzes,
        'attempt_counts': attempt_counts,
        'search_query': search_query
    }
    return render(request, 'dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'admindashboard.html', {'user': request.user})

@login_required
def profile(request):
    # Get user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get quiz results for the user
    quiz_results = QuizResult.objects.filter(user=request.user)
    
    # Calculate statistics
    total_quizzes = quiz_results.count()
    if total_quizzes > 0:
        average_score = quiz_results.aggregate(avg_score=models.Avg('score'))['avg_score']
    else:
        average_score = 0
    
    # Update user profile
    user_profile.total_quizzes = total_quizzes
    user_profile.average_score = average_score
    user_profile.completed_quizzes = total_quizzes
    user_profile.save()
    
    context = {
        'user': request.user,
        'user_profile': user_profile
    }
    return render(request, 'profile.html', context)

def ques(request):
    questions = [
        "What is Flask?",
        "How do you set up a Flask route?",
        "What is Jinja templating?",
        "How do you serve static files in Flask?"
    ]
    return render(request, 'ques.html', {'questions': questions})

def pyquiz(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        messages.warning(request, 'Staff members cannot attempt quizzes')
        return redirect('staff_dashboard')
    
    # Get Python quiz questions
    questions = Question.objects.filter(quiz__title='Python Quiz')
    
    if not questions.exists():
        # Create default Python quiz questions if none exist
        python_quiz = Quiz.objects.create(title='Python Quiz', created_by=request.user)
        
        default_questions = [
            {
                'question_text': 'What is Python?',
                'option_a': 'A snake species',
                'option_b': 'A programming language',
                'option_c': 'A type of coffee',
                'option_d': 'A car model',
                'correct_answer': 'B'
            },
            {
                'question_text': 'Which of the following is not a Python data type?',
                'option_a': 'List',
                'option_b': 'Dictionary',
                'option_c': 'Table',
                'option_d': 'Tuple',
                'correct_answer': 'C'
            },
            {
                'question_text': 'What is the output of print(2 ** 3)?',
                'option_a': '6',
                'option_b': '8',
                'option_c': '5',
                'option_d': 'Error',
                'correct_answer': 'B'
            },
            {
                'question_text': 'Which keyword is used to define a function in Python?',
                'option_a': 'func',
                'option_b': 'def',
                'option_c': 'function',
                'option_d': 'define',
                'correct_answer': 'B'
            },
            {
                'question_text': 'What is the correct way to create a list in Python?',
                'option_a': 'list = (1, 2, 3)',
                'option_b': 'list = [1, 2, 3]',
                'option_c': 'list = {1, 2, 3}',
                'option_d': 'list = <1, 2, 3>',
                'correct_answer': 'B'
            }
        ]
        
        for q in default_questions:
            Question.objects.create(
                quiz=python_quiz,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer']
            )
        
        questions = Question.objects.filter(quiz=python_quiz)
    
    return render(request, 'pyquiz.html', {'questions': questions})

def cppquiz(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        messages.warning(request, 'Staff members cannot attempt quizzes')
        return redirect('staff_dashboard')
    
    # Get C++ quiz questions
    questions = Question.objects.filter(quiz__title='C++ Quiz')
    
    if not questions.exists():
        # Create default C++ quiz questions if none exist
        cpp_quiz = Quiz.objects.create(title='C++ Quiz', created_by=request.user)
        
        default_questions = [
            {
                'question_text': 'What is C++?',
                'option_a': 'A high-level programming language',
                'option_b': 'A low-level programming language',
                'option_c': 'A hardware description language',
                'option_d': 'A markup language',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is used to declare a class in C++?',
                'option_a': 'class MyClass {}',
                'option_b': 'MyClass class {}',
                'option_c': 'class = MyClass {}',
                'option_d': 'MyClass {}',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is a C++ standard library?',
                'option_a': 'iostream',
                'option_b': 'java.io',
                'option_c': 'stdlib.h',
                'option_d': 'conio.h',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which operator is used to allocate memory dynamically in C++?',
                'option_a': 'new',
                'option_b': 'malloc',
                'option_c': 'alloc',
                'option_d': 'malloc_new',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is NOT a valid C++ access modifier?',
                'option_a': 'public',
                'option_b': 'private',
                'option_c': 'protected',
                'option_d': 'secure',
                'correct_answer': 'D'
            }
        ]
        
        for q in default_questions:
            Question.objects.create(
                quiz=cpp_quiz,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer']
            )
        
        questions = Question.objects.filter(quiz=cpp_quiz)
    
    return render(request, 'cppquiz.html', {'questions': questions})

@login_required
def submit_quiz(request, quiz_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        messages.warning(request, 'Staff members cannot submit quizzes')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        score = 0
        total_questions = questions.count()
        results = []
        user_answers = {}
        
        for question in questions:
            user_answer = request.POST.get(f'q{question.id}')
            # Handle unanswered questions
            if user_answer is None:
                user_answer = ''
            
            # Convert both answers to uppercase for case-insensitive comparison
            correct = user_answer.upper() == question.correct_answer.upper()
            if correct:
                score += 1
            
            # Store user's answer for this question
            user_answers[str(question.id)] = {
                'question_text': question.question_text,
                'selected_answer': user_answer.upper() if user_answer else '',  # Handle empty answers
                'correct_answer': question.correct_answer.upper(),
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d
                },
                'is_correct': correct
            }
            
            results.append({
                'question': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'correct': correct
            })
        
        percentage = (score / total_questions) * 100
        
        # Save the quiz result with answers
        quiz_result = QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=percentage,
            total_questions=total_questions,
            correct_answers=score,
            answers=user_answers
        )
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update user's total quizzes and average score
        user_results = QuizResult.objects.filter(user=request.user)
        total_quizzes = user_results.count()
        average_score = user_results.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
        
        # Update the user profile
        user_profile.total_quizzes = total_quizzes
        user_profile.average_score = average_score
        user_profile.completed_quizzes = total_quizzes
        user_profile.save()
        
        return redirect('quiz_result', attempt_id=quiz_result.id)
    
    return redirect('take_quiz', quiz_id=quiz_id)

def submit_cpp_quiz(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        messages.warning(request, 'Staff members cannot submit quizzes')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        questions = Question.objects.filter(quiz__title='C++ Quiz')
        score = 0
        total_questions = questions.count()
        results = []
        user_answers = {}
        
        for question in questions:
            user_answer = request.POST.get(f'q{question.id}')
            correct = user_answer == question.correct_answer
            if correct:
                score += 1
            
            # Store user's answer for this question
            user_answers[str(question.id)] = {
                'question_text': question.question_text,
                'selected_answer': user_answer,
                'correct_answer': question.correct_answer,
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d
                }
            }
            
            results.append({
                'question': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'correct': correct
            })
        
        percentage = (score / total_questions) * 100
        
        # Save the quiz result with answers
        QuizResult.objects.create(
            user=request.user,
            quiz=questions.first().quiz,
            score=percentage,
            total_questions=total_questions,
            correct_answers=score,
            answers=user_answers
        )
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update user's total quizzes and average score
        user_results = QuizResult.objects.filter(user=request.user)
        total_quizzes = user_results.count()
        average_score = user_results.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
        
        # Update the user profile
        user_profile.total_quizzes = total_quizzes
        user_profile.average_score = average_score
        user_profile.completed_quizzes = total_quizzes
        user_profile.save()
        
        context = {
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'results': results,
            'user': request.user
        }
        return render(request, 'results.html', context)
    
    return redirect('cppquiz')

def submit_answer(request):
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        # Process the answer (e.g., check if it is correct)
        # Redirect to next question or results page
    return redirect('ques')

def contact_us(request):
    return render(request, 'contactus.html')

def about_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('about_us')
    
    return render(request, 'about_us.html')

@login_required
def create_quiz(request):
    if request.method == "POST":
        quiz_title = request.POST.get("quiz_title")
        questions = request.POST.getlist("question[]")
        optionsA = request.POST.getlist("optionA[]")
        optionsB = request.POST.getlist("optionB[]")
        optionsC = request.POST.getlist("optionC[]")
        optionsD = request.POST.getlist("optionD[]")
        answers = request.POST.getlist("answer[]")

        quiz = Quiz.objects.create(title=quiz_title, created_by=request.user)
        
        for i in range(len(questions)):
            Question.objects.create(
                quiz=quiz,
                question_text=questions[i],
                option_a=optionsA[i],
                option_b=optionsB[i],
                option_c=optionsC[i],
                option_d=optionsD[i],
                correct_answer=answers[i]
            )
        
        messages.success(request, "Quiz Created Successfully!")
        return redirect('home')
    
    return render(request, 'create_quiz.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    # Get search query if present
    search_query = request.GET.get('search', '')
    
    # Get all quiz results with attempt counts
    quiz_results = QuizResult.objects.all().order_by('-completed_at')
    
    # Filter results based on search query
    if search_query:
        quiz_results = quiz_results.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(quiz__title__icontains=search_query)
        )
    
    quizzes = Quiz.objects.all()
    
    # Get attempt counts for each user-quiz combination
    attempt_counts = {}
    for result in quiz_results:
        key = f"{result.user.id}_{result.quiz.id}"
        if key not in attempt_counts:
            attempt_counts[key] = 1
        else:
            attempt_counts[key] += 1
    
    # Calculate average score
    if quiz_results.exists():
        average_score = quiz_results.aggregate(avg_score=models.Avg('score'))['avg_score']
    else:
        average_score = 0
    
    unread_messages = ContactMessage.objects.filter(is_read=False)
    all_messages = ContactMessage.objects.all()
    
    context = {
        'user': request.user,
        'quiz_results': quiz_results,
        'quizzes': quizzes,
        'attempt_counts': attempt_counts,
        'average_score': average_score,
        'search_query': search_query,
        'unread_messages': unread_messages,
        'all_messages': all_messages
    }
    return render(request, 'staff_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_attempt(request, attempt_id):
    result = get_object_or_404(QuizResult, id=attempt_id)
    
    # Get the user whose attempt is being deleted
    user = result.user
    
    # Delete the attempt
    result.delete()
    
    # Update user's statistics
    user_profile = UserProfile.objects.get(user=user)
    user_results = QuizResult.objects.filter(user=user)
    
    # Recalculate statistics
    total_quizzes = user_results.count()
    if total_quizzes > 0:
        average_score = user_results.aggregate(avg_score=models.Avg('score'))['avg_score']
    else:
        average_score = 0
    
    # Update user profile
    user_profile.total_quizzes = total_quizzes
    user_profile.average_score = average_score
    user_profile.completed_quizzes = total_quizzes
    user_profile.save()
    
    messages.success(request, 'Quiz attempt deleted successfully.')
    return redirect('staff_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_quiz_staff(request):
    if request.method == "POST":
        quiz_title = request.POST.get("quiz_title")
        if not quiz_title:
            messages.error(request, "Quiz title is required")
            return redirect('create_quiz_staff')
        
        # Get all question-related fields
        questions = []
        options_a = []
        options_b = []
        options_c = []
        options_d = []
        correct_answers = []
        
        # Find the maximum question number
        max_question = 0
        for key in request.POST.keys():
            if key.startswith('question_'):
                try:
                    question_num = int(key.split('_')[1])
                    max_question = max(max_question, question_num)
                except ValueError:
                    continue
        
        # Collect all question data
        for i in range(1, max_question + 1):
            question = request.POST.get(f'question_{i}')
            option_a = request.POST.get(f'option_a_{i}')
            option_b = request.POST.get(f'option_b_{i}')
            option_c = request.POST.get(f'option_c_{i}')
            option_d = request.POST.get(f'option_d_{i}')
            correct_answer = request.POST.get(f'correct_answer_{i}')
            
            if all([question, option_a, option_b, option_c, option_d, correct_answer]):
                questions.append(question)
                options_a.append(option_a)
                options_b.append(option_b)
                options_c.append(option_c)
                options_d.append(option_d)
                correct_answers.append(correct_answer)
        
        if not questions:
            messages.error(request, "At least one question is required")
            return redirect('create_quiz_staff')
        
        # Create the quiz
        quiz = Quiz.objects.create(title=quiz_title, created_by=request.user)
        
        # Create questions
        for i in range(len(questions)):
            Question.objects.create(
                quiz=quiz,
                question_text=questions[i],
                option_a=options_a[i],
                option_b=options_b[i],
                option_c=options_c[i],
                option_d=options_d[i],
                correct_answer=correct_answers[i]
            )
        
        messages.success(request, "Quiz Created Successfully!")
        return redirect('staff_dashboard')
    
    # For GET request, just render the template
    return render(request, 'create_quiz_staff.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully')
    except Quiz.DoesNotExist:
        messages.error(request, 'Quiz not found')
    return redirect('staff_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_answers(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    results = QuizResult.objects.filter(quiz=quiz).order_by('-completed_at')
    
    context = {
        'quiz': quiz,
        'results': results
    }
    return render(request, 'review_answers.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_attempt(request, attempt_id):
    result = get_object_or_404(QuizResult, id=attempt_id)
    
    context = {
        'result': result,
        'quiz': result.quiz,
        'user': result.user,
        'score': result.score,
        'total_questions': result.total_questions,
        'correct_answers': result.correct_answers,
        'completed_at': result.completed_at
    }
    return render(request, 'view_attempt.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        # Update quiz title
        quiz.title = request.POST.get('title')
        quiz.save()
        
        # Update questions
        questions = Question.objects.filter(quiz=quiz)
        for question in questions:
            question_id = str(question.id)
            question.question_text = request.POST.get(f'question_{question_id}')
            question.option_a = request.POST.get(f'option_a_{question_id}')
            question.option_b = request.POST.get(f'option_b_{question_id}')
            question.option_c = request.POST.get(f'option_c_{question_id}')
            question.option_d = request.POST.get(f'option_d_{question_id}')
            question.correct_answer = request.POST.get(f'correct_answer_{question_id}')
            question.save()
        
        messages.success(request, 'Quiz updated successfully!')
        return redirect('staff_dashboard')
    
    # GET request - display the edit form
    questions = Question.objects.filter(quiz=quiz)
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'edit_quiz.html', context)

@login_required
def take_quiz(request, quiz_id):
    if request.user.is_staff:
        messages.warning(request, 'Staff members cannot attempt quizzes')
        return redirect('staff_dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    
    if not questions.exists():
        messages.error(request, 'This quiz has no questions yet.')
        return redirect('dashboard')
    
    # Check maximum attempts (3 attempts per quiz)
    MAX_ATTEMPTS = 3
    user_attempts = QuizResult.objects.filter(user=request.user, quiz=quiz).count()
    
    if user_attempts >= MAX_ATTEMPTS:
        messages.error(request, f'You have reached the maximum number of attempts ({MAX_ATTEMPTS}) for this quiz.')
        return redirect('dashboard')
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempts_remaining': MAX_ATTEMPTS - user_attempts
    }
    return render(request, 'take_quiz.html', context)

@login_required
def quiz_result(request, attempt_id):
    result = get_object_or_404(QuizResult, id=attempt_id)
    
    # Ensure the user can only view their own results unless they're staff
    if not request.user.is_staff and result.user != request.user:
        messages.error(request, "You don't have permission to view this result.")
        return redirect('dashboard')
    
    context = {
        'result': result,
        'quiz': result.quiz,
        'user': result.user,
        'score': result.score,
        'total_questions': result.total_questions,
        'correct_answers': result.correct_answers,
        'completed_at': result.completed_at,
        'answers': result.answers
    }
    return render(request, 'quiz_result.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_default_quizzes(request):
    # Create Python Quiz if it doesn't exist
    python_quiz, created = Quiz.objects.get_or_create(
        title='Python Quiz',
        defaults={'created_by': request.user}
    )
    
    if created:
        # Add Python quiz questions
        python_questions = [
            {
                'question_text': 'What is Python?',
                'option_a': 'A snake species',
                'option_b': 'A programming language',
                'option_c': 'A type of coffee',
                'option_d': 'A car model',
                'correct_answer': 'B'
            },
            {
                'question_text': 'Which of the following is not a Python data type?',
                'option_a': 'List',
                'option_b': 'Dictionary',
                'option_c': 'Table',
                'option_d': 'Tuple',
                'correct_answer': 'C'
            },
            {
                'question_text': 'What is the output of print(2 ** 3)?',
                'option_a': '6',
                'option_b': '8',
                'option_c': '5',
                'option_d': 'Error',
                'correct_answer': 'B'
            },
            {
                'question_text': 'Which keyword is used to define a function in Python?',
                'option_a': 'func',
                'option_b': 'def',
                'option_c': 'function',
                'option_d': 'define',
                'correct_answer': 'B'
            },
            {
                'question_text': 'What is the correct way to create a list in Python?',
                'option_a': 'list = (1, 2, 3)',
                'option_b': 'list = [1, 2, 3]',
                'option_c': 'list = {1, 2, 3}',
                'option_d': 'list = <1, 2, 3>',
                'correct_answer': 'B'
            }
        ]
        
        for q in python_questions:
            Question.objects.create(
                quiz=python_quiz,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer']
            )
    
    # Create C++ Quiz if it doesn't exist
    cpp_quiz, created = Quiz.objects.get_or_create(
        title='C++ Quiz',
        defaults={'created_by': request.user}
    )
    
    if created:
        # Add C++ quiz questions
        cpp_questions = [
            {
                'question_text': 'What is C++?',
                'option_a': 'A high-level programming language',
                'option_b': 'A low-level programming language',
                'option_c': 'A hardware description language',
                'option_d': 'A markup language',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is used to declare a class in C++?',
                'option_a': 'class MyClass {}',
                'option_b': 'MyClass class {}',
                'option_c': 'class = MyClass {}',
                'option_d': 'MyClass {}',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is a C++ standard library?',
                'option_a': 'iostream',
                'option_b': 'java.io',
                'option_c': 'stdlib.h',
                'option_d': 'conio.h',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which operator is used to allocate memory dynamically in C++?',
                'option_a': 'new',
                'option_b': 'malloc',
                'option_c': 'alloc',
                'option_d': 'malloc_new',
                'correct_answer': 'A'
            },
            {
                'question_text': 'Which of the following is NOT a valid C++ access modifier?',
                'option_a': 'public',
                'option_b': 'private',
                'option_c': 'protected',
                'option_d': 'secure',
                'correct_answer': 'D'
            }
        ]
        
        for q in cpp_questions:
            Question.objects.create(
                quiz=cpp_quiz,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer']
            )
    
    messages.success(request, 'Default quizzes have been recreated successfully!')
    return redirect('staff_dashboard')

# Add the new search view function
def search_results(request):
    query = request.GET.get('q', '')
    quiz_results = []
    page_results = [] # Placeholder for page results

    if query:
        # Search for quizzes matching the title OR the creator's username
        quiz_results = Quiz.objects.filter(
            Q(title__icontains=query) | Q(created_by__username__icontains=query)
        ).distinct() # Use distinct() to avoid duplicates if a title also contains the username
        # --- Page Search Logic ---
        # (Existing page search logic remains here)
        # You would add logic here to search for static pages or other content.
        # For example, you might have a list of known static pages:
        known_pages = {
            'home': {'name': 'Home', 'url_name': 'home'},
            'about': {'name': 'About Us', 'url_name': 'about_us'},
            'contact': {'name': 'Contact Us', 'url_name': 'contact_us'},
            # Add other relevant static pages like dashboard, profile if needed
            'dashboard': {'name': 'Dashboard', 'url_name': 'dashboard'},
            'profile': {'name': 'Profile', 'url_name': 'profile'},
            'login': {'name': 'Login', 'url_name': 'login'},
            'register': {'name': 'Sign Up', 'url_name': 'register'},
        }
        for key, page_info in known_pages.items():
            if query.lower() in page_info['name'].lower():
                 # Avoid adding duplicates if already found via quiz search (less likely here)
                 # Add URL resolution using reverse()
                 try:
                     page_info['url'] = reverse(page_info['url_name'])
                     page_results.append(page_info)
                 except Exception as e:
                     # Handle cases where URL name might be wrong or needs args
                     print(f"Error reversing URL {page_info['url_name']}: {e}")
                     pass # Or log the error
        # --- End Placeholder ---


    context = {
        'query': query,
        'quiz_results': quiz_results,
        'page_results': page_results, # Pass page results to template
        'has_results': bool(quiz_results or page_results) # Check if any results exist
    }
    return render(request, 'search_results.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            # Check if username is already taken by another user
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Username is already taken'
                })
            
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email is already taken'
                })
            
            # Update user information
            request.user.username = username
            request.user.email = email
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'username': username,
                'email': email
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def mark_message_read(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    return redirect('staff_dashboard')

def quiz_categories(request):
    categories = Quiz.objects.values('category').distinct()
    return render(request, 'quiz_app/quiz_categories.html', {'categories': categories})

def statistics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_results = QuizResult.objects.filter(user=request.user)
    total_quizzes = user_results.count()
    average_score = user_results.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    return render(request, 'quiz_app/statistics.html', {
        'total_quizzes': total_quizzes,
        'average_score': average_score,
        'user_results': user_results
    })

def leaderboard(request):
    top_users = User.objects.annotate(
        total_score=Sum('quizresult__score'),
        quiz_count=Count('quizresult')
    ).order_by('-total_score')[:10]
    
    return render(request, 'quiz_app/leaderboard.html', {'top_users': top_users})

def help_center(request):
    return render(request, 'quiz_app/help_center.html')

def privacy_policy(request):
    return render(request, 'quiz_app/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'quiz_app/terms_of_service.html')

def cookie_policy(request):
    return render(request, 'quiz_app/cookie_policy.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you would typically save the email to your newsletter database
        # and possibly send a confirmation email
        messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect('home')
    return redirect('home')

def faq(request):
    faqs = [
        {
            'question': 'How do I create a quiz?',
            'answer': 'To create a quiz, go to your dashboard and click on the "Create Quiz" button. Follow the step-by-step process to add questions and answers.'
        },
        {
            'question': 'How are quiz scores calculated?',
            'answer': 'Quiz scores are calculated based on the number of correct answers. Each question carries equal weight, and the final score is presented as a percentage.'
        },
        {
            'question': 'Can I retake a quiz?',
            'answer': 'Yes, you can retake any quiz multiple times. However, only your best score will be recorded in your statistics.'
        },
        {
            'question': 'How do I report an issue?',
            'answer': 'You can report issues by clicking on the "Report Issue" link in the footer or by contacting our support team directly.'
        },
        {
            'question': 'Is there a mobile app available?',
            'answer': 'Yes, we have mobile apps available for both iOS and Android. You can download them from the respective app stores.'
        },
        {
            'question': 'How do I reset my password?',
            'answer': 'You can reset your password by clicking on the "Forgot Password" link on the login page. Follow the instructions sent to your email.'
        }
    ]
    return render(request, 'quiz_app/faq.html', {'faqs': faqs})

def feedback(request):
    if request.method == 'POST':
        # Handle feedback submission
        messages.success(request, 'Thank you for your feedback!')
        return redirect('home')
    return render(request, 'quiz_app/feedback.html')

def report_issue(request):
    if request.method == 'POST':
        # Handle issue report submission
        messages.success(request, 'Thank you for reporting the issue. We will look into it.')
        return redirect('home')
    return render(request, 'quiz_app/report_issue.html')

def suggest_quiz(request):
    if request.method == 'POST':
        # Handle quiz suggestion submission
        messages.success(request, 'Thank you for your suggestion! We will review it.')
        return redirect('home')
    return render(request, 'quiz_app/suggest_quiz.html')

def sitemap(request):
    pages = [
        {'title': 'Home', 'url': reverse('home')},
        {'title': 'About Us', 'url': reverse('about_us')},
        {'title': 'Contact Us', 'url': reverse('contact_us')},
        {'title': 'FAQ', 'url': reverse('faq')},
        {'title': 'Help Center', 'url': reverse('help_center')},
        {'title': 'Privacy Policy', 'url': reverse('privacy_policy')},
        {'title': 'Terms of Service', 'url': reverse('terms_of_service')},
        {'title': 'Cookie Policy', 'url': reverse('cookie_policy')},
    ]
    
    if request.user.is_authenticated:
        user_pages = [
            {'title': 'Dashboard', 'url': reverse('dashboard')},
            {'title': 'Profile', 'url': reverse('profile')},
            {'title': 'Quiz Categories', 'url': reverse('quiz_categories')},
            {'title': 'Statistics', 'url': reverse('statistics')},
            {'title': 'Leaderboard', 'url': reverse('leaderboard')},
        ]
        pages.extend(user_pages)
    
    if request.user.is_staff:
        staff_pages = [
            {'title': 'Staff Dashboard', 'url': reverse('staff_dashboard')},
            {'title': 'Create Quiz', 'url': reverse('create_quiz_staff')},
        ]
        pages.extend(staff_pages)
    
    return render(request, 'quiz_app/sitemap.html', {'pages': pages})