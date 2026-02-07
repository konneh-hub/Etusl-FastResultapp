from django.db import models


class Exam(models.Model):
    """Exam model"""
    EXAM_TYPES = [
        ('mid_term', 'Mid Term'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('practical', 'Practical'),
    ]
    
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    date = models.DateTimeField()
    duration_minutes = models.IntegerField()
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.get_exam_type_display()}"


class ExamPeriod(models.Model):
    """Exam period model"""
    semester = models.ForeignKey('universities.Semester', on_delete=models.CASCADE, related_name='exam_periods')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.semester} - {self.start_date} to {self.end_date}"


class ExamCalendar(models.Model):
    """Exam calendar/timetable"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='calendar_entries')
    venue = models.CharField(max_length=255)
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.course.name} - {self.venue}"


class ExamTimetable(models.Model):
    """Exam timetable entries"""
    exam_period = models.ForeignKey(ExamPeriod, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.course.code} - {self.date}"
