import math
from typing import List, Optional, Type, TypeVar, Iterator, Union, Tuple

import networkx as nx

from leaf.power import PowerAware, PowerMeasurement, PowerModelNode , PowerModelNodeCarbon
from leaf.mobility import Location


class Node(PowerAware):
    def __init__(self, type: str,
                 name: str,
                 cu: Optional[float] = None,
                 power_model: Optional["PowerModelNode"] = None,
                 location: Optional[Location] = None,
                 initial_power: Optional[float] = None,
                 remaining_power: Optional[float] = None,
                 id: Optional[int] = None,
                 ):
        """A compute node in the infrastructure graph.

        This can represent any kind of node, e.g.
        - simple sensors without processing capabilities
        - resource constrained nodes fog computing nodes
        - mobile nodes like cars or smartphones
        - entire data centers with virtually unlimited resources

        Args:
            name: Name of the node. This is used to refer to nodes when defining links.
            cu: Maximum processing power the node provides in "compute units", a imaginary unit for computational power
                to express differences between hardware platforms. If None, the node has unlimited processing power.
            power_model: Power model which determines the power usage of the node.
            location: The (x,y) coordinates of the node
        """
        # NNEEWW
        self.initial_power = initial_power
        self.remaining_power = remaining_power

        self.name = name
        self.type = type
        if cu is None:
            self.cu = math.inf
        else:
            self.cu = cu
        self.used_cu = 0
        self.tasks: List["Task"] = []
        if id is not None:
            self.id = id

        # This value is for calculating carbon footprint
        # footprint = emmision_rate (kg co2 per kWh) * energy
        # if emission_rate is not None:
        #     self.emission_rate = emission_rate

        if power_model:
            if cu is None and power_model.max_power is not None:
                raise ValueError("Cannot use PowerModelNode with `max_power` on a compute node with unlimited "
                                 "processing power")

            #Added for carbon_free nodes, If type is carbon_free, then powermodel hardcoded as PowerModelNodeCarbon
            # if self.type.lower() == "carbonfree":
            #     self.power_model= PowerModelNodeCarbon

            self.power_model = power_model
            self.power_model.set_parent(self)

        self.location = location

    def update_remain_energy_consumption(self, usage_power):
        """
        Updates the remaining energy based on the energy consumed during the given period.
        """
        self.remaining_power -= usage_power
        print('remain_energy_consumption: ', self.remaining_power)
        # if self.power_model:
        #     power_measurement = self.measure_power()
        #     energy_consumed = (power_measurement.dynamic + power_measurement.static) * self.utilization()
        #     self.remaining_power -= energy_consumed
        #     print('energy_consumption: ', energy_consumed)
        #     print('remain_energy_consumption: ', self.remaining_power)
        # else:
        #     raise RuntimeError("Node has no power model to calculate energy consumption.")

    def __repr__(self):
        cu_repr = self.cu if self.cu is not None else "∞"
        return f"{self.__class__.__name__}('{self.name}', cu={self.used_cu}/{cu_repr})"

    def utilization(self) -> float:
        """Return the current utilization of the resource in the range [0, 1]."""
        try:
            return self.used_cu / self.cu  # 5/10 = 50
        except ZeroDivisionError:
            assert self.used_cu == 0
            return 0

    def utilization_requirement(self, processing_task) -> float:
        """Return the utilization_requirement utilization of the resource in the range [0, 1]."""
        try:
            return processing_task / self.cu
        except ZeroDivisionError:
            assert self.used_cu == 0
            return 0

    def _add_task(self, task: "Task"):
        """Add a task to the node.
        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        self._reserve_cu(task.cu)
        self.tasks.append(task)
        # self._remaining_power(task.cu)

    def _remove_task(self, task: "Task"):
        """Remove a task from the node.

        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        self._release_cu(task.cu)
        # try added by reza for debugging
        # try:
        self.tasks.remove(task)
        # except Exception as ex:
        #    print(ex)

    def measure_power(self) -> PowerMeasurement:
        try:
            return self.power_model.measure()
        except AttributeError:
            raise RuntimeError(f"{self} has no power model.")

    def _reserve_cu(self, cu: float):
        new_used_cu = self.used_cu + cu
        if new_used_cu > self.cu:
            raise ValueError(f"Cannot reserve {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu

    def _release_cu(self, cu: float):
        new_used_cu = self.used_cu - cu
        if new_used_cu < 0:
            raise ValueError(f"Cannot release {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu

    # def _remaining_power(self,cu:float):
    #     new_remaining_power = self.remaining_power


class NodeCarbon(Node,PowerModelNodeCarbon):
    def __init__(self, type: str,
                 name: str,
                 cu: Optional[float] = None,
                 power_model: Optional["PowerModelNode"] = None,
                 location: Optional[Location] = None,
                 initial_power: Optional[float] = None,
                 remaining_power: Optional[float] = None,
                 id: Optional[int] = None,
                 emission_rate: Optional[float] = 0.5,
                 battery_power= None):

        # NNEEWW
        self.initial_power = initial_power
        self.remaining_power = remaining_power

        self.name = name
        self.type = type
        if cu is None:
            self.cu = math.inf
        else:
            self.cu = cu
        self.used_cu = 0
        self.tasks: List["Task"] = []
        if id is not None:
            self.id = id

        # This value is for calculating carbon footprint
        # footprint = emmision_rate (kg co2 per kWh) * energy
        # if emission_rate is not None:
        #     self.emission_rate = emission_rate

        if battery_power is not None:
            self.battery_power = battery_power
            self.free_battery= battery_power
            self.used_battery= 0

        if power_model:
            if cu is None and power_model.max_power is not None:
                raise ValueError("Cannot use PowerModelNode with `max_power` on a compute node with unlimited "
                                 "processing power")

            #Added for carbon_free nodes, If type is carbon_free, then powermodel hardcoded as PowerModelNodeCarbon
            # if self.type.lower() == "carbonfree":
            #     self.power_model= PowerModelNodeCarbon

            self.power_model = power_model
            self.power_model.set_parent(self)

        self.location = location

    def _add_task(self, task: "Task"):
        """Add a task to the node.
        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        super()._add_task(task)

        # added for calculation of CO2 and get energy resource from battery
        power = self.measure_power()

        self.used_battery = self.used_battery + power.dynamic

        self.free_battery = self.free_battery - self.used_battery

    def _get_free_battery(self):
        #self.used_battery=
        return self.free_battery

    def _remove_task(self, task: "Task"):
        """Remove a task from the node.

        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        super()._remove_task(task)

class Link(PowerAware):
    def __init__(self, src: Node, dst: Node, bandwidth: float, power_model: "PowerModelLink", latency: float = 0,
                 name=""):
        """A network link in the infrastructure graph.

        This can represent any kind of network link, e.g.

        - direct cable connections
        - wireless connections such as WiFi, Bluetooth, LoRaWAN, 4G LTE, 5G, ...
        - entire wide area network connections that incorporate different networking equipment you do not want to
          model explicitly.

        Args:
            src: Source node of the network link.
            dst: Target node of the network link.
            bandwidth: Bandwidth provided by the network link.
            power_model: Power model which determines the power usage of the link.
            latency: Latency of the network link which can be used to implement routing policies.
        """
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.latency = latency
        self.used_bandwidth = 0
        self.power_model = power_model
        self.power_model.set_parent(self)
        self.data_flows: List["DataFlow"] = []

    def __repr__(self):
        latency_repr = f", latency={self.latency}" if self.latency else ""
        return f"{self.__class__.__name__}('{self.src.name}' -> '{self.dst.name}', bandwidth={self.used_bandwidth}/{self.bandwidth}{latency_repr})"

    def _add_data_flow(self, data_flow: "DataFlow"):
        """Add a data flow to the link.

        Private as this is only called by leaf.application.DataFlow and not part of the public interface.
        """
        self._reserve_bandwidth(data_flow.bit_rate)
        self.data_flows.append(data_flow)

    def _remove_data_flow(self, data_flow: "DataFlow"):
        """Remove a data flow from the link.

        Private as this is only called by leaf.application.DataFlow and not part of the public interface.
        """
        self._release_bandwidth(data_flow.bit_rate)
        self.data_flows.remove(data_flow)

    def measure_power(self) -> PowerMeasurement:
        try:
            return self.power_model.measure()
        except AttributeError:
            raise RuntimeError(f"{self} has no power model.")

    # def measure_power_requirment_infrastructure(self) -> PowerMeasurement:
    #     try:
    #         return self.power_model.measure_power_requirement()
    #     except AttributeError:
    #         raise RuntimeError(f"{self} has no power model.")

    def _reserve_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth + bandwidth
        if new_used_bandwidth > self.bandwidth:
            raise ValueError(f"Cannot reserve {bandwidth} bandwidth on network link {self}.")
        self.used_bandwidth = new_used_bandwidth

    def _release_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth - bandwidth
        if new_used_bandwidth < 0:
            raise ValueError(f"Cannot release {bandwidth} bandwidth on network link {self}.")
        self.used_bandwidth = new_used_bandwidth


class Infrastructure(PowerAware):
    _TNode = TypeVar("_TNode", bound=Node)  # Generics
    _TLink = TypeVar("_TLink", bound=Link)  # Generics
    _NodeTypeFilter = Union[Type[_TNode], Tuple[Type[_TNode], ...]]
    _LinkTypeFilter = Union[Type[_TLink], Tuple[Type[_TLink], ...]]

    def __init__(self):
        """Infrastructure graph of the simulated scenario.

        The infrastructure is a weighted, directed multigraph where every node contains a :class:`Node` and every edge
        between contains a :class:`Link`.
        """
        self.graph = nx.MultiDiGraph()

    def node(self, node_name: str) -> Node:
        """Return a specific node by name."""
        return self.graph.nodes[node_name]["data"]

    # TODO link()

    def add_link(self, link: Link):
        """Add a link to the infrastructure. Missing nodes will be added automatically."""
        self.add_node(link.src)
        self.add_node(link.dst)
        self.graph.add_edge(link.src.name, link.dst.name, data=link, latency=link.latency)

    def add_node(self, node: Node):
        """Adds a node to the infrastructure."""
        if node.name not in self.graph:
            self.graph.add_node(node.name, data=node)

    def remove_node(self, node: Node):
        """Removes a node from the infrastructure."""
        self.graph.remove_node(node.name)

    def nodes(self, type_filter: Optional[_NodeTypeFilter] = None) -> List[_TNode]:
        """Return all nodes in the infrastructure, optionally filtered by class."""
        nodes: Iterator[Node] = (v for _, v in self.graph.nodes.data("data"))
        if type_filter is not None:
            nodes = (node for node in nodes if isinstance(node, type_filter))
        return list(nodes)

    def links(self, type_filter: Optional[_LinkTypeFilter] = None) -> List[_TLink]:
        """Return all links in the infrastructure, optionally filtered by class."""
        links: Iterator[Link] = (v for _, _, v in self.graph.edges.data("data"))
        if type_filter is not None:
            links = (link for link in links if isinstance(link, type_filter))
        return list(links)

    def measure_power(self) -> PowerMeasurement:
        measurements = [node.measure_power() for node in self.nodes()] + [link.measure_power() for link in self.links()]
        return PowerMeasurement.sum(measurements)
