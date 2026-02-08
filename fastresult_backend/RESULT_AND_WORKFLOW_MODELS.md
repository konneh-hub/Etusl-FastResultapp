# Django Result Storage & Workflow Engines - SRMS

**Scope**: Lecturer result entry + Multi-stage approval workflow  
**Status**: Model Design (No Implementation Code)

---

## PART I: RESULT STORAGE MODELS

Result storage handles lecturer entry through to publication and locking.

### **Model 1: StudentCourseEnrollment**

**Purpose**: Links student to course in specific semester  
**Prerequisite**: Must exist before result can be entered

```python
class StudentCourseEnrollment(models.Model):
    """
    Records student enrollment in a course for a semester.
    One enrollment per student per course per semester.
    """
    
    # Foreign Keys
    student_profile = models.ForeignKey(
        'enrollment.StudentProfile',
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    
    course = models.ForeignKey(
        'academic_structure.Course',
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    
    semester = models.ForeignKey(
        'academic_structure.Semester',
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    
    # Status
    ENROLLMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('deferred', 'Deferred'),
        ('unknown', 'Unknown'),
    ]
    status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        default='active'
    )
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrollment_student_course'
        verbose_name = 'Student Course Enrollment'
        verbose_name_plural = 'Student Course Enrollments'
        
        # One enrollment per (student, course, semester)
        constraints = [
            models.UniqueConstraint(
                fields=['student_profile', 'course', 'semester'],
                name='unique_student_course_enrollment'
            )
        ]
        
        indexes = [
            models.Index(fields=['student_profile', 'semester']),
            models.Index(fields=['course', 'semester']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student_profile.matric_number} - {self.course.code} ({self.semester})"
    
    @property
    def university(self):
        return self.course.program.department.faculty.university


# Constraints:
# - Course and Semester must belong to same university
```

---

### **Model 2: AssessmentComponent**

**Purpose**: Define types of assessments (CA, Exam, Practical)  
**Shared**: Per course per semester

```python
class AssessmentComponent(models.Model):
    """
    Defines components that make up a course grade.
    Examples: CA (30%), Exam (60%), Practical (10%)
    """
    
    # Foreign Keys
    course = models.ForeignKey(
        'academic_structure.Course',
        on_delete=models.CASCADE,
        related_name='assessment_components'
    )
    
    semester = models.ForeignKey(
        'academic_structure.Semester',
        on_delete=models.CASCADE,
        related_name='assessment_components'
    )
    
    # Component Type
    COMPONENT_TYPE_CHOICES = [
        ('ca', 'Continuous Assessment'),
        ('exam', 'Final Exam'),
        ('practical', 'Practical/Lab'),
        ('project', 'Project'),
        ('presentation', 'Presentation'),
        ('assignment', 'Assignment'),
    ]
    component_type = models.CharField(
        max_length=20,
        choices=COMPONENT_TYPE_CHOICES
    )
    
    # Scoring
    total_marks = models.IntegerField()
    # Maximum marks for this component (e.g., 30 for CA)
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    # Percentage contribution to final grade (e.g., 0.30 for 30%)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'result_assessment_component'
        verbose_name = 'Assessment Component'
        verbose_name_plural = 'Assessment Components'
        
        # One component type per course per semester
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'semester', 'component_type'],
                name='unique_component_per_course_semester'
            ),
            models.CheckConstraint(
                check=models.Q(weight__gt=0) & models.Q(weight__lte=1.0),
                name='weight_between_0_and_1'
            ),
            models.CheckConstraint(
                check=models.Q(total_marks__gt=0),
                name='total_marks_positive'
            ),
        ]
        
        indexes = [
            models.Index(fields=['course', 'semester']),
        ]
    
    def __str__(self):
        return f"{self.course.code} - {self.component_type} ({self.weight*100}%)"
    
    @property
    def university(self):
        return self.course.program.department.faculty.university


# Validation Rule (application):
# - Sum of all weights for a course ≈ 1.0 (or 100%)
```

---

### **Model 3: ResultRecord**

**Purpose**: Container for all scores for one student in one course

```python
class ResultRecord(models.Model):
    """
    Represents all assessment scores for a student in a course.
    Contains multiple ResultComponentScores (CA, Exam, etc).
    """
    
    # Foreign Keys
    student_enrollment = models.OneToOneField(
        StudentCourseEnrollment,
        on_delete=models.CASCADE,
        related_name='result'
    )
    
    lecturer = models.ForeignKey(
        'university_users.UniversityUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )
    # Lecturer who entered the result
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('released', 'Released'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Scores
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    # Calculated: sum(component_score × component_weight)
    
    grade = models.CharField(
        max_length=2,
        null=True,
        blank=True
    )
    # Letter grade: A, B, C, D, F
    
    # Metadata
    entered_by = models.CharField(max_length=100)  # User email
    entered_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=100)
    
    # Publishing
    released_at = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)  # Published & locked
    
    class Meta:
        db_table = 'result_record'
        verbose_name = 'Result Record'
        verbose_name_plural = 'Result Records'
        
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['student_enrollment']),
            models.Index(fields=['is_locked']),
        ]
    
    def __str__(self):
        return f"{self.student_enrollment} - {self.status}"
    
    @property
    def university(self):
        return self.student_enrollment.course.program.department.faculty.university
    
    @property
    def is_editable(self):
        """Can this result still be edited?"""
        return self.status == 'draft' and not self.is_locked
    
    def can_user_edit(self, user):
        """Check if user can edit this result"""
        if not self.is_editable:
            return False
        return user.university_users.filter(
            university=self.university,
            role__code='lecturer'
        ).exists() and self.lecturer == user.university_users.get(university=self.university)


# Constraints:
# - status='released' → is_locked=True
# - Can only edit if status='draft'
```

---

### **Model 4: ResultComponentScore**

**Purpose**: Stores score for one component (CA score, Exam score, etc)

```python
class ResultComponentScore(models.Model):
    """
    Stores the score for one assessment component.
    One entry per (ResultRecord, AssessmentComponent).
    """
    
    # Foreign Keys
    result_record = models.ForeignKey(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name='component_scores'
    )
    
    component = models.ForeignKey(
        AssessmentComponent,
        on_delete=models.CASCADE,
        related_name='result_scores'
    )
    
    # Score
    score_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    # Actual score (e.g., 25/30 for CA)
    
    # Metadata
    entered_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    lecturer_comments = models.TextField(blank=True)
    # Optional notes from lecturer
    
    class Meta:
        db_table = 'result_component_score'
        verbose_name = 'Result Component Score'
        verbose_name_plural = 'Result Component Scores'
        
        # One score per (result, component)
        constraints = [
            models.UniqueConstraint(
                fields=['result_record', 'component'],
                name='unique_component_score_per_result'
            ),
            models.CheckConstraint(
                check=models.Q(score_obtained__gte=0) | models.Q(score_obtained__isnull=True),
                name='score_obtained_non_negative'
            ),
        ]
        
        indexes = [
            models.Index(fields=['result_record']),
        ]
    
    def __str__(self):
        return f"{self.result_record} - {self.component.component_type}: {self.score_obtained}/{self.component.total_marks}"
    
    def can_edit(self):
        """Can this score still be edited?"""
        return self.result_record.is_editable


# Validation:
# - score_obtained <= component.total_marks
# - Can only add if result_record.status='draft'
```

---

### **Model 5: ResultVersion**

**Purpose**: Version history of result record  
**Used for**: Audit trail and reverting changes

```python
class ResultVersion(models.Model):
    """
    Snapshot of result at each status change.
    Immutable record for audit trail.
    """
    
    # Foreign Keys
    result_record = models.ForeignKey(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    # Version Info
    version_number = models.IntegerField()
    # 1, 2, 3, ... sequential
    
    # Snapshot (JSON of all component scores + metadata)
    snapshot_data = models.JSONField()
    # {
    #   "status": "submitted",
    #   "total_score": 75.5,
    #   "grade": "B",
    #   "components": {
    #     "ca": {"score": 28, "out_of": 30},
    #     "exam": {"score": 47.5, "out_of": 70}
    #   },
    #   "timestamp": "2024-01-15T10:30:00Z"
    # }
    
    # Change tracking
    changed_by = models.CharField(max_length=100)  # User email
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'result_version'
        verbose_name = 'Result Version'
        verbose_name_plural = 'Result Versions'
        
        # Unique version per result
        constraints = [
            models.UniqueConstraint(
                fields=['result_record', 'version_number'],
                name='unique_version_per_result'
            )
        ]
        
        ordering = ['result_record', 'version_number']
        indexes = [
            models.Index(fields=['result_record']),
        ]
    
    def __str__(self):
        return f"{self.result_record} v{self.version_number}"


# Creation Logic:
# - Created automatically when status changes
# - Created when any component score changes
# - Immutable: no updates, only creates
```

---

## PART II: RESULT APPROVAL WORKFLOW MODELS

Multi-stage approval orchestration: Lecturer → HOD → Exam Officer → Admin

### **Model 6: ResultApprovalInstance**

**Purpose**: Tracks result through approval workflow stages  

```python
class ResultApprovalInstance(models.Model):
    """
    Represents result in workflow - tracks current stage, transitions.
    One approval instance per result.
    """
    
    # Foreign Keys
    result_record = models.OneToOneField(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name='approval_instance'
    )
    
    workflow_definition = models.ForeignKey(
        'result_workflow.WorkflowDefinition',
        on_delete=models.PROTECT,
        related_name='approval_instances'
    )
    
    # Current Stage
    # Stages: 1=draft, 2=submitted→HOD, 3=submitted→ExamOfficer, 4=ready_release, 5=released
    current_stage_number = models.IntegerField(default=1)
    
    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'result_approval_instance'
        verbose_name = 'Result Approval Instance'
        verbose_name_plural = 'Result Approval Instances'
        
        indexes = [
            models.Index(fields=['current_stage_number']),
            models.Index(fields=['result_record']),
        ]
    
    def __str__(self):
        return f"{self.result_record} - Stage {self.current_stage_number}"
    
    @property
    def current_stage(self):
        """Get current workflow stage"""
        return self.workflow_definition.stages.get(
            stage_number=self.current_stage_number
        )
    
    def get_next_stage(self):
        """Get next stage in workflow"""
        return self.workflow_definition.stages.filter(
            stage_number__gt=self.current_stage_number
        ).order_by('stage_number').first()
    
    def advance_to_next_stage(self):
        """Move to next stage"""
        next_stage = self.get_next_stage()
        if next_stage:
            self.current_stage_number = next_stage.stage_number
            self.save()
            return True
        return False
    
    def revert_to_draft(self):
        """Send back to draft for correction"""
        self.current_stage_number = 1
        self.save()
```

---

### **Model 7: WorkflowStage** (Reference Data)

**Purpose**: Define workflow stages (created once at setup)  

```python
class WorkflowStage(models.Model):
    """
    Defines a stage in the approval workflow.
    Seeded at initialization - immutable in production.
    """
    
    # Foreign Keys
    workflow_definition = models.ForeignKey(
        'result_workflow.WorkflowDefinition',
        on_delete=models.CASCADE,
        related_name='stages'
    )
    
    # Sequence
    stage_number = models.IntegerField()
    # 1, 2, 3, 4, 5, ...
    
    stage_name = models.CharField(max_length=100)
    # "Lecturer Entry", "HOD Review", "Exam Officer Verification", "Release"
    
    # Role Required
    ROLE_CHOICES = [
        ('lecturer', 'Lecturer'),
        ('hod', 'Head of Department'),
        ('dean', 'Dean'),
        ('exam_officer', 'Examination Officer'),
        ('university_admin', 'University Administrator'),
    ]
    required_role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES
    )
    
    # Scope
    SCOPE_CHOICES = [
        ('self', 'Self (own entry only)'),
        ('course', 'Course level'),
        ('department', 'Department level'),
        ('faculty', 'Faculty level'),
        ('university', 'University level'),
    ]
    scope = models.CharField(
        max_length=50,
        choices=SCOPE_CHOICES
    )
    
    # Permissions
    can_approve = models.BooleanField(default=True)
    can_reject = models.BooleanField(default=True)
    can_request_correction = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'workflow_stage'
        verbose_name = 'Workflow Stage'
        verbose_name_plural = 'Workflow Stages'
        
        unique_together = ('workflow_definition', 'stage_number')
        ordering = ['workflow_definition', 'stage_number']
    
    def __str__(self):
        return f"{self.stage_name} (Stage {self.stage_number})"


# Seeded Stages for "Standard" Workflow:
STAGES = [
    (1, "Lecturer Entry", "lecturer", "self", True, True, False),
    (2, "HOD Review", "hod", "department", True, True, True),
    (3, "Exam Officer Verification", "exam_officer", "university", True, True, False),
    (4, "Release", "university_admin", "university", True, False, False),
]
```

---

### **Model 8: ApprovalActionLog**

**Purpose**: Audit trail of all approvals/rejections/corrections  

```python
class ApprovalActionLog(models.Model):
    """
    Records every approval/rejection/correction action.
    Immutable audit trail.
    """
    
    # Foreign Keys
    approval_instance = models.ForeignKey(
        ResultApprovalInstance,
        on_delete=models.CASCADE,
        related_name='action_logs'
    )
    
    stage = models.ForeignKey(
        WorkflowStage,
        on_delete=models.PROTECT,
        related_name='action_logs'
    )
    
    # Action
    ACTION_CHOICES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('correction_requested', 'Correction Requested'),
        ('resubmitted', 'Resubmitted'),
    ]
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    # Actor
    actor_email = models.CharField(max_length=100)
    actor_role = models.CharField(max_length=50)
    
    # Comments
    comments = models.TextField(blank=True)
    
    # Timestamp
    action_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'approval_action_log'
        verbose_name = 'Approval Action Log'
        verbose_name_plural = 'Approval Action Logs'
        
        ordering = ['action_at']
        indexes = [
            models.Index(fields=['approval_instance']),
            models.Index(fields=['action_at']),
        ]
    
    def __str__(self):
        return f"{self.approval_instance} - {self.action} by {self.actor_email}"


# Constraints:
# - Immutable after creation (no updates)
```

---

### **Model 9: CorrectionRequest**

**Purpose**: Record requests to fix/edit result  

```python
class CorrectionRequest(models.Model):
    """
    Records when a result is sent back for correction.
    Allows HOD/Exam Officer to annotate issues.
    """
    
    # Foreign Keys
    result_record = models.ForeignKey(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name='correction_requests'
    )
    
    # Request Info
    requested_by_email = models.CharField(max_length=100)
    requested_by_role = models.CharField(max_length=50)
    
    reason = models.TextField()
    # Why is correction being requested?
    # "Missing exam score", "Grade calculation error", etc
    
    specific_components = models.JSONField(default=list)
    # ["exam", "practical"] - which components need fixing
    
    # Timeline
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'correction_request'
        verbose_name = 'Correction Request'
        verbose_name_plural = 'Correction Requests'
        
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['result_record']),
        ]
    
    def __str__(self):
        return f"Correction for {self.result_record} - {self.reason[:50]}"
    
    @property
    def is_resolved(self):
        return self.resolved_at is not None


# Constraints:
# - Can't create new request if status != 'rejected' or 'under_review'
```

---

### **Model 10: WorkflowDefinition** (Reference Data)

**Purpose**: Define workflow templates (usually just 1 standard workflow)  

```python
class WorkflowDefinition(models.Model):
    """
    Template defining a complete approval workflow.
    Usually one "Standard" workflow per university.
    Can create alternate workflows if needed.
    """
    
    # Foreign Keys
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='workflow_definitions'
    )
    
    # Identity
    name = models.CharField(max_length=100)
    # "Standard Workflow", "Alternative Fast-Track"
    
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_definition'
        verbose_name = 'Workflow Definition'
        verbose_name_plural = 'Workflow Definitions'
    
    def __str__(self):
        return f"{self.name} ({self.university.name})"
    
    def get_stages(self):
        """Get all stages in order"""
        return self.stages.all().order_by('stage_number')
    
    def get_stage(self, stage_number):
        """Get specific stage"""
        return self.stages.get(stage_number=stage_number)


# Standard Workflow (seeded):
# - Lecturer entry (Stage 1)
# - HOD review (Stage 2)
# - Exam Officer verification (Stage 3)
# - Admin release (Stage 4)
```

---

## PART III: RELATIONSHIPS & FLOW

```
StudentCourseEnrollment (1)
    ├─ Result Record (1)
    │   ├─ ResultComponentScore (many)
    │   │   └─ AssessmentComponent
    │   ├─ ResultVersion (many - historical)
    │   └─ ResultApprovalInstance (1)
    │       └─ ApprovalActionLog (many)
    │       └─ CorrectionRequest (many)
    │
    └─ AssessmentComponent (per course)
```

---

## PART IV: STATUS WORKFLOW

```
┌──────────┐
│  Draft   │  (Lecturer entering scores)
└────┬─────┘
     │ Lecturer Submit
     ↓
┌──────────────┐
│  Submitted   │  (Awaiting HOD review)
└────┬─────────┘
     │ HOD Approve → OR ← Return for Correction (back to Draft)
     ↓
┌──────────────┐
│ Under Review │  (Exam Officer verification)
└────┬─────────┘
     │ Exam Officer Approve → OR ← Reject (back to Draft)
     ↓
┌──────────────┐
│  Approved    │  (Ready for release)
└────┬─────────┘
     │ Admin Release
     ↓
┌──────────────┐
│  Released    │  (Published to students, locked)
└──────────────┘
```

---

## PART V: VALIDATION RULES

```python
# Can only add/edit component scores if:
- result_record.status == 'draft'
- result_record.is_locked == False

# Can only transition if:
- All required components have scores
- Total score calculated and valid (0-100)
- Grade assigned based on total score

# Can only approve if:
- Current stage actor has role
- Result meets stage requirements

# Can only reject if:
- Stage allows rejection
- Reason provided

# Version created on:
- Every status change
- Every score modification
- Every approval/rejection
```

---

## SUMMARY TABLE

| Model | Purpose | Foreign Keys | Constraints |
|-------|---------|--------------|-------------|
| StudentCourseEnrollment | Student in course per semester | student, course, semester | unique (student, course, semester) |
| AssessmentComponent | Component types per course | course, semester | unique (course, semester, type) |
| ResultRecord | Container for all scores | enrollment, lecturer | unique enrollment, editable only if draft |
| ResultComponentScore | Score for one component | result, component | unique (result, component), ≤ total_marks |
| ResultVersion | Historical snapshot | result | immutable |
| ResultApprovalInstance | Result in workflow | result, workflow | one per result |
| WorkflowStage | Workflow stage definition | workflow | unique (workflow, stage_number) |
| ApprovalActionLog | Action audit trail | approval, stage | immutable |
| CorrectionRequest | Correction needed marker | result | resolved_at optional |
| WorkflowDefinition | Workflow template | university | one active per university |

---

**Status**: Result & Workflow Models Complete  
**Next Steps**: GPA Engine, Transcript Generator, Audit System  
**Last Updated**: 2026-02-07
