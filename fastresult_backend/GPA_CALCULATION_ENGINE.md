# GPA Calculation Engine - SRMS

**Scope**: Semester GPA + Cumulative GPA + Academic Standing  
**Status**: Design Specification (No Implementation Code)

---

## PART I: GPA MODELS

### **Model 1: SemesterGPA**

**Purpose**: Stores calculated GPA for student in a semester  
**Recalculated**: When results released or changed

```python
class SemesterGPA(models.Model):
    """
    Represents calculated GPA for a student in a semester.
    Recalculated whenever result released/updated.
    """
    
    # Foreign Keys
    student_profile = models.ForeignKey(
        'enrollment.StudentProfile',
        on_delete=models.CASCADE,
        related_name='semester_gpas'
    )
    
    semester = models.ForeignKey(
        'academic_structure.Semester',
        on_delete=models.CASCADE,
        related_name='student_gpas'
    )
    
    # GPA Calculation (Formula: Σ(credit_units × grade_point) / Σ(credit_units))
    total_credit_units = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    # Sum of credit units for all courses taken this semester
    
    total_grade_points = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Sum of (course_credit × grade_point) for all courses
    
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )
    # Calculated GPA: total_grade_points / total_credit_units
    # Range: 0.0 - 4.0
    
    # Credit Tracking
    credit_units_earned = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    # Credits counted toward degree (passed grades with grade_point > 0)
    
    credit_units_failed = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    # Credits not counted (F grade, grade_point = 0)
    
    # Academic Standing
    STANDING_CHOICES = [
        ('good', 'Good Standing'),
        ('probation', 'Academic Probation'),
        ('warning', 'Academic Warning'),
        ('suspension', 'Suspension'),
    ]
    academic_standing = models.CharField(
        max_length=50,
        choices=STANDING_CHOICES,
        default='good'
    )
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.CharField(max_length=100)  # "gpa_engine" service
    
    class Meta:
        db_table = 'gpa_semester_gpa'
        verbose_name = 'Semester GPA'
        verbose_name_plural = 'Semester GPAs'
        
        # One per (student, semester)
        constraints = [
            models.UniqueConstraint(
                fields=['student_profile', 'semester'],
                name='unique_semester_gpa'
            ),
            models.CheckConstraint(
                check=models.Q(gpa__gte=0) & models.Q(gpa__lte=4.0),
                name='gpa_between_0_and_4'
            ),
            models.CheckConstraint(
                check=models.Q(total_credit_units__gt=0),
                name='credit_units_positive'
            ),
        ]
        
        indexes = [
            models.Index(fields=['student_profile', 'semester']),
            models.Index(fields=['academic_standing']),
        ]
        
        ordering = ['student_profile', 'semester']
    
    def __str__(self):
        return f"{self.student_profile} - {self.semester}: GPA {self.gpa}"
    
    @property
    def is_passing(self):
        """Check if GPA meets minimum requirement"""
        rule = self.semester.academic_year.university.credit_unit_rule
        return self.gpa >= rule.gpa_threshold_for_good_standing


# Calculation Rule:
# gpa = Σ(course.credit_units × grade_point) / Σ(course.credit_units)
# Only include courses with released results
```

---

### **Model 2: CumulativeGPA**

**Purpose**: All-time GPA from program start  
**Updated**: Each semester after GPA calculation

```python
class CumulativeGPA(models.Model):
    """
    Cumulative GPA from student's program start.
    Updated each semester as semesters are added.
    """
    
    # Foreign Keys
    student_profile = models.ForeignKey(
        'enrollment.StudentProfile',
        on_delete=models.CASCADE,
        related_name='cumulative_gpa',
        unique=True
    )
    # Only one cumulative GPA record per student
    
    # Cumulative Calculation
    total_credit_units_earned = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    # Total credits counted (all passed courses, all semesters)
    
    total_credit_units_attempted = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    # Total credits taken (all courses, all semesters)
    
    total_grade_points = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Sum of all (credit × grade_point) across ALL semesters
    
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )
    # Cumulative GPA: total_grade_points / total_credit_units_attempted
    # Range: 0.0 - 4.0
    
    # Classification
    CLASSIFICATION_CHOICES = [
        ('1st_class', 'First Class'),      # CGPA >= 3.5
        ('2nd_upper', '2nd Class Upper'),  # CGPA 3.0 - 3.4
        ('2nd_lower', '2nd Class Lower'),  # CGPA 2.0 - 2.9
        ('3rd_class', '3rd Class'),        # CGPA 1.0 - 1.9
        ('pass', 'Pass'),                  # CGPA 0.5 - 0.9
        ('not_classified', 'Not Yet Classified'),
    ]
    classification = models.CharField(
        max_length=50,
        choices=CLASSIFICATION_CHOICES,
        default='not_classified'
    )
    
    # Academic Standing
    STANDING_CHOICES = [
        ('good', 'Good Standing'),
        ('probation', 'Academic Probation'),
        ('warning', 'Academic Warning'),
        ('suspension', 'Suspension'),
        ('dismissed', 'Dismissed'),
    ]
    academic_standing = models.CharField(
        max_length=50,
        choices=STANDING_CHOICES,
        default='good'
    )
    
    # Repeated Courses
    repeated_courses_count = models.IntegerField(default=0)
    # How many courses have been retaken
    
    # Best Grades Policy (if enabled)
    uses_best_grades_policy = models.BooleanField(default=False)
    # Only highest grade counted for repeated courses
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)  # "gpa_engine" service
    
    class Meta:
        db_table = 'gpa_cumulative_gpa'
        verbose_name = 'Cumulative GPA'
        verbose_name_plural = 'Cumulative GPAs'
        
        constraints = [
            models.CheckConstraint(
                check=models.Q(cgpa__gte=0) & models.Q(cgpa__lte=4.0),
                name='cgpa_between_0_and_4'
            ),
        ]
        
        indexes = [
            models.Index(fields=['student_profile']),
            models.Index(fields=['classification']),
        ]
    
    def __str__(self):
        return f"{self.student_profile} - CGPA: {self.cgpa} ({self.classification})"
    
    @property
    def is_eligible_for_graduation(self):
        """Check graduation eligibility"""
        rule = self.student_profile.program.department.faculty.university.credit_unit_rule
        return (
            self.cgpa >= rule.min_overall_gpa and
            self.total_credit_units_earned >= self.student_profile.program.total_credit_units
        )


# Calculation Rule:
# cgpa = Σ(all_semesters: course.credit_units × grade_point) / Σ(all_semesters: credit_units)
# Classification buckets configurable per university
```

---

### **Model 3: CourseRepetitionRecord**

**Purpose**: Track repeated courses (for best-grade policy)  
**Policy**: "Only count best grade for repeated courses"

```python
class CourseRepetitionRecord(models.Model):
    """
    Records attempts at a course.
    Used for "Best Grade Policy".
    """
    
    # Foreign Keys
    student_profile = models.ForeignKey(
        'enrollment.StudentProfile',
        on_delete=models.CASCADE,
        related_name='course_repetitions'
    )
    
    course = models.ForeignKey(
        'academic_structure.Course',
        on_delete=models.CASCADE,
        related_name='repetition_records'
    )
    
    # Attempts
    attempt_number = models.IntegerField()
    # 1st attempt, 2nd attempt, 3rd attempt, etc
    
    # Result
    semester = models.ForeignKey(
        'academic_structure.Semester',
        on_delete=models.PROTECT,
        related_name='repetition_records'
    )
    
    score_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    grade = models.CharField(max_length=2, null=True, blank=True)
    grade_point = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True
    )
    
    # Policy
    is_best_attempt = models.BooleanField(default=False)
    # If best-grade policy enabled, only this counts
    
    is_counted_in_gpa = models.BooleanField(default=True)
    # If False, this attempt doesn't count toward GPA
    
    class Meta:
        db_table = 'gpa_course_repetition'
        verbose_name = 'Course Repetition Record'
        verbose_name_plural = 'Course Repetition Records'
        
        unique_together = ('student_profile', 'course', 'attempt_number')
        ordering = ['student_profile', 'course', 'attempt_number']
    
    def __str__(self):
        return f"{self.student_profile} - {self.course} (Attempt {self.attempt_number})"


# Rules:
# - Created when student enrolls in course again
# - is_best_attempt = True only if grade_point > previous attempts
# - is_counted_in_gpa = False for non-best attempts (if policy enabled)
```

---

## PART II: GPA CALCULATION SERVICE LAYER

### **Service: GPACalculationService**

**Purpose**: Orchestrates all GPA calculations  

```python
class GPACalculationService:
    """
    Calculate semester GPA, cumulative GPA, and academic standing.
    Core business logic for GPA engine.
    """
    
    def __init__(self, university):
        self.university = university
        self.credit_rule = university.credit_unit_rule
        self.grading_scale = self._build_grading_scale()
    
    # ────────────────────────────────────
    # SEMESTER GPA CALCULATION
    # ────────────────────────────────────
    
    def calculate_semester_gpa(self, student_profile, semester):
        """
        Calculate GPA for student for a semester.
        
        Formula: Σ(credit_units × grade_point) / Σ(credit_units)
        
        Inputs:
        - Student enrollments in semester with RELEASED results
        - Grading scale for converting scores to grades
        
        Returns:
        - SemesterGPA instance (saved to DB)
        """
        # 1. Get all released results for this semester
        results = self._get_released_results(student_profile, semester)
        
        if not results:
            # No results released yet
            return None
        
        # 2. Calculate components
        total_credit_units = 0
        total_grade_points = 0
        credit_units_earned = 0
        credit_units_failed = 0
        
        for result in results:
            course = result.student_enrollment.course
            grade_point = self.grading_scale.get(result.grade, 0)
            credit_units = course.credit_units
            
            # Accumulate
            total_credit_units += credit_units
            total_grade_points += credit_units * grade_point
            
            if grade_point > 0:  # Passing grade
                credit_units_earned += credit_units
            else:  # F grade
                credit_units_failed += credit_units
        
        # 3. Calculate GPA
        if total_credit_units == 0:
            gpa = 0.0
        else:
            gpa = total_grade_points / total_credit_units
        
        # 4. Determine academic standing
        standing = self._determine_standing(gpa, credit_units_earned)
        
        # 5. Save to DB
        semester_gpa, created = SemesterGPA.objects.update_or_create(
            student_profile=student_profile,
            semester=semester,
            defaults={
                'total_credit_units': total_credit_units,
                'total_grade_points': total_grade_points,
                'gpa': round(gpa, 2),
                'credit_units_earned': credit_units_earned,
                'credit_units_failed': credit_units_failed,
                'academic_standing': standing,
                'calculated_by': 'gpa_engine',
            }
        )
        return semester_gpa
    
    # ────────────────────────────────────
    # CUMULATIVE GPA CALCULATION
    # ────────────────────────────────────
    
    def calculate_cumulative_gpa(self, student_profile):
        """
        Calculate cumulative GPA from all semesters.
        
        Formula: Σ(all_semesters: credit × grade_point) / Σ(all_semesters: credit)
        
        Handles:
        - Best grade policy for repeated courses
        - Course repetition tracking
        - Classification assignment
        """
        # 1. Get all semester GPAs
        semester_gpas = student_profile.semester_gpas.all()
        
        if not semester_gpas:
            return None  # No semesters with GPA yet
        
        # 2. Aggregate across semesters
        total_grade_points = 0
        total_credit_units_attempted = 0
        total_credit_units_earned = 0
        repeated_count = 0
        
        for sem_gpa in semester_gpas:
            total_grade_points += sem_gpa.total_grade_points
            total_credit_units_attempted += sem_gpa.total_credit_units
            total_credit_units_earned += sem_gpa.credit_units_earned
        
        # 3. Apply best-grade policy
        if self.credit_rule.uses_best_grades_for_repeats:
            total_grade_points, repeated_count = self._apply_best_grade_policy(
                student_profile
            )
        
        # 4. Calculate CGPA
        if total_credit_units_attempted == 0:
            cgpa = 0.0
        else:
            cgpa = total_grade_points / total_credit_units_attempted
        
        # 5. Classify
        classification = self._classify_student(cgpa)
        
        # 6. Determine standing
        standing = self._determine_standing(cgpa, total_credit_units_earned)
        
        # 7. Save to DB
        cumulative_gpa, _ = CumulativeGPA.objects.update_or_create(
            student_profile=student_profile,
            defaults={
                'total_credit_units_earned': total_credit_units_earned,
                'total_credit_units_attempted': total_credit_units_attempted,
                'total_grade_points': total_grade_points,
                'cgpa': round(cgpa, 2),
                'classification': classification,
                'academic_standing': standing,
                'repeated_courses_count': repeated_count,
                'updated_by': 'gpa_engine',
            }
        )
        return cumulative_gpa
    
    # ────────────────────────────────────
    # HELPER METHODS
    # ────────────────────────────────────
    
    def _get_released_results(self, student_profile, semester):
        """Get all RELEASED results for student in semester"""
        return ResultRecord.objects.filter(
            student_enrollment__student_profile=student_profile,
            student_enrollment__semester=semester,
            status='released'
        ).select_related(
            'student_enrollment__course'
        )
    
    def _build_grading_scale(self):
        """Build grade → grade_point mapping from GradingScale"""
        scale = {}
        for grading in GradingScale.objects.filter(university=self.university):
            scale[grading.grade_letter] = grading.grade_point
        return scale
    
    def _determine_standing(self, gpa, credits_earned):
        """Determine academic standing based on GPA"""
        if gpa >= self.credit_rule.gpa_threshold_for_good_standing:
            return 'good'
        elif gpa >= self.credit_rule.gpa_threshold_for_warning:
            return 'warning'
        elif gpa >= self.credit_rule.gpa_threshold_for_probation:
            return 'probation'
        else:
            return 'suspension'
    
    def _classify_student(self, cgpa):
        """Classify by CGPA buckets"""
        if cgpa >= 3.5:
            return '1st_class'
        elif cgpa >= 3.0:
            return '2nd_upper'
        elif cgpa >= 2.0:
            return '2nd_lower'
        elif cgpa >= 1.0:
            return '3rd_class'
        elif cgpa >= 0.5:
            return 'pass'
        else:
            return 'not_classified'
    
    def _apply_best_grade_policy(self, student_profile):
        """
        Apply best-grade policy for repeated courses.
        Recalculate total_grade_points using only best attempts.
        """
        # Get all repetitions
        repetitions = CourseRepetitionRecord.objects.filter(
            student_profile=student_profile
        )
        
        # Mark best attempts
        best_grade_points = 0
        repeated_count = 0
        
        for course_reps in repetitions.values('course').distinct():
            course_id = course_reps['course']
            
            # Get all attempts for this course, ordered by grade descending
            attempts = repetitions.filter(
                course_id=course_id
            ).order_by('-grade_point')
            
            if attempts.count() > 1:
                # Mark first (best) attempt
                attempts[0].is_best_attempt = True
                attempts[0].is_counted_in_gpa = True
                attempts[0].save()
                
                # Mark other attempts
                for attempt in attempts[1:]:
                    attempt.is_best_attempt = False
                    attempt.is_counted_in_gpa = False
                    attempt.save()
                
                repeated_count += 1
        
        # Recalculate using best attempts only
        best_results = ResultRecord.objects.filter(
            student_enrollment__student_profile=student_profile,
            status='released'
        ).select_related('student_enrollment__course')
        
        total = 0
        for result in best_results:
            # Check if this course has repetitions
            reps = CourseRepetitionRecord.objects.filter(
                student_profile=student_profile,
                course=result.student_enrollment.course,
                is_counted_in_gpa=True
            )
            if reps.exists() or not CourseRepetitionRecord.objects.filter(
                student_profile=student_profile,
                course=result.student_enrollment.course
            ).exists():
                # Include this result
                grade_point = self.grading_scale.get(result.grade, 0)
                total += result.student_enrollment.course.credit_units * grade_point
        
        return total, repeated_count
    
    # ────────────────────────────────────
    # TRIGGER RECALCULATION
    # ────────────────────────────────────
    
    def recalculate_on_result_release(self, result_record):
        """
        Called when a result is RELEASED.
        Triggers:
        1. Semester GPA recalculation
        2. Cumulative GPA recalculation
        3. Academic standing evaluation
        """
        student = result_record.student_enrollment.student_profile
        semester = result_record.student_enrollment.semester
        
        # Update semester GPA
        self.calculate_semester_gpa(student, semester)
        
        # Update cumulative GPA
        self.calculate_cumulative_gpa(student)
        
        # Check academic standing policy
        self._evaluate_academic_standing_action(student)
    
    def _evaluate_academic_standing_action(self, student_profile):
        """
        Check academic standing changes.
        Trigger notifications if:
        - Moved to probation
        - Moved to suspension
        - Restored to good standing
        """
        # Logic for notifications goes here
        pass
```

---

## PART III: CALCULATION TRIGGERS

### **When to Calculate?**

1. **Semester GPA**:
   - When result released (status → 'released')
   - When result is changed after being locked
   - Admin manual recalculation

2. **Cumulative GPA**:
   - After semester GPA calculated
   - When semester closes
   - Admin manual recalculation

3. **Course Repetition**:
   - When student enrolls in same course again
   - When grade is recorded (to compare)
   - When best-grade policy is applied

---

## PART IV: GPA MODELS SUMMARY

| Model | Purpose | Foreign Keys | Key Properties |
|-------|---------|--------------|-----------------|
| SemesterGPA | Semester GPA calculation | student, semester | gpa (0-4), standing, classification |
| CumulativeGPA | All-time GPA | student (1-to-1) | cgpa (0-4), classification, standing |
| CourseRepetitionRecord | Repeated course tracking | student, course, semester | is_best_attempt, grade_point |

---

## PART V: SERVICE LAYER DESIGN

```
GPACalculationService:
├─ calculate_semester_gpa(student, semester) → SemesterGPA
├─ calculate_cumulative_gpa(student) → CumulativeGPA
├─ recalculate_on_result_release(result) → triggers both
├─ _apply_best_grade_policy(student) → recalculated total
├─ _determine_standing(gpa) → 'good'/'warning'/'probation'
├─ _classify_student(cgpa) → '1st_class'/'2nd_upper'/etc
├─ _get_released_results(student, semester)
└─ _build_grading_scale() → grade → grade_point map

API Usage:
├─ ResultService.on_result_released() → calls GPACalculationService.recalculate_on_result_release()
├─ TranscriptService.get_semester_details() → calls GPACalculationService.get_semester_gpa()
└─ StudentDashboardService.get_academic_summary() → calls GPACalculationService.get_cumulative_gpa()
```

---

## PART VI: CONFIGURATION

**Per University** (via CreditUnitRule):
- `min_overall_gpa`: Minimum GPA for graduation (default 1.0)
- `gpa_threshold_for_good_standing`: Minimum GPA (default 2.0)
- `gpa_threshold_for_warning`: Warning threshold (default 1.5)
- `gpa_threshold_for_probation`: Probation threshold (default 1.0)
- `uses_best_grades_for_repeats`: Best grade policy enabled? (default False)
- `max_repeats_per_course`: Max times can retake (default 2)

**Classification Buckets** (hardcoded, configurable):
```
1st Class:    CGPA >= 3.5
2nd Upper:    3.0 <= CGPA < 3.5
2nd Lower:    2.0 <= CGPA < 3.0
3rd Class:    1.0 <= CGPA < 2.0
Pass:         0.5 <= CGPA < 1.0
Not Classified: CGPA < 0.5
```

---

**Status**: GPA Calculation Engine Design Complete  
**Next Steps**: Transcript Generator, Audit Logging  
**Last Updated**: 2026-02-07
