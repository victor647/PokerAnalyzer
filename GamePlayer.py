import itertools
import random
import Tools
import MatchFinder
from PokerAnalyzer import smallBlindBaseBet, numPlayers


# 玩家策略，随着游戏进行动态调整
class PlayerStrategy:
    # 牌力小于多少时会弃牌
    foldPowerThreshold = 0
    # 当投入大于多少时不会弃牌
    foldBetThreshold = 0
    # 牌力大于多少时会加注
    raisePowerThreshold = 0
    # 成牌概率大于多少时会加注
    raiseProbabilityThreshold = 0
    # 成牌概率大于多少时会梭哈
    allInProbabilityThreshold = 0

    def __init__(self):
        self.generate_random_strategy()

    # 随机生成策略
    def generate_random_strategy(self):
        self.foldPowerThreshold = random.randrange(10, 40)
        self.foldBetThreshold = random.randrange(20, 200)
        self.allInProbabilityThreshold = random.randrange(50)

    # 玩法更加保守
    def play_less_aggressive(self):
        self.foldPowerThreshold = min(40, self.foldPowerThreshold + 4)
        self.allInProbabilityThreshold = max(0, self.allInProbabilityThreshold - 5)

    # 玩法更加激进
    def play_more_aggressive(self):
        self.foldPowerThreshold = max(10, self.foldPowerThreshold - 4)
        self.allInProbabilityThreshold = min(50, self.allInProbabilityThreshold + 5)


# 玩家信息
class Player:
    # 手牌
    handCards = []
    # 筹码
    tokens = 0
    # 牌力
    power = 0
    # 牌型
    strengths = []
    # 位置，0为小盲，1为大盲
    position = 0
    # 策略
    strategy = PlayerStrategy()

    def __init__(self, tokens: int):
        self.tokens = tokens

    # 下盲注
    def preflop_bet(self, call_token: int):
        if self.position == 0:
            self.tokens -= call_token

    # 计算底牌牌力
    def calculate_card_power(self):
        self.handCards.sort(key=lambda x: x[1], reverse=True)
        self.power = self.handCards[0][1] + self.handCards[1][1]

        if self.handCards[0][0] == self.handCards[1][0]:
            self.power = max(self.power * 2, self.power + 10)
            self.strengths.append('同花')

        difference = abs(self.handCards[0][1] - self.handCards[1][1])
        if difference == 0:
            self.power = max(self.power * 2, self.power + 10)
            self.strengths.append('对子')
        elif difference < 5:
            self.power = max(self.power * 1.5, self.power + 5)
            self.strengths.append('顺子')

        if self.handCards[0][1] > 10:
            difference = self.handCards[0][1] - 10
            factor = 1 + difference * 0.1
            self.power = max(self.power * factor, self.power + difference)
            self.strengths.append('高牌')
        self.power = round(self.power)


# 单局游戏信息
class Game:
    # 剩余没翻出的牌
    remainingCards = list(itertools.product(['♥', '♦', '♠', '♣'], range(2, 15)))
    # 玩家信息
    players = []
    # 已翻出的公共牌
    communityCards = []
    # 翻牌
    flopCards = []
    # 转牌
    turnCard = None
    # 河牌
    riverCard = None
    # 总计投入的筹码
    totalTokens = 0
    # 单轮需要的筹码
    roundTokens = 0

    def __init__(self, players: list):
        if 2 <= len(players) <= 9:
            self.players = players
            self.start_game()

    # 开始游戏
    def start_game(self):
        self.shuffle_positions()
        # 洗牌
        random.shuffle(self.remainingCards)
        self.preflop_round()
        self.flop_round()
        self.river_round()
        self.calculate_results()

    # 更换大小盲
    def shuffle_positions(self):
        self.players = self.players[-1] + self.players[:-1]
        for i in range(len(self.players)):
            self.players[i].position = i

    # 翻牌前回合
    def preflop_round(self):
        i = 1
        for player in self.players:
            # 发玩家手牌
            player.handCards = (self.remainingCards[:2])
            self.remainingCards = self.remainingCards[2:]
            player.calculate_card_power()
            print('玩家{}的手牌：{}，牌力：{}'.format(i, Tools.display_cards(player.handCards), player.power))
            i += 1
            player.preflop_bet()

    # 翻牌回合
    def flop_round(self):
        # 切牌并发翻牌
        self.communityCards = self.flopCards = self.remainingCards[1:4]
        print('\n翻牌：{}\n'.format(Tools.display_cards(self.flopCards)))
        self.check_win_possibilities()

    # 转牌回合
    def turn_round(self):
        # 切牌
        self.remainingCards = self.remainingCards[4:]
        # 发转牌
        self.turnCard = self.remainingCards[1]
        self.communityCards.append(self.turnCard)
        print('\n转牌：{}\n'.format(Tools.display_card(self.turnCard)))
        self.check_win_possibilities()

    # 河牌回合
    def river_round(self):
        # 切牌
        self.remainingCards = self.remainingCards[1:]
        # 发河牌
        self.riverCard = self.remainingCards[1]
        self.communityCards.append(self.riverCard)
        print('\n河牌：{}\n'.format(Tools.display_card(self.riverCard)))
        self.check_win_possibilities()

    # 计算各玩家出现各种牌型的概率
    def check_win_possibilities(self):
        for i in range(numPlayers):
            print('玩家{}的成牌可能：\n{}'.format(i + 1, self.check_turnouts(self.players[i].handCards + self.communityCards)))

    # 计算每种牌型的概率
    def check_turnouts(self, visible_cards):
        message = ''

        # 皇家同花顺
        existing_cards, possible_cards = MatchFinder.find_royal_flush_cards(visible_cards)
        # 已经成牌
        if len(existing_cards) == 5:
            return '皇家同花顺!!! 成牌：{}\n'.format(Tools.display_cards(existing_cards))
        # 可能成牌
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards))
            message += '皇家同花顺：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 同花顺
        results = MatchFinder.find_straight_flush_cards(visible_cards)
        if len(results) > 0:
            for result in results:
                existing_cards = result[0]
                possible_cards = result[1]
                if len(existing_cards) == 5:
                    return message + '同花顺：{}\n'.format(Tools.display_cards(existing_cards))
                elif len(possible_cards) > 0 and len(visible_cards) < 7:
                    probability = self.calculate_probability(len(possible_cards))
                    message += '同花顺：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 四条
        existing_cards, possible_cards = MatchFinder.find_pair_cards(4, visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '四条：{}\n'.format(Tools.display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards))
            message += '四条：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 葫芦
        existing_cards, possible_cards, has_two_pairs = MatchFinder.find_full_house_cards(visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '葫芦：{}\n'.format(Tools.display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards) * (2 if has_two_pairs else 3))
            message += '葫芦：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 同花
        existing_cards, possible_card = MatchFinder.find_flush_cards(visible_cards)
        if len(existing_cards) == 5:
            return message + '同花!\n'
        elif possible_card and len(visible_cards) < 7:
            probability = self.calculate_probability(9)
            message += '同花：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_card(possible_card))

        # 顺子
        results = MatchFinder.find_straight_cards(visible_cards)
        if len(results) > 0:
            for result in results:
                existing_cards = result[0]
                possible_cards = result[1]
                if len(existing_cards) == 5:
                    return message + '顺子：{}\n'.format(Tools.display_cards(existing_cards))
                elif len(possible_cards) > 0 and len(visible_cards) < 7:
                    probability = self.calculate_probability(len(possible_cards) * 4)
                    message += '顺子：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 三条
        existing_cards, possible_cards = MatchFinder.find_pair_cards(3, visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '三条：{}\n'.format(Tools.display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards) * 2)
            message += '三条：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        # 两对
        existing_cards, possible_cards = MatchFinder.find_two_pairs(visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '两对：{}\n'.format(Tools.display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards) * 3)
            message += '两对：{}%，已有{}，需要{}\n'.format(probability, Tools.display_cards(existing_cards), Tools.display_cards(possible_cards))

        return message

    # 计算牌型需要的牌抽中的概率
    def calculate_probability(self, possible_cards_count):
        # 还差两张牌
        # 只差一张牌，反向推算
        fail_probability = 1
        for i in range(self.unflopped_card_count()):
            hidden_cards_count = 50 - len(self.communityCards) - i
            fail_probability *= (hidden_cards_count - possible_cards_count) / hidden_cards_count * 1.0
        result = round((1 - fail_probability) * 100, 1)
        return result

    # 剩余没翻牌的公共牌数量
    def unflopped_card_count(self):
        return 5 - len(self.communityCards)

    # 结算
    def calculate_results(self):
        for player in self.players:
            # 输光出局
            if player.tokens == 0:
                self.players.remove(player)