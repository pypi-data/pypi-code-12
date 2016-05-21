from csgo.enums import ECsgoGCMsg

class Player(object):
    def __init__(self):
        super(Player, self).__init__()

        # register our handlers
        self.on(ECsgoGCMsg.EMsgGCCStrike15_v2_PlayersProfile, self.__handle_player_profile)

    def request_player_profile(self, account_id, request_level=32):
        """
        Request player profile

        :param account_id: account id
        :type account_id: :class:`int`
        :param request_level: no clue what this is used for; if you do, please make pull request
        :type request_level: :class:`int`

        Response event: ``player_profile``

        :param message: `CMsgGCCStrike15_v2_MatchmakingGC2ClientHello <https://github.com/ValvePython/csgo/blob/master/protobufs/cstrike15_gcmessages.proto#L456>`_ proto message

        """
        self.send(ECsgoGCMsg.EMsgGCCStrike15_v2_ClientRequestPlayersProfile, {
                    'account_id': account_id,
                    'request_level': request_level,
                 })

    def __handle_player_profile(self, message):
        if message.account_profiles:
            self.emit("player_profile", message.account_profiles[0])
