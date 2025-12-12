from django.db import models
from django.contrib.auth.models import User

# ---------------- USER PROFILE ----------------
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


# ---------------- SUBJECT ----------------
class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ---------------- EXAM ----------------
class Exam(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

    def question_count(self):
        return self.questions.count()


# ---------------- QUESTION ----------------
from django.db import models

class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short', 'Short Answer'),
    )
    
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    question_text = models.TextField()
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    question_image = models.ImageField(upload_to='question_images/', blank=True, null=True)

    # New fields
    options = models.JSONField(blank=True, null=True)       # e.g., ["A", "B", "C", "D"]
    correct_answer = models.TextField(blank=True, null=True)  # store the correct answer

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
    
    class Meta:
        ordering = ['order']



# ---------------- CHOICE ----------------
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.choice_text
    


class ExamAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    status = models.CharField(max_length=20, default="in_progress")
    submitted_at = models.DateTimeField(null=True, blank=True)

    @property
    def percentage(self):
        """Return score as percentage of total marks"""
        total_marks = sum(q.marks for q in self.exam.questions.all())
        if total_marks == 0:
            return 0
        return round((self.score / total_marks) * 100, 2)

    @property
    def marks_obtained(self):
        """Alias for score to maintain compatibility"""
        return self.score

    @property
    def total_marks(self):
        """Total marks of all questions in the exam"""
        return sum(q.marks for q in self.exam.questions.all())

    @property
    def passed(self):
        """Check if the attempt is passed based on exam passing_marks"""
        if hasattr(self.exam, 'passing_marks'):
            return self.score >= self.exam.passing_marks
        return False






# ---------------- EXAM ATTEMPT ----------------
# class ExamAttempt(models.Model):
#     STATUS_CHOICES = (
#         ('started', 'Started'),
#         ('in_progress', 'In Progress'),
#         ('submitted', 'Submitted'),
#     )
    
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
#     student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts')
#     start_time = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
#     score = models.FloatField(default=0)
#     percentage = models.FloatField(default=0)
#     passed = models.BooleanField(default=False)
    
#     def __str__(self):
#         return f"{self.student.username} - {self.exam.title}"
    
#     class Meta:
#         ordering = ['-start_time']
#         unique_together = ('exam', 'student')


# ---------------- ANSWER ----------------
# class Answer(models.Model):
#     attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
#     answer_text = models.TextField(null=True, blank=True)
#     is_correct = models.BooleanField(default=False)
#     marks_obtained = models.FloatField(default=0)
#     answered_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.attempt.student.username} - Q{self.question.order}"
    
#     class Meta:
#         ordering = ['question__order']



from django.db import models
from django.contrib.auth.models import User

class ContactTeacher(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_messages")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_messages")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.teacher.username}"


# exams/models.py
class TeacherMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.CASCADE, 
        related_name='child_messages'  # <-- changed to avoid clash
    )

    def __str__(self):
        return f"Message from {self.sender.username} to {self.teacher.username}"

    
class TeacherReply(models.Model):
    message = models.ForeignKey(
        TeacherMessage, 
        on_delete=models.CASCADE, 
        related_name='teacher_replies'  # <-- changed to avoid clash
    )
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.teacher.username} to {self.message.sender.username}"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)


# exams/models.py
class ContactTeacher(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_messages_sent')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_messages_received')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Add this line
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.student} to {self.teacher}: {self.subject}"

class Answer(models.Model):
    attempt = models.ForeignKey('ExamAttempt', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    selected_choice = models.ForeignKey('Choice', on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    marks_obtained = models.FloatField(default=0)  # Make sure this exists
    # OR change to marks_awarded if that's what you want:
    # marks_awarded = models.FloatField(default=0)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question__order']
    
    def __str__(self):
        return f"Answer for {self.question}"
    

class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)  # stores choice ID or text
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'exam', 'question')



# from django.db import models
# from django.contrib.auth.models import User

# class StudentExamAttempt(models.Model):
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
#     marks_obtained = models.FloatField(default=0)
#     percentage = models.FloatField(default=0)
#     submitted_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('student', 'exam')

#     def __str__(self):
#         return f"{self.student.username} - {self.exam.title}"

