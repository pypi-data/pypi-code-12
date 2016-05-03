from ArcUUID.ArcUUID import ArcUUID
import sys

hex_id = sys.argv[1]
print(str(ArcUUID.from_hex(hex_id)))
