#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
import logging
import os 

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )

class FatTree(Topo):
    logger.debug("Class FatTree")
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []
    iNUMBER = 0
    cost   = 0
    
    def __init__(self):
        iNUMBER = 100
        
        self.iNUMBER = iNUMBER
        self.iCoreLayerSwitch = 2
        self.iAggLayerSwitch = 4
        self.iEdgeLayerSwitch = 13
        self.iHost = 100
        self.cost = (self.iCoreLayerSwitch + self.iAggLayerSwitch + self.iEdgeLayerSwitch) * 300
    
        #Init Topo
        Topo.__init__(self)
        #self.createTopo()
        #self.createLink()
        self.CoreSwitchList.append(self.addSwitch("c1"))
        self.CoreSwitchList.append(self.addSwitch("c2"))

        self.AggSwitchList.append(self.addSwitch("a1"))
        self.AggSwitchList.append(self.addSwitch("a2"))
        self.AggSwitchList.append(self.addSwitch("a3"))
        self.AggSwitchList.append(self.addSwitch("a4"))

        for x in range(1, self.iEdgeLayerSwitch+1):
            self.EdgeSwitchList.append(self.addSwitch('e%d' % x)) 

        for x in range(1, self.iHost+1):
            self.HostList.append(self.addHost(str(x)))

        self.addLink(self.CoreSwitchList[0], self.CoreSwitchList[1], bw=1000)

        self.addLink(self.CoreSwitchList[0], self.AggSwitchList[0], bw=1000)
        self.addLink(self.CoreSwitchList[0], self.AggSwitchList[1], bw=1000)
        self.addLink(self.CoreSwitchList[1], self.AggSwitchList[2], bw=1000)
        self.addLink(self.CoreSwitchList[1], self.AggSwitchList[3], bw=1000)

    # 5 links * cost of 1000Mbps link
	self.cost += 5 * 15

	# add 4 edges to first agg switch
        self.addLink(self.AggSwitchList[0], self.EdgeSwitchList[0], bw=1000)
        self.addLink(self.AggSwitchList[0], self.EdgeSwitchList[1], bw=1000)
        self.addLink(self.AggSwitchList[0], self.EdgeSwitchList[2], bw=1000)
        self.addLink(self.AggSwitchList[0], self.EdgeSwitchList[3], bw=1000)

	# add 3 edges to second agg switch
        self.addLink(self.AggSwitchList[1], self.EdgeSwitchList[4], bw=1000)
        self.addLink(self.AggSwitchList[1], self.EdgeSwitchList[5], bw=1000)
        self.addLink(self.AggSwitchList[1], self.EdgeSwitchList[6], bw=1000)

    	# add 4 edges to third agg switch
        self.addLink(self.AggSwitchList[2], self.EdgeSwitchList[7], bw=1000)
        self.addLink(self.AggSwitchList[2], self.EdgeSwitchList[8], bw=1000)
        self.addLink(self.AggSwitchList[2], self.EdgeSwitchList[9], bw=1000)
        self.addLink(self.AggSwitchList[2], self.EdgeSwitchList[10], bw=1000)

    	# add 4 edges to last agg switch
        self.addLink(self.AggSwitchList[3], self.EdgeSwitchList[11], bw=1000)
        self.addLink(self.AggSwitchList[3], self.EdgeSwitchList[12], bw=1000)

        # 13 links * cost of 100Mbps link * bw
        self.cost += 13 * 15

        for x in range(0, 12):
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 1],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 2],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 3],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 4],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 5],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 6],bw=100)
            self.addLink(self.EdgeSwitchList[x], self.HostList[8 * x + 7],bw=100)
            self.cost += 8 * 1

        self.addLink(self.EdgeSwitchList[12], self.HostList[96],b=100)
        self.addLink(self.EdgeSwitchList[12], self.HostList[97],b=100)
        self.addLink(self.EdgeSwitchList[12], self.HostList[98],b=100)
        self.addLink(self.EdgeSwitchList[12], self.HostList[99],b=100) 
        self.cost += 4 * 1

def enableSTP():
    """
    //HATE: Dirty Code
    """
    for x in range(1,3):
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("c" + str(x))
        os.system(cmd)
        print cmd 

    for x in range(1, 5):
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("a" + str(x))
        os.system(cmd)  
        print cmd

    for x in range(1, 14): 
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("e" + str(x))
        os.system(cmd)
        print cmd

def iperfTest(net, topo):
    logger.debug("Start iperf test for all hosts")
    h1, h50, h99 = net.get(topo.HostList[0], topo.HostList[49], topo.HostList[99])
    
    #iperf Server
    h1.popen('iperf -s -u -i 1 > iperf_server_differentPod_result', shell=True)

    #iperf Server
    h50.popen('iperf -s -u -i 1 > iperf_server_samePod_result', shell=True)

    #iperf Client
    h99.cmdPrint('iperf -c ' + h1.IP() + ' -u -t 10 -i 1 -b 1000m')
    h99.cmdPrint('iperf -c ' + h50.IP() + ' -u -t 10 -i 1 -b 1000m')

def pingTest(net):
    logger.debug("Starting pingAll test")
    net.pingAll()

def createTopo():
    logging.debug("Creating a Fat tree topology")
    topo = FatTree()


    logger.debug("cost of topology is after creating topo is" + str(topo.cost))
    
    CONTROLLER_IP = "127.0.0.1"
    CONTROLLER_PORT = 6633
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController( 'controller',controller=RemoteController,ip=CONTROLLER_IP,port=CONTROLLER_PORT)
    net.start()
    enableSTP()
    dumpNodeConnections(net.hosts)
    
    pingTest(net)
    iperfTest(net, topo)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logger.debug("You are NOT root")
    elif os.getuid() == 0:
        createTopo()

topos = { 'ftree' : (lambda: FatTree()) }
