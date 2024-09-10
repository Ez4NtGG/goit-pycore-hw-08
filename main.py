import pickle

class Contact:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return f"{self.name}: {self.phone}"

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, contact):
        self.contacts.append(contact)

    def __repr__(self):
        return "\n".join([str(contact) for contact in self.contacts])

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    
    while True:
        print("\nАдресна книга:")
        print(book)
        
        print("\nВведіть команду:")
        print("1. Додати контакт")
        print("2. Вийти")
        
        choice = input("Ваш вибір: ")
        
        if choice == "1":
            name = input("Введіть ім'я: ")
            phone = input("Введіть номер телефону: ")
            book.add_contact(Contact(name, phone))
        elif choice == "2":
            break
        else:
            print("Некоректний вибір. Спробуйте ще раз.")

    save_data(book)  # Викликати перед виходом з програми

if __name__ == "__main__":
    main()