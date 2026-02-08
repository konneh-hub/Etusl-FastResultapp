from rest_framework import serializers
from approvals.models import ResultSubmission, ApprovalStage, ApprovalAction, ApprovalHistory, CorrectionRequest


class ApprovalActionSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    
    class Meta:
        model = ApprovalAction
        fields = ['id', 'stage', 'approver', 'approver_name', 'action', 'comments', 'acted_at']
        read_only_fields = ['id', 'acted_at']


class ApprovalStageSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    actions = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalStage
        fields = ['id', 'submission', 'stage_number', 'approver_role', 'status', 'assigned_to', 'assigned_to_name', 'actions']
        read_only_fields = ['id']
    
    def get_actions(self, obj):
        actions = obj.actions.all()
        return ApprovalActionSerializer(actions, many=True).data


class ApprovalHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = ApprovalHistory
        fields = ['id', 'submission', 'action_type', 'performed_by', 'performed_by_name', 'timestamp', 'details']
        read_only_fields = ['id', 'timestamp']


class CorrectionRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    
    class Meta:
        model = CorrectionRequest
        fields = ['id', 'submission', 'requested_by', 'requested_by_name', 'issue_description', 'requested_at', 'resolved_at']
        read_only_fields = ['id', 'requested_at']


class ResultSubmissionSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    result_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultSubmission
        fields = ['id', 'result', 'result_info', 'submitted_by', 'submitted_by_name', 'submitted_at', 'status']
        read_only_fields = ['id', 'submitted_at']
    
    def get_result_info(self, obj):
        return {
            'student_matric': obj.result.student.matric_number,
            'course_code': obj.result.course.code,
            'course_name': obj.result.course.name,
        }


class ResultSubmissionDetailSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    result_info = serializers.SerializerMethodField()
    stages = serializers.SerializerMethodField()
    histories = serializers.SerializerMethodField()
    corrections = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultSubmission
        fields = ['id', 'result', 'result_info', 'submitted_by', 'submitted_by_name', 'submitted_at', 'status', 'stages', 'histories', 'corrections']
        read_only_fields = ['id', 'submitted_at']
    
    def get_result_info(self, obj):
        return {
            'student_matric': obj.result.student.matric_number,
            'student_name': obj.result.student.user.get_full_name(),
            'course_code': obj.result.course.code,
            'course_name': obj.result.course.name,
        }
    
    def get_stages(self, obj):
        stages = obj.stages.all()
        return ApprovalStageSerializer(stages, many=True).data
    
    def get_histories(self, obj):
        histories = obj.histories.all()
        return ApprovalHistorySerializer(histories, many=True).data
    
    def get_corrections(self, obj):
        corrections = obj.corrections.all()
        return CorrectionRequestSerializer(corrections, many=True).data
