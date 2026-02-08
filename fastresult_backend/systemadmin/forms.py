from django import forms
from django.core.exceptions import ValidationError
from .models import (
    UniversityRegistry, RoleTemplate, PermissionTemplate,
    AcademicTemplate, WorkflowTemplate, ResultEngineTemplate,
    PlatformSetting, FeatureFlag
)


class UniversityRegistryForm(forms.ModelForm):
    class Meta:
        model = UniversityRegistry
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        code = cleaned_data.get('code')

        if not name or not code:
            raise ValidationError("Name and code are required.")

        return cleaned_data


class RoleTemplateForm(forms.ModelForm):
    class Meta:
        model = RoleTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
            'permissions': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        hierarchy_level = cleaned_data.get('hierarchy_level')

        if hierarchy_level is not None and (hierarchy_level < 0 or hierarchy_level > 10):
            raise ValidationError("Hierarchy level must be between 0 and 10.")

        return cleaned_data


class PermissionTemplateForm(forms.ModelForm):
    class Meta:
        model = PermissionTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
            'roles': forms.CheckboxSelectMultiple(),
        }

    def clean_codename(self):
        codename = self.cleaned_data.get('codename')
        if codename:
            codename = codename.lower().replace(' ', '_')
        return codename


class AcademicTemplateForm(forms.ModelForm):
    class Meta:
        model = AcademicTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'configuration': forms.Textarea(attrs={'rows': 6}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_configuration(self):
        import json
        config = self.cleaned_data.get('configuration')
        if config:
            try:
                json.loads(config)
            except json.JSONDecodeError:
                raise ValidationError("Configuration must be valid JSON.")
        return config


class WorkflowTemplateForm(forms.ModelForm):
    class Meta:
        model = WorkflowTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'stages': forms.Textarea(attrs={'rows': 6}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_stages(self):
        import json
        stages = self.cleaned_data.get('stages')
        if stages:
            try:
                json.loads(stages)
            except json.JSONDecodeError:
                raise ValidationError("Stages must be valid JSON.")
        return stages

    def clean_timeout_days(self):
        timeout = self.cleaned_data.get('timeout_days')
        if timeout is not None and timeout < 1:
            raise ValidationError("Timeout days must be at least 1.")
        return timeout


class ResultEngineTemplateForm(forms.ModelForm):
    class Meta:
        model = ResultEngineTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'formula': forms.Textarea(attrs={'rows': 6}),
            'input_parameters': forms.Textarea(attrs={'rows': 4}),
            'output_parameters': forms.Textarea(attrs={'rows': 4}),
            'metadata': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_formula(self):
        formula = self.cleaned_data.get('formula')
        if formula:
            try:
                compile(formula, '<string>', 'eval')
            except SyntaxError as e:
                raise ValidationError(f"Invalid formula: {str(e)}")
        return formula

    def clean_min_passing_score(self):
        score = self.cleaned_data.get('min_passing_score')
        if score is not None and (score < 0 or score > 100):
            raise ValidationError("Min passing score must be between 0 and 100.")
        return score


class PlatformSettingForm(forms.ModelForm):
    class Meta:
        model = PlatformSetting
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'value': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        setting_type = cleaned_data.get('setting_type')
        value = cleaned_data.get('value')

        if setting_type and value:
            if setting_type == 'integer':
                try:
                    int(value)
                except ValueError:
                    raise ValidationError("Value must be a valid integer.")
            elif setting_type == 'decimal':
                try:
                    float(value)
                except ValueError:
                    raise ValidationError("Value must be a valid decimal number.")
            elif setting_type == 'boolean':
                if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                    raise ValidationError("Value must be 'true' or 'false'.")
            elif setting_type == 'json':
                import json
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    raise ValidationError("Value must be valid JSON.")

        return cleaned_data


class FeatureFlagForm(forms.ModelForm):
    class Meta:
        model = FeatureFlag
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'target_users': forms.Textarea(attrs={'rows': 4}),
            'config': forms.Textarea(attrs={'rows': 4}),
            'target_roles': forms.CheckboxSelectMultiple(),
        }

    def clean_rollout_percentage(self):
        percentage = self.cleaned_data.get('rollout_percentage')
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise ValidationError("Rollout percentage must be between 0 and 100.")
        return percentage

    def clean_target_users(self):
        import json
        users = self.cleaned_data.get('target_users')
        if users:
            try:
                json.loads(users)
            except json.JSONDecodeError:
                raise ValidationError("Target users must be valid JSON.")
        return users
