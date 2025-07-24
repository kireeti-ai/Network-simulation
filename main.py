from src.network import NetworkList
import sys

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_pos_input(prompt):
    while True:
        try:
            coords = input(prompt).strip().split(',')
            if len(coords) == 2:
                x = float(coords[0].strip())
                y = float(coords[1].strip())
                return (x, y)
            else:
                print("Invalid format. Please enter coordinates as 'x,y' (e.g., 10,20).")
        except ValueError:
            print("Invalid coordinate values. Please enter numbers.")

def main():
    network_list = NetworkList()
    current_network = None

    print("--- Mobile Network Simulation System ---")

    # Initial network setup
    num_networks = get_int_input("Enter the number of networks to create: ")
    for i in range(num_networks):
        name = input(f"Enter name for Network {i+1}: ").strip()
        if not name:
            print("Network name cannot be empty. Skipping network creation.")
            continue
        msc_x = get_float_input(f"Enter MSC X-coordinate for Network '{name}': ")
        msc_y = get_float_input(f"Enter MSC Y-coordinate for Network '{name}': ")
        new_net = network_list.add_network(name, (msc_x, msc_y))
        if not current_network and new_net: # Set first created network as current
            current_network = new_net

    if not current_network:
        print("No networks created. Exiting.")
        sys.exit()

    print(f"\nCurrently active network: {current_network.name}")

    while True:
        print("\n--- Main Menu ---")
        print(f"Active Network: {current_network.name}")
        print("1. Add Tower")
        print("2. Register User")
        print("3. Move User")
        print("4. Make Call")
        print("5. End Call")
        print("6. Switch Network")
        print("7. Display Current Network Info")
        print("8. Display All Network Summary")
        print("9. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            tower_name = input("Enter tower name: ").strip()
            if not tower_name:
                print("Tower name cannot be empty.")
                continue
            pos = get_pos_input("Enter tower position (x,y): ")
            height = get_float_input("Enter tower height (e.g., 50): ")
            current_network.add_tower(tower_name, pos, height)

        elif choice == '2':
            user_name = input("Enter user name: ").strip()
            if not user_name:
                print("User name cannot be empty.")
                continue
            phone_number = input("Enter user phone number: ").strip()
            if not phone_number.isdigit() or len(phone_number) < 7:
                print("Invalid phone number. Must be digits only and at least 7 digits long.")
                continue
            initial_pos = get_pos_input("Enter user initial position (x,y): ")
            current_network.register_user(user_name, phone_number, initial_pos)

        elif choice == '3':
            phone_number = input("Enter user phone number to move: ").strip()
            new_pos = get_pos_input("Enter new user position (x,y): ")
            current_network.move_user(phone_number, new_pos)

        elif choice == '4':
            caller_phone = input("Enter caller's phone number: ").strip()
            receiver_phone = input("Enter receiver's phone number: ").strip()
            current_network.make_call(caller_phone, receiver_phone)

        elif choice == '5':
            user_phone = input("Enter phone number of user to end call for: ").strip()
            current_network.end_call(user_phone)

        elif choice == '6':
            network_name = input("Enter network name to switch to: ").strip()
            new_network = network_list.get_network(network_name)
            if new_network:
                current_network = new_network
                print(f"Switched to network: {current_network.name}")
            else:
                print(f"Network '{network_name}' not found.")

        elif choice == '7':
            current_network.display_network_info()

        elif choice == '8':
            network_list.display_all_networks()

        elif choice == '9':
            print("Exiting Mobile Network Simulation. Goodbye!")
            sys.exit()

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()