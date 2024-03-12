from dataclasses import dataclass
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

@dataclass(frozen=True)
class Email:
    _email: str

    def __post_init__(self):
        try:
            v = validate_email(self._email)
        except EmailNotValidError as e:
            raise ValueError("Invalid email") from e

    @property
    def email(self):
        return self._email

    @property
    def local_part(self):
        return validate_email(self._email)["local"].lower()

    @property
    def domain(self):
        return validate_email(self._email)["domain"].lower()

    @property
    def domain_name(self):
        return self.domain.rsplit('.', 1)[0]

    @property
    def top_level_domain(self):
        return self.domain.rsplit('.', 1)[1]

@dataclass(frozen=True)
class PhoneNumber:
    _phone_number: str

    def __post_init__(self):
        try:
            parsed_number = phonenumbers.parse(self._phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")
            object.__setattr__(self, '_parsed_number', parsed_number)
        except NumberParseException:
            raise ValueError("Invalid phone number")

    @property
    def phone_number(self):
        return self._phone_number

    @property
    def country_code(self):
        return self._parsed_number.country_code

    @property
    def national_number(self):
        return self._parsed_number.national_number