from GamePlayer import Game, Player

# 单局玩家数量
numPlayers = 2
# 小盲下注的最小筹码数
smallBlindBaseBet = 10


class PokerAnalyzer:
    tokens = 1000
    players = []

    def __init__(self):
        for i in range(numPlayers):
            player = Player(self.tokens)
            self.players.append(player)

        max_tokens = self.tokens * numPlayers
        while self.players[0].tokens < max_tokens:
            game = Game(self.players)
            game.start_game()
            self.players.sort(key=lambda x: x.tokens, reverse=True)


poker_analyzer = PokerAnalyzer()
