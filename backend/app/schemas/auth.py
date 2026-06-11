import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegisterIn(BaseModel):
    email: EmailStr
    # ✅ Валидация: минимум 8 символов, максимум 128
    # ⛔ БЫЛО: password: str (принимал пароль "1"!)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255, strip_whitespace=True)
    referral_code: str | None = Field(None, max_length=20)
    
    # ✅ Поле role УДАЛЕНО — роль назначается только сервером!
    # ⛔ БЫЛО: role: str = "buyer"  → можно было передать "superadmin"!

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Проверка сложности пароля"""
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Имя слишком короткое")
        return v.strip()


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """✅ Ответ с профилем пользователя — не включает password_hash!"""
    id: int
    email: str
    full_name: str
    role: str
    referral_code: str
    is_active: bool
    
    model_config = {"from_attributes": True}