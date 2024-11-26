from faker import Faker

fake = Faker()


def create_fake_plan():
    fake_data = {
        "id": fake.random_int(min=1000, max=9999),
        "name": fake.company(),
        "description": fake.text(max_nb_chars=100),
        "price": fake.random_number(digits=2) + 0.00,
        "durationDays": fake.random_int(min=7, max=365),
        "currency": fake.currency_code(),
        "features": fake.sentence(nb_words=5),
        "isActive": fake.boolean(),
        "trialDays": fake.random_int(min=0, max=30),
    }
    return fake_data