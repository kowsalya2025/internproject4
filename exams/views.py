from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Exam, Question, Choice, ExamAttempt, Answer, Subject, UserProfile
from .forms import UserRegisterForm, ExamForm, QuestionForm, ChoiceForm, SubjectForm
from .decorators import teacher_required, student_required
import json
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Exam, Question



def home(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.user_type == 'teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        except UserProfile.DoesNotExist:
            pass
    return render(request, 'home.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user_type == "student":
                return redirect("student_dashboard")
            elif user_type == "teacher":
                return redirect("teacher_dashboard")
            elif user_type == "admin":
                return redirect("admin_dashboard")
        else:
            return render(request, "login.html", {"form": {"errors": True}})

    return render(request, "login.html")



# exams/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

def register(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        account_type = request.POST.get('account_type')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'registration/register.html')
        
        # Create user
        from django.contrib.auth.models import User
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Save account type if you have a profile model
            # user.profile.user_type = account_type
            # user.profile.save()
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/register.html')
    
    return render(request, 'registration/register.html')

def home(request):
    return render(request, 'home.html')




def profile(request):
    return render(request, 'profile.html')

def contact(request):
    return render(request, 'contact.html')



@login_required
@student_required
def student_dashboard(request):
    now = timezone.now()

    # ✅ COMPLETED ATTEMPTS - Changed 'submitted' to 'completed'
    completed_attempts = ExamAttempt.objects.filter(
        student=request.user,
        status='completed'  # ✅ FIXED: Match what submit_exam saves
    ).select_related('exam', 'exam__subject').order_by('-submitted_at')

    # ✅ Extract completed exam IDs
    completed_exam_ids = completed_attempts.values_list('exam_id', flat=True)

    # ✅ EXAMS NOT ATTEMPTED
    exams_not_attempted = Exam.objects.filter(is_active=True).exclude(
        id__in=completed_exam_ids
    )

    # ✅ CATEGORIZE EXAMS
    available_exams = exams_not_attempted.filter(
        start_time__lte=now,
        end_time__gte=now
    ).order_by('start_time')

    upcoming_exams = exams_not_attempted.filter(
        start_time__gt=now
    ).order_by('start_time')

    # ✅ Missed exams (ended but not attempted)
    ended_exams = exams_not_attempted.filter(
        end_time__lt=now
    ).order_by('-end_time')

    # ✅ MESSAGES & REPLIES
    student_messages = TeacherMessage.objects.filter(
        sender=request.user
    ).order_by('-created_at')

    teacher_replies = TeacherReply.objects.filter(
        message__sender=request.user
    ).select_related('teacher', 'message').order_by('-created_at')

    # ✅ FINAL CONTEXT
    context = {
        'now': now,
        'available_exams': available_exams,
        'upcoming_exams': upcoming_exams,
        'ended_exams': ended_exams,
        'completed_attempts': completed_attempts,  # ✅ This is all you need
        'student_messages': student_messages,
        'teacher_replies': teacher_replies,
    }

    return render(request, 'exams/student_dashboard.html', context)


# from django.utils import timezone
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .decorators import student_required
# from .models import Exam, ExamAttempt, TeacherMessage, TeacherReply

# @login_required
# @student_required
# def student_dashboard(request):
#     now = timezone.now()

#     # -------------------------
#     # ✅ COMPLETED ATTEMPTS (Already Attempted & Submitted)
#     # -------------------------
#     completed_attempts = ExamAttempt.objects.filter(
#         student=request.user,
#         status='submitted'
#     ).select_related('exam').order_by('-end_time')

#     # ✅ Extract completed exam IDs
#     completed_exam_ids = completed_attempts.values_list('exam_id', flat=True)

#     # -------------------------
#     # ✅ EXAMS NOT ATTEMPTED
#     # -------------------------
#     exams_not_attempted = Exam.objects.filter(is_active=True).exclude(
#         id__in=completed_exam_ids
#     )

#     # -------------------------
#     # ✅ CATEGORIZE EXAMS
#     # -------------------------
#     available_exams = exams_not_attempted.filter(
#         start_time__lte=now,
#         end_time__gte=now
#     ).order_by('start_time')

#     upcoming_exams = exams_not_attempted.filter(
#         start_time__gt=now
#     ).order_by('start_time')

#     # ✅ These are ended BUT NOT attempted (missed exams)
#     ended_exams = exams_not_attempted.filter(
#         end_time__lt=now
#     ).order_by('-end_time')

#     # ✅ These are exams the student HAS COMPLETED
#     completed_exams = Exam.objects.filter(
#         id__in=completed_exam_ids
#     ).order_by('-end_time')

#     # -------------------------
#     # ✅ MESSAGES & REPLIES
#     # -------------------------
#     student_messages = TeacherMessage.objects.filter(
#         sender=request.user
#     ).order_by('-created_at')

#     teacher_replies = TeacherReply.objects.filter(
#         message__sender=request.user
#     ).select_related('teacher', 'message').order_by('-created_at')

#     # -------------------------
#     # ✅ FINAL CONTEXT
#     # -------------------------
#     context = {
#         'now': now,
#         'available_exams': available_exams,
#         'upcoming_exams': upcoming_exams,
#         'ended_exams': ended_exams,              # missed exams
#         'completed_exams': completed_exams,      # ✅ ADD THIS
#         'completed_attempts': completed_attempts,
#         'student_messages': student_messages,
#         'teacher_replies': teacher_replies,
#     }

#     return render(request, 'exams/student_dashboard.html', context)






@login_required
@teacher_required
def teacher_dashboard(request):
    subjects = Subject.objects.filter(teacher=request.user)
    exams = Exam.objects.filter(created_by=request.user)
    total_students = ExamAttempt.objects.filter(
        exam__created_by=request.user
    ).values('student').distinct().count()

    messages_received = request.user.received_messages.all().order_by('-created_at')

    context = {
        'subjects': subjects,
        'exams': exams,
        'total_students': total_students,
        'messages_received': messages_received,
    }
    return render(request, 'exams/teacher_dashboard.html', context)





from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Exam, ExamAttempt

@login_required
def exam_list(request):
    now = timezone.now()

    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'teacher':
        # Teacher sees only exams they created
        exams = Exam.objects.filter(created_by=request.user)
    else:
        # Student sees live exams OR exams they attempted
        attempted_exam_ids = ExamAttempt.objects.filter(student=request.user).values_list('exam_id', flat=True)

        exams = Exam.objects.filter(
            Q(start_time__lte=now, end_time__gte=now) | Q(id__in=attempted_exam_ids)
        ).distinct()

    # Map of student attempts: { exam_id: attempt }
    attempts = ExamAttempt.objects.filter(student=request.user)
    attempt_map = {a.exam_id: a for a in attempts}

    return render(request, 'exams/exam_list.html', {
        'exams': exams,
        'attempt_map': attempt_map,
        'now': now,
    })




@login_required
def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    return render(request, "exams/attempt_detail.html", {"attempt": attempt})




from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Exam, ExamAttempt

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Current timezone-aware time
    now = timezone.now()
    
    # Check if student has already attempted
    attempted = ExamAttempt.objects.filter(exam=exam, student=request.user).exists()
    
    # Get all questions for this exam
    questions = exam.questions.all()  # Use related_name from your Question model
    
    context = {
        'exam': exam,
        'questions': questions,
        'attempted': attempted,
         'now': now,  # pass current time to template
    }
    return render(request, 'exams/exam_detail.html', context)

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)

    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'questions': questions
    })




@login_required
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    # Ensure user can view this result
    if attempt.student != request.user and attempt.exam.created_by != request.user:
        messages.error(request, 'You do not have permission to view this result.')
        return redirect('home')
    
    answers = attempt.answers.all().select_related('question', 'selected_choice')
    
    context = {
        'attempt': attempt,
        'answers': answers,
    }
    return render(request, 'exams/exam_result.html', context)


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# ... other imports ...

# Keep this decorator function (it's correct)
def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user has a profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found.")
            return redirect('home')

        # Check if the user is a teacher
        if request.user.profile.user_type != 'teacher':
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


from django.utils.dateparse import parse_datetime

@login_required
def create_exam(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'teacher':
        messages.error(request, "You do not have permission to create exams.")
        return redirect('home')

    subjects = Subject.objects.filter(teacher=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        total_marks = request.POST.get('total_marks')
        passing_marks = request.POST.get('passing_marks')
        difficulty = request.POST.get('difficulty')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not all([title, subject_id, description, duration, total_marks, passing_marks, difficulty, start_time, end_time]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'exams/create_exam.html', {'subjects': subjects})

        try:
            subject = Subject.objects.get(id=subject_id, teacher=request.user)
        except Subject.DoesNotExist:
            messages.error(request, "Invalid subject selected.")
            return render(request, 'exams/create_exam.html', {'subjects': subjects})

        exam = Exam.objects.create(
            title=title,
            subject=subject,
            description=description,
            duration=int(duration),
            total_marks=int(total_marks),
            passing_marks=int(passing_marks),
            difficulty=difficulty,
            start_time=parse_datetime(start_time),
            end_time=parse_datetime(end_time),
            created_by=request.user,
            is_active=True   # ✅ CRITICAL FIX
        )

        messages.success(request, f"Exam '{exam.title}' created successfully!")
        return redirect('add_question', exam_id=exam.id)

    return render(request, 'exams/create_exam.html', {'subjects': subjects})




# views.py
@login_required
@teacher_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.exam = exam
            
            # If order is 0, auto-increment
            if question.order == 0:
                last_question = Question.objects.filter(exam=exam).order_by('-order').first()
                question.order = last_question.order + 1 if last_question else 1
            
            question.save()
            
            # Add choices for MCQ and True/False
            if question.question_type in ['mcq', 'true_false']:
                if question.question_type == 'true_false':
                    Choice.objects.create(question=question, choice_text='True', is_correct=False)
                    Choice.objects.create(question=question, choice_text='False', is_correct=False)
                    messages.info(request, 'True/False question added! Please mark the correct answer.')
                else:
                    messages.info(request, 'MCQ added! Now add choices and mark the correct one.')
                
                return redirect('edit_question', question_id=question.id)
            
            messages.success(request, 'Short answer question added successfully!')
            return redirect('add_question', exam_id=exam.id)
    else:
        question_form = QuestionForm()
    
    questions = exam.questions.all()
    context = {
        'exam': exam,
        'question_form': question_form,
        'questions': questions,
    }
    return render(request, 'exams/add_question.html', context)






@login_required
@teacher_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        # Handle adding choices
        if 'add_choice' in request.POST:
            choice_form = ChoiceForm(request.POST)
            if choice_form.is_valid():
                choice = choice_form.save(commit=False)
                choice.question = question
                choice.save()
                messages.success(request, 'Choice added successfully!')
                return redirect('edit_question', question_id=question.id)

        # Handle updating correct answer
        elif 'update_correct' in request.POST:
            correct_choice_id = request.POST.get('correct_choice')
            if correct_choice_id:
                question.choices.update(is_correct=False)
                Choice.objects.filter(id=correct_choice_id).update(is_correct=True)
                messages.success(request, 'Correct answer updated!')
                return redirect('edit_question', question_id=question.id)

        # Handle deleting a choice
        elif 'delete_choice' in request.POST:
            choice_id = request.POST.get('delete_choice')
            choice = get_object_or_404(Choice, id=choice_id, question=question)
            choice.delete()
            messages.success(request, 'Choice deleted successfully!')
            return redirect('edit_question', question_id=question.id)

        # Handle deleting the question
        elif 'delete_question' in request.POST:
            exam_id = question.exam.id
            question.delete()
            messages.success(request, 'Question deleted successfully!')
            return redirect('add_question', exam_id=exam_id)

    # GET request or fallback
    choice_form = ChoiceForm()
    choices = question.choices.all()

    context = {
        'question': question,
        'choice_form': choice_form,
        'choices': choices,
    }
    return render(request, 'exams/edit_question.html', context)





@login_required
@teacher_required
def analytics(request):
    exams = Exam.objects.filter(created_by=request.user)
    
    # Overall statistics
    total_exams = exams.count()
    total_attempts = ExamAttempt.objects.filter(exam__created_by=request.user, status='submitted').count()
    
    if total_attempts > 0:
        avg_score = ExamAttempt.objects.filter(
            exam__created_by=request.user, 
            status='submitted'
        ).aggregate(Avg('percentage'))['percentage__avg']
        
        pass_rate = ExamAttempt.objects.filter(
            exam__created_by=request.user, 
            status='submitted',
            passed=True
        ).count() / total_attempts * 100
    else:
        avg_score = 0
        pass_rate = 0
    
    # Per exam statistics
    exam_stats = []
    for exam in exams:
        attempts = exam.attempts.filter(status='submitted')
        if attempts.exists():
            stats = {
                'exam': exam,
                'total_attempts': attempts.count(),
                'avg_score': attempts.aggregate(Avg('percentage'))['percentage__avg'],
                'pass_rate': attempts.filter(passed=True).count() / attempts.count() * 100,
                'highest_score': attempts.order_by('-score').first().score if attempts.exists() else 0,
            }
            exam_stats.append(stats)
    
    context = {
        'total_exams': total_exams,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 2) if avg_score else 0,
        'pass_rate': round(pass_rate, 2),
        'exam_stats': exam_stats,
    }
    return render(request, 'exams/analytics.html', context)


@login_required
@teacher_required
def create_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = request.user
            subject.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('teacher_dashboard')
    else:
        form = SubjectForm()
    
    return render(request, 'exams/create_subject.html', {'form': form})


def create_exam_test(request):
    teacher_subjects = Subject.objects.filter(teacher=request.user)
    
    if request.method == 'POST':
        try:
            # Create exam manually
            exam = Exam.objects.create(
                title=request.POST.get('title'),
                subject_id=request.POST.get('subject'),
                description=request.POST.get('description'),
                duration=request.POST.get('duration'),
                total_marks=request.POST.get('total_marks'),
                passing_marks=request.POST.get('passing_marks'),
                difficulty=request.POST.get('difficulty'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                created_by=request.user,
                is_active=False
            )
            messages.success(request, f"Exam created with ID: {exam.id}")
            return redirect('add_question', exam_id=exam.id)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'exams/create_exam_simple.html', {
        'teacher_subjects': teacher_subjects
    })





@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    exams = subject.exams.all()  # or related_name from your Exam model
    context = {
        'subject': subject,
        'exams': exams,
    }
    return render(request, 'exams/subject_detail.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def profile_edit(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()
        return redirect("profile")

    return render(request, "profile_edit.html")




@login_required
def exam_result(request, attempt_id):
    """Display exam results for a specific attempt"""
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )
    
    # Get all answers for this attempt
    answers = Answer.objects.filter(attempt=attempt).select_related(
        'question', 'selected_choice'
    ).order_by('question__order')
    
    # Calculate statistics
    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()
    wrong_answers = total_questions - correct_answers
    
    # Check if passed
    passed = attempt.marks_obtained >= attempt.exam.passing_marks
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
        'passed': passed,
    }
    
    return render(request, 'exams/exam_result.html', context)






@login_required
def leaderboard(request):
    results = ExamAttempt.objects.select_related('user', 'exam').order_by('-score')

    return render(request, 'exams/leaderboard.html', {
        'results': results
    })


# accounts/views.py or exams/views.py
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

def oauth_debug(request):
    context = {
        'google_key': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY[:10] + '...' if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY else 'Not set',
        'google_secret': 'Set' if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET else 'Not set',
        'microsoft_key': settings.SOCIAL_AUTH_MICROSOFT_GRAPH_KEY[:10] + '...' if settings.SOCIAL_AUTH_MICROSOFT_GRAPH_KEY else 'Not set',
        'microsoft_secret': 'Set' if settings.SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET else 'Not set',
        'github_key': settings.SOCIAL_AUTH_GITHUB_KEY[:10] + '...' if settings.SOCIAL_AUTH_GITHUB_KEY else 'Not set',
        'github_secret': 'Set' if settings.SOCIAL_AUTH_GITHUB_SECRET else 'Not set',
        'debug': settings.DEBUG,
    }
    return render(request, 'oauth_debug.html', context)


# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@login_required
@teacher_required
@require_POST
@csrf_exempt  # Add this if you're having CSRF issues
def reorder_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        order_data = data.get('order', [])
        
        for index, question_id in enumerate(order_data, start=1):
            try:
                question = Question.objects.get(id=int(question_id), exam=exam)
                question.order = index
                question.save()
            except (Question.DoesNotExist, ValueError):
                continue
        
        return JsonResponse({'success': True, 'message': 'Questions reordered successfully!'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



def get_exam_performance_data(self):
    """Get exam performance data"""
    exams = Exam.objects.filter(attempts__isnull=False).distinct()[:5]
    data = []
    
    for exam in exams:
        attempts = exam.attempts.filter(status='submitted')
        if attempts.exists():
            avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
            pass_rate = (attempts.filter(passed=True).count() / attempts.count()) * 100
        else:
            avg_score = 0
            pass_rate = 0
        
        data.append({
            'exam': exam.title,
            'avg_score': round(avg_score, 2),
            'pass_rate': round(pass_rate, 2),
            'attempts': attempts.count()
        })
    
    return data



def get_average_score(self):
    """Get average score across all submitted attempts"""
    submitted = ExamAttempt.objects.filter(status='submitted')
    if submitted.exists():
        avg = submitted.aggregate(avg=Avg('percentage'))['avg'] or 0
        return round(avg, 2)
    return 0

def get_completion_rate(self):
    """Get exam completion rate"""
    total = ExamAttempt.objects.count()
    completed = ExamAttempt.objects.filter(status='submitted').count()
    
    if total > 0:
        return round((completed / total) * 100, 2)


@login_required
def contact(request):
    teachers = User.objects.filter(profile__user_type='teacher')

    if request.method == "POST":
        teacher_id = request.POST.get("teacher")
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        teacher = User.objects.filter(id=teacher_id, profile__user_type='teacher').first()
        if not teacher:
            messages.error(request, "Selected teacher does not exist.")
            return redirect("contact")

        if not subject or not message_text:
            messages.error(request, "Subject and message cannot be empty.")
            return redirect("contact")

        TeacherMessage.objects.create(
            sender=request.user,
            teacher=teacher,
            subject=subject,
            message=message_text
        )

        messages.success(request, "Your message has been sent to the teacher successfully!")
        return redirect("contact")

    return render(request, "contact.html", {"teachers": teachers})


# exams/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TeacherMessage, User

def contact_teacher(request):
    teachers = User.objects.filter(profile__user_type='teacher')  # fetch all teachers
    if request.method == "POST":
        teacher_id = request.POST.get("teacher")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")

        if teacher_id and subject and message_text:
            teacher = User.objects.get(id=teacher_id)
            TeacherMessage.objects.create(
                sender=request.user,
                teacher=teacher,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact_teacher')

    return render(request, 'contact_teacher.html', {'teachers': teachers})

# exams/views.py
from django.contrib.auth.decorators import login_required

@login_required
def teacher_inbox(request):
    if request.user.profile.user_type != 'teacher':
        return redirect('home')  # only teachers can see this

    messages_received = request.user.received_messages.all().order_by('-created_at')
    return render(request, 'teacher_inbox.html', {'messages': messages_received})

# exams/views.py
from django.shortcuts import get_object_or_404
from .models import TeacherMessage, TeacherReply
from django.contrib.auth.decorators import login_required

@login_required
def reply_to_student(request, message_id):
    msg = get_object_or_404(TeacherMessage, id=message_id)

    if request.method == "POST":
        reply_text = request.POST.get("reply")
        TeacherReply.objects.create(
            message=msg,
            teacher=request.user,
            message_text=reply_text
        )
        return redirect("teacher_dashboard")  # redirect back to dashboard

    return render(request, "exams/reply_to_student.html", {"msg": msg})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import TeacherMessage, TeacherReply

@login_required
def student_messages(request):
    # Get all messages sent by this student
    messages_sent = TeacherMessage.objects.filter(sender=request.user, parent__isnull=True).order_by('-created_at')

    context = {
        'messages_sent': messages_sent
    }
    return render(request, 'exams/student_messages.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {'form': form}
    return render(request, 'exams/edit_profile.html', context)


# # exams/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from django.db import transaction
# from .models import Exam, Question, Choice, ExamAttempt, Answer

# @login_required
# @transaction.atomic
# def submit_exam(request, exam_id):
#     exam = get_object_or_404(Exam, id=exam_id)
    
#     # Create exam attempt
#     attempt = ExamAttempt.objects.create(
#         user=request.user,
#         exam=exam,
#         start_time=timezone.now() - timezone.timedelta(minutes=exam.duration),  # Adjust based on your timer
#         end_time=timezone.now(),
#         status='completed'
#     )
    
#     # Process each question
#     for question in exam.questions.all():
#         answer_value = request.POST.get(f'question_{question.id}')
        
#         if answer_value:  # If user answered this question
#             if question.question_type == 'multiple_choice':
#                 # For MCQ, answer_value is the Choice ID
#                 try:
#                     selected_choice = Choice.objects.get(id=answer_value)
#                     Answer.objects.create(
#                         attempt=attempt,
#                         question=question,
#                         selected_choice=selected_choice,
#                         text_answer=''
#                     )
#                 except Choice.DoesNotExist:
#                     pass
                    
#             elif question.question_type == 'true_false':
#                 # For True/False
#                 Answer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     text_answer=answer_value  # Will be "true" or "false"
#                 )
                
#             elif question.question_type == 'short_answer':
#                 # For Short Answer
#                 Answer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     text_answer=answer_value
#                 )
    
#     # Calculate score
#     calculate_score(attempt)
    
#     # Clear localStorage
#     # (This will be handled by JavaScript after submission)
    
#     return redirect('exam_results', attempt_id=attempt.id)

# def calculate_score(attempt):
#     total_score = 0
#     max_score = attempt.exam.total_marks
    
#     for answer in attempt.answers.all():
#         question = answer.question
        
#         if question.question_type == 'multiple_choice':
#             if answer.selected_choice and answer.selected_choice.is_correct:
#                 total_score += question.marks
                
#         elif question.question_type == 'true_false':
#             if answer.text_answer.lower() == str(question.correct_answer).lower():
#                 total_score += question.marks
                
#         elif question.question_type == 'short_answer':
#             # For short answer, you might need manual grading
#             # Or implement auto-grading based on keywords
#             pass
    
#     attempt.score = total_score
#     attempt.save()

# # exams/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from django.db import transaction
# from django.contrib import messages
# from .models import Exam, Question, Choice, ExamAttempt, Answer
# # exams/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from django.db import transaction
# from django.contrib import messages
# from .models import Exam, Question, Choice, ExamAttempt, Answer

# @login_required
# def take_exam(request, exam_id):
#     exam = get_object_or_404(Exam, id=exam_id)
#     questions = exam.questions.all().prefetch_related('choices')
    
#     # Get or create attempt
#     attempt = ExamAttempt.objects.filter(
#         student=request.user,
#         exam=exam,
#         status='in_progress'
#     ).first()
    
#     if not attempt:
#         attempt = ExamAttempt.objects.create(
#             student=request.user,
#             exam=exam,
#             status='in_progress'
#         )
    
#     return render(request, 'exams/take_exam.html', {
#         'exam': exam,
#         'questions': questions,
#         'attempt': attempt  # Pass attempt to template
    # })

# @login_required
# @transaction.atomic
# def submit_exam(request, exam_id):
#     if request.method != 'POST':
#         return redirect('take_exam', exam_id=exam_id)
    
#     exam = get_object_or_404(Exam, id=exam_id)
    
#     # Check if user (student) already completed this exam
#     existing_attempt = ExamAttempt.objects.filter(
#         student=request.user,  # Changed from 'user' to 'student'
#         exam=exam,
#         status='completed'
#     ).first()
    
#     if existing_attempt:
#         messages.info(request, 'You have already submitted this exam.')
#         return redirect('exam_results', attempt_id=existing_attempt.id)
    
#     # Check for in-progress attempt to resume
#     in_progress_attempt = ExamAttempt.objects.filter(
#         student=request.user,  # Changed from 'user' to 'student'
#         exam=exam,
#         status='in_progress'
#     ).first()
    
#     if in_progress_attempt:
#         # Update existing in-progress attempt
#         attempt = in_progress_attempt
#         attempt.end_time = timezone.now()
#         attempt.status = 'completed'
#         attempt.score = 0
#         attempt.save()
        
#         # Clear previous answers
#         attempt.answers.all().delete()
#     else:
#         # Create new exam attempt
#         attempt = ExamAttempt.objects.create(
#             student=request.user,  # Changed from 'user' to 'student'
#             exam=exam,
#             start_time=timezone.now() - timezone.timedelta(minutes=exam.duration),
#             end_time=timezone.now(),
#             status='completed',
#             score=0
#         )
    
#     total_marks = 0
    
#     # Process each question
#     for question in exam.questions.all():
#         answer_value = request.POST.get(f'question_{question.id}')
        
#         if answer_value:  # If user answered this question
#             if question.question_type == 'multiple_choice':
#                 try:
#                     selected_choice = Choice.objects.get(id=answer_value, question=question)
#                     is_correct = selected_choice.is_correct
#                     marks_awarded = question.marks if is_correct else 0
                    
#                     Answer.objects.create(
#                         attempt=attempt,
#                         question=question,
#                         selected_choice=selected_choice,
#                         text_answer='',
#                         marks_awarded=marks_awarded
#                     )
                    
#                     total_marks += marks_awarded
#                 except Choice.DoesNotExist:
#                     pass
                    
#             elif question.question_type == 'true_false':
#                 correct_answer = str(question.correct_answer).lower() if question.correct_answer else ''
#                 user_answer = answer_value.lower()
#                 is_correct = (user_answer == correct_answer)
#                 marks_awarded = question.marks if is_correct else 0
                
#                 Answer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     text_answer=answer_value,
#                     marks_awarded=marks_awarded
#                 )
                
#                 total_marks += marks_awarded
                
#             elif question.question_type == 'short_answer':
#                 # For short answer, initially award 0 marks
#                 # Teacher will grade later
#                 Answer.objects.create(
#                     attempt=attempt,
#                     question=question,
#                     text_answer=answer_value,
#                     marks_awarded=0  # Will be graded manually
#                 )
    
#     # Update attempt score
#     attempt.score = total_marks
#     attempt.save()
    
#     messages.success(request, 'Exam submitted successfully!')
#     return redirect('exam_results', attempt_id=attempt.id)

@login_required
def exam_results(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)  # Changed to 'student'
    
    # Calculate percentage
    total_possible = attempt.exam.total_marks
    percentage = (attempt.score / total_possible * 100) if total_possible > 0 else 0
    
    return render(request, 'exams/exam_results.html', {
        'attempt': attempt,
        'percentage': percentage
    })

# exams/views.py
@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check if user already has a completed attempt
    completed_attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        status='completed'
    ).exists()
    
    if completed_attempt:
        messages.warning(request, 'You have already completed this exam.')
        return redirect('student_dashboard')
    
    # Check for existing in-progress attempt
    attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        status='in_progress'
    ).first()
    
    if not attempt:
        # Create new attempt
        attempt = ExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            status='in_progress'
        )
    
    return redirect('take_exam', exam_id=exam_id)

@login_required
def submit_exam(request, exam_id):
    if request.method != 'POST':
        return redirect('exam_detail', exam_id=exam_id)

    exam = get_object_or_404(Exam, id=exam_id)

    attempts = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam
    ).order_by('-start_time')

    completed_attempt = attempts.filter(status='completed').first()
    if completed_attempt:
        return redirect('exam_result', attempt_id=completed_attempt.id)

    attempt = attempts.filter(status='in_progress').first()
    if not attempt:
        attempt = ExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            start_time=timezone.now(),
            status='in_progress'
        )

    questions = exam.questions.all().order_by('order')

    total_marks = 0
    obtained_marks = 0

    for question in questions:

        submitted_answer = request.POST.get(f"question_{question.id}", "").strip()
        answer_obj = Answer.objects.create(
            attempt=attempt,
            question=question,
            answered_at=timezone.now()
        )

        # MCQ and True/False
        if question.question_type in ['mcq', 'true_false']:
            if submitted_answer:
                try:
                    selected_choice = Choice.objects.get(
                        id=int(submitted_answer),
                        question=question
                    )
                    answer_obj.selected_choice = selected_choice

                    if selected_choice.is_correct:
                        answer_obj.is_correct = True
                        answer_obj.marks_obtained = question.marks
                        obtained_marks += question.marks
                    else:
                        answer_obj.is_correct = False
                        answer_obj.marks_obtained = 0

                except (ValueError, Choice.DoesNotExist):
                    answer_obj.is_correct = False
                    answer_obj.marks_obtained = 0

            else:
                answer_obj.is_correct = False
                answer_obj.marks_obtained = 0

        # Short Answers
        elif question.question_type == 'short':
            answer_obj.text_answer = submitted_answer
            answer_obj.is_correct = False
            answer_obj.marks_obtained = 0  # Manual grading later

        answer_obj.save()
        total_marks += question.marks

    # Calculate percentage
    percentage = round((obtained_marks / total_marks) * 100, 2) if total_marks > 0 else 0

    # Update attempt with ALL needed fields
    attempt.end_time = timezone.now()
    attempt.submitted_at = timezone.now()
    attempt.status = "completed"
    attempt.score = obtained_marks
    attempt.total_marks = total_marks
    attempt.percentage = percentage
    attempt.save()

    return redirect("exam_result", attempt_id=attempt.id)



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExamAttempt, Answer

@login_required
def exam_result(request, attempt_id):
    """Display exam results for a specific attempt"""
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )

    # Fetch all answers for this attempt
    answers = Answer.objects.filter(attempt=attempt).select_related(
        "question", "selected_choice"
    ).order_by("question__order")

    all_questions = attempt.exam.questions.all().order_by("order")
    total_questions = all_questions.count()

    # Count correct, wrong, not answered
    correct_answers = 0
    wrong_answers = 0
    not_answered = 0

    for ans in answers:
        if ans.marks_obtained is None:
            not_answered += 1
        elif ans.marks_obtained == ans.question.marks:
            correct_answers += 1
        elif ans.marks_obtained == 0:
            wrong_answers += 1

    # If some questions have no Answer object (not answered)
    answer_q_ids = {a.question_id for a in answers}
    for q in all_questions:
        if q.id not in answer_q_ids:
            not_answered += 1

    # Pass/Fail logic
    passed = attempt.score >= attempt.exam.passing_marks

    context = {
        "attempt": attempt,
        "answers": answers,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "not_answered": not_answered,
        "passed": passed,
    }

    return render(request, "exams/exam_result.html", context)


# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import ExamAttempt, Answer

# @login_required
# def exam_result(request, attempt_id):
#     """Display exam results for a specific attempt"""
#     attempt = get_object_or_404(
#         ExamAttempt,
#         id=attempt_id,
#         student=request.user
#     )

#     # Fetch answers for this attempt
#     answers = Answer.objects.filter(attempt=attempt).select_related(
#         'question', 'selected_choice'
#     ).order_by('question__order')

#     # For unanswered questions, create Answer objects dynamically with None values
#     all_questions = attempt.exam.questions.all().order_by('order')
#     answered_q_ids = [a.question_id for a in answers]
#     for q in all_questions:
#         if q.id not in answered_q_ids:
#             answers |= Answer.objects.filter(id=None)  # placeholder
#             # We'll handle display in template as "Not Answered"

#     total_questions = all_questions.count()
#     correct_answers = sum(1 for a in answers if a.marks_awarded == a.question.marks)
#     wrong_answers = sum(1 for a in answers if a.marks_awarded == 0)
#     not_answered = total_questions - len(answers)

#     passed = attempt.score >= attempt.exam.passing_marks

#     context = {
#         'attempt': attempt,
#         'answers': answers,
#         'total_questions': total_questions,
#         'correct_answers': correct_answers,
#         'wrong_answers': wrong_answers,
#         'not_answered': not_answered,
#         'passed': passed,
#     }

#     return render(request, 'exams/exam_result.html', context)




# from .models import Exam, Question, StudentAnswer, StudentExamAttempt

# @login_required
# def submit_exam(request, exam_id):
#     exam = get_object_or_404(Exam, id=exam_id)
#     questions = Question.objects.filter(exam=exam)

#     if request.method == 'POST':
#         total_marks_obtained = 0
#         for question in questions:
#             answer = request.POST.get(f'question_{question.id}')
#             sa, created = StudentAnswer.objects.update_or_create(
#                 student=request.user,
#                 exam=exam,
#                 question=question,
#                 defaults={'answer': answer}
#             )
#             # Simple marking logic (example: correct answer field)
#             if question.correct_answer == answer:
#                 total_marks_obtained += question.marks

#         # Save or update a StudentExamAttempt record
#         StudentExamAttempt.objects.update_or_create(
#             student=request.user,
#             exam=exam,
#             defaults={
#                 'marks_obtained': total_marks_obtained,
#                 'percentage': (total_marks_obtained / exam.total_marks) * 100,
#                 'submitted_at': timezone.now()
#             }
#         )

#         return redirect('student_dashboard')  # redirect to dashboard

#     return redirect('take_exam', exam_id=exam.id)


@login_required
def exam_submitted(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    # Use a separate template for students
    return render(request, 'exams/exam_submitted.html', {'exam': exam})

from django.http import HttpResponse
# Add to views.py
def debug_submit(request):
    if request.method == 'POST':
        print("DEBUG - Form data received:")
        for key, value in request.POST.items():
            if key.startswith('question_'):
                print(f"{key}: {value}")
        return HttpResponse("Debug complete - check console")
    

@login_required
@student_required
def view_missed_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Block if already attempted
    if ExamAttempt.objects.filter(student=request.user, exam=exam).exists():
        messages.error(request, "You already attempted this exam.")
        return redirect('student_dashboard')

    # Allow only after exam ended
    if exam.end_time > timezone.now():
        messages.error(request, "Exam not finished yet.")
        return redirect('student_dashboard')

    questions = Question.objects.filter(exam=exam).prefetch_related("choices")

    return render(request, "exams/view_missed_exam.html", {
        "exam": exam,
        "questions": questions
    })

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    now = timezone.now()

    # Time validations
    if not exam.is_active:
        messages.error(request, "This exam is not active.")
        return redirect("exam_list")
    if now < exam.start_time:
        messages.error(request, "Exam has not started yet.")
        return redirect("exam_detail", exam_id=exam.id)
    if now > exam.end_time:
        messages.error(request, "Exam has ended.")
        return redirect("exam_detail", exam_id=exam.id)

    # If already completed, redirect to result
    completed_attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        status='completed'
    ).order_by('-id').first()

    if completed_attempt:
        return redirect('exam_result', attempt_id=completed_attempt.id)

    # Get *only* in-progress attempt
    attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        status='in_progress'
    ).order_by('-id').first()

    # If no in-progress, create a new one
    if attempt is None:
        attempt = ExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            start_time=now,
            status='in_progress'
        )

    # Prefetch questions + choices
    questions = exam.questions.all().prefetch_related('choices').order_by('order')

    # Load saved answers
    saved_answers = {}
    for ans in Answer.objects.filter(attempt=attempt):
        if ans.selected_choice:
            saved_answers[ans.question.id] = ans.selected_choice.id

    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'questions': questions,
        'attempt': attempt,
        'saved_answers': saved_answers
    })








@login_required
def exam_result(request, attempt_id):
    """Show the exam result for a completed attempt"""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)

    # Permission check
    if attempt.student != request.user and attempt.exam.created_by != request.user:
        messages.error(request, "You do not have permission to view this result.")
        return redirect('home')

    answers = attempt.answers.select_related('question', 'selected_choice').order_by('question__order')
    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()
    wrong_answers = total_questions - correct_answers
    passed = attempt.marks_obtained >= attempt.exam.passing_marks

    context = {
        'attempt': attempt,
        'answers': answers,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
        'passed': passed
    }
    return render(request, 'exams/exam_result.html', context)


from django.db.models import F, FloatField, ExpressionWrapper

def analytics(request):
    attempts = ExamAttempt.objects.annotate(
        percentage=ExpressionWrapper(
            F('score') * 100.0 / F('exam__total_marks'),
            output_field=FloatField()
        )
    )
    return render(request, 'exams/analytics.html', {'attempts': attempts})



