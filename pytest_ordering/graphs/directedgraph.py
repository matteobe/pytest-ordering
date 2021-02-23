"""
DirectedGraph implements a direct graph class, with methods to detect cycles, perform topological sorting and other
directed graph operations. The edges can be defined using either integer, floats or string.
DirectedGraph is an extension of the BaseDirectedGraph class and handles the mapping of user-defined IDs to strictly
integers IDs.
"""

from typing import Union, List
import copy

from pytest_ordering.graphs.basegraph import BaseDirectedGraph
from pytest_ordering.utils import require_in_list


class DirectedGraph:

    def __init__(self):
        """
        Initialize a new graph object, including dictionaries to keep track of the vertices numeric IDs
        """
        # ID generator counter
        self.new_id = 0

        # Vertices IDs tracking
        self.vertices_map = {}
        self.vertices_map_inv = {}

        # Graph object
        self.graph = BaseDirectedGraph()

    # ----------------------------- VERTICES ------------------------------#
    def _get_vertex_id(self, vertex: Union[str, int, float]) -> int:
        """
        Function returns the internal vertex ID for an input vertex definition, if the vertex does not exist,
        it creates it.
        """
        if vertex in self.vertices_map:
            vertex_id = self.vertices_map[vertex]
        else:
            vertex_id = self.add_vertex(vertex)

        return vertex_id

    def add_vertex(self, vertex: Union[str, int, float]) -> int:
        """
        Add new vertex to the graph, including assigning a new unique ID to the vertex.

        Args:
            vertex (str, int, float): the vertex identifier specified by the user.
        Returns:
            vertex_id (int): internal numerical vertex ID
        """

        # Get new vertex ID and keep track of the mapping in both directions
        vertex_id = self.new_id
        self.new_id += 1
        self.vertices_map[vertex] = vertex_id
        self.vertices_map_inv[vertex_id] = vertex

        # Add the vertex to the graph
        self.graph.add_vertex(vertex_id)

        return vertex_id

    def remove_vertex(self, vertex: Union[str, int, float]) -> None:
        """
        Remove a vertex from the graph
        Args:
            vertex (str, int, float): the vertex identifier specified by the user
        """

        if vertex in self.vertices_map:
            # Remove from vertices map list
            vertex_id = self.vertices_map.pop(vertex)
            _ = self.vertices_map_inv.pop(vertex_id)

            # Remove vertex from graph
            self.graph.remove_vertex(vertex_id)

    # ----------------------------- EDGES ------------------------------#
    def add_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Add new edge to the graph
        Args:
            start_vertex (str, int, float): the start vertex identifier specified by the user
            end_vertex (str, int, float): the end vertex identifier specified by the user
        """
        self.graph.add_edge(self._get_vertex_id(start_vertex),
                            self._get_vertex_id(end_vertex))

    def remove_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Remove an edge from the graph
        Args:
            start_vertex (str, int, float): the start vertex identifier specified by the user
            end_vertex (str, int, float): the end vertex identifier specified by the user
        """
        self.graph.remove_edge(self._get_vertex_id(start_vertex),
                               self._get_vertex_id(end_vertex))

    # ----------------------------- CYCLES ------------------------------#
    def graph_cycle(self) -> List:
        """
        Test if the graph is cyclic and return a list containing the user-defined IDs in the cycle if one is found

        Returns:
            cyclic (list): list containing the user-defined IDs of the cycle vertices if a cycle exists
        """

        # Get the graph cycle from the integers graph
        cycle_ids = self.graph.get_graph_cycle()
        cycle_vertices = [self.vertices_map_inv[vertex] for vertex in cycle_ids]

        return cycle_vertices

    def is_graph_acyclic(self) -> bool:
        """
        Test that the graph does not contain a cyclic component
        """
        cycle_vertices = self.graph_cycle()

        if not cycle_vertices:
            return True

        return False

    # ----------------------------- DEPENDANTS ------------------------------#
    def get_vertex_dependants(self, vertex: Union[str, int, float], direction: str = 'forward') -> List:
        """
        Get dependant vertices, based on a starting vertex
        Args:
            vertex (str, int, float): user-defined vertex ID to get dependants for
            direction (str): direction in which the graph needs to be traversed, i.e. forward or backward
        Returns:
            vertices (list): List of dependant vertices
        """

        require_in_list(direction, ['forward', 'backward'])
        vertex_id = self._get_vertex_id(vertex)

        dependant_ids = self.graph.get_vertex_dependants(vertex_id, direction=direction)
        dependant_vertices = [self.vertices_map_inv[vertex_id] for vertex_id in dependant_ids]

        return dependant_vertices

    # ----------------------------- SORTING ------------------------------#
    def sort_graph(self, isolated_vertices_position: str = 'end') -> List:
        """
        Create a topological sorting of the graph, based on the directions in the graph.
        Args:
            isolated_vertices_position (str): define if isolated vertices go at the beginning or at the end of the
                sorted list. Valid values are 'start' and 'end'.
        """

        require_in_list(isolated_vertices_position, ['start', 'end'])

        # Create a copy of the graph that can be manipulated
        graph = copy.deepcopy(self.graph)

        # Retrieve the sorting of the vertices and map them to the user-defined IDs
        sorted_vertices_ids = graph.sort_graph(isolated_vertices_position=isolated_vertices_position)
        sorted_vertices = [self.vertices_map_inv[vertex_id] for vertex_id in sorted_vertices_ids]

        return sorted_vertices
