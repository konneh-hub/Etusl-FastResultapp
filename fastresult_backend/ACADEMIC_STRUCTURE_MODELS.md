# Django Academic Structure Models - SRMS

**Scope**: University Admin only  
**Purpose**: Define university academic hierarchy  
**Status**: Model Design (No Implementation Code)

---

## I. ACADEMIC HIERARCHY

```
University (1)
  │
  ├─── Faculty (many)
  │      │
  │      └─── Department (many)
  │             │
  │             └─── Program (many)
  │                    │
  │                    └─── Course (many)
  │                           │
  │                           └─── Subject (optional, many)
  │
  ├─── AcademicYear (many)
  │      └─── Semester (many)
  │
  ├─── CreditUnitRule (1 per university)
  │
  └─── GradingScale (many)


Constraints:
- Faculty.code unique per university (not globally)
- Department.code unique per faculty
- Program.code unique per department
- Course.code unique per program
- Subject.code unique per course
```

---

## II. MODEL DEFINITIONS

### **Model 1: Faculty**

**Purpose**: Top-level academic division  
**Example**: Faculty of Engineering, Faculty of Arts & Sciences  

```python
class Faculty(models.Model):
    """
    Faculty represents a major academic division within a university.
    Examples: Engineering, Medicine, Arts & Sciences, Law
    """
    
    # Foreign Keys
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='faculties'
    )
    
    # Identity
    code = models.CharField(max_length=50)
    # Examples: 'ENG', 'MED', 'LAW', 'AGR'
    
    name = models.CharField(max_length=255)
    # Examples: "Faculty of Engineering"
    
    description = models.TextField(blank=True)
    
    # Metadata
    head = models.ForeignKey(
        'platform_accounts.PlatformUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculty_head'
    )
    # Dean/head of faculty
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_faculty'
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
        
        # Unique constraint: code per university
        constraints = [
            models.UniqueConstraint(
                fields=['university', 'code'],
                name='unique_faculty_code_per_university'
            )
        ]
        
        indexes = [
            models.Index(fields=['university', 'code']),
            models.Index(fields=['university']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def department_count(self):
        return self.departments.count()
    
    @property
    def program_count(self):
        return Program.objects.filter(
            department__faculty=self
        ).count()


# Constraints at application level:
# - head must be a UniversityUser with role='dean' in same university
```

---

### **Model 2: Department**

**Purpose**: Sub-division within a faculty  
**Example**: Department of Mechanical Engineering, Department of English  

```python
class Department(models.Model):
    """
    Department is a sub-unit within a Faculty.
    Examples: Mechanical Engineering, Computer Science, Biology
    """
    
    # Foreign Keys
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    
    # Identity
    code = models.CharField(max_length=50)
    # Examples: 'MECH', 'CS', 'BIO'
    
    name = models.CharField(max_length=255)
    # Examples: "Department of Mechanical Engineering"
    
    description = models.TextField(blank=True)
    
    # Metadata
    head = models.ForeignKey(
        'platform_accounts.PlatformUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_head'
    )
    # HOD (Head of Department)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        
        # Unique constraint: code per faculty
        constraints = [
            models.UniqueConstraint(
                fields=['faculty', 'code'],
                name='unique_department_code_per_faculty'
            )
        ]
        
        indexes = [
            models.Index(fields=['faculty', 'code']),
            models.Index(fields=['faculty']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def university(self):
        return self.faculty.university
    
    @property
    def program_count(self):
        return self.programs.count()


# Constraints at application level:
# - head must be UniversityUser with role='hod' in same university
# - head.department_assignment.department = this department
```

---

### **Model 3: Program**

**Purpose**: Curriculum/Degree program  
**Example**: B.Sc. Computer Science, B.Tech. Mechanical Engineering  

```python
class Program(models.Model):
    """
    Program represents a degree/curriculum offering.
    Examples: B.Sc. Computer Science (100-200-300-400), 
              M.Tech Mechanical Engineering
    """
    
    # Foreign Keys
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programs'
    )
    
    # Identity
    code = models.CharField(max_length=50)
    # Examples: 'CS', 'CSE', 'MECS'
    
    name = models.CharField(max_length=255)
    # Examples: "Bachelor of Science in Computer Science"
    
    description = models.TextField(blank=True)
    
    # Academic Details
    level = models.IntegerField(default=100)
    # 100, 200, 300, 400 (year level)
    
    duration_years = models.IntegerField(default=4)
    # Standard duration in years
    
    total_credit_units = models.IntegerField(default=124)
    # Total credits for full program
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_program'
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        
        # Unique constraint: code per department
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'code'],
                name='unique_program_code_per_department'
            )
        ]
        
        indexes = [
            models.Index(fields=['department', 'code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.level})"
    
    @property
    def university(self):
        return self.department.faculty.university


# Constraints:
# - duration_years >= 1
# - total_credit_units > 0
# - level in [100, 200, 300, 400]
```

---

### **Model 4: Course**

**Purpose**: Individual course/subject offering  
**Example**: INT201 - Data Structures, ENG101 - English Composition  

```python
class Course(models.Model):
    """
    Course represents an individual subject offering.
    Linked to program(s) and taught by lecturers.
    """
    
    # Foreign Keys
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    
    # Identity
    code = models.CharField(max_length=50)
    # Examples: 'INT201', 'INT202', 'CSC301'
    
    name = models.CharField(max_length=255)
    # Examples: "Data Structures", "Database Design"
    
    description = models.TextField(blank=True)
    
    # Academic Details
    credit_units = models.IntegerField()
    # 1-6 typical for semester courses
    
    # Course Type
    COURSE_TYPE_CHOICES = [
        ('core', 'Core/Compulsory'),
        ('elective', 'Elective'),
        ('prerequisite', 'Prerequisite'),
    ]
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        default='core'
    )
    
    is_practical = models.BooleanField(default=False)
    # Lab/practical component?
    
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.CharField(max_length=100)  # Email
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_course'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        
        # Unique constraint: code per program (but may be used in multiple programs)
        constraints = [
            models.UniqueConstraint(
                fields=['program', 'code'],
                name='unique_course_code_per_program',
                condition=models.Q(is_active=True)  # Only for active courses
            ),
            models.CheckConstraint(
                check=models.Q(credit_units__gt=0),
                name='course_credit_units_positive'
            ),
        ]
        
        indexes = [
            models.Index(fields=['program', 'code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def university(self):
        return self.program.department.faculty.university


# Constraints:
# - credit_units > 0 and <= 10
# - Can be shared across programs in same department
```

---

### **Model 5: Subject** (Optional)

**Purpose**: Sub-topic within a course  
**Example**: "Linear Algebra" is a subject of "Mathematics I" course  

```python
class Subject(models.Model):
    """
    Optional: Subject represents sub-topics within a course.
    Not always used - depends on university structure.
    """
    
    # Foreign Keys
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    
    # Identity
    code = models.CharField(max_length=50, blank=True)
    # Optional code
    
    name = models.CharField(max_length=255)
    # Examples: "Linear Algebra", "Calculus", "Differential Equations"
    
    description = models.TextField(blank=True)
    
    # Weighting (if multiple subjects per course)
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0
    )
    # If course has multiple subjects, each has a weight
    
    # Metadata
    order = models.IntegerField(default=0)  # Display order
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'academic_subject'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        
        indexes = [
            models.Index(fields=['course']),
        ]
        
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.course.code} - {self.name}"


# Constraints:
# - weight > 0
# - sum(weights) for all subjects in course should ideally = 1.0 (or 100)
```

---

### **Model 6: AcademicYear**

**Purpose**: Calendar year dividing institution  
**Example**: 2024/2025 Academic Year  

```python
class AcademicYear(models.Model):
    """
    Academic year represents a calendar-based period.
    Format typically: "2024/2025" or "2024-2025"
    """
    
    # Foreign Keys
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='academic_years'
    )
    
    # Identity
    year = models.CharField(max_length=9)
    # Format: "2024/2025" or "2024-2025"
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=False)
    # Only ONE academic year per university should be active
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_year'
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
        
        # Unique: only one year per university
        constraints = [
            models.UniqueConstraint(
                fields=['university', 'year'],
                name='unique_academic_year_per_university'
            ),
            # Only one active per university
            models.UniqueConstraint(
                fields=['university'],
                condition=models.Q(is_active=True),
                name='unique_active_academic_year_per_university'
            ),
            models.CheckConstraint(
                check=models.Q(start_date__lt=models.F('end_date')),
                name='academic_year_dates_valid'
            ),
        ]
        
        ordering = ['-year']
        indexes = [
            models.Index(fields=['university', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.year} ({'Active' if self.is_active else 'Inactive'})"
    
    @property
    def university_id(self):
        return self.university_id


# Constraints:
# - start_date < end_date
# - Activate new year → deactivate old year (service layer logic)
```

---

### **Model 7: Semester**

**Purpose**: Division of academic year (usually 2 per year)  
**Example**: Semester 1 (Sept-Dec), Semester 2 (Jan-May)  

```python
class Semester(models.Model):
    """
    Semester is a sub-period within an AcademicYear.
    Typically: Semester 1 and Semester 2 per academic year.
    """
    
    SEMESTER_NUMBER_CHOICES = [
        (1, 'First Semester'),
        (2, 'Second Semester'),
        (3, 'Third Semester (if trimester)'),
    ]
    
    # Foreign Keys
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='semesters'
    )
    
    # Identity
    number = models.IntegerField(choices=SEMESTER_NUMBER_CHOICES)
    # 1 = first semester, 2 = second semester
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Important dates
    enrollment_deadline = models.DateField(null=True, blank=True)
    result_submission_deadline = models.DateField(null=True, blank=True)
    result_release_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=False)
    # Only ONE semester per academic year should be active
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'semester'
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
        
        # Unique: one semester number per academic year
        constraints = [
            models.UniqueConstraint(
                fields=['academic_year', 'number'],
                name='unique_semester_per_academic_year'
            ),
            # Only one active per academic year
            models.UniqueConstraint(
                fields=['academic_year'],
                condition=models.Q(is_active=True),
                name='unique_active_semester_per_academic_year'
            ),
            models.CheckConstraint(
                check=models.Q(start_date__lt=models.F('end_date')),
                name='semester_dates_valid'
            ),
        ]
        
        ordering = ['academic_year', 'number']
        indexes = [
            models.Index(fields=['academic_year', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.academic_year.year} - Sem {self.number}"
    
    @property
    def university(self):
        return self.academic_year.university
    
    @property
    def is_current(self):
        return self.is_active and self.academic_year.is_active


# Constraints:
# - start_date within academic_year date range
# - end_date within academic_year date range
# - Semester 1 should start before Semester 2
```

---

### **Model 8: CreditUnitRule**

**Purpose**: University-wide credit policies  

```python
class CreditUnitRule(models.Model):
    """
    Defines credit unit rules for the university.
    One-to-one relationship with University.
    """
    
    # Foreign Keys
    university = models.OneToOneField(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='credit_rules'
    )
    
    # Rules
    min_credit_per_semester = models.IntegerField(default=12)
    # Minimum credits student must take per semester
    
    max_credit_per_semester = models.IntegerField(default=30)
    # Maximum credits per semester
    
    gpa_threshold_for_max_credit = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=2.0
    )
    # GPA below this → can only take min credits
    
    gpa_threshold_for_good_standing = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0
    )
    # Below this = academic probation
    
    max_repeats_per_course = models.IntegerField(default=2)
    # How many times can student retake a failed course
    
    min_overall_gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0
    )
    # Minimum CGPA to graduate
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100)  # Admin email
    
    class Meta:
        db_table = 'credit_unit_rule'
        verbose_name = 'Credit Unit Rule'
        verbose_name_plural = 'Credit Unit Rules'
    
    def __str__(self):
        return f"Credit Rules - {self.university.name}"
    
    def validate_credit_load(self, planned_credits, student_gpa):
        """Check if student can take this many credits"""
        if student_gpa >= self.gpa_threshold_for_max_credit:
            max_allowed = self.max_credit_per_semester
        else:
            max_allowed = self.min_credit_per_semester
        
        return self.min_credit_per_semester <= planned_credits <= max_allowed


# Constraints:
# - min_credit_per_semester < max_credit_per_semester
# - gpa_threshold_for_good_standing >= 0
# - All decimals between 0 and 4.0
```

---

### **Model 9: GradingScale**

**Purpose**: Define grade-to-point conversion  

```python
class GradingScale(models.Model):
    """
    Defines the grading scale used by the university.
    Example: A=4.0, B=3.0, C=2.0, D=1.0, F=0.0
    """
    
    # Foreign Keys
    university = models.ForeignKey(
        'university_registry.University',
        on_delete=models.CASCADE,
        related_name='grading_scales'
    )
    
    # Identity
    name = models.CharField(max_length=100)
    # Examples: "Standard A-F Scale", "Alternative Scale"
    
    # Grade
    grade_letter = models.CharField(max_length=2)
    # 'A', 'B', 'C', 'D', 'F', 'A+', etc.
    
    # Score Range
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    # Examples: A: 80-100, B: 70-79, C: 60-69, D: 50-59, F: 0-49
    
    # Grade Points (used in GPA calculation)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    # Examples: A=4.0, B=3.0, C=2.0, D=1.0, F=0.0
    
    # Metadata
    is_passing = models.BooleanField(default=True)
    # False for F/Fail grades
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'grading_scale'
        verbose_name = 'Grading Scale'
        verbose_name_plural = 'Grading Scales'
        
        # Unique: one entry per (university, grade_letter)
        constraints = [
            models.UniqueConstraint(
                fields=['university', 'grade_letter'],
                name='unique_grade_per_university'
            ),
            models.CheckConstraint(
                check=models.Q(min_score__lte=models.F('max_score')),
                name='grade_scale_range_valid'
            ),
            models.CheckConstraint(
                check=models.Q(grade_point__gte=0) & models.Q(grade_point__lte=4.0),
                name='grade_point_valid_range'
            ),
        ]
        
        ordering = ['-grade_point']
        indexes = [
            models.Index(fields=['university', 'min_score']),
        ]
    
    def __str__(self):
        return f"{self.grade_letter} ({self.min_score}-{self.max_score}): {self.grade_point} points"
    
    @staticmethod
    def get_grade_for_score(university_id, score):
        """Get grade letter for a given score"""
        grading_scale = GradingScale.objects.filter(
            university_id=university_id,
            min_score__lte=score,
            max_score__gte=score
        ).first()
        return grading_scale.grade_letter if grading_scale else 'F'
    
    @staticmethod
    def get_grade_point_for_score(university_id, score):
        """Get grade point for a given score"""
        grading_scale = GradingScale.objects.filter(
            university_id=university_id,
            min_score__lte=score,
            max_score__gte=score
        ).first()
        return grading_scale.grade_point if grading_scale else 0.0


# Standard Grading Scales (to seed):
STANDARD_GRADING_SCALE = [
    ('A', 80, 100, 4.0, True),
    ('B', 70, 79, 3.0, True),
    ('C', 60, 69, 2.0, True),
    ('D', 50, 59, 1.0, True),
    ('F', 0, 49, 0.0, False),
]
```

---

## III. RELATIONSHIPS DIAGRAM

```
University (Root)
    │
    ├─ Faculty (many)
    │      └─ Department (many)
    │             └─ Program (many)
    │                    └─ Course (many)
    │                           └─ Subject (optional, many)
    │
    ├─ AcademicYear (many)
    │      └─ Semester (many per year, typically 2)
    │
    ├─ CreditUnitRule (1 per university)
    │
    └─ GradingScale (many, typically 5)
```

---

## IV. UNIQUE CONSTRAINTS SUMMARY

| Model | Unique Constraint |
|-------|-------------------|
| Faculty | (university, code) |
| Department | (faculty, code) → implies (university, dept.name) |
| Program | (department, code) |
| Course | (program, code) - active only |
| Subject | None (can repeat names) |
| AcademicYear | (university, year) + unique active per university |
| Semester | (academic_year, number) + unique active per academic_year |
| CreditUnitRule | university (1-to-1) |
| GradingScale | (university, grade_letter) |

---

## V. CHECK CONSTRAINTS

| Model | Constraint |
|-------|-----------|
| AcademicYear | start_date < end_date |
| Semester | start_date < end_date |
| Course | credit_units > 0 |
| CreditUnitRule | min_credits < max_credits, all GPA 0-4.0 |
| GradingScale | min_score ≤ max_score, grade_point 0-4.0 |
| Subject | weight > 0 |

---

## VI. CASCADING DELETIONS

```
Delete University
    → Delete Faculty (cascade)
        → Delete Department (cascade)
            → Delete Program (cascade)
                → Delete Course (cascade)
                    → Delete Subject (cascade)
    → Delete AcademicYear (cascade)
        → Delete Semester (cascade)

Delete Faculty/Department/Program
    → Just remove from hierarchy (foreign keys have on_delete=CASCADE)
```

---

## VII. ADMIN CREATION FLOW

```
University Admin:
    1. Create Academic Year for next cycle
    2. Create Semesters within year
    3. Create Faculties
    4. Create Departments within faculties
    5. Create Programs within departments
    6. Create Courses within programs
    7. (Optional) Create Subjects within courses
    8. Set up CreditUnitRule (one time)
    9. Set up GradingScale (usually once, can update)
    10. Assign Faculty head (Dean)
    11. Assign Department head (HOD)
    12. Assign Lecturers to courses (per semester)
```

---

## VIII. VALIDATION RULES (Application Level)

```python
# When creating Department:
- Must belong to Faculty in same University

# When creating Program:
- Must belong to Department
- Level should be 100, 200, 300, or 400
- Duration_years >= 1

# When creating Course:
- Must belong to Program
- credit_units 1-6 (typically)
- Cannot have duplicate course_type=core if already exists

# When creating Subject:
- Must belong to Course
- Sum of all Subject weights ≈ 1.0

# When activating Semester:
- Deactivate previously active semester in same academic year
- start_date >= academic_year.start_date
- end_date <= academic_year.end_date

# When setting up CreditUnitRule:
- min_credits < max_credits
- All GPA thresholds 0-4.0
- max_repeats >= 1

# When setting up GradingScale:
- No overlapping score ranges for same university
- Total of all grades should cover 0-100
```

---

## IX. SUMMARY TABLE

| Model | Purpose | Foreign Keys | Unique Constraints | Use Case |
|-------|---------|--------------|-------------------|----------|
| Faculty | Top-level division | university | (univ, code) | Organize by discipline |
| Department | Mid-level division | faculty | (faculty, code) | Group programs |
| Program | Degree curriculum | department | (dept, code) | B.S., B.Tech., M.Tech |
| Course | Individual subject | program | (prog, code)-active | Math 101, Physics 201 |
| Subject | Optional sub-topic | course | None | Used if needed |
| AcademicYear | Calendar year | university | (univ, year), one active | 2024/2025 |
| Semester | Half of academic year | academic_year | (year, number), one active | Jan-May period |
| CreditUnitRule | Credit policies | university | 1-to-1 | Min/max per semester |
| GradingScale | Grade conversion | university | (univ, grade_letter) | A=4.0, B=3.0, etc |

---

**Status**: Academic Structure Models Complete  
**Next Steps**: Result storage models, workflow models, GPA engine  
**Last Updated**: 2026-02-07
