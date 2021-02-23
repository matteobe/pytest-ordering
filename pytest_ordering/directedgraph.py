"""
DirectedGraph implements a direct graph class, with methods to detect cycles, perform topological sorting and other
directed graph operations. The edges can be defined using either integer, floats or string.
DirectedGraph is an extension of the BaseDirectedGraph class and handles the mapping of user-defined IDs to strictly
integers IDs.
"""

from typing import Union, List
import copy

from pytest_ordering.basegraph import BaseDirectedGraph
from pytest_ordering.utils import require_in_list


class DirectedGraph:

    def __init__(self):
        """
        Initialize a new graph object, including dictionaries to keep track of the vertices numeric IDs
        """
        # ID generator counter and other counters
        self.new_id = 0
        self.num_vertices = 0

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
        self.num_vertices += 1
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
            self.num_vertices -= 1

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
    def sort_graph(self) -> List:
        """
        Create a topological sorting of the graph, based on the directions in the graph
        """

        graph = copy.deepcopy(self)

        if graph.check_start_edges():
            return []

        # TODO: How do you construct the execution list
        #  Apply topological sort algorithm (https://personal.utdallas.edu/~ravip/cs3345/slidesweb/node7.html)
        #  Step in procedure
        #  - Identify vertex without incoming edges
        #  - Add vertex to reversed_execution list
        #  - Remove the vertex from the graph (including incoming edges)
        #  - Repeat procedure for rest of graph
        #  Procedure order
        #  - Begin with bottom10 vertices
        #  - Perform on rest of graph (excluding top10 vertices)
        #  - Conclude with top10 vertices

        # Check that the start_vertices sequence is respected
        start_vertices = [vertex_id for vertex_id in self.start_vertices if vertex_id is not None]

        # Check that end_vertices sequence is respected
        end_vertices = [vertex_id for vertex_id in self.end_vertices if vertex_id is not None]

        return []

    def check_start_edges(self) -> List:
        """
        Check that the start edges ('first' to 'tenth') can be executed in the correct sequence

        Return:
            start_vertices (list): List of the ordered start vertices, if they can be executed in the correct sequence
        """

        # TODO: Identify if there is a priority conflict for the top10 vertices
        #   Approach: Create the "source" tree for the nr. 10 vertex and if there are vertices other than the top 10,
        #   then here is a priority conflict

        return [vertex_id for vertex_id in self.start_vertices if vertex_id is not None]

    def check_end_edges(self) -> List:
        """
        Check that the end edges ('tenth-to-last' to 'last') can be executed in the correct sequence

        Return:
            end_vertices (list): List of the ordered end vertices if they can be executed in the correct sequence
        """
        # TODO: Identify if there is a priority conflict for the bottom10 vertices
        #  Approach: Reverse graphs direction of edge and perform the same procedure as for the nr. 10 vertex, this
        #  time starting with the nr. 10-to-last vertex

        return [vertex_id for vertex_id in self.end_vertices if vertex_id is not None]
