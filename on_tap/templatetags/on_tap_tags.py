from typing import Iterable, Tuple, TypeVar, Union

from django import template

register = template.Library()


@register.filter
def srm_to_hex(srm: Union[int, str]):
    """
    Takes an srm value as an int such as 1 or string such as '1' and returns a hex color code for it.
    """
    mapping = {
        1: '#FFE699',
        2: '#FFD878',
        3: '#FFCA5A',
        4: '#FFBF42',
        5: '#FBB123',
        6: '#F8A600',
        7: '#F39C00',
        8: '#EA8F00',
        9: '#E58500',
        10: '#DE7C00',
        11: '#D77200',
        12: '#CF6900',
        13: '#CB6200',
        14: '#C35900',
        15: '#BB5100',
        16: '#B54C00',
        17: '#B04500',
        18: '#A63E00',
        19: '#A13700',
        20: '#9B3200',
        21: '#952D00',
        22: '#8E2900',
        23: '#882300',
        24: '#821E00',
        25: '#7B1A00',
        26: '#771900',
        27: '#701400',
        28: '#6A0E00',
        29: '#660D00',
        30: '#5E0B00',
        31: '#5A0A02',
        32: '#600903',
        33: '#520907',
        34: '#4C0505',
        35: '#470606',
        36: '#440607',
        37: '#3F0708',
        38: '#3B0607',
        39: '#3A070B',
        40: '#36080A',
    }
    return mapping.get(int(srm))
