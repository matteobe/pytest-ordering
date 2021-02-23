"""
DirectedGraph implements a direct graph class, with methods to detect cycles, perform topological sorting and other
directed graph operations. The internal handling of ID is strictly using integers.
"""

# TODO: Check compatibility of __future__ import
from __future__ import annotations
from typing import List
from collections import defaultdict
import copy

from pytest_ordering.utils import require_in_list


class BaseDirectedGraph:

    def __init__(self):
        """
        Initialize a new graph object, including dictionaries to keep track of the vertices and edges
        """

        self.vertices = []
        self.graph = defaultdict(list)
        self.graph_inv = defaultdict(list)

        # Implement caching of responses to avoid recalculating them
        self._recompute_cycle = True
        self._cycle = []

    # ----------------------------- VERTICES ------------------------------#
    def add_vertex(self, vertex_id: int) -> None:
        """
        Add new vertex to the graph, check that the vertex ID is not already taken.
        Args:
            vertex_id (int): the numeric vertex ID
        """

        if vertex_id not in self.vertices:
            self._recompute_cycle = True
            self.vertices.append(vertex_id)

    def remove_vertex(self, vertex_id: int) -> None:
        """
        Remove a vertex from the graph and edges to and from it
        Args:
            vertex_id (int): the numeric vertex ID
        """

        if vertex_id in self.vertices:
            # Remove vertex from vertex list
            self._recompute_cycle = True
            self.vertices.remove(vertex_id)

            # Remove vertex as starting point from graph & inverted graph
            _ = self.graph.pop(vertex_id, None)
            _ = self.graph_inv.pop(vertex_id, None)

            # Remove vertex as end point from graph & inverted graph only if they exist in the list
            for start_vertex_id in self.graph:
                if vertex_id in self.graph[start_vertex_id]:
                    self.graph[start_vertex_id].remove(vertex_id)
            for start_vertex_id in self.graph_inv:
                if vertex_id in self.graph_inv[start_vertex_id]:
                    self.graph_inv[start_vertex_id].remove(vertex_id)

    # ----------------------------- EDGES ------------------------------#
    def add_edge(self, start_vertex_id: int, end_vertex_id: int) -> None:
        """
        Add an edge using the numeric vertices IDs. An edge is added only if it is not already present (to avoid
        duplication).
        Args:
            start_vertex_id (int): the numeric vertex ID of the starting vertex
            end_vertex_id (int): the numeric vertex ID of the ending vertex
        """

        self.add_vertex(start_vertex_id)
        self.add_vertex(end_vertex_id)

        if end_vertex_id not in self.graph[start_vertex_id]:
            self._recompute_cycle = True
            self.graph[start_vertex_id].append(end_vertex_id)
            self.graph_inv[end_vertex_id].append(start_vertex_id)

    def remove_edge(self, start_vertex_id: int, end_vertex_id: int) -> None:
        """
        Remove an edge from the graph.
        Args:
            start_vertex_id (int): the numeric vertex ID of the starting vertex
            end_vertex_id (int): the numeric vertex ID of the ending vertex
        """

        if start_vertex_id in self.graph:
            if end_vertex_id in self.graph[start_vertex_id]:
                self._recompute_cycle = True
                self.graph[start_vertex_id].remove(end_vertex_id)
                self.graph_inv[end_vertex_id].remove(start_vertex_id)

    # ----------------------------- CYCLES ------------------------------#
    def get_subcycle(self, vertex_id: int, vertex_visited: List[bool], recursion_stack: List[bool]) -> List:
        """
        Function checks if any of the children nodes is in the recursion stack and returns a list with the
        cycle elements in it.
        Args:
            vertex_id (int): the vertex ID for which the sub_cycle search needs to be performed
            vertex_visited (list): list of booleans indicating if a vertex has been visited
            recursion_stack (list): list of booleans indicating which vertices have been visited in the recursion
                procedure
        Returns:
            subcycle (list): list containing the IDs of elements part of an identified cycle
        """

        # Mark current node as visited and add it to the recursion stack
        vertex_idx = self.vertices.index(vertex_id)
        vertex_visited[vertex_idx] = True
        recursion_stack[vertex_idx] = True

        # Recur for all neighbours, if any neighbour is visited and in recursion stack then graph is cyclic
        for neighbour_id in self.graph[vertex_id]:
            neighbour_idx = self.vertices.index(neighbour_id)
            if not vertex_visited[neighbour_idx]:
                subcycle_ids = self.get_subcycle(neighbour_id, vertex_visited, recursion_stack)
                if subcycle_ids:
                    subcycle_ids.append(vertex_id)
                    return subcycle_ids
            elif recursion_stack[neighbour_idx]:
                return [vertex_id]

        # The node needs to be popped from recursion stack (because not cycle was found) before function ends
        recursion_stack[vertex_idx] = False

        return []

    def get_graph_cycle(self) -> List:
        """
        If a cycle exist in the graph, return a list containing the ID in the cycle
        Returns:
            cycle (list): list containing the IDs of the cycle elements if a cycle exists
        """

        # Returned cached response, if no changes have been made to the cycle
        if not self._recompute_cycle:
            return self._cycle

        # Initialize the tracking list to be the size of the new id, to avoid problems with deleted vertices
        num_vertices = len(self.vertices)
        vertex_visited = [False] * num_vertices
        recursion_stack = [False] * num_vertices

        for vertex_idx, vertex_id in enumerate(self.vertices):
            if not vertex_visited[vertex_idx]:
                cycle_ids = self.get_subcycle(vertex_id, vertex_visited, recursion_stack)
                if cycle_ids:
                    cycle_ids.reverse()
                    cycle_ids.append(vertex_id)

                    # Cache results
                    self._cycle = cycle_ids
                    self._recompute_cycle = False
                    return cycle_ids

        # Cache results
        self._cycle = []
        self._recompute_cycle = False
        return []

    def is_cyclic(self) -> bool:
        """
        Test if the graph is cyclic, use cached response if possible
        """

        if self._recompute_cycle:
            _ = self.get_graph_cycle()

        return True if self._cycle else False

    # ----------------------------- DEPENDANTS ------------------------------#
    def get_vertex_dependants(self, vertex_id: int, direction: str = 'forward') -> List:
        """
        Get dependant vertices, based on a starting vertex ID
        Args:
            vertex_id (int): numerical vertex ID to start from
            direction (str): direction in which the graph needs to be traversed, i.e. forward or backward
        Returns:
            vertices (list): List of dependant vertices IDs
        """

        require_in_list(direction, ['forward', 'backward'])

        try:
            vertex_dependants = self._get_vertex_dependants(vertex_id, direction=direction)
            vertex_dependants = list(set(vertex_dependants))
        except RecursionError:
            print("A recursion error is probably being caused by a cycle in the graph. Please make sure your directed "
                  "graph has no cycles.")
            raise

        return vertex_dependants

    def _get_vertex_dependants(self, vertex_id: int, direction: str = 'forward') -> List:
        """
        Private method: Get dependant vertices, based on a starting vertex ID.
        Separates dependants list creation from error handling performed in the corresponding public method
        """

        dependant_vertices = self.graph[vertex_id] if direction == 'forward' else self.graph_inv[vertex_id]

        if dependant_vertices:
            for dependant_vertex in dependant_vertices:
                dependant_vertex_dependants = self._get_vertex_dependants(dependant_vertex, direction=direction)
                dependant_vertices += dependant_vertex_dependants

        return dependant_vertices

    # ----------------------------- SORTING ------------------------------#
    def sort_graph(self) -> List:
        """
        Create a topological sorting of the graph, based on the directions in the graph.
        """

        # Create a copy of the graph that can be manipulated for sorting
        graph = copy.deepcopy(self)

        # Initialize the tracking list of which vertices have already been sorted and the sorting order
        unsorted_vertices = copy.deepcopy(self.vertices)
        sorted_vertices = []

        while len(unsorted_vertices) > 1:
            # Get next end-vertex add it to the sorted list
            vertex_id = self.get_next_end_vertex(graph, unsorted_vertices)
            sorted_vertices.append(vertex_id)

            # Remove the vertex from the graph and the unsorted vertices list and repeat
            unsorted_vertices.remove(vertex_id)
            graph.remove_vertex(vertex_id)

        # Add last unsorted vertex (which by default will not have any edges) and reverse list
        sorted_vertices.append(unsorted_vertices[0])
        sorted_vertices.reverse()

        return sorted_vertices

    @staticmethod
    def get_next_end_vertex(graph: BaseDirectedGraph, remaining_vertices: List[int]) -> int:
        """
        Function returns the first possible vertex that is a dead-end (i.e. no outgoing edge)
        Args:
            graph (BaseDirectedGraph): BaseDirectedGraph containing the edges information
            remaining_vertices (list): list of IDs of remaining vertices
        Returns:
            next_vertex (int): ID of next vertex without outgoing edges
        """

        if not remaining_vertices:
            raise ValueError("Input 'remaining_vertices' is empty. Please provide a non-empty input list.")

        # Loop over the remaining vertices and return the first remaining vertex without outgoing edges
        for vertex_id in remaining_vertices:
            if not graph.graph[vertex_id]:
                return vertex_id

        err_msg = "None of the remaining vertices has no outgoing edges, i.e. they are part of a cycle. " \
                  "Please use the get_graph_cycle function to identify the vertex that are part of the cycle."
        raise ValueError(err_msg)
