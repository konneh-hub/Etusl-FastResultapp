from rest_framework import serializers
from exams.models import Exam, ExamPeriod, ExamCalendar, ExamTimetable


class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'course', 'course_name', 'course_code', 'exam_type', 'exam_type_display', 'date', 'duration_minutes', 'total_marks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    calendar_entries = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'course', 'course_name', 'course_code', 'exam_type', 'exam_type_display', 'date', 'duration_minutes', 'total_marks', 'calendar_entries', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_calendar_entries(self, obj):
        entries = obj.calendar_entries.all()
        return ExamCalendarSerializer(entries, many=True).data


class ExamPeriodSerializer(serializers.ModelSerializer):
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamPeriod
        fields = ['id', 'semester', 'semester_display', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"


class ExamCalendarSerializer(serializers.ModelSerializer):
    exam_course = serializers.CharField(source='exam.course.code', read_only=True)
    exam_type = serializers.CharField(source='exam.get_exam_type_display', read_only=True)
    
    class Meta:
        model = ExamCalendar
        fields = ['id', 'exam', 'exam_course', 'exam_type', 'venue', 'capacity', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExamTimetableSerializer(serializers.ModelSerializer):
    exam_period_display = serializers.SerializerMethodField()
    exam_course = serializers.CharField(source='exam.course.code', read_only=True)
    exam_type = serializers.CharField(source='exam.get_exam_type_display', read_only=True)
    
    class Meta:
        model = ExamTimetable
        fields = ['id', 'exam_period', 'exam_period_display', 'exam', 'exam_course', 'exam_type', 'date', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_exam_period_display(self, obj):
        return f"{obj.exam_period.semester.academic_year.year} - Semester {obj.exam_period.semester.number}"
