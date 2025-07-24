class TelephoneHashMap:
    """
    Implements a hash map for quick user lookup using phone numbers.
    Each bucket is a list to handle collisions.
    """
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

    def _hash(self, key):
        """Simple hash function based on the sum of digits in the phone number."""
        if not isinstance(key, str) or not key.isdigit():
            raise ValueError("Phone number must be a string of digits.")
        return sum(int(digit) for digit in key) % self.capacity

    def insert(self, key, value):
        """
        Inserts a key-value pair into the hash map.
        Args:
            key (str): The phone number (user ID).
            value (User object): The User object to store.
        """
        index = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key:
                self.buckets[index][i] = (key, value) # Update if key exists
                return
        self.buckets[index].append((key, value))
        self.size += 1

    def get(self, key):
        """
        Retrieves the value associated with a given key.
        Args:
            key (str): The phone number (user ID).
        Returns:
            User object or None: The User object if found, else None.
        """
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return None

    def remove(self, key):
        """
        Removes a key-value pair from the hash map.
        Args:
            key (str): The phone number (user ID).
        Returns:
            User object or None: The removed User object if found, else None.
        """
        index = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key:
                del self.buckets[index][i]
                self.size -= 1
                return v
        return None

    def __len__(self):
        return self.size

    def __str__(self):
        items = []
        for i, bucket in enumerate(self.buckets):
            if bucket:
                items.append(f"Bucket {i}: {[(k, v.name if hasattr(v, 'name') else 'N/A') for k, v in bucket]}")
        return "\n".join(items)

    def get_all_users(self):
        """Returns a list of all user objects stored in the hash map."""
        all_users = []
        for bucket in self.buckets:
            for _, user_obj in bucket:
                all_users.append(user_obj)
        return all_users