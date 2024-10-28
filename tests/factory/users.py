from faker import Faker

fake = Faker()


def create_fake_user():
    password = fake.password(length=12)
    email = fake.email()
    return {
        "password": password,
        "email": email,
    }
