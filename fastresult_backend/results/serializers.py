from rest_framework import serializers
from results.models import Result, ResultComponent, Grade, GPARecord, CGPARecord, Transcript, ResultLock, ResultRelease


class ResultComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultComponent
        fields = ['id', 'result', 'component_name', 'marks_obtained', 'marks_total', 'weight']


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'result', 'total_score', 'letter_grade', 'grade_point', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResultSerializer(serializers.ModelSerializer):
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = ['id', 'student', 'student_matric', 'course', 'course_name', 'course_code', 'semester', 'semester_display', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"


class ResultDetailSerializer(serializers.ModelSerializer):
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_display = serializers.SerializerMethodField()
    components = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = ['id', 'student', 'student_matric', 'student_name', 'course', 'course_name', 'course_code', 'semester', 'semester_display', 'status', 'components', 'grade', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"
    
    def get_components(self, obj):
        components = obj.components.all()
        return ResultComponentSerializer(components, many=True).data
    
    def get_grade(self, obj):
        if hasattr(obj, 'grade'):
            return GradeSerializer(obj.grade).data
        return None


class GPARecordSerializer(serializers.ModelSerializer):
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GPARecord
        fields = ['id', 'student', 'student_matric', 'semester', 'semester_display', 'gpa', 'total_credits', 'quality_points', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"


class CGPARecordSerializer(serializers.ModelSerializer):
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    
    class Meta:
        model = CGPARecord
        fields = ['id', 'student', 'student_matric', 'cgpa', 'total_credits', 'quality_points', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class TranscriptSerializer(serializers.ModelSerializer):
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = Transcript
        fields = ['id', 'student', 'student_matric', 'student_name', 'generated_date', 'file']
        read_only_fields = ['id', 'generated_date']


class ResultLockSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    locked_by_name = serializers.CharField(source='locked_by.get_full_name', read_only=True)
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultLock
        fields = ['id', 'semester', 'semester_display', 'course', 'course_code', 'locked_by', 'locked_by_name', 'locked_at']
        read_only_fields = ['id', 'locked_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"


class ResultReleaseSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True, allow_null=True)
    released_by_name = serializers.CharField(source='released_by.get_full_name', read_only=True)
    semester_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultRelease
        fields = ['id', 'semester', 'semester_display', 'course', 'course_code', 'released_at', 'released_by', 'released_by_name']
        read_only_fields = ['id', 'released_at']
    
    def get_semester_display(self, obj):
        return f"{obj.semester.academic_year.year} - Semester {obj.semester.number}"
