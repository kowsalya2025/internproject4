from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # ---------------- HOME & AUTH ----------------
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # ---------------- DASHBOARDS ----------------
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # ---------------- PROFILE ----------------
    path('profile/', views.profile, name='profile'),
    path("profile/edit/", views.profile_edit, name="profile_edit"),

    # ---------------- SUBJECTS ----------------
    path('create-subject/', views.create_subject, name='create_subject'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),

    # ---------------- EXAMS ----------------
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('exam/<int:exam_id>/result/', views.exam_result, name='exam_result'),

    # ---------------- QUESTIONS ----------------
    path('exam/<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('exam/<int:exam_id>/reorder-questions/', views.reorder_questions, name='reorder_questions'),

    # ---------------- TEACHER ----------------
    path('create-exam/', views.create_exam, name='create_exam'),

    # ---------------- RESULTS & ANALYTICS ----------------
    # path('result/<int:exam_id>/', views.exam_result, name='exam_result'),
    path('analytics/', views.analytics, name='analytics'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # ---------------- OTHER ----------------
    path('contact/', views.contact, name='contact'),
    path('oauth-debug/', views.oauth_debug, name='oauth_debug'),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path('contact/', views.contact, name='contact'),

    path('contact/', views.contact_teacher, name='contact_teacher'),  # student contact page
    path('inbox/', views.teacher_inbox, name='teacher_inbox'),
    path('reply/<int:message_id>/', views.reply_to_student, name='reply_to_student'),

    path('student-messages/', views.student_messages, name='student_messages'),

    path('edit-profile/', views.edit_profile, name='edit_profile'),

      path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('results/<int:attempt_id>/', views.exam_results, name='exam_results'),
    path('submit_exam/<int:exam_id>/', views.submit_exam, name='submit_exam'),

    path('debug/submit/', views.debug_submit, name='debug_submit'),
    path('missed-exam/<int:exam_id>/', views.view_missed_exam, name='view_missed_exam'),

    path("exam/<int:exam_id>/submit/", views.submit_exam, name="submit_exam"),
    path('exam/<int:exam_id>/submitted/', views.exam_submitted, name='exam_submitted'), 
    # urls.py
path('result/<int:attempt_id>/', views.exam_result, name='exam_result'),
  path('attempt/<int:attempt_id>/', views.attempt_detail, name='attempt_detail'),

  
 path('exams/', views.exam_list, name='exam_list'),
    path('attempt/<int:attempt_id>/', views.attempt_detail, name='view_attempt'),
    path('take/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    


]
