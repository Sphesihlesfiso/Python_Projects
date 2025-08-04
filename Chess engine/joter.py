class Animal:
    def __init__(self, name):
        self.name = name  # ← this is an attribute

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # inherits name setup
        self.breed = breed      # new attribute for Dog

d = Dog("Buddy", "Labrador")
print(d.name)   # Buddy  ← inherited!
print(d.breed)  # Labrador
