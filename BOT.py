import pickle
import os
from datetime import datetime, timedelta

# Decorator to handle input errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except IndexError:
            return "Please provide all necessary arguments."
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper

# Base field class
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Name class
class Name(Field):
    pass

# Phone class
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

# Birthday class
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Record class (enhanced with email)
class Record:
    def __init__(self, name, phone=None, email=""):
        self.name = Name(name)
        self.phones = []
        if phone:
            self.add_phone(phone)
        self.email = email
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                found = True
                break
        if not found:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(str(phone) for phone in self.phones)
        email_info = f", email: {self.email}" if self.email else ""
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"{self.name}: {phones}{email_info}{birthday}"

# AddressBook class (with save/load functionality)
class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    # Adjust for weekends
                    if birthday_this_year.weekday() >= 5:  # Saturday (5) or Sunday (6)
                        days_to_add = 7 - birthday_this_year.weekday()
                        birthday_this_year += timedelta(days=days_to_add)

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays

    def save_to_file(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    def load_from_file(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                self.data = pickle.load(f)
        except (FileNotFoundError, pickle.PickleError):
            self.data = {}  # Return empty address book in case of error

    def __repr__(self):
        if not self.data:
            return "Address book is empty"
        return "\n".join([f"{i+1}. {record}" for i, record in enumerate(self.data.values())])

# Command handlers
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *rest = args
    email = rest[0] if rest else ""
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name, phone, email)
        book.add_record(record)
        message = "Contact added."
    else:
        if phone:
            record.add_phone(phone)
        if email:
            record.email = email
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise ValueError(f"Contact {name} not found.")

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.phones:
        return f"{name}: {', '.join(str(phone) for phone in record.phones)}"
    else:
        raise ValueError(f"No phone found for {name}.")

@input_error
def show_all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        raise ValueError(f"Contact {name} not found.")

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday.value}"
    else:
        raise ValueError(f"No birthday found for {name}.")

@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    return "\n".join(f"{entry['name']}: {entry['birthday']}" for entry in upcoming)

def parse_input(user_input):
    if not user_input.strip():  # Handle empty input
        return "", []
    parts = user_input.split()
    return parts[0].lower(), parts[1:]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    book = AddressBook()
    book.load_from_file()
    
    print("Welcome to the enhanced assistant bot!")
    while True:
        user_input = input("\nEnter a command (or 'menu' for options): ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() == "menu":
            clear_screen()
            print("\nAvailable commands:")
            print("1. hello - Greet the bot")
            print("2. add <name> <phone> [email] - Add or update contact")
            print("3. change <name> <old_phone> <new_phone> - Change phone number")
            print("4. phone <name> - Show phone number(s) for contact")
            print("5. all - Show all contacts")
            print("6. add-birthday <name> <DD.MM.YYYY> - Add birthday")
            print("7. show-birthday <name> - Show birthday")
            print("8. birthdays - Show upcoming birthdays")
            print("9. exit/close - Save and exit")
            continue
            
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_to_file()
            print("Data saved. Good bye!")
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
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command. Type 'menu' to see available commands.")

if __name__ == "__main__":
    main()