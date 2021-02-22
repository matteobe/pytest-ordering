"""
DirectedGraph implements the capability to reason about order of execution of items collected by pytest.
Cardinal ordering information (first, second, ..., second-to-last, last) can be integrated in the graph
"""

from typing import Union, List
from collections import defaultdict
import copy

from pytest_ordering.configs import start_vertices_map, end_vertices_map
from pytest_ordering.utils import require_in_list


class DirectedGraph:

    def __init__(self):
        """
        Initialize a new graph object, including dictionaries to keep track of the vertices and edges
        """
        # Counters
        self.new_id = 0
        self.vertices = 0

        # Vertices tracking
        self.vertices_map = {}
        self.vertices_map_inv = {}
        self.start_vertices = [None] * len(start_vertices_map)
        self.end_vertices = [None] * len(end_vertices_map)

        # Edges tracking
        self.graph = defaultdict(list)
        self.graph_inv = defaultdict(list)

    # ----------------------------- VERTICES ------------------------------#
    def add_vertex(self, vertex: Union[str, int, float], special_vertex: str = None) -> int:
        """
        Add new vertex to the graph, including assigning a new unique ID to the vertex.
        Internally, the graph is represented using integer ID for vertices (faster calculation than with strings)

        Args:
            vertex (str, int, float): the vertex identifier chosen by the user
            special_vertex (str): can be used to identify special vertices, can be 'first', ..., 'tenth' for starting
            vertices and 'last', ..., 'tenth_to_last' for ending vertices
        """

        if special_vertex is not None:
            require_in_list(special_vertex, list(start_vertices_map.keys()) + list(end_vertices_map.keys()))

        vertex_id = self.new_id
        self.new_id += 1
        self.vertices += 1
        self.vertices_map[vertex] = vertex_id
        self.vertices_map_inv[vertex_id] = vertex

        if special_vertex is not None:
            if special_vertex in list(start_vertices_map.keys()):
                self.start_vertices[start_vertices_map[special_vertex]] = vertex_id
            else:
                self.end_vertices[end_vertices_map[special_vertex]] = vertex_id

        return vertex_id

    def remove_vertex(self, vertex: Union[str, int, float]) -> None:
        """
        Remove a vertex from the graph
        """

        # Remove vertex only if it's listed in the vertex list
        if vertex in self.vertices_map:
            self.vertices -= 1
            # Remove from vertices list
            vertex_id = self.vertices_map.pop(vertex)
            _ = self.vertices_map_inv.pop(vertex_id)

            # Remove from start or end vertices list
            if vertex_id in self.start_vertices:
                self.start_vertices[self.start_vertices.index(vertex_id)] = None
            elif vertex_id in self.end_vertices:
                self.end_vertices[self.end_vertices.index(vertex_id)] = None

            # Remove vertex as starting point from graph & inverted graph only if it was used
            if vertex_id in self.graph:
                _ = self.graph.pop(vertex_id)
            if vertex_id in self.graph_inv:
                _ = self.graph_inv.pop(vertex_id)

            # Remove vertex as end point from graph & inverted graph only if it was used
            for start_vertex_id in self.graph:
                if vertex_id in self.graph[start_vertex_id]:
                    self.graph[start_vertex_id].remove(vertex_id)
            for start_vertex_id in self.graph_inv:
                if vertex_id in self.graph_inv[start_vertex_id]:
                    self.graph_inv[start_vertex_id].remove(vertex_id)

    def get_vertex_id(self, vertex: Union[str, int, float]) -> int:
        """
        Function returns the vertex ID for an input vertex definition, if the vertex does not exist, it creates it
        """
        if vertex in self.vertices_map:
            vertex_id = self.vertices_map[vertex]
        else:
            vertex_id = self.add_vertex(vertex)

        return vertex_id

    # ----------------------------- EDGES ------------------------------#
    def add_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Add new edge to the graph
        """
        start_vertex = self.get_vertex_id(start_vertex)
        end_vertex = self.get_vertex_id(end_vertex)
        self.graph[start_vertex].append(end_vertex)
        self.graph_inv[end_vertex].append(start_vertex)

    def remove_edge(self, start_vertex: Union[str, int, float], end_vertex: Union[str, int, float]) -> None:
        """
        Remove an edge from the graph
        """
        start_vertex = self.get_vertex_id(start_vertex)
        end_vertex = self.get_vertex_id(end_vertex)

        if start_vertex in self.graph:
            if end_vertex in self.graph[start_vertex]:
                self.graph[start_vertex].remove(end_vertex)
                self.graph_inv[end_vertex].remove(start_vertex)

    def add_start_edges(self) -> None:
        """
        Add the edges for the start vertices (e.g., 'first', ..., 'tenth') if they don't already exist
        """

        # TODO: Implement addition of start edges w/ check for duplication
        # To deal with the starting conditions (first, second, third, etc..)
        # They can be added as the root of the tree
        # TODO: Decide where to attach the end of the first-priority execution list to the graph of before/after
        #  relationships
        #  - Case 1: top10 priorities is a separate graph, in which case it gets executed first
        #  - Case 2: top10 priorities is attached to rest of graph, in which case the normal algorithm is applied
        start_vertices = [vertex_id for vertex_id in self.start_vertices if vertex_id is not None]

    def add_end_edges(self) -> None:
        """
        Add the edges for the end vertices (e.g., 'last', ..., 'tenth_to_last') if they don't already exist
        """

        # TODO: Implement addition of end edges w/ check for duplication
        # To deal with the ending conditions (last, second-to-last, etc...)
        # They can be added as a leaf of the tree
        # TODO: Decide where to attach the start of the last-priority execution list to the graph of before/after
        #  relationships
        #  - Case 1: bottom10 priorities is a separate graph, in which case it gets executed last
        #  - Case 2: bottom10 priorities is attached to rest of graph, in which case the normal algorithm is applied
        end_vertices = [vertex_id for vertex_id in self.end_vertices if vertex_id is not None]

    # ----------------------------- CYCLES ------------------------------#
    def sub_cycle(self, vertex_id, vertex_visited, recursion_stack) -> List:
        """
        Function checks if any of the children nodes is in the recursion stack and returns a list with the
        cycle elements in it
        """

        # Mark current node as visited and add it to the recursion stack
        vertex_visited[vertex_id] = True
        recursion_stack[vertex_id] = True

        # Recur for all neighbours, if any neighbour is visited and in recursion stack then graph is cyclic
        for neighbour_id in self.graph[vertex_id]:
            if not vertex_visited[neighbour_id]:
                sub_cycle_ids = self.sub_cycle(neighbour_id, vertex_visited, recursion_stack)
                if sub_cycle_ids:
                    sub_cycle_ids.append(vertex_id)
                    return sub_cycle_ids
            elif recursion_stack[neighbour_id]:
                return [vertex_id]

        # The node needs to be popped from recursion stack before function ends
        recursion_stack[vertex_id] = False

        return []

    def graph_cycle(self) -> List:
        """
        Test if the graph is cyclic and return a list containing the ID in the cycle if one is found

        Returns:
            cyclic (bool): True if graph contains a cyclic component, False if not
        """

        # Initialize the tracking list to be the size of the new id, to avoid problems with deleted vertices
        vertex_visited = [False] * self.new_id
        recursion_stack = [False] * self.new_id

        for vertex_id in self.vertices_map_inv.keys():
            if not vertex_visited[vertex_id]:
                cycle_ids = self.sub_cycle(vertex_id, vertex_visited, recursion_stack)
                if cycle_ids:
                    cycle_ids.reverse()
                    cycle_ids.append(vertex_id)

                    # Return cycle with original vertices names
                    cycle = [self.vertices_map_inv[vertex_id] for vertex_id in cycle_ids]

                    return cycle

        return []

    def is_cyclic(self) -> bool:
        """
        Test if the graph is cyclic
        """
        cycle = self.graph_cycle()
        return True if cycle else False

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
