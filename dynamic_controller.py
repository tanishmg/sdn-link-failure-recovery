from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

from ryu.lib.packet import packet, ethernet
from ryu.topology import event
from ryu.topology.api import get_switch, get_link

import networkx as nx
import time


class DynamicRouting(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicRouting, self).__init__(*args, **kwargs)
        self.net = nx.Graph()
        self.mac_map = {}
        self.datapaths = {}
        self.recovery_start = None

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        self.datapaths[dp.id] = dp

        parser = dp.ofproto_parser
        ofp = dp.ofproto

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER)]
        self.add_flow(dp, 0, match, actions)

    def add_flow(self, dp, priority, match, actions):
        parser = dp.ofproto_parser
        ofp = dp.ofproto

        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=priority,
            match=match,
            instructions=inst
        )
        dp.send_msg(mod)

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology(self, ev):
        self.net.clear()

        switch_list = get_switch(self, None)
        switches = [sw.dp.id for sw in switch_list]
        self.net.add_nodes_from(switches)

        links = get_link(self, None)
        for link in links:
            self.net.add_edge(link.src.dpid, link.dst.dpid)

        print("Topology:", self.net.edges())

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        dpid = dp.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        src = eth.src
        dst = eth.dst
        in_port = msg.match['in_port']

        self.mac_map[src] = dpid

        if dst in self.mac_map:
            try:
                path = nx.shortest_path(self.net,
                                       self.mac_map[src],
                                       self.mac_map[dst])
                print("Path:", path)
            except:
                pass

    @set_ev_cls(event.EventLinkDelete)
    def link_failure(self, ev):
        src = ev.link.src.dpid
        dst = ev.link.dst.dpid

        print(f"Link Failure: {src} -> {dst}")

        if self.net.has_edge(src, dst):
            self.net.remove_edge(src, dst)

        self.recovery_start = time.time()

        recovery_time = time.time() - self.recovery_start
        print(f"Recovery Time: {recovery_time:.4f} sec")