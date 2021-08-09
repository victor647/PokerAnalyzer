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