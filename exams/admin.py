from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Subject, Exam, Question, Choice, ExamAttempt, Answer, ContactTeacher


# ---------------------------
# UserProfile Admin
# ---------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone', 'roll_number', 'department')
    search_fields = ('user__username', 'roll_number', 'department')
    list_filter = ('user_type',)


# ---------------------------
# Subject Admin
# ---------------------------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'created_at')
    search_fields = ('name', 'code', 'teacher__username')
    list_filter = ('teacher',)


# ---------------------------
# Question Inline for Exam
# ---------------------------
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


# ---------------------------
# Choice Inline for Question
# ---------------------------
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


# ---------------------------
# Answer Inline for ExamAttempt
# ---------------------------
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'selected_choice', 'text_answer_display', 'marks_display']
    can_delete = False
    
    def text_answer_display(self, obj):
        return obj.text_answer[:100] if obj.text_answer else "No text answer"
    text_answer_display.short_description = 'Text Answer'
    
    def marks_display(self, obj):
        # Check which field exists in your model
        if hasattr(obj, 'marks_awarded'):
            return obj.marks_awarded
        elif hasattr(obj, 'marks_obtained'):
            return obj.marks_obtained
        return 0
    marks_display.short_description = 'Marks'


# ---------------------------
# Exam Admin
# ---------------------------
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty_badge', 'active_badge', 'total_marks', 'duration', 'start_time', 'end_time')
    list_filter = ('subject', 'difficulty', 'is_active')
    search_fields = ('title', 'description', 'subject__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline]
    actions = ['activate_exams', 'deactivate_exams']
    date_hierarchy = 'start_time'

    # Active / Inactive Badge
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">Active</span>')
        return format_html('<span class="badge bg-danger">Inactive</span>')
    active_badge.short_description = 'Status'

    # Difficulty Badge
    def difficulty_badge(self, obj):
        colors = {'easy': 'success', 'medium': 'warning', 'hard': 'danger'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.difficulty, 'secondary'),
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'

    # Actions
    def activate_exams(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} exams activated.")
    activate_exams.short_description = "Activate selected exams"

    def deactivate_exams(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} exams deactivated.")
    deactivate_exams.short_description = "Deactivate selected exams"


# ---------------------------
# Question Admin
# ---------------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'order', 'short_question', 'marks', 'question_type', 'has_image')
    search_fields = ('question_text', 'exam__title')
    list_filter = ('question_type', 'exam')
    inlines = [ChoiceInline]

    def short_question(self, obj):
        return obj.question_text[:50] + ('...' if len(obj.question_text) > 50 else '')
    short_question.short_description = "Question"
    
    def has_image(self, obj):
        return bool(obj.question_image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'


# ---------------------------
# Choice Admin
# ---------------------------
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'short_choice_text', 'is_correct')
    search_fields = ('choice_text', 'question__question_text')
    list_filter = ('is_correct', 'question__exam')
    
    def short_choice_text(self, obj):
        return obj.choice_text[:50] + ('...' if len(obj.choice_text) > 50 else '')
    short_choice_text.short_description = "Choice Text"


# ---------------------------
# ExamAttempt Admin
# ---------------------------
@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'exam', 'status', 'score', 'percentage_display', 'passed_display', 'start_time', 'end_time', 'duration_display']
    list_filter = ['status', 'exam', 'student']
    search_fields = ['student__username', 'student__email', 'exam__title']
    readonly_fields = ['percentage_display', 'passed_display', 'duration_display', 'start_time', 'end_time', 'score']
    inlines = [AnswerInline]
    
    def percentage_display(self, obj):
        if hasattr(obj, 'percentage') and obj.percentage is not None:
            color = 'green' if obj.percentage >= 70 else 'orange' if obj.percentage >= 40 else 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, obj.percentage)
        # Calculate percentage if not a property
        if obj.exam.total_marks > 0:
            percentage = round((obj.score / obj.exam.total_marks) * 100, 2)
            color = 'green' if percentage >= 70 else 'orange' if percentage >= 40 else 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, percentage)
        return 'N/A'
    percentage_display.short_description = 'Percentage'
    
    def passed_display(self, obj):
        # Calculate if passed (assuming 40% is passing)
        percentage = 0
        if hasattr(obj, 'percentage') and obj.percentage is not None:
            percentage = obj.percentage
        elif obj.exam.total_marks > 0:
            percentage = (obj.score / obj.exam.total_marks) * 100
        
        if percentage >= 40:
            return format_html('<span style="color: green; font-weight: bold;">✓ PASS</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ FAIL</span>')
    passed_display.short_description = 'Passed'
    
    def duration_display(self, obj):
        if obj.end_time:
            duration = obj.end_time - obj.start_time
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return "In progress"
    duration_display.short_description = 'Duration'


# ---------------------------
# Answer Admin
# ---------------------------
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question_type', 'short_answer', 'marks_display', 'question_marks', 'is_correct_display')
    list_filter = ('is_correct', 'question__question_type', 'attempt__exam')
    search_fields = ('text_answer', 'attempt__student__username', 'question__question_text')
    readonly_fields = ('answered_at', 'marks_display', 'is_correct_display')
    
    def question_type(self, obj):
        return obj.question.get_question_type_display()
    question_type.short_description = 'Type'
    
    def short_answer(self, obj):
        if obj.selected_choice:
            return f"MCQ: {obj.selected_choice.choice_text[:50]}{'...' if len(obj.selected_choice.choice_text) > 50 else ''}"
        elif obj.text_answer:
            return f"Text: {obj.text_answer[:50]}{'...' if len(obj.text_answer) > 50 else ''}"
        return "No answer"
    short_answer.short_description = 'Answer'
    
    def marks_display(self, obj):
        # Check which field exists in your model
        if hasattr(obj, 'marks_awarded'):
            return obj.marks_awarded
        elif hasattr(obj, 'marks_obtained'):
            return obj.marks_obtained
        return 0
    marks_display.short_description = 'Marks'
    
    def question_marks(self, obj):
        return obj.question.marks
    question_marks.short_description = 'Max Marks'
    
    def is_correct_display(self, obj):
        if obj.is_correct:
            return format_html('<span style="color: green;">✓</span>')
        else:
            return format_html('<span style="color: red;">✗</span>')
    is_correct_display.short_description = 'Correct'


# ---------------------------
# ContactTeacher Admin
# ---------------------------
@admin.register(ContactTeacher)
class ContactTeacherAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'subject', 'short_message', 'sent_at', 'read_status')
    list_filter = ('teacher', 'subject')  # Removed 'is_read' filter
    search_fields = ('student__username', 'teacher__username', 'subject', 'message')
    readonly_fields = ('sent_at', 'read_status')
    
    def short_message(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    short_message.short_description = 'Message'
    
    def read_status(self, obj):
        # Check if is_read field exists
        if hasattr(obj, 'is_read'):
            if obj.is_read:
                return format_html('<span style="color: green;">Read</span>')
            else:
                return format_html('<span style="color: orange;">Unread</span>')
        return "Status not available"
    read_status.short_description = 'Read Status'
