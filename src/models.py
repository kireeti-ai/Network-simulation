from collections import deque
from src.utils import calculate_distance, is_within_range

class Stack:
    """
    Implements a basic Stack using Python's deque (doubly-ended queue) for efficiency.
    """
    def __init__(self):
        self._items = deque()

    def push(self, item):
        """Adds an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Removes and returns the item from the top of the stack.
        Raises IndexError if the stack is empty."""
        if not self.is_empty():
            return self._items.pop()
        raise IndexError("pop from empty stack")

    def peek(self):
        """Returns the item at the top of the stack without removing it.
        Raises IndexError if the stack is empty."""
        if not self.is_empty():
            return self._items[-1]
        raise IndexError("peek from empty stack")

    def is_empty(self):
        """Checks if the stack is empty."""
        return len(self._items) == 0

    def size(self):
        """Returns the number of items in the stack."""
        return len(self._items)

    def display(self):
        """Displays the contents of the stack from top to bottom."""
        if self.is_empty():
            print("Stack is empty.")
        else:
            print("Stack (Top to Bottom):", list(self._items)[::-1])

class Edge:
    """Represents a connection (edge) between two vertices (towers)."""
    def __init__(self, origin, destination, distance=0):
        self.origin = origin          # Vertex object (Tower or MSC)
        self.destination = destination # Vertex object (Tower or MSC)
        self.distance = distance      # Distance between origin and destination

    def __repr__(self):
        return f"Edge({self.origin.name} -> {self.destination.name}, dist={self.distance:.2f})"

class Vertex:
    """
    Represents a generic node in the network graph (e.g., a Tower or an MSC).
    """
    def __init__(self, name, pos, type="generic"):
        self.name = name
        self.pos = pos  # (x, y) coordinates
        self.type = type
        self.adjacencies = {} # {Vertex: Edge_object}

    def add_edge(self, neighbor, distance):
        """Adds an edge to a neighbor."""
        edge = Edge(self, neighbor, distance)
        self.adjacencies[neighbor] = edge

    def get_neighbors(self):
        """Returns a list of neighboring vertices."""
        return list(self.adjacencies.keys())

    def get_edge_to(self, neighbor):
        """Returns the edge connecting to a specific neighbor."""
        return self.adjacencies.get(neighbor)

    def __repr__(self):
        return f"{self.type}({self.name}, Pos={self.pos})"

class Tower(Vertex):
    """
    Represents a mobile network tower.
    Coverage radius is calculated based on height.
    """
    BASE_COVERAGE_FACTOR = 50 # Meters per unit of height, example value

    def __init__(self, name, pos, height):
        super().__init__(name, pos, type="Tower")
        if not isinstance(height, (int, float)) or height <= 0:
            raise ValueError("Tower height must be a positive number.")
        self.height = height
        self.coverage_radius = self.height * self.BASE_COVERAGE_FACTOR
        self.connected_users = {} # {phone_number: User_object}

    def get_coverage_area(self):
        return self.coverage_radius

    def connect_user(self, user):
        if user.phone_number not in self.connected_users:
            self.connected_users[user.phone_number] = user
            print(f"User {user.name} ({user.phone_number}) connected to Tower {self.name}.")
            user.current_tower = self
            return True
        return False

    def disconnect_user(self, user):
        if user.phone_number in self.connected_users:
            del self.connected_users[user.phone_number]
            print(f"User {user.name} ({user.phone_number}) disconnected from Tower {self.name}.")
            user.current_tower = None
            return True
        return False

    def __repr__(self):
        return f"Tower({self.name}, Pos={self.pos}, Height={self.height}, Coverage={self.coverage_radius:.2f}m)"


class MSCVertex(Vertex):
    """
    Represents a Mobile Switching Center (MSC).
    It manages the central user directory for call routing within its network zone.
    """
    def __init__(self, name, pos, telephone_hash_map):
        super().__init__(name, pos, type="MSC")
        if not isinstance(telephone_hash_map, object) or not hasattr(telephone_hash_map, 'insert'):
            raise TypeError("telephone_hash_map must be an instance of TelephoneHashMap or similar.")
        self.registered_users = telephone_hash_map # Reference to the network's user registry
        self.connected_towers = {} # {Tower_name: Tower_object} - not all towers connect to MSC directly
                                   # this is more for conceptual routing than direct physical connection graph
    def __repr__(self):
        return f"MSC({self.name}, Pos={self.pos}, Users={len(self.registered_users)})"

class User:
    """
    Represents a mobile network user.
    """
    def __init__(self, name, phone_number, initial_pos):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("User name cannot be empty.")
        if not isinstance(phone_number, str) or not phone_number.isdigit() or len(phone_number) < 7: # Basic phone number validation
            raise ValueError("Phone number must be a string of digits and at least 7 digits long.")
        if not isinstance(initial_pos, tuple) or len(initial_pos) != 2:
            raise ValueError("Initial position must be a tuple (x, y).")

        self.name = name
        self.phone_number = phone_number
        self._position = initial_pos # Stored internally
        self.current_network = None # Reference to the Network object
        self.current_tower = None   # Reference to the Tower object they are connected to
        self.call_status = "idle"   # "idle", "calling", "receiving"
        self.call_partner = None    # Reference to another User object

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_pos):
        if not isinstance(new_pos, tuple) or len(new_pos) != 2:
            raise ValueError("New position must be a tuple (x, y).")
        self._position = new_pos
        # In a real system, moving the user would trigger a check for tower handover.
        # This will be handled in the Network class's user movement logic.

    def __repr__(self):
        tower_name = self.current_tower.name if self.current_tower else "None"
        network_name = self.current_network.name if self.current_network else "None"
        return (f"User(Name={self.name}, Phone={self.phone_number}, Pos={self.position}, "
                f"ConnectedTower={tower_name}, Network={network_name}, Status={self.call_status})")