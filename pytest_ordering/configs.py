"""
Configuration variables
"""

start_test_items_map = {
    'first': 0,
    'second': 1,
    'third': 2,
    'fourth': 3,
    'fifth': 4,
    'sixth': 5,
    'seventh': 6,
    'eighth': 7,
    'ninth': 8,
    'tenth': 9,
}

end_test_items_map = {
    'tenth_to_last': 0,
    'ninth_to_last': 1,
    'eighth_to_last': 2,
    'seventh_to_last': 3,
    'sixth_to_last': 4,
    'fifth_to_last': 5,
    'fourth_to_last': 6,
    'third_to_last': 7,
    'second_to_last': 8,
    'last': 9,
}

special_test_items = list(start_test_items_map.keys()) + list(end_test_items_map.keys())
