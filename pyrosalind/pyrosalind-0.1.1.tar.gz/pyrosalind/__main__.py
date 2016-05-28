from pyrosalind import User


if __name__ == "__main__":
    USER = 'aluriak'


    aluriak = User.from_name(USER)
    print(aluriak)
    print(aluriak.solved)
