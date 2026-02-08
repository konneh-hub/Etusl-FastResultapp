# Transcript Generator Module - SRMS

**Scope**: Official academic transcript generation + versioning  
**Status**: Design Specification (No Implementation Code)

---

## PART I: TRANSCRIPT MODELS

### **Model 1: TranscriptRecord**

**Purpose**: Master record for a student's transcript  
**Generated**: On demand from released results + GPA data

```python
class TranscriptRecord(models.Model):
    """
    Represents a student's academic transcript.
    Immutable snapshot once generated.
    """
    
    # Foreign Keys
    student_profile = models.ForeignKey(
        'enrollment.StudentProfile',
        on_delete=models.CASCADE,
        related_name='transcripts'
    )
    
    program = models.ForeignKey(
        'academic_structure.Program',
        on_delete=models.PROTECT,
        related_name='transcripts'
    )
    
    # Transcript Status
    TRANSCRIPT_STATUS_CHOICES = [
        ('draft', 'Draft - For Review'),
        ('issued', 'Issued - Official'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=TRANSCRIPT_STATUS_CHOICES,
        default='draft'
    )
    
    # Content (JSON array of semester results)
    transcript_data = models.JSONField()
    # {
    #   "student": {
    #     "id": 123,
    #     "name": "John Doe",
    #     "matric_number": "STU-2020-001",
    #     "program": "B.Sc. Computer Science"
    #   },
    #   "semesters": [
    #     {
    #       "semester": "Semester 1",
    #       "academic_year": "2020/2021",
    #       "courses": [
    #         {
    #           "code": "CS101",
    #           "name": "Introduction to Programming",
    #           "credit_units": 3,
    #           "score": 78.5,
    #           "grade": "B",
    #           "grade_point": 3.0,
    #           "status": "PASSED"
    #         }
    #       ],
    #       "semester_gpa": 3.25,
    #       "credits_earned": 12,
    #       "credits_attempted": 15
    #     }
    #   ],
    #   "summary": {
    #     "total_credits_attempted": 120,
    #     "total_credits_earned": 115,
    #     "cgpa": 3.45,
    #     "classification": "1st Class",
    #     "academic_standing": "Good Standing"
    #   }
    # }
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=100)  # User email
    
    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.CharField(max_length=100, null=True, blank=True)  # Admin email
    
    # Authenticity
    signature_token = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    # Hash for verification (prevents tampering)
    
    is_locked = models.BooleanField(default=False)
    # Once locked, cannot be modified
    
    class Meta:
        db_table = 'transcript_record'
        verbose_name = 'Transcript Record'
        verbose_name_plural = 'Transcript Records'
        
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['student_profile']),
            models.Index(fields=['status']),
            models.Index(fields=['signature_token']),
        ]
    
    def __str__(self):
        return f"Transcript: {self.student_profile} - {self.status}"
    
    def can_issue(self):
        """Can this transcript be issued?"""
        student = self.student_profile
        cumulative = student.cumulative_gpa
        
        # Requirements
        return (
            self.status == 'draft' and
            not self.is_locked and
            cumulative is not None and
            cumulative.total_credit_units_earned >= self.program.total_credit_units
            # And other validation rules
        )
    
    def issue(self, issuing_user):
        """Issue as official transcript"""
        if not self.can_issue():
            raise ValidationError("Transcript not ready for issuance")
        
        self.status = 'issued'
        self.issued_at = timezone.now()
        self.issued_by = issuing_user.email
        self.is_locked = True
        self.signature_token = self._generate_signature()
        self.save()
    
    def _generate_signature(self):
        """Generate cryptographic signature for verification"""
        # Hash of: student_id + data + issued_date
        signature_string = f"{self.student_profile.id}{self.transcript_data}{self.issued_at}"
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    @property
    def is_issued(self):
        return self.status == 'issued' and self.is_locked


# Constraints:
# - status='issued' → is_locked=True
# - signature_token unique (if not None)
```

---

### **Model 2: TranscriptSnapshot**

**Purpose**: Historical versions of transcript  
**Use Case**: Track corrections/updates

```python
class TranscriptSnapshot(models.Model):
    """
    Immutable snapshot of transcript at point in time.
    Created when transcript is issued.
    Allows tracking of corrections/updates.
    """
    
    # Foreign Keys
    transcript_record = models.ForeignKey(
        TranscriptRecord,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    
    # Version
    version_number = models.IntegerField()
    # 1, 2, 3, ... sequential
    
    # Status
    SNAPSHOT_STATUS_CHOICES = [
        ('current', 'Current'),
        ('superseded', 'Superseded'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=20,
        choices=SNAPSHOT_STATUS_CHOICES,
        default='current'
    )
    
    # Snapshot (complete copy of transcript_data at this time)
    snapshot_data = models.JSONField()
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(
        max_length=200,
        blank=True
    )
    # "Initial issuance", "Correction for CS101", etc
    
    # Authenticity
    issued_at = models.DateTimeField()
    issued_by = models.CharField(max_length=100)
    signature_token = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'transcript_snapshot'
        verbose_name = 'Transcript Snapshot'
        verbose_name_plural = 'Transcript Snapshots'
        
        unique_together = ('transcript_record', 'version_number')
        ordering = ['transcript_record', 'version_number']
        indexes = [
            models.Index(fields=['transcript_record']),
        ]
    
    def __str__(self):
        return f"{self.transcript_record} v{self.version_number}"


# Constraints:
# - Immutable after creation
# - status='current' only on latest snapshot
```

---

### **Model 3: TranscriptComponent** (Optional - for performance)

**Purpose**: Denormalized transcript components for fast retrieval  
**Use Case**: Quick preview without parsing JSON

```python
class TranscriptComponent(models.Model):
    """
    Denormalized components of transcript for indexing/search.
    Populated when transcript generated.
    """
    
    # Foreign Keys
    transcript_record = models.ForeignKey(
        TranscriptRecord,
        on_delete=models.CASCADE,
        related_name='components'
    )
    
    # Components
    total_credits_attempted = models.DecimalField(max_digits=6, decimal_places=2)
    total_credits_earned = models.DecimalField(max_digits=6, decimal_places=2)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    classification = models.CharField(max_length=50)
    academic_standing = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'transcript_component'
        unique_together = ('transcript_record',)
    
    def __str__(self):
        return f"Components: {self.transcript_record}"


# Utility for quick stats without JSON parsing
```

---

## PART II: TRANSCRIPT GENERATION SERVICE

### **Service: TranscriptGenerationService**

**Purpose**: Generate transcripts from results + GPA data  

```python
class TranscriptGenerationService:
    """
    Generate official academic transcripts.
    Pulls from:
    - Released results (ResultRecord)
    - Semester GPAs (SemesterGPA)
    - Cumulative GPA (CumulativeGPA)
    - Academic structure (Program, etc)
    """
    
    def __init__(self, university):
        self.university = university
    
    # ────────────────────────────────────
    # MAIN GENERATION
    # ────────────────────────────────────
    
    def generate_transcript(self, student_profile, is_official=False):
        """
        Generate a transcript for a student.
        
        Input:
        - student_profile: Student to generate for
        - is_official: Mark as official/issued?
        
        Returns:
        - TranscriptRecord (saved to DB)
        """
        # 1. Validate prerequisites
        if not self._validate_transcript_prerequisites(student_profile):
            raise ValidationError("Student not eligible for transcript")
        
        # 2. Collect semester data
        semester_data = self._collect_semester_data(student_profile)
        
        if not semester_data:
            raise ValidationError("No completed semesters found")
        
        # 3. Build transcript JSON
        transcript_json = self._build_transcript_json(student_profile, semester_data)
        
        # 4. Save or update
        transcript = TranscriptRecord.objects.create(
            student_profile=student_profile,
            program=student_profile.program,
            status='draft' if not is_official else 'issued',
            transcript_data=transcript_json,
            generated_by=self.university.name,
            issued_at=timezone.now() if is_official else None,
            is_locked=is_official,
        )
        
        # 5. Create snapshot if official
        if is_official:
            self._create_snapshot(transcript, "Initial issuance")
        
        return transcript
    
    # ────────────────────────────────────
    # DATA COLLECTION
    # ────────────────────────────────────
    
    def _validate_transcript_prerequisites(self, student_profile):
        """
        Check if student can have transcript generated.
        Requirements:
        - At least 1 semester completed
        - Has cumulative GPA
        """
        has_completed_semesters = student_profile.semester_gpas.exists()
        has_cumulative = student_profile.cumulative_gpa is not None
        
        return has_completed_semesters and has_cumulative
    
    def _collect_semester_data(self, student_profile):
        """
        Collect all semester data for transcript.
        Gets all released results grouped by semester.
        """
        semester_data = []
        
        # Get all semesters with results
        semesters = Semester.objects.filter(
            academic_year__university=self.university,
            student_gpas__student_profile=student_profile
        ).distinct().order_by(
            'academic_year__year',
            'number'
        )
        
        for semester in semesters:
            sem_gpa = student_profile.semester_gpas.get(semester=semester)
            
            # Get courses for this semester
            courses = self._collect_semester_courses(student_profile, semester)
            
            semester_data.append({
                'semester': semester,
                'sem_gpa': sem_gpa,
                'courses': courses,
            })
        
        return semester_data
    
    def _collect_semester_courses(self, student_profile, semester):
        """
        Get all released result records for a semester.
        """
        results = ResultRecord.objects.filter(
            student_enrollment__student_profile=student_profile,
            student_enrollment__semester=semester,
            status='released'
        ).select_related(
            'student_enrollment__course'
        )
        
        courses = []
        for result in results:
            course_data = {
                'code': result.student_enrollment.course.code,
                'name': result.student_enrollment.course.name,
                'credit_units': result.student_enrollment.course.credit_units,
                'score': result.total_score,
                'grade': result.grade,
                'grade_point': self._get_grade_point(result.grade),
                'status': 'PASSED' if result.grade != 'F' else 'FAILED',
                'components': self._get_component_breakdown(result),
            }
            courses.append(course_data)
        
        return courses
    
    def _get_component_breakdown(self, result_record):
        """
        Get breakdown of component scores for result.
        E.g., CA: 28/30, Exam: 47.5/70
        """
        breakdown = {}
        
        for comp_score in result_record.component_scores.all():
            breakdown[comp_score.component.component_type] = {
                'obtained': comp_score.score_obtained,
                'total': comp_score.component.total_marks,
                'percentage': (
                    (comp_score.score_obtained / comp_score.component.total_marks * 100)
                    if comp_score.score_obtained else 0
                ),
            }
        
        return breakdown
    
    # ────────────────────────────────────
    # TRANSCRIPT JSON BUILDING
    # ────────────────────────────────────
    
    def _build_transcript_json(self, student_profile, semester_data):
        """
        Build complete transcript JSON structure.
        """
        cumulative = student_profile.cumulative_gpa
        
        transcript = {
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'university': self.university.name,
                'transcript_type': 'Official Academic Transcript',
            },
            
            'student': {
                'id': student_profile.id,
                'name': f"{student_profile.user.first_name} {student_profile.user.last_name}",
                'matric_number': student_profile.matric_number,
                'email': student_profile.user.email,
                'date_of_birth': student_profile.user.date_of_birth.isoformat() if student_profile.user.date_of_birth else None,
                'program': student_profile.program.name,
                'program_code': student_profile.program.code,
                'department': student_profile.program.department.name,
                'faculty': student_profile.program.department.faculty.name,
            },
            
            'semesters': self._format_semesters(semester_data),
            
            'summary': {
                'total_credits_attempted': cumulative.total_credit_units_attempted,
                'total_credits_earned': cumulative.total_credit_units_earned,
                'cgpa': cumulative.cgpa,
                'classification': cumulative.classification,
                'academic_standing': cumulative.academic_standing,
                'graduation_eligible': cumulative.is_eligible_for_graduation,
            }
        }
        
        return transcript
    
    def _format_semesters(self, semester_data):
        """Format semester data for transcript"""
        semesters = []
        
        for sem_data in semester_data:
            semester = sem_data['semester']
            sem_gpa = sem_data['sem_gpa']
            
            sem_info = {
                'semester': f"Semester {semester.number}",
                'academic_year': semester.academic_year.year,
                'start_date': semester.start_date.isoformat(),
                'end_date': semester.end_date.isoformat(),
                
                'courses': sem_data['courses'],
                
                'semester_summary': {
                    'courses_taken': len(sem_data['courses']),
                    'courses_passed': sum(1 for c in sem_data['courses'] if c['status'] == 'PASSED'),
                    'courses_failed': sum(1 for c in sem_data['courses'] if c['status'] == 'FAILED'),
                    'credits_attempted': sem_gpa.total_credit_units,
                    'credits_earned': sem_gpa.credit_units_earned,
                    'semester_gpa': sem_gpa.gpa,
                    'academic_standing': sem_gpa.academic_standing,
                },
            }
            semesters.append(sem_info)
        
        return semesters
    
    def _get_grade_point(self, grade):
        """Get grade point for letter grade"""
        grading_scale = GradingScale.objects.filter(
            university=self.university,
            grade_letter=grade
        ).first()
        
        return grading_scale.grade_point if grading_scale else 0
    
    # ────────────────────────────────────
    # VERSIONING & SNAPSHOTS
    # ────────────────────────────────────
    
    def _create_snapshot(self, transcript_record, reason=""):
        """
        Create an immutable snapshot of transcript.
        Called when transcript is issued.
        """
        # Get next version number
        next_version = (
            transcript_record.snapshots.aggregate(
                max_version=models.Max('version_number')
            )['max_version'] or 0
        ) + 1
        
        # Mark previous snapshots as superseded
        transcript_record.snapshots.all().update(status='superseded')
        
        # Create new snapshot
        snapshot = TranscriptSnapshot.objects.create(
            transcript_record=transcript_record,
            version_number=next_version,
            status='current',
            snapshot_data=transcript_record.transcript_data,
            issued_at=transcript_record.issued_at,
            issued_by=transcript_record.issued_by,
            signature_token=transcript_record.signature_token,
            reason=reason,
        )
        
        return snapshot
    
    # ────────────────────────────────────
    # UPDATES & CORRECTIONS
    # ────────────────────────────────────
    
    def regenerate_transcript(self, transcript_record, reason="Correction"):
        """
        Regenerate transcript (e.g., after grade correction).
        Creates new snapshot and updates transcript data.
        """
        if transcript_record.is_locked:
            raise ValidationError("Cannot modify locked transcript")
        
        # Regenerate data
        semester_data = self._collect_semester_data(
            transcript_record.student_profile
        )
        
        new_json = self._build_transcript_json(
            transcript_record.student_profile,
            semester_data
        )
        
        # Update
        transcript_record.transcript_data = new_json
        transcript_record.save()
        
        # Create snapshot if official
        if transcript_record.status == 'issued':
            self._create_snapshot(transcript_record, reason)
```

---

## PART III: TRANSCRIPT EXPORT SERVICE

### **Service: TranscriptExportService**

**Purpose**: Export transcript in various formats  

```python
class TranscriptExportService:
    """
    Export transcripts in different formats:
    - PDF (official)
    - JSON (API)
    - CSV (bulk export)
    """
    
    def export_as_pdf(self, transcript_record):
        """
        Export transcript as official PDF document.
        Includes signature for authenticity.
        """
        # Generate PDF using ReportLab or similar
        # Include: header, student info, semester details, summary, footer, signature
        pass
    
    def export_as_json(self, transcript_record):
        """Export transcript data as JSON"""
        return {
            'transcript': transcript_record.transcript_data,
            'status': transcript_record.status,
            'issued_at': transcript_record.issued_at,
            'signature': transcript_record.signature_token,
        }
    
    def export_bulk_as_csv(self, student_profiles, include_scores=False):
        """
        Export multiple transcripts as CSV summary.
        Columns: Matric, Name, Program, CGPA, Classification, Credits
        """
        csv_data = []
        
        for student in student_profiles:
            cumulative = student.cumulative_gpa
            
            row = {
                'Matric Number': student.matric_number,
                'Name': f"{student.user.first_name} {student.user.last_name}",
                'Program': student.program.name,
                'CGPA': cumulative.cgpa if cumulative else 'N/A',
                'Classification': cumulative.classification if cumulative else 'N/A',
                'Credits Earned': cumulative.total_credit_units_earned if cumulative else 0,
            }
            
            if include_scores:
                # Include detailed semester data
                pass
            
            csv_data.append(row)
        
        return csv_data
```

---

## PART IV: TRANSCRIPT VERIFICATION

### **Service: TranscriptVerificationService**

**Purpose**: Verify authenticity of transcripts  

```python
class TranscriptVerificationService:
    """
    Verify transcripts via signature token.
    Prevents tampering/forgery.
    """
    
    def verify_transcript(self, transcript_record):
        """
        Verify transcript signature.
        Returns: (is_valid, reason)
        """
        if not transcript_record.is_issued:
            return False, "Transcript not issued"
        
        # Recalculate signature
        expected_signature = self._calculate_signature(transcript_record)
        
        if transcript_record.signature_token != expected_signature:
            return False, "Signature mismatch - transcript may be tampered"
        
        return True, "Valid"
    
    def _calculate_signature(self, transcript_record):
        """Recalculate expected signature"""
        signature_string = (
            f"{transcript_record.student_profile.id}"
            f"{transcript_record.transcript_data}"
            f"{transcript_record.issued_at}"
        )
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    def get_verification_link(self, transcript_record):
        """
        Generate public verification link.
        Format: /verify-transcript/?id={student_id}&token={signature}
        """
        return f"/verify-transcript/?student_id={transcript_record.student_profile.id}&token={transcript_record.signature_token}"
```

---

## PART V: TRANSCRIPT WORKFLOW

```
┌─────────────────────────────────┐
│ Generate Transcript (Draft)     │ ← Student requests or admin initiates
└────────┬────────────────────────┘
         │ (collect released results + GPAs)
         ↓
┌─────────────────────────────────┐
│ Review Transcript (Draft)       │ ← Student/Admin reviews
└────────┬────────────────────────┘
         │
         ├─ If errors found:
         │  └─ Correct underlying results
         │     └─ Regenerate transcript
         │
         └─ If approved:
             ↓
         ┌────────────────────────┐
         │ Issue Transcript       │ ← Lock & sign
         └────────┬───────────────┘
                  │
                  ↓
         ┌────────────────────────┐
         │ Create Snapshot (v1)   │ ← Immutable
         └────────┬───────────────┘
                  │
                  ↓
         ┌────────────────────────┐
         │ Export as PDF          │ ← For printing/download
         └────────────────────────┘

Correction Workflow:
┌────────────────────────────────────┐
│ Grade Corrected in Source Result   │
└────────┬─────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ Regenerate Transcript              │
└────────┬─────────────────────────────┘
         │
         ↓
┌────────────────────────────────────┐
│ Create New Snapshot (v2)           │ ← Previous marked "superseded"
└────────────────────────────────────┘
```

---

## PART VI: MODELS SUMMARY

| Model | Purpose | Foreign Keys | Key Constraints |
|-------|---------|--------------|-----------------|
| TranscriptRecord | Master transcript | student, program | unique issued + signature |
| TranscriptSnapshot | Version history | transcript | immutable after creation |
| TranscriptComponent | Denormalized summary | transcript | 1-to-1 per transcript |

---

**Status**: Transcript Generator Module Complete  
**Next Steps**: Audit Logging, API Layer Design, Permission System  
**Last Updated**: 2026-02-07
