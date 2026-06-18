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

//
// Topology phức tạp dùng để đánh giá ảnh hưởng của số switch và số vòng lặp
// lên STP. host1 vẫn nối vào sw1, host2 vẫn nối vào sw3. Đường ngắn nhất giữa
// sw1 và sw3 vẫn chỉ có 2 liên kết (qua sw2 hoặc sw4), giống STPRingNetwork.
//
// So với topology hiện tại:
// - STPRingNetwork: 4 switch, 4 liên kết liên-switch.
// - STPComplexNetwork: 8 switch, 9 liên kết liên-switch.
//
network STPComplexNetwork
{
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=440,40");
        }
        sw1: EthernetSwitch {
            parameters:
                @display("p=180,220;i=device/switch");
        }
        sw2: EthernetSwitch {
            parameters:
                @display("p=380,120;i=device/switch");
        }
        sw3: EthernetSwitch {
            parameters:
                @display("p=580,220;i=device/switch");
        }
        sw4: EthernetSwitch {
            parameters:
                @display("p=380,320;i=device/switch");
        }
        sw5: EthernetSwitch {
            parameters:
                @display("p=180,420;i=device/switch");
        }
        sw6: EthernetSwitch {
            parameters:
                @display("p=580,420;i=device/switch");
        }
        sw7: EthernetSwitch {
            parameters:
                @display("p=280,520;i=device/switch");
        }
        sw8: EthernetSwitch {
            parameters:
                @display("p=480,520;i=device/switch");
        }
        host1: StandardHost {
            parameters:
                @display("p=60,220;i=device/pc");
        }
        host2: StandardHost {
            parameters:
                @display("p=700,220;i=device/pc");
        }
        scenarioManager: ScenarioManager {
            parameters:
                @display("p=700,40");
        }
    connections:
        // Vòng lõi giữ nguyên thứ tự cổng. sw1.ethg[0] <-> sw2.ethg[0]
        // được dùng trong kịch bản đứt cáp của cả hai topology.
        sw1.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw2.ethg++;
        sw2.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw3.ethg++;
        sw3.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw4.ethg++;
        sw4.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw1.ethg++;

        // Nhánh ngoài dài làm tăng đường kính miền STP và tạo thêm một vòng
        // dự phòng, nhưng không làm tăng khoảng cách ngắn nhất giữa hai host.
        sw1.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw5.ethg++;
        sw5.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw6.ethg++;
        sw6.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw7.ethg++;
        sw7.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw8.ethg++;
        sw8.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw3.ethg++;

        host1.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw1.ethg++;
        host2.ethg++ <--> { delay=0.1ms; datarate=100Mbps; } <--> sw3.ethg++;
}
