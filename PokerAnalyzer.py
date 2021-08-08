import random
import itertools
import MatchFinder


# 将卡片数值转为字符串
def display_card(card):
    if card[1] == 14:
        return card[0] + 'A'
    elif card[1] == 13:
        return card[0] + 'K'
    elif card[1] == 12:
        return card[0] + 'Q'
    elif card[1] == 11:
        return card[0] + 'J'
    else:
        return card[0] + str(card[1])


# 将多张卡片数值转为字符串
def display_cards(cards):
    message = ''
    for card in cards:
        message += display_card(card) + ', '
    return message[:-2]


class PokerAnalyzer:
    possiblePairNumbers = []
    # 指定玩家数量
    numPlayers = 2
    # 初始化牌库
    remainingCards = list(itertools.product(['♥', '♦', '♠', '♣'], range(2, 15)))
    playerCards = []

    def __init__(self):
        # 洗牌
        random.shuffle(self.remainingCards)
        # 发玩家手牌
        for i in range(self.numPlayers):
            self.playerCards.append(self.remainingCards[:2])
            self.remainingCards = self.remainingCards[2:]
            print('玩家{}的手牌：{}'.format(i + 1, display_cards(self.playerCards[i])))
        # 切牌并发翻牌
        self.communityCards = self.flopCards = self.remainingCards[1:4]
        print('\n翻牌：{}\n'.format(display_cards(self.flopCards)))
        self.check_win_possibilities()
        # 切牌
        self.remainingCards = self.remainingCards[4:]
        # 发转牌
        self.turnCard = self.remainingCards[1]
        self.communityCards.append(self.turnCard)
        print('\n转牌：{}\n'.format(display_card(self.turnCard)))
        self.check_win_possibilities()
        # 切牌
        self.remainingCards = self.remainingCards[1:]
        # 发河牌
        self.riverCard = self.remainingCards[1]
        self.communityCards.append(self.riverCard)
        print('\n河牌：{}\n'.format(display_card(self.riverCard)))
        self.check_win_possibilities()

    # 计算各玩家出现各种牌型的概率
    def check_win_possibilities(self):
        for i in range(len(self.playerCards)):
            print('玩家{}的成牌可能：\n{}'.format(i + 1, self.check_turnouts(self.playerCards[i] + self.communityCards)))

    # 计算每种牌型的概率
    def check_turnouts(self, visible_cards):
        message = ''

        # 皇家同花顺
        existing_cards, possible_cards = MatchFinder.find_royal_flush_cards(visible_cards)
        # 已经成牌
        if len(existing_cards) == 5:
            return '皇家同花顺!!! 成牌：{}\n'.format(display_cards(existing_cards))
        # 可能成牌
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards))
            message += '皇家同花顺：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))

        # 同花顺
        results = MatchFinder.find_straight_flush_cards(visible_cards)
        if len(results) > 0:
            for result in results:
                existing_cards = result[0]
                possible_cards = result[1]
                if len(existing_cards) == 5:
                    return message + '同花顺：{}\n'.format(display_cards(existing_cards))
                elif len(possible_cards) > 0 and len(visible_cards) < 7:
                    probability = self.calculate_probability(len(possible_cards))
                    message += '同花顺：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))
                    
        # 四条
        existing_cards, possible_cards = MatchFinder.find_pair_cards(4, visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '四条：{}\n'.format(display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards))
            message += '四条：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))


        # 同花
        existing_cards, possible_cards = MatchFinder.find_flush_cards(visible_cards)
        if len(existing_cards) == 5:
            return message + '同花!\n'
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards))
            message += '同花：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))

        # 顺子
        results = MatchFinder.find_straight_cards(visible_cards)
        if len(results) > 0:
            for result in results:
                existing_cards = result[0]
                possible_cards = result[1]
                if len(existing_cards) == 5:
                    return message + '顺子：{}\n'.format(display_cards(existing_cards))
                elif len(possible_cards) > 0 and len(visible_cards) < 7:
                    probability = self.calculate_probability(len(possible_cards) * 4)
                    message += '顺子：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))

        # 三条
        existing_cards, possible_cards = MatchFinder.find_pair_cards(3, visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '三条：{}\n'.format(display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards) * 2)
            message += '三条：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))

        # 两对
        existing_cards, possible_cards = MatchFinder.find_two_pairs(visible_cards)
        if len(possible_cards) == 0 and len(existing_cards) > 0:
            return message + '两对：{}\n'.format(display_cards(existing_cards))
        elif len(possible_cards) > 0 and len(visible_cards) < 7:
            probability = self.calculate_probability(len(possible_cards) * 3)
            message += '两对：{}%，已有{}，需要{}\n'.format(probability, display_cards(existing_cards), display_cards(possible_cards))

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


poker_analyzer = PokerAnalyzer()
