import itertools
from collections import Counter


# 计算皇家同花顺需要的牌
def find_royal_flush_cards(visible_cards: list):
    existing_cards = []
    possible_cards = []
    # 至少要先能凑成同花
    possible_suit = is_flush_possible(visible_cards)
    if possible_suit != '':
        for card in visible_cards:
            if card[0] == possible_suit and card[1] >= 10:
                existing_cards.append(card)
        # 听牌
        if len(existing_cards) == 4:
            # 找到还需要凑齐的卡片
            full_cards = list(itertools.product([possible_suit], range(10, 15)))
            for card in full_cards:
                if card not in existing_cards:
                    possible_cards.append(card)
    return existing_cards, possible_cards


# 计算同花顺需要的牌
def find_straight_flush_cards(visible_cards: list):
    results = []
    possible_suit = is_flush_possible(visible_cards)
    if possible_suit != '':
        results = find_straight_cards(visible_cards, possible_suit)
    return results


# 计算葫芦需要的牌
def find_full_house_cards(visible_cards: list):
    existing_cards = []
    possible_cards = []
    has_two_pairs = False
    card_numbers = [card[1] for card in visible_cards]
    pair_datas = Counter(card_numbers).most_common()
    # 已经凑出三条
    if pair_datas[0][1] == 3:
        existing_cards = [card for card in visible_cards if card[1] == pair_datas[0][0]]
        for i in range(1, len(pair_datas)):
            card_number = pair_datas[i][0]
            if pair_datas[i][1] >= 2:
                existing_cards.extend([card for card in visible_cards if card[1] == card_number])
                break
            else:
                possible_cards.append(('*', card_number))
    # 已经有两对，差一个三条
    elif pair_datas[0][1] == pair_datas[1][1] == 2:
        has_two_pairs = True
        for i in range(len(pair_datas)):
            if pair_datas[i][1] == 2:
                card_number = pair_datas[i][0]
                existing_cards.extend([card for card in visible_cards if card[1] == card_number])
                possible_cards.append(('*', card_number))
            else:
                break
    return existing_cards, possible_cards, has_two_pairs


# 计算同花需要的牌
def find_flush_cards(visible_cards: list):
    existing_cards = []
    possible_card = None
    possible_suit = is_flush_possible(visible_cards)
    if possible_suit != '':
        for card in visible_cards:
            if card[0] == possible_suit:
                existing_cards.append(card)
        # 听牌
        if len(existing_cards) == 4:
            possible_card = (possible_suit, '*')
    return existing_cards, possible_card


# 判断同花是否可能出现
def is_flush_possible(visible_cards: list):
    card_colors = [card[0] for card in visible_cards]
    suit_data = Counter(card_colors).most_common(1)
    most_common_suit_count = suit_data[0][1]
    # 如果少于4张，则同花无法听牌
    if most_common_suit_count < 4:
        return ''
    # 返回同花的花色
    return suit_data[0][0]


# 计算两对需要的牌
def find_two_pairs(visible_cards: list):
    existing_cards = []
    possible_cards = []
    card_numbers = [card[1] for card in visible_cards]
    pair_datas = Counter(card_numbers).most_common()
    # 不成对子或者成了三条都不行
    if pair_datas[0][1] == 2:
        existing_cards = [card for card in visible_cards if card[1] == pair_datas[0][0]]
        for i in range(1, len(pair_datas)):
            card_number = pair_datas[i][0]
            matching_cards = [card for card in visible_cards if card[1] == card_number]
            # 已经成牌
            if pair_datas[i][1] == 2:
                existing_cards.extend(matching_cards)
                break
            else:
                possible_cards.append(('*', card_number))
    return existing_cards, possible_cards


# 计算四条和三条需要的牌
def find_pair_cards(pair_number: int, visible_cards: list):
    existing_cards = []
    possible_cards = []
    possible_numbers = is_pair_possible(pair_number, visible_cards)
    if len(possible_numbers) > 0:
        for possible_number in possible_numbers:
            existing_cards.extend([card for card in visible_cards if card[1] == possible_number])
            possible_cards.append(('*', possible_number))
    return existing_cards, possible_cards


# 判断四条/三条是否可能出现
def is_pair_possible(pair_count: int, visible_cards: list):
    possible_numbers = []
    card_numbers = [card[1] for card in visible_cards]
    pair_datas = Counter(card_numbers).most_common()
    for data in pair_datas:
        if data[1] >= pair_count - 1:
            possible_numbers.append(data[0])
    return possible_numbers


# 计算顺子需要的牌
def find_straight_cards(visible_cards: list, possible_suit='*'):
    results = []
    sorted_cards = visible_cards.copy()
    sorted_cards.sort(key=lambda x: x[1])
    # A也可看做1
    if sorted_cards[-1][1] == 14:
        temp_card = (sorted_cards[-1][0], 1)
        sorted_cards.insert(0, temp_card)
    # 卡片去重
    i = 0
    while i < len(sorted_cards) - 1:
        if sorted_cards[i][1] == sorted_cards[i+1][1]:
            # 同花顺时不要删除同花的牌
            if possible_suit != '*' and sorted_cards[i][0] == possible_suit:
                del sorted_cards[i+1]
            else:
                del sorted_cards[i]
        else:
            i += 1
    # X张牌一组进行测算（X为公共牌数量）
    for i in range(len(sorted_cards) - 3):
        low_card = sorted_cards[i]
        high_card = sorted_cards[i+3]
        # 要想组成顺子，已有的4张牌差值不能超过5，如3467缺5，但3468就组不成
        if high_card[1] - low_card[1] < 5:
            # 找到所有的顺子组合，如4567则最低34567，最高45678
            for lowest_number in range(high_card[1] - 4, low_card[1] + 1):
                if lowest_number == 0 or lowest_number > 10:
                    continue
                existing_cards = []
                possible_numbers = list(range(lowest_number, lowest_number + 5))
                for card in sorted_cards[i:i+4]:
                    # 同花顺不同花，排除
                    if possible_suit == '*' or card[0] == possible_suit:
                        existing_cards.append(card)
                    possible_numbers.remove(card[1])
                possible_cards = list(itertools.product([possible_suit], possible_numbers))
                if len(existing_cards) >= 4:
                    results.append((existing_cards, possible_cards))
    return results