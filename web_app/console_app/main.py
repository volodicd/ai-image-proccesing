# main.py
from cities import display_cities

def main():
    while True:
        print("\n1. Display cities")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            display_cities()
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
