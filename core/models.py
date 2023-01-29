from product.models import JobRole
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):

    def create_user(self, email, first_name, middle_name, last_name, password, employee_id, **kw):
        if not email:
            raise ValueError('The given email address must be set')
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            middle_name = middle_name,
            employee_id = employee_id,
            **kw
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, middle_name, last_name, password, employee_id, **kw):

        user = self.create_user(email, first_name, middle_name, last_name, password, employee_id, **kw)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default = uuid.uuid4, editable = False)
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    first_name = models.CharField(max_length=240)
    middle_name =  models.CharField(max_length=120)
    last_name =  models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    employee_id = models.CharField(max_length=120)
    joined_on = models.DateTimeField(blank=True, null=True)
    job_role = models.ForeignKey(JobRole, to_field="job_role", db_column="job_role", on_delete=models.DO_NOTHING, null=True)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'