"""
DirectedGraph implements a direct graph class, with methods to detect cycles, perform topological sorting and other
directed graph operations
"""

from typing import List
import copy

import pytest
from pytest_ordering.graphs.directedgraph import DirectedGraph
from pytest_ordering.configs import start_test_items_map, end_test_items_map, special_test_items
from pytest_ordering.utils import require_in_list, SortingError


class TestItemsSorter:
    """
    The test items sorter class implements only methods to add test items to the sorting graph, as the assumption is
    that the test items sorter is only called once.
    """

    def __init__(self):
        """
        Initialize a test items sorter object
        """

        # Items dictionaries (key: item name, value: test item)
        self.test_items = {}
        self.start_items = [None] * len(start_test_items_map)
        self.end_items = [None] * len(end_test_items_map)

        # Graph
        self.graph = DirectedGraph()

    # ----------------------------- TEST ITEMS ------------------------------#
    @staticmethod
    def get_test_item_id(test_item: pytest.Item) -> str:
        """
        Return a test item identifier
        Args:
            test_item (pytest.Item): test item for which to return an ID
        """

        return test_item.name

    def add_test_item(self, test_item: pytest.Item, special_test_item: str = None) -> None:
        """
        Add a test item to the TestItemsSorter
        Args:
            test_item (pytest.Item): test item to be added to the sorter
            special_test_item (str): can be used to identify special item, can be:
                'first', ..., 'tenth' for starting test items and,
                'last', ..., 'tenth_to_last' for ending test items
        """

        test_item_id = self.get_test_item_id(test_item)

        if special_test_item is not None:
            require_in_list(special_test_item, special_test_items)

        if test_item_id not in self.test_items.keys():
            self.test_items[test_item_id] = test_item
            self.graph.add_vertex(test_item_id)

        if special_test_item is not None:
            if special_test_item in start_test_items_map.keys():
                self.start_items[start_test_items_map[special_test_item]] = test_item_id
            else:
                self.end_items[end_test_items_map[special_test_item]] = test_item_id

    # ----------------------------- TEST ITEMS RELATIONS ------------------------------#
    def add_relation(self, start_test_item_id: str, end_test_item_id: str) -> None:
        """
        Add a test item relation based on the test items ID
        """
        self.graph.add_edge(start_test_item_id, end_test_item_id)

    def add_start_relations(self) -> None:
        """
        Add the relations for the start test items (e.g., 'first', ..., 'tenth')
        """
        start_test_items_ids = [test_item_id for test_item_id in self.start_items if test_item_id is not None]

        for start_test_item_id, end_test_item_id in zip(start_test_items_ids, start_test_items_ids[1:]):
            self.graph.add_edge(start_test_item_id, end_test_item_id)

    def add_end_relations(self) -> None:
        """
        Add the relations for the end test items (e.g., 'last', ..., 'tenth_to_last')
        """
        end_test_items_ids = [test_item_id for test_item_id in self.end_items if test_item_id is not None]

        for start_test_item_id, end_test_item_id in zip(end_test_items_ids, end_test_items_ids[1:]):
            self.graph.add_edge(start_test_item_id, end_test_item_id)

    # ----------------------------- TEST ITEMS RELATIONS CHECKS ------------------------------#
    def check_if_sorting_possible(self) -> None:
        """
        Check if sorting of the test priorities is possible.
        """
        self.add_start_relations()
        self.add_end_relations()

        self.check_no_execution_loop()
        self.check_start_items_execution_order()
        self.check_end_items_execution_order()

    def check_no_execution_loop(self) -> None:
        """
        Check that no execution loop exists in the relations graph
        """
        if not self.graph.is_graph_acyclic():
            message = "The test items contain a relations loop:\n" \
                     f"{' -> '.join(self.graph.graph_cycle())}\n"
            raise SortingError(message)

    def check_start_items_execution_order(self) -> None:
        """
        Check if the start items can be executed in the correct order
        """

        start_test_items_ids = [test_item_id for test_item_id in self.start_items if test_item_id is not None]
        if not start_test_items_ids:
            return None

        execution_order = self.graph.get_vertex_dependants(start_test_items_ids[-1], direction='backward')
        execution_order.reverse()
        execution_order.append(start_test_items_ids[-1])

        if start_test_items_ids != execution_order:
            message = "\n The start test items cannot be executed in the correct order.\n Items: " \
                     f"{', '.join(list(set(execution_order) - set(start_test_items_ids)))} point to a start item.\n " \
                      "Please remove these dependencies to execute the tests in the desired order."
            raise SortingError(message)

    def check_end_items_execution_order(self) -> None:
        """
        Check if the end items can be executed in the correct order
        """

        end_test_items_ids = [test_item_id for test_item_id in self.end_items if test_item_id is not None]
        if not end_test_items_ids:
            return None

        execution_order = self.graph.get_vertex_dependants(end_test_items_ids[0], direction='forward')
        execution_order.insert(0, end_test_items_ids[0])

        if end_test_items_ids != execution_order:
            message = "\n The end test items cannot be executed in the correct order.\n End test items are pointing " \
                     f"to items: {', '.join(list(set(execution_order) - set(end_test_items_ids)))}.\n " \
                      "Please remove these dependencies to execute the tests in the desired order."
            raise SortingError(message)

    # ----------------------------- TEST ITEMS SORTING ------------------------------#
    def sort_test_items(self) -> List[pytest.Item]:
        """
        Return a sorted list of the test items
        """
        # TODO: Return list of sorted items

    def sort_test_items_ids(self) -> List[str]:
        """
        Return a sorted list of the test items IDs, that can be used to sort the te
        """

        self.check_if_sorting_possible()
        graph = copy.deepcopy(self.graph)

        # Remove starting test items from graph
        start_test_items_ids = [test_item_id for test_item_id in self.start_items if test_item_id is not None]
        if start_test_items_ids:
            for start_test_item_id in start_test_items_ids:
                graph.remove_vertex(start_test_item_id)

        # Remove ending test items from graph
        end_test_items_ids = [test_item_id for test_item_id in self.end_items if test_item_id is not None]
        if end_test_items_ids:
            for end_test_item_id in end_test_items_ids:
                graph.remove_vertex(end_test_item_id)

        # Retrieve the sorted list for the remaining test items
        remaining_test_items_ids = graph.sort_graph(isolated_vertices_position='end')

        # Build the full sorted items list
        sorted_test_items_ids = copy.deepcopy(start_test_items_ids)
        sorted_test_items_ids.extend(remaining_test_items_ids)
        sorted_test_items_ids.extend(end_test_items_ids)

        return sorted_test_items_ids
