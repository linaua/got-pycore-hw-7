from collections import UserDict
from datetime import datetime, timedelta, date

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return str(e) if str(e) else "Invalid input or argument missing."
    return inner

def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, *args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        self.value = self._validate_and_parse(value)

    @staticmethod
    def _validate_and_parse(date_str: str) -> date:
        date_format = "%d.%m.%Y"

        try:
            dt = datetime.strptime(date_str, date_format)
            if dt.date() > date.today():
                raise ValueError("Дата народження не може бути в майбутньому.")

            return dt.date()
        
        except ValueError:
            raise ValueError("Некоректний формат дати. Очікується DD.MM.YYYY")

class Name(Field):
    pass

class Phone(Field):
   def __init__(self, value):
       if not (value.isdigit() and len(value) == 10):
           raise ValueError("Номер телефону не складається з 10 цифр")
       super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]

    def find_phone(self, phone_number):
        for p in self.phones:
            if p.value == phone_number:
                return p
        return None

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Номер не знайдено")

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
    
    def __str__(self):
        bday_str = (
            f", birthday: {self.birthday}" if self.birthday else ""
        )
        phones_str = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = record.birthday.value
            birthday_this_year = bday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days
            if 0 <= days_until_birthday <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)
                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime(
                            "%d.%m.%Y"
                        ),
                    }
                )

        return upcoming_birthdays

@input_error
def add_contact(args, book: AddressBook):
        name, phone, *_ = args
        record = book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return f"{name}: {'; '.join(p.value for p in record.phones)}"

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())
    
@input_error
def add_birthday(args, book: AddressBook):
        name, bday = args
        record = book.find(name)
        if not record:
          return f"Контакт з ім'ям '{name}' не знайдено."
        record.add_birthday(bday)
        return f"День народження для {name} успішно додано."

@input_error
def show_birthday(args, book: AddressBook):
        (name,) = args
        record = book.find(name)
        if not record:
           return f"Контакт з ім'ям '{name}' не знайдено."
        if not record.birthday:
           return f"У контакту {name} не вказано день народження."
        return f"День народження {name}: {record.birthday}"

@input_error
def birthdays(args, book: AddressBook):
        upcoming = book.get_upcoming_birthdays()
        if not upcoming:
           return "На наступному тижні немає днів народження."
        result = []
        for user in upcoming:
            result.append(f"{user['name']}: {user['congratulation_date']}")
        return "\n".join(result)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_birthday("01.01.2000")
book.add_record(john_record)

print(book.find("John"))
print("Привітання цього тижня:", book.get_upcoming_birthdays)