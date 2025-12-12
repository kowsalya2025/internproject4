from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'teacher':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be a teacher to access this page.')
        return redirect('home')
    return wrapper

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'student':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You must be a student to access this page.')
        return redirect('home')
    return wrapper