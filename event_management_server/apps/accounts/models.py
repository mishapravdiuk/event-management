from typing import Optional

from api.api_core.schemas.accounts_schemas import AccountSchema
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def _check_extra_required_fields(self, **extra_fields):
        if "first_name" not in extra_fields:
            raise TypeError("Users should have a first name")
        if "last_name" not in extra_fields:
            raise TypeError("Users should have a last name")

    def create_user(self, email=None, password=None, **extra_fields):
        self._check_extra_required_fields(**extra_fields)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        self._check_extra_required_fields(**extra_fields)

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255,
        null=True,
        db_index=True,
        verbose_name="Email",
        unique=True,
    )
    phone_number = PhoneNumberField(
        verbose_name="Phone number",
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="First name",
        blank=True,
        default="",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Last name",
        blank=True,
        default="",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is active",
        help_text="Indication that user is active",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Is staff",
        help_text="Indication that user is a staff",
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name="Is admin",
        help_text="Indication that user is admin of current radio"
        " station, and can add DJ to that one",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def user_role(self):
        if self.is_superuser:
            return "Superuser"
        elif self.is_admin:
            return "Admin"
        elif self.is_staff:
            return "Staff"
        else:
            return "Customer"

    class Meta:
        db_table = "Users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def to_pydantic(self) -> AccountSchema:
        phone: Optional[str] = None
        try:
            phone = str(self.phone_number) if self.phone_number else None
        except Exception:
            phone = None

        return AccountSchema(
            id=self.id,
            email=self.email,
            phone=phone,
            first_name=self.first_name,
            last_name=self.last_name,
        )
