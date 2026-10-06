# NOS3를 여러 대의 컴퓨터에서 빌드하고 실행하기(NOS3 Building and Running on Multiple Machines)

NOS3를 실행할 때, 지상 소프트웨어는 한 대의 컴퓨터에서, 위성 시뮬레이터는 다른 컴퓨터에서 실행되도록 여러 VM 또는 물리 컴퓨터에 나누어 실행하는 것도 가능합니다. 방법은 다음과 같습니다:

## VM 설정(VM Setup)

먼저 서로 통신할 수 있는 두 대의 VM 또는 물리 머신이 필요합니다. VM의 경우, 설정에서 두 번째 네트워크 카드를 활성화해야 합니다:

![image](https://github.com/user-attachments/assets/68ca0685-139d-45bc-9c3d-8ac31837dcc0)

VM 전원이 꺼진 상태에서 'Enable Network Adapter(네트워크 어댑터 활성화)' 체크박스를 체크하고, VM 자체를 NAT 네트워크(같은 호스트 상의 서로 다른 VM들 간의 통신을 가능하게 하는 것으로, 기본 NAT 어댑터와는 다릅니다)에 연결하면 됩니다. NAT 네트워크가 아직 없다면, VirtualBox의 'Tools' 메뉴에서 새로 만들 수 있습니다.

물리 머신의 경우, 두 대 모두 같은 네트워크에 있어야 하며 서로 ping이 가능해야 합니다.

## GSW 컴퓨터/VM

먼저, Docker swarm에서 'manager(관리자)' 노드와 'worker(작업자)' 노드를 각각 만들어야 합니다. swarm이 제공하는 컨테이너나 실행 방식은 사용하지 않고, 오직 네트워킹 측면만 사용할 것입니다. 저자는 현재 지상 소프트웨어(COSMOS)를 실행하는 VM을 'manager'로 지정하기로 했으며, 다음 명령을 실행하는 것만으로 준비할 수 있습니다

        make prep-gsw

이 명령은 고정 IP 주소를 설정하고 swarm을 초기화하며, 이 명령을 실행한 VM이 'manager' 노드로 설정됩니다. 출력 결과에는 다른 VM에서 실행해야 하는 명령이 함께 제공되는데, 'swarm join' 명령에는 무작위로 할당되는 토큰이 포함되어 있어 미리 하드코딩할 수 없기 때문입니다. 그런 다음, 그 명령을 실행하고 나면 단순히

        make start-gsw

를 실행하는 것만으로 지상 소프트웨어(COSMOS)가 실행되고 관련된 오버레이 네트워크(overlay network)가 생성됩니다. 오버레이 네트워크는 기존의 브리지 네트워크(bridge network)와 이름이 완전히 동일하며, 유일한 차이점은 이론적으로 여러 VM에 걸쳐 확장될 수 있다는 점입니다.

엄밀히 말하면, `make prep-gsw`를 항상 실행할 필요는 없습니다. 두 컴퓨터가 같은 네트워크에 있다면 단순히

        docker swarm init --advertise-addr <your_ip_address>

를 실행하는 것만으로도 동작합니다.

# 위성 컴퓨터/VM

위에서 언급했듯이, `make prep-gsw`의 출력 결과에는 위성 컴퓨터/VM을 swarm 네트워크에 연결하기 위해 실행해야 하는 명령이 포함되어 있습니다. 이 명령은 다음과 같은 형식입니다

        docker swarm join --token <your_token> <your_ip_address>:2377

여기서 <your_ip_address>는 대부분 10.10.10.101일 것입니다(그렇지 않다면 10.10.10.100일 가능성이 높습니다). 이 명령은 `make prep-gsw` 또는 `docker swarm init --advertise-addr <your_ip_address>`의 출력 결과로 제공되며,

        make prep-sat

를 먼저 실행한 뒤에 이어서 실행해야 합니다. 이는 `make prep-gsw` 이후에 실행하는 경우, IP 주소가 올바르게 설정되어 두 컴퓨터가 서로 통신할 수 있도록 하기 위함입니다. 그런 다음, 위성 쪽을 실행하려면 단순히

        make start-sat

를 실행하면 됩니다. 이 명령은 필요한 네트워크를 생성하지 않으므로, 반드시 `make start-gsw`를 실행한 이후에 실행해야 합니다.

# 문제 해결(Troubleshooting)

두 VM이 모두 NAT 네트워크에 추가되고 나면, 앞서 설명한 지상 소프트웨어 VM/컴퓨터에 대한 안내대로 잘 동작할 것입니다. 만약 그렇지 않다면, /etc/netplan 아래의 netplan 파일을 수정하고 `sudo netplan apply`를 실행하여 각 컴퓨터에 "eth1" 네트워크 인터페이스를 추가해야 할 수도 있습니다. 필요한 변경 사항은 다음과 같습니다(위성 컴퓨터의 IP 주소는 10.10.10.101, GSW 컴퓨터의 IP 주소는 10.10.10.100이라고 가정):

![image](https://github.com/user-attachments/assets/14b733f1-3d04-4c4a-8209-9b5004bfec44)

한 가지 더 참고할 점으로, 만약 지상 소프트웨어가 제대로 로드되지 않는다면(특히 시작했다가 멈추고 다시 시작한 이후에), 다시 빌드하고 재실행하면 문제가 해결되는 경우가 많습니다.
