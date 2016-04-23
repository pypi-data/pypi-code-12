import random

class ServerConfiguration(object):
    DESCRIPTION = (                  
        ("nightlengthmodifier", float, 1.0),
        ("PVP", bool, True),
        ("PauseEmpty", bool, False),
        ("GlobalChat", bool, True),
        ("Open", bool, True),
        ("ServerWelcomeMessage", str, " <RGB:1,0,0> Welcome to Project Zomboid MP ! to chat locally press \"t\", to global chat press \"y\" or add \"/all\" before chatting <LINE> Press /help to have a list of server commands <LINE> <RGB:1,1,1> "),        
        ("LogLocalChat", bool, False),
        ("AutoCreateUserInWhiteList", bool, False),
        ("DisplayUserName", bool, True),
        ("SpawnPoint", str, "0,0,0"),
        ("SafetySystem", bool, True),
        ("ShowSafety", bool, True),
        ("SafetyToggleTimer", int, 100),
        ("SafetyCooldownTimer", int, 120),
        ("SpawnItems", str, ""),
        ("DefaultPort", int, 16261),
        ("ResetID", int, random.randint(42,1000000000)),
        ("Mods", str, ""),
        ("Map", str, "Muldraugh, KY"),
        ("SpawnRegions", str, ""),
        ("DoLuaChecksum", bool, True),
        ("Public", bool, False),
        ("PublicName", str, "My PZ Server"),
        ("PublicDescription", str, ""),
        ("MaxPlayers", int, 64),
        ("PingFrequency", int, 10),
        ("PingLimit", int, 400),
        ("HoursForLootRespawn", int, 0),
        ("MaxItemsForLootRespawn", int, 4),
        ("ConstructionPreventsLootRespawn", bool, True),
        ("DropOffWhiteListAfterDeath", bool, False),
        ("NoFireSpread", bool, False),
        ("NoFire", bool, False),
        ("AnnounceDeath", bool, False),
        ("MinutesPerPage", float, 1.0),
        ("HoursForCorpseRemoval", int, 0),
        ("SaveWorldEveryMinutes", int, 0),
        ("PlayerSafehouse", bool, False),
        ("AdminSafehouse", bool, False),
        ("SafehouseAllowTrepass", bool, True),
        ("SafehouseAllowFire", bool, True),
        ("SafehouseAllowLoot", bool, True),
        ("SafehouseAllowRespawn", bool, False),
        ("SafehouseDaySurvivedToClaim", int, 0),
        ("SafeHouseRemovalTime", int, 144),
        ("AllowDestructionBySledgehammer", bool, True),
        ("KickFastPlayers", bool, False),
        ("ServerPlayerID", int, random.randint(42,0x7fffffff)),
        ("RCONPort", int, 27015),
        ("RCONPassword", str, ""),
        ("Password", str, ""),
        ("MaxAccountsPerUser", int, 0),
        
        ("SteamPort1", int, 8766),
        ("SteamPort2", int, 8767),
        ("WorkshopItems", str, ""),
        ("SteamScoreboard", bool, True),
        ("SteamVAC", bool, True),
    )

    def __init__(self):
        self.values = {}
        for n,t,d in ServerConfiguration.DESCRIPTION:
            self.values[n] = t(d)
        
    def get_description(self, key):
        for n,t,d in ServerConfiguration.DESCRIPTION:
            if n == key:
                return n,t,d
        return None

    def read(self, fp):
        for line in fp.readlines():
            line = line.strip()
            if not "=" in line:
                continue
            name, value = [ i.strip() for i in line.split("=",1) ]
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            self.values[name] = value

    def write(self, fp):
        for k,v in self.values.items():
            if type(v) is bool:
                fp.write("%s=%s\r\n" % (k,"true" if v else "false"))
            else:
                fp.write("%s=%s\r\n" % (k,v))

    def get(self, name, default=None):
        return self.values.get(name, default)

    def __contains__(self, key):
        return self.values.__contains__(key)

    def __getitem__(self, key):
        return self.values.__getitem__(key)

    def __setitem__(self, key, value):
        desc = self.get_description(key)
        if desc is None:
            raise Exception("unknown key '%s'" % key)
        self.values.__setitem__(key, value)