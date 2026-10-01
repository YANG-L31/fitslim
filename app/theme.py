from kivy.metrics import dp, sp


def hx(s, a=1.0):
    s = s.lstrip('#')
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0, int(s[4:6], 16) / 255.0, a)


class C:
    BG        = hx('EEF3F9')
    BG_TOP    = hx('F8FBFF')
    BG_BOT    = hx('E9F0F8')

    CARD      = hx('FFFFFF')
    INK       = hx('1F2D40')
    INK2      = hx('55677E')
    MUTED     = hx('98A6BA')
    LINE      = hx('EAF0F6')
    TRACK     = hx('EDF2F8')

    # primary (muted, low saturation)
    GREEN     = hx('1FAE87')
    GREEN_D   = hx('15876A')
    GREEN_L   = hx('5FD6B2')
    MINT      = hx('EAF5F1')

    TEAL      = hx('4FA8A2')
    BLUE      = hx('6A9FC6')
    BLUE_L    = hx('EDF3F9')
    ORANGE    = hx('CB9A6A')
    ORANGE_L  = hx('F5EEE6')
    PURPLE    = hx('918FBE')
    PURPLE_L  = hx('F0EFF7')

    GOLD      = hx('E5B472')
    GOLD_L    = hx('F7EFDF')
    RED       = hx('DE8B8B')

    WHITE     = (1, 1, 1, 1)
    WHITE_D   = (1, 1, 1, 0.80)
    WHITE_M   = (1, 1, 1, 0.55)
    WHITE_L   = (1, 1, 1, 0.26)


PAD       = dp(20)
GAP       = dp(14)
RADIUS    = dp(20)
CARD_PAD  = dp(14)
NAV_H     = dp(74)
STAT_H    = dp(108)
