from src.models import Tower, MSCVertex, User
from src.data_structures import TelephoneHashMap
from src.utils import calculate_distance, is_within_range, is_overlapping
from collections import deque

class Network:
    """
    Represents a single mobile network zone, managing its towers, MSC, and users.
    """
    def __init__(self, name, msc_pos=(0, 0)):
        self.name = name
        self.towers = {}  # {tower_name: Tower_object}
        self.graph_vertices = {} # {vertex_name: Vertex_object} for all graph nodes (towers + MSC)
        self.telephone_hash_map = TelephoneHashMap() # Central registry for users in this network
        self.msc = MSCVertex(f"{name}_MSC", msc_pos, self.telephone_hash_map)
        self._add_graph_vertex(self.msc) # Add MSC as a central node in the graph

    def _add_graph_vertex(self, vertex):
        """Helper to add any Vertex (Tower, MSC) to the internal graph representation."""
        if vertex.name in self.graph_vertices:
            print(f"Warning: Vertex '{vertex.name}' already exists in network {self.name}.")
            return False
        self.graph_vertices[vertex.name] = vertex
        return True

    def add_tower(self, tower_name, pos, height):
        """
        Adds a new tower to the network, ensuring no overlapping coverage.
        Args:
            tower_name (str): Unique name for the tower.
            pos (tuple): (x, y) coordinates of the tower.
            height (float): Height of the tower, influences coverage.
        Returns:
            Tower or None: The added Tower object if successful, None otherwise.
        """
        if not isinstance(tower_name, str) or not tower_name.strip():
            print("Error: Tower name cannot be empty.")
            return None
        if tower_name in self.towers:
            print(f"Error: Tower '{tower_name}' already exists in network '{self.name}'.")
            return None

        new_tower = Tower(tower_name, pos, height)

        # Check for overlapping coverage with existing towers
        for existing_tower in self.towers.values():
            if is_overlapping(new_tower.pos, new_tower.coverage_radius,
                              existing_tower.pos, existing_tower.coverage_radius):
                print(f"Error: Tower '{tower_name}' coverage overlaps with '{existing_tower.name}'. "
                      "Cannot add tower.")
                return None

        self.towers[tower_name] = new_tower
        self._add_graph_vertex(new_tower)

        # Connect new tower to MSC and vice versa in the graph (simplified model)
        # In a real network, towers connect to base station controllers, which then connect to MSC.
        # Here, we directly connect towers to MSC for call routing pathfinding.
        distance_to_msc = calculate_distance(new_tower.pos, self.msc.pos)
        new_tower.add_edge(self.msc, distance_to_msc)
        self.msc.add_edge(new_tower, distance_to_msc) # MSC also knows about the tower
        print(f"Tower '{tower_name}' added to network '{self.name}' with coverage radius {new_tower.coverage_radius:.2f}m.")
        return new_tower

    def register_user(self, user_name, phone_number, initial_pos):
        """
        Registers a new user to this network and attempts to connect them to the nearest tower.
        Args:
            user_name (str): User's name.
            phone_number (str): User's phone number (unique identifier).
            initial_pos (tuple): User's initial (x, y) position.
        Returns:
            User or None: The registered User object if successful, None otherwise.
        """
        if self.telephone_hash_map.get(phone_number):
            print(f"Error: User with phone number {phone_number} already registered in network '{self.name}'.")
            return None

        user = User(user_name, phone_number, initial_pos)
        self.telephone_hash_map.insert(phone_number, user)
        user.current_network = self
        print(f"User {user.name} ({user.phone_number}) registered to network '{self.name}'.")

        # Attempt to connect to the nearest tower
        self._connect_user_to_nearest_tower(user)
        return user

    def _connect_user_to_nearest_tower(self, user):
        """Internal method to find and connect a user to the nearest available tower."""
        nearest_tower = None
        min_distance = float('inf')

        for tower in self.towers.values():
            if is_within_range(user.position, tower.pos, tower.coverage_radius):
                distance = calculate_distance(user.position, tower.pos)
                if distance < min_distance:
                    min_distance = distance
                    nearest_tower = tower

        if nearest_tower:
            if user.current_tower and user.current_tower != nearest_tower:
                # Handover scenario
                print(f"Handover: User {user.name} moving from {user.current_tower.name} to {nearest_tower.name}")
                user.current_tower.disconnect_user(user)
                nearest_tower.connect_user(user)
            elif not user.current_tower:
                nearest_tower.connect_user(user)
            else:
                print(f"User {user.name} remains connected to {user.current_tower.name}.")
            return True
        else:
            if user.current_tower:
                user.current_tower.disconnect_user(user)
            user.current_tower = None
            print(f"User {user.name} ({user.phone_number}) is currently outside network '{self.name}' coverage.")
            return False

    def move_user(self, user_phone_number, new_pos):
        """
        Simulates user movement and handles tower handovers.
        Args:
            user_phone_number (str): The phone number of the user to move.
            new_pos (tuple): The new (x, y) position of the user.
        Returns:
            bool: True if user was moved, False otherwise.
        """
        user = self.telephone_hash_map.get(user_phone_number)
        if not user:
            print(f"Error: User with phone number {user_phone_number} not found in network '{self.name}'.")
            return False

        old_pos = user.position
        user.position = new_pos
        print(f"User {user.name} moved from {old_pos} to {new_pos}.")

        self._connect_user_to_nearest_tower(user)
        return True

    def _find_path_to_msc(self, start_tower):
        """
        Finds the path from a start_tower to the MSC using Breadth-First Search (BFS).
        Returns a list of vertices representing the path, or None if no path.
        """
        if not isinstance(start_tower, Tower) or start_tower.name not in self.graph_vertices:
            return None # Not a valid starting point in this graph

        # BFS for shortest path
        queue = deque()
        queue.append(start_tower)
        visited = {start_tower.name}
        parent_map = {start_tower.name: None}

        while queue:
            current_vertex = queue.popleft()

            if current_vertex == self.msc:
                # Path found, reconstruct
                path = []
                while current_vertex:
                    path.insert(0, current_vertex)
                    current_vertex = parent_map[current_vertex.name]
                return path

            for neighbor in current_vertex.get_neighbors():
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    parent_map[neighbor.name] = current_vertex
                    queue.append(neighbor)
        return None # No path found

    def make_call(self, caller_phone_number, receiver_phone_number):
        """
        Establishes a call between two users within the same network.
        Routes the call through their connected towers and the MSC.
        Args:
            caller_phone_number (str): Phone number of the calling user.
            receiver_phone_number (str): Phone number of the receiving user.
        Returns:
            bool: True if call is established, False otherwise.
        """
        caller = self.telephone_hash_map.get(caller_phone_number)
        receiver = self.telephone_hash_map.get(receiver_phone_number)

        if not caller:
            print(f"Error: Caller ({caller_phone_number}) not found in network '{self.name}'.")
            return False
        if not receiver:
            print(f"Error: Receiver ({receiver_phone_number}) not found in network '{self.name}'.")
            return False

        if caller == receiver:
            print("Error: Cannot call yourself.")
            return False

        if caller.call_status != "idle" or receiver.call_status != "idle":
            print(f"Error: One or both users are already on a call. Caller status: {caller.call_status}, Receiver status: {receiver.call_status}")
            return False

        if not caller.current_tower:
            print(f"Call failed: Caller {caller.name} is outside network coverage.")
            return False
        if not receiver.current_tower:
            print(f"Call failed: Receiver {receiver.name} is outside network coverage.")
            return False

        print(f"\nAttempting call from {caller.name} ({caller_phone_number}) to {receiver.name} ({receiver_phone_number})...")

        # Path for caller to MSC
        path_caller_to_msc = self._find_path_to_msc(caller.current_tower)
        if not path_caller_to_msc:
            print(f"Call failed: No path found from caller's tower ({caller.current_tower.name}) to MSC.")
            return False

        # Path for MSC to receiver
        path_msc_to_receiver = self._find_path_to_msc(receiver.current_tower)
        if not path_msc_to_receiver:
            print(f"Call failed: No path found from MSC to receiver's tower ({receiver.current_tower.name}).")
            return False

        # Construct full call path
        # The path from MSC to receiver's tower is typically the reverse of receiver's tower to MSC.
        # So, we reverse the receiver's path to get MSC -> ... -> receiver_tower
        full_call_path = path_caller_to_msc + path_msc_to_receiver[::-1][1:] # [1:] to avoid duplicating MSC
        path_names = " -> ".join([v.name for v in full_call_path])

        print(f"Call established! Routing path: {path_names}")
        caller.call_status = "calling"
        receiver.call_status = "receiving"
        caller.call_partner = receiver
        receiver.call_partner = caller
        return True

    def end_call(self, user_phone_number):
        """Ends a call involving the specified user."""
        user = self.telephone_hash_map.get(user_phone_number)
        if not user:
            print(f"Error: User {user_phone_number} not found.")
            return False

        if user.call_status == "idle":
            print(f"User {user.name} is not on a call.")
            return False

        partner = user.call_partner
        if partner:
            print(f"Call between {user.name} and {partner.name} ended.")
            user.call_status = "idle"
            user.call_partner = None
            partner.call_status = "idle"
            partner.call_partner = None
            return True
        else:
            print(f"Error: User {user.name} in call state {user.call_status} but no partner found.")
            user.call_status = "idle" # Reset just in case
            return False

    def display_network_info(self):
        """Prints details about the network, its towers, and connected users."""
        print(f"\n--- Network: {self.name} ---")
        print(f"  MSC: {self.msc}")
        print(f"  Towers ({len(self.towers)}):")
        if not self.towers:
            print("    No towers added yet.")
        for tower in self.towers.values():
            print(f"    - {tower}")
            if tower.connected_users:
                print(f"      Connected Users ({len(tower.connected_users)}):")
                for user_phone, user_obj in tower.connected_users.items():
                    print(f"        - {user_obj.name} ({user_obj.phone_number}) at {user_obj.position}")
            else:
                print("      No users connected.")
        print(f"  Registered Users ({len(self.telephone_hash_map)}):")
        if len(self.telephone_hash_map) == 0:
            print("    No users registered yet.")
        else:
            for user in self.telephone_hash_map.get_all_users():
                print(f"    - {user}")

class NetworkList:
    """
    Manages a collection of different network zones.
    """
    def __init__(self):
        self.networks = {} # {network_name: Network_object}

    def add_network(self, network_name, msc_pos=(0, 0)):
        """Adds a new network zone to the system."""
        if network_name in self.networks:
            print(f"Error: Network '{network_name}' already exists.")
            return None
        new_network = Network(network_name, msc_pos)
        self.networks[network_name] = new_network
        print(f"Network '{network_name}' created.")
        return new_network

    def get_network(self, network_name):
        """Retrieves a network by its name."""
        return self.networks.get(network_name)

    def display_all_networks(self):
        """Displays summary information for all networks."""
        if not self.networks:
            print("\nNo networks created yet.")
            return
        print("\n--- All Networks Summary ---")
        for name, net in self.networks.items():
            print(f"- Network: {name}, Towers: {len(net.towers)}, Users: {len(net.telephone_hash_map)}")