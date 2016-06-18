import ormithorynque
   
database = ormithorynque.Database(":memory:", debug_sql = True)


class Person(database.Object):
  name       = database.SQLAttribute(str, indexed = True)
  first_name = database.SQLAttribute(str)
  age        = database.SQLAttribute(int)

jiba = Person(name = "Lamy", first_name="Jean-Baptiste", age = 36)


jiba.age = 37


class House(database.Object):
  address = database.SQLAttribute("Nowhere") # String attribute with a default value
  owner   = database.SQLAttribute(object)
   
class Person(database.Object):
  name       = database.SQLAttribute(str, indexed = True)
  first_name = database.SQLAttribute(str)
  age        = database.SQLAttribute(int)
  houses     = database.SQLOneToMany("House", "owner")

someone = Person(name = "Some", first_name="One")
house1 = House(address = "Somewhere", owner = someone)
house2 = House(address = "Somewhere else")


class House(database.Object):
  address     = database.SQLAttribute("Nowhere") # String attribute with a default value
  owner       = database.SQLAttribute(object)
  inhabitants = database.SQLManyToMany("inhabitant", "lives_in")
   
class Person(database.Object):
  name        = database.SQLAttribute(str, indexed = True)
  first_name  = database.SQLAttribute(str)
  age         = database.SQLAttribute(int)
  houses      = database.SQLOneToMany("House", "owner")
  lives_in    = database.SQLManyToMany("lives_in", "inhabitant")

someone1 = Person(name = "Some", first_name="One")
someone2 = Person(name = "Some", first_name="Two")
   
house1 = House(address = "Somewhere")
house2 = House(address = "Somewhere else")

someone1.add_lives_in(house1)
house1.add_inhabitant(someone2)

print(database.select_one("select max(age) from Person"))
print(database.select_one("select count(id) from Person"))

class Teacher(Person):
  domain = database.SQLAttribute(str)

class Student(Person):
  grade = database.SQLAttribute(str)

class PhD(Student, Teacher):
  year = database.SQLAttribute(1)

phd = PhD(name = "Ph", first_name = "D", year = 3, domain = "computer science", grade = "high school")


class Museum(database.Object):
  name = database.SQLAttribute(str)

class Room(database.Object):
  name   = database.SQLAttribute(str)
  museum = database.SQLAttribute(object)

class Artwork(database.Object):
  title  = database.SQLAttribute(str)
  artist = database.SQLAttribute(str)

class DecoratedRoom(Room, Artwork):
  architect  = database.SQLAttribute(str)

my_museum = Museum(name = "My virtual museum")
my_decorated_room = DecoratedRoom(museum = my_museum, name = "Collumn gallery", title = "Column gallery", artist = "de Vinci", architect = "Vitruve")
