from rest_framework import serializers
from reports.models import Report


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True, allow_null=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'title', 'report_type', 'report_type_display', 'description', 'generated_by', 'generated_by_name', 'generated_at', 'updated_at', 'file', 'filters']
        read_only_fields = ['id', 'generated_at', 'updated_at']
