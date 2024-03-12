from contact import Email, PhoneNumber
import pytest

def test_email_is_valid():
    email = Email("emiryegnidemir@hotmail.com")
    assert email.email is not None

def test_email_fields_are_valid():
    email = Email("test@hotmail.com")
    assert email.email == "test@hotmail.com"
    assert email.local_part == "test"
    assert email.domain == "hotmail.com"

def test_phone_number_is_valid():
    phone_number = PhoneNumber("+14155552671")
    assert phone_number.phone_number is not None

def test_phone_number_fields_are_valid():
    phone_number = PhoneNumber("+14155552671")
    assert phone_number.phone_number == "+14155552671"
    assert phone_number.country_code == 1
    assert phone_number.national_number == 4155552671

def test_invalid_phone_number():
    with pytest.raises(ValueError):
        PhoneNumber("invalid_phone_number")
   