package src;

import inet.node.ethernet.EthernetSwitch;
import inet.node.inet.StandardHost;
import inet.common.scenario.ScenarioManager;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;

network STPRingNetwork
{
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,50");
        }
        sw1: EthernetSwitch {
            parameters:
                @display("p=200,150;i=device/switch");
        }
        sw2: EthernetSwitch {
            parameters:
                @display("p=450,150;i=device/switch");
        }
        sw3: EthernetSwitch {
            parameters:
                @display("p=450,350;i=device/switch");
        }
        sw4: EthernetSwitch {
            parameters:
                @display("p=200,350;i=device/switch");
        }
        host1: StandardHost {
            parameters:
                @display("p=80,150;i=device/pc");
        }
        host2: StandardHost {
            parameters:
                @display("p=580,350;i=device/pc");
        }
        scenarioManager: ScenarioManager {
    parameters:
        @display("p=350,50");
        }
    connections:
    sw1.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw2.ethg++;
    sw2.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw3.ethg++;
    sw3.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw4.ethg++;
    sw4.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw1.ethg++;
    host1.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw1.ethg++;
    host2.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw3.ethg++;
}