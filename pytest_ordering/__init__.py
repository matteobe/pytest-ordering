# -*- coding: utf-8 -*-
from ._version import __version__

import operator

import pytest

orders_map = {
    'first': 0,
    'second': 1,
    'third': 2,
    'fourth': 3,
    'fifth': 4,
    'sixth': 5,
    'seventh': 6,
    'eighth': 7,
    'last': -1,
    'second_to_last': -2,
    'third_to_last': -3,
    'fourth_to_last': -4,
    'fifth_to_last': -5,
    'sixth_to_last': -6,
    'seventh_to_last': -7,
    'eighth_to_last': -8,
}


def pytest_configure(config):
    """Register the "run" marker."""

    provided_by_pytest_ordering = (
        'Provided by pytest-ordering. '
        'See also: http://pytest-ordering.readthedocs.org/'
    )

    config_line = (
        'run: specify ordering information for when tests should run '
        'in relation to one another. ' + provided_by_pytest_ordering
    )
    config.addinivalue_line('markers', config_line)

    for mark_name in orders_map.keys():
        config_line = '{}: run test {}. {}'.format(mark_name,
                                                   mark_name.replace('_', ' '),
                                                   provided_by_pytest_ordering)
        config.addinivalue_line('markers', config_line)


def pytest_collection_modifyitems(session, config, items) -> None:
    """
    Modify (inplace) the items collected by pytest. In our case, we want to sort the execution of the items according
    to the rules set out in the @pytest.mark.run(**kwargs)

    The run marker can have the following keyword arguments:

    - order: numerical or string identifying the execution order
      First tests to be executed use a positive numeric argument (1,2,3) or the corresponding description
      'first', 'second', 'third'
      Last test to be executed use a negative numeric argument (-3,-2,-1) or the corresponding description
      'third-to-last', 'second-to-last', 'last'
    - after: name of the test that needs to be run before the present test can be run
      e.g. @pytest.mark.run(after='test_some_other_function')
    - before: name of the test that needs to wait for the present test to be run, before being run
      e.g. @pytest.mark.run(before='test_dependant_functionality')
    """

    grouped_items = {}

    # Loop over the collected items
    # An item has the following properties that can be helpful to create a after/before marker
    # - originalname / name: contains the name of the test function connected to the item

    for item in items:

        for mark_name, order in orders_map.items():
            mark = item.get_closest_marker(mark_name)

            if mark:
                item.add_marker(pytest.mark.run(order=order))
                break

        mark = item.get_closest_marker('run')

        if mark:
            order = mark.kwargs.get('order')
        else:
            order = None

        grouped_items.setdefault(order, []).append(item)

    sorted_items = []
    unordered_items = [grouped_items.pop(None, [])]

    start_list = sorted((i for i in grouped_items.items() if i[0] >= 0),
                        key=operator.itemgetter(0))
    end_list = sorted((i for i in grouped_items.items() if i[0] < 0),
                      key=operator.itemgetter(0))

    sorted_items.extend([i[1] for i in start_list])
    sorted_items.extend(unordered_items)
    sorted_items.extend([i[1] for i in end_list])

    items[:] = [item for sublist in sorted_items for item in sublist]
