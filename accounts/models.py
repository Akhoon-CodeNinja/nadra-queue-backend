import re
from django.db import models
from django.core.exceptions import ValidationError


# ==========================================================
# VALIDATORS
# ==========================================================
def validate_cnic(value):
    """
    Validates Pakistani CNIC format:
    XXXXX-XXXXXXX-X
    """
    pattern = r'^\d{5}-\d{7}-\d{1}$'

    if not re.match(pattern, value):
        raise ValidationError(
            'CNIC must be in format XXXXX-XXXXXXX-X'
        )


def validate_mobile(value):
    """
    Validates Pakistani Mobile Number:
    03XXXXXXXXX
    """
    pattern = r'^03\d{9}$'

    if not re.match(pattern, value):
        raise ValidationError(
            'Mobile number must be in format 03XXXXXXXXX'
        )


# ==========================================================
# USERS TABLE
# ==========================================================
class Users(models.Model):

    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    CNIC = models.CharField(
        max_length=15,
        unique=True,
        validators=[validate_cnic]
    )
    password = models.CharField(max_length=128)
    DOB = models.DateField()
    Mobile_number = models.CharField(
        max_length=15,
        validators=[validate_mobile]
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'Users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.full_name} ({self.CNIC})"


# ==========================================================
# CITY TABLE
# ==========================================================
class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = 'City'
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.city_name


# ==========================================================
# DISTRICT TABLE
# ==========================================================
class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=150)
    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE, 
        related_name='districts'
    )

    class Meta:
        db_table = 'District'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

    def __str__(self):
        return f"{self.district_name} ({self.city.city_name})"


# ==========================================================
# OFFICE TABLE
# ==========================================================
class Office(models.Model):

    office_id = models.AutoField(primary_key=True)
    
    # Ye foreign key link karegi office ko district se
    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE, 
        related_name='offices',
        null=True,  
        blank=True
    )

    branch_name = models.CharField(max_length=150)
    google_address = models.TextField()
    capacity = models.PositiveIntegerField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    open_days = models.CharField(max_length=100)

    class Meta:
        db_table = 'Office'
        verbose_name = 'Office'
        verbose_name_plural = 'Offices'

    def __str__(self):
        return self.branch_name


# ==========================================================
# TOKEN TABLE
# ==========================================================
class Token(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    token_id = models.AutoField(primary_key=True)
    token_number = models.PositiveIntegerField()
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='tokens'
    )
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        db_column='office_id',
        related_name='tokens'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    estimated_wait_time = models.PositiveIntegerField(
        help_text='Minutes'
    )

    class Meta:
        db_table = 'Token'
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"Token {self.token_number} - {self.status}"


# ==========================================================
# DOCUMENT GUIDE TABLE
# (FOR COSINE SIMILARITY SEARCH)
# ==========================================================
class DocumentGuide(models.Model):

    guide_id = models.AutoField(primary_key=True)
    service_name = models.CharField(
        max_length=150
    )
    keywords = models.TextField(
        help_text='Comma separated keywords'
    )
    common_phrases = models.TextField(
        blank=True,
        null=True,
        help_text='User natural phrases for smart search'
    )
    required_documents = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'DocumentGuide'
        verbose_name = 'Document Guide'
        verbose_name_plural = 'Document Guides'
        ordering = ['guide_id']

    def __str__(self):
        return self.service_name

    def searchable_text(self):
        """
        Used for Cosine Similarity Matching
        """
        return f"{self.service_name} {self.keywords} {self.common_phrases or ''}"