# 시뮬레이터

NOS3 시뮬레이터 코드는 C++와 Boost로 개발되었으며, UART(범용 비동기 송수신기), I2C(Inter-Integrated Circuit), SPI(Serial Peripheral Interface), CAN(Controller Area Network), 그리고 discrete I/O(입출력) 신호/연결/버스와 같은 하드웨어 버스를 시뮬레이션하는 소프트웨어 버스, 노드, 기타 연결을 제공하기 위해 NASA Operational Simulator(NOS) Engine에 의존합니다. NOS Engine은 또한 모든 시뮬레이터(그리고 비행 소프트웨어)에 시간을 배포하는 메커니즘도 제공합니다.

> 💡 **초보자 가이드**
> UART, I2C, SPI, CAN은 모두 전자기기들이 서로 데이터를 주고받는 "통신 규격"의 이름이에요. 예를 들어 UART는 두 개의 선으로 데이터를 순서대로 주고받는 단순한 방식이고, I2C·SPI는 여러 부품이 하나의 버스(선)를 공유하며 통신하는 방식입니다. 실제 위성 부품들이 이런 방식으로 통신하기 때문에, 시뮬레이터도 이 통신 방식들을 흉내 내야 진짜처럼 작동해요.

## 아키텍처 설계 이유
### 왜 NOS Engine인가?
NOS Engine은 두 가지 이유로 추상 하드웨어 버스 인터페이스로 선택되었습니다.
1.  비행 소프트웨어 측면에서, 다양한 공통 하드웨어 버스 유형(UART, SPI, I2C 등)에 대한 API를 갖춘 단일 하드웨어 라이브러리를 작성하면, 실제 하드웨어용과 (NOS3) 시뮬레이션된 하드웨어용을 모두 거의 동일하게 빌드할 수 있습니다.
1.  시뮬레이터 측면에서, NOS Engine은 사용하기 쉬운 인터페이스를 제공하며, (향후 기능으로) 하드웨어 결함, 버스 단절/오류 등을 모델링할 수 있는 능력도 제공합니다.

### 왜 하드웨어 모델, 플러그인, 추상 팩토리 등을 쓰는가?
이를 통해 하드웨어 시뮬레이터를 철저하게 XML 기반으로 구동할 수 있습니다. 시뮬레이터 실행 파일이 시뮬레이터 하드웨어 라이브러리의 출처를 알고 있거나(디렉터리를 가리키거나) 찾을 수 있는 한(XML에서 공유 객체 라이브러리 파일을 지정), 시뮬레이터 실행 파일은 매우 작고 확장 가능하게 만들 수 있으며, 필요한 하드웨어 시뮬레이터를 제공하기 위해 플러그인 형태의 공유 객체 라이브러리에 의존할 수 있습니다. 이 플러그인 아키텍처가 제공하는 강력함을 보여주는 예시로는 `sim_common` 서브모듈 저장소에 있는 `all_simulators.cpp` / `nos3-all-simulators`(XML 설정 파일에 있는 모든 활성 하드웨어 모델을 각각 자신만의 스레드에서 실행)와 `single_simulator.cpp` / `nos3-single-simulator`(명령줄에서 이름을 지정하여 XML 파일 내 단일 활성 하드웨어 모델을 실행)를 참고하시기 바랍니다.

> 💡 **초보자 가이드**
> "플러그인(plug-in)" 방식이란, 프로그램 본체를 건드리지 않고도 별도의 부품(라이브러리 파일)을 끼워 넣어 기능을 추가할 수 있게 만든 구조를 말해요. 마치 레고 블록처럼, 새로운 하드웨어 시뮬레이터가 필요하면 새 블록(플러그인)만 만들어 끼우면 되고 기존 코드는 그대로 둘 수 있습니다.

### 왜 데이터 제공자(Data Provider)를 쓰는가?
NOS Engine은 하드웨어 모델이 다양한 일반적인 하드웨어 버스 유형에 접근할 수 있는 깔끔한 인터페이스를 제공하고, 플러그인은 하드웨어 모델을 플러그 앤 플레이 방식으로 만드는 동기를 부여합니다.

하지만 왜 플러그인 형태의 데이터 제공자가 필요할까요?

그 이유는 하드웨어 모델을 태양 벡터, 태양각, 위치 등과 같은 "실제 값(truth)" 데이터의 출처로부터 분리(decouple)하기 위해서입니다. GPS 하드웨어의 모델은 여러 가지가 있을 수 있지만, 어떤 GPS 하드웨어 모델이든 하드웨어 버스를 통해 전송할 위치 데이터의 출처가 필요합니다(UART를 통한 NMEA 형식이나 어떤 독자적인 바이너리 형식 등으로). 이 데이터의 출처는 파일(NOS3 초기 개발에서 광범위하게 사용됨)일 수도 있고, 42(현재 시뮬레이터에서 "실제 값" 데이터로 광범위하게 사용됨)일 수도 있습니다. 또한 이는 아직 생각조차 하지 못한 미래의 데이터 제공자나 42의 대안으로도 쉽게 확장할 수 있게 해줍니다. 하드웨어 시뮬레이터 개발자인 여러분이 자신의 하드웨어 모델 플러그인과 데이터 제공자 플러그인 사이의 인터페이스에 대해 스스로 합의하기만 한다면, 현재와 미래의 유연성/확장성에는 한계가 없습니다. 그리고 외부 "실제 값" 제공자(예: 42)와의 인터페이스와 달리, 이 (하드웨어 모델과 데이터 제공자 간) 인터페이스는 여러분이 완전히 통제할 수 있습니다.

## 배경 지식 및 관련 개념
### 추상 팩토리 디자인 패턴 (Abstract Factory Design Pattern)
C++는 객체지향 프로그래밍(Object Oriented) 패러다임을 지원하는 프로그래밍 언어이며, 그 패러다임 안에서 가장 강력한 설계 추상화 방법 중 하나가 바로 디자인 패턴(design pattern)입니다. NOS3 시뮬레이터를 유연하고 확장 가능하게 만들기 위해 많이 사용된 특정 디자인 패턴이 바로 추상 팩토리(Abstract Factory) 패턴입니다. 이 디자인 패턴은 여러 곳에서 설명되고 있는데, 비교적 이해하기 쉬운 설명으로는 ["Abstract Factory Step-by-Step Implementation in C++"](http://www.codeproject.com/Articles/751869/Abstract-Factory-Step-by-Step-Implementation-in-Cp) 글을 참고할 수 있습니다.

> 💡 **초보자 가이드**
> "팩토리(Factory)" 패턴은 이름 그대로 "공장"처럼 객체를 찍어내는 방식이에요. 코드 어딘가에서 직접 `new FooHardwareModel()` 같이 객체를 만드는 대신, "이름표"(문자열)만 건네주면 팩토리가 알아서 알맞은 객체를 만들어서 돌려주는 방식입니다. 덕분에 나중에 새로운 하드웨어 모델을 추가해도 기존 코드를 고칠 필요 없이 팩토리에 등록만 하면 됩니다.

초기 NOS3 시뮬레이터 코드베이스가 개발된 이후에도 추가적인 시뮬레이터를 플러그인 라이브러리 형태로 쉽게 구성하고 빌드할 수 있게 해주는 것이 바로 이 팩토리 디자인 패턴입니다. 앞서 언급한 글에 나오는 도형(shape)과 도형 팩토리 대신, NOS3 시뮬레이터에서 팩토리를 통해 생성되는 구성 요소는 하드웨어 모델과 데이터 제공자입니다.

### XML 설정
팩토리 디자인 패턴을 사용하는 것 외에도, 각 개별 시뮬레이터는 생성할 하드웨어 모델을 지정하도록 설정되어야 합니다. 또한 하드웨어 모델은 하드웨어가 어떻게 동작할지 설정하기 위한 매개변수가 필요할 수 있습니다. 또한 하드웨어는 discrete I/O, I2C, UART와 같은 통신을 위한 연결(connection)을 가지고 있으므로, 시뮬레이션에서 하드웨어 모델은 이러한 연결의 소프트웨어 버전을 만들어야 하며, 이 연결들 역시 버스 유형, 버스 이름, 버스 주소와 같은 설정 데이터가 필요할 수 있습니다. 또한 일부 하드웨어 모델(GPS나 자력계 시뮬레이터 등)은 환경 데이터가 필요할 수 있으므로, 하드웨어 모델은 환경 데이터를 제공할 데이터 제공자를 생성해야 합니다. 데이터 제공자는 데이터 제공자의 유형이나 파일명, 혹은 호스트와 포트와 같은 설정 데이터가 필요할 수 있습니다.

특정 시뮬레이션 실행 파일에 대한 설정은 XML(eXtensible Markup Language) 형식의 파일로 지정되며, 이 파일은 해당 실행 파일 안에서 인스턴스화될 시뮬레이터들의 목록을 제공합니다. 각 시뮬레이터는 하드웨어 모델을 지정하며, 하드웨어 모델은 추가적인 설정 매개변수를 가질 수 있습니다. 하드웨어 모델은 데이터 제공자 설정 매개변수를 갖는 선택적인 데이터 제공자에 의존한다고 지정할 수도 있습니다. 하드웨어 모델은 또한 연결 설정 매개변수를 갖는 하나 이상의 소프트웨어 통신 연결을 지정할 수도 있습니다.

## 나만의 하드웨어 모델 구현하기 (데이터 제공자, 연결 포함)
다음 섹션들은 자신만의 하드웨어 모델을 구현하는 방법을 설명합니다.

### 설정 데이터 프로퍼티 트리 (Configuration Data Property Tree)
프로퍼티 트리(property tree)로 표현되는 XML 파일의 설정 데이터가 필요한 경우, 다음과 같은 코드를 사용해 가져옵니다:

```c
std::string param = config.get("simulator.<subname>.<subsubname>", "LITERAL");
```

이 코드에 대해 몇 가지 참고 사항이 있습니다. 먼저, `config`는 `const boost::property_tree::ptree&` 타입의 변수입니다. 각 하드웨어 모델과 데이터 제공자는 이 타입의 매개변수 하나를 받는 생성자를 반드시 제공해야 하며(아래 참고), 따라서 이 매개변수는 필요한 설정과 초기화를 수행하는 생성자 코드에서 사용할 수 있습니다.

둘째로, 위 코드가 실행될 때 리터럴 `"LITERAL"`의 데이터 타입이 `ptree`가 매개변수를 반환하려고 시도하는 데이터 타입을 결정합니다(여기서는 리터럴 문자열이므로, 값이 할당되는 변수도 그에 맞게 `std::string`으로 선언됩니다). 또한 검색할 키 이름에서 중첩된 XML 태그 레벨을 나타내기 위해 XML 태그 이름을 마침표로 구분한다는 점에도 유의하세요. 또한 키 이름에는 `"nos3-configuration"`이나 `"simulators"` 접두사를 포함하지 않는다는 점도 유의하세요(이것들은 기본 설정 파일에 나타납니다). 이 접두사들은 메인 프로그램에서 설정 데이터를 읽고 파싱하는 데 사용되는 `SimConfig` 객체에 의해 제거됩니다. 따라서 키 이름은 `"common."` 또는 `"simulator."`로 시작해야 합니다. (XML을 표현하는) 프로퍼티 트리에서 해당 키를 찾을 수 없는 경우, `"LITERAL"` 값이 기본값으로 사용됩니다.

다음은 일반적인 키 목록입니다:
1. `common.log-config-file` – ITC Logger 클래스를 사용하는 로깅용 설정 파일의 이름입니다. 보통 이 항목은 직접 손댈 필요가 없습니다.
1. `common.nos-connection-string` – NOS Engine 서버로의 연결 정보
1. `common.absolute-start-time` – J2000 기점(epoch)으로부터 십진수 초 단위로 표현된 시뮬레이션의 절대 시작 시간입니다.
1. `common.sim-microseconds-per-tick` – 매 시간 틱(tick)마다 시뮬레이션이 진행해야 할 마이크로초 수를 나타내는 정수입니다. NOS Engine은 버스 상에서 시간을 틱의 개수로 배포한다는 점에 유의하세요. 따라서 여러분의 하드웨어 모델이나 데이터 제공자가 (시간 마스터가 시간을 구동하는 버스로부터) 시뮬레이션 시간을 나타내는 틱 수를 받는다면, 다음과 같이 이를 NOS3와 동기화된 시뮬레이션 실세계 시간으로 변환할 수 있습니다:
```c
double abs_time =_absolute_start_time + (double(ticks *_sim_microseconds_per_tick)) / 1000000.0;
```
5. `common.real-microseconds-per-tick` – 보통 NOS Engine 버스 상에 시뮬레이션된 틱을 보낼 때 얼마나 지연할지를 결정하는 단일 메인 시간 드라이버에서 사용됩니다. 드물지만 하드웨어 시뮬레이터가 실제 시간만큼 지연해야 할 필요가 있을 때 사용될 수도 있습니다(하드웨어 시뮬레이터는 일반적으로 시뮬레이션 시간을 사용해야 합니다).
1. `simulator.name` – 여러분이 시뮬레이터에 붙인 이름입니다. `nos3-single-simulator`를 실행할 때 지정하는 문자열과 일치해야 합니다.
1. `simulator.active` – 보통 true입니다. false인 경우, 메인 함수에서 `SimConfig::run_simulator` 메소드가 호출될 때 해당 시뮬레이터는 실행되지 않습니다(아래 참고).
1. `simulator.hardware-model.type` – 하드웨어 모델의 이름 문자열입니다. 플러그인 모델을 따르는 모든 하드웨어 모델의 소스 코드에 반드시 있어야 하는 `REGISTER_HARDWARE_MODEL` 호출에 주어진 이름 문자열과 매칭됩니다.
1. `simulator.hardware-model.connections` – 하드웨어 모델이 가진 연결들을 기술하는 \<connection\>\</connection\> 태그의 목록입니다.
1. `simulator.hardware-model.data-provider` – (데이터 제공자 팩토리를 사용해 데이터 제공자가 만들어진 경우) 그 데이터 제공자에 대한 정보입니다.
1. `simulator.hardware-model.data-provider.type` – (데이터 제공자를 사용하는 경우) 데이터 제공자의 이름 문자열입니다. 플러그인 모델을 따르는 모든 데이터 제공자의 소스 코드에 반드시 있어야 하는 `REGISTER_DATA_PROVIDER` 호출에 주어진 이름 문자열과 매칭됩니다.

### 하드웨어 모델
새로운 하드웨어 모델을 만드는 공식은 다음과 같습니다:
1. `Nos3` 네임스페이스 안에, `SimIHardwareModel`을 public으로 상속받는 클래스(예: `FooHardwareModel`)를 만듭니다.
1. 설정 데이터를 담고 있는 `const boost::property_tree::ptree&` 매개변수를 받는 생성자를 만듭니다. 이 생성자가 설정 데이터를 가져오고 매개변수를 저장하며, 연결이나 데이터 제공자를 생성하거나, 하드웨어 모델에 필요한 그 밖의 초기화 작업을 수행하도록 합니다.
1. `void run(void)` 메소드를 만듭니다. 이 메소드는 하드웨어 모델이 실행 중일 때 수행해야 할 작업들을 처리해야 합니다.
1. 하드웨어 모델에 대한 이름 문자열(예: `FOOHARDWARE`)을 만들고, 소스 파일에 다음과 같은 줄을 추가합니다:
```c
REGISTER_HARDWARE_MODEL(FooHardwareModel,"FOOHARDWARE");
```
5. 하드웨어 모델이 데이터 제공자를 사용한다면, 하드웨어 모델은 `SimIDataProvider *` 타입의 멤버 변수를 가질 수 있으며, 이는 다음과 같은 코드로(멤버 변수 이름이 `_sim_data_provider`라고 가정할 때) 설정 데이터를 기반으로 하드웨어 모델 생성자에서 설정할 수 있습니다:
```c
std::string dp_name = config.get("simulator.hardware-model.data-provider.type", "BARPROVIDER");
_sim_data_provider = SimDataProviderFactory::Instance().Create(dp_name, config);
```

> 💡 **초보자 가이드**
> "네임스페이스(namespace)"는 이름 충돌을 막기 위한 일종의 "구역 표시"예요. 예를 들어 다른 라이브러리에도 `Foo`라는 클래스가 있을 수 있는데, `Nos3::Foo`처럼 네임스페이스를 붙이면 서로 구분이 됩니다. 그리고 "상속(inherit)"이란, 기존 클래스(부모, 여기서는 `SimIHardwareModel`)가 가진 기본 기능을 새 클래스가 그대로 물려받아 시작할 수 있게 해주는 개념입니다.

#### 명령 연결 (Command Connection)
시뮬레이션 하드웨어 모델의 명령 연결은 하드웨어가 하드웨어 버스에 대해 가지는 일반적인 의미의 연결이 아닙니다. 이는 단지 시뮬레이션 자체를 대역 외(out of band)로 명령하기 위해 사용됩니다. 이러한 명령을 수행하는 한 가지 방법은 NOS3의 일부인 SimTerminal 실행 파일을 사용하는 것입니다. 이 터미널은 시작되면 명령 버스의 한 노드로 등록됩니다. 그런 다음 명령 버스에 있는 다른 어떤 노드로도 메시지를 보내는 데 사용할 수 있습니다. 이 메시지들은 ASCII이거나 16진수 바이트일 수 있습니다.

기본 `SimIHardwareModel`은 어떤 하드웨어 모델 시뮬레이션이든 명령을 받을 수 있도록 명령 버스에 노드를 생성합니다. 시뮬레이션이 명령 버스에서 수신한 명령에 기반해 동작을 수행하도록 하려면, 하드웨어 모델에서 해야 할 일은 다음이 전부입니다:
1. 하드웨어 모델 클래스에서 `SimIHardwareModel` 메소드를 오버라이드합니다:
```c
void command_callback(NosEngine::Common::Message msg)
```

명령에 대한 응답으로 하드웨어 모델이 데이터를 주고받는 방식의 예시는 기본 `SimIHardwareModel` 클래스의 `command_callback` 메소드를 참고하세요.

#### 시간 연결 (Time Connection)
하드웨어 시뮬레이터가 실세계 시간 개념을 갖도록 하기 위해, NOS Engine에 시간 클라이언트 노드로 노드를 등록합니다. 시간 클라이언트 노드를 만들고 사용하는 공식은 다음과 같습니다:
하드웨어 모델 클래스에, 버스와 시간 노드용 멤버 변수를 추가합니다. 예:
```c
std::unique_ptr<NosEngine::Client::Bus> _time_bus;
NosEngine::Client::TimeClient* _time_node;
```
하드웨어 모델 생성자에서:
1. 기본 `SimIHardwareModel` 클래스에는 연결할 버스를 위한 기존 허브(멤버 변수 `_hub`)가 있습니다. NOS Engine을 위한 연결 문자열은 다음과 같은 호출로 XML 설정 데이터에서 가져올 수 있습니다:
```c
std::string connection_string = config.get("common.nos-connection-string", "tcp://127.0.0.1:12001");
```
2. XML 설정 파일에 다음과 같은 "time" 유형 연결을 추가합니다:
```xml
<connection><type>time</type><bus-name>command</bus-name><node-name>my-time-node</node-name></connection>
```
3. 버스 이름과 노드 이름을 `time_bus_name`, `time_node_name`과 같은 `std::string` 변수로 가져옵니다. 이를 수행하는 방법의 예시는 예제 시뮬레이터를 참고하세요.
4. 버스 객체를 생성합니다:
```c
_time_bus.reset(new NosEngine::Client::Bus(_hub, connection_string, time_bus_name));
```
5. 버스에 시간 클라이언트 노드를 생성합니다:
```c
_time_node = _time_bus->get_or_create_time_client(time_node_name);
```
시간이 필요한 하드웨어 모델 메소드에서:
1. 경과한 "틱(tick)"의 수를 얻으려면 다음을 호출합니다:
```c
_time_node->get_last_time()
```
2. 이를 실세계 시간으로 변환하려면, `SimIHardwareModel`은 (XML 설정 파일의 common 섹션 데이터로부터 설정되는) `_absolute_start_time`과 `_sim_microseconds_per_tick` 멤버 변수를 가지고 있으며, 다음과 같이 실세계 시간을 계산하는 데 사용할 수 있습니다:
```c
_absolute_start_time + (double(_time_node->get_last_time() * _sim_microseconds_per_tick)) / 1000000.0);
```
정리하려면, 하드웨어 모델 소멸자에서 다음을 호출합니다:
```c
_time_bus.reset();
```

#### UART 연결
UART를 통해 연결되는 하드웨어의 경우, 하드웨어가 UART 버스의 노드를 만들고 사용하는 공식은 다음과 같습니다:
하드웨어 모델 클래스에, 다음과 같이 UART 연결용 멤버 변수를 추가합니다:
```c
std::unique_ptr<NosEngine::Uart::Uart> _uart_connection;
```
하드웨어 모델 생성자에서:
1. 기본 `SimIHardwareModel` 클래스에는 연결할 버스를 위한 기존 허브(멤버 변수 `_hub`)가 있습니다. NOS Engine을 위한 연결 문자열은 다음과 같은 호출로 XML 설정 데이터에서 가져올 수 있습니다:
```c
std::string connection_string = config.get("common.nos-connection-string", "tcp://127.0.0.1:12001");
```
2. XML 설정 파일에 다음과 같은 "usart" 유형 연결을 추가합니다:
```xml
<connection><type>usart</type><bus-name>usart_0</bus-name><node-port>99999</node-port></connection>
```
3. 버스 이름과 노드 포트를 `bus_name`, `node_port`와 같은 `std::string` 변수로 가져옵니다. 이를 수행하는 방법의 예시는 예제 시뮬레이터를 참고하세요.
4. UART 연결 객체를 생성합니다:
```c
_uart_connection.reset(new NosEngine::Uart::Uart(_hub, config.get("simulator.name", "foosim"), connection_string, bus_name));
```
5. 연결을 열고, 하드웨어 UART가 읽힐 때 실행될 콜백을 설정합니다:
```c
_uart_connection->open(node_port);
_uart_connection->set_read_callback(std::bind(&FooHardwareModel::uart_read_callback, this, std::placeholders::_1, std::placeholders::_2));
```
콜백을 처리할 하드웨어 모델 메소드를 만듭니다(특정 하드웨어 모델을 위한 대부분의 커스텀 작업이 이루어지는 곳입니다):
1. 시그니처는 다음과 같아야 합니다:
```c
void FooHardwareModel::uart_read_callback(const uint8_t *buf, size_t len);
```
2. 데이터를 반환하려면 UART 메소드를 사용합니다:
```c
size_t UART::write(const uint8_t *const buf, size_t len);
```
예시가 필요하면 예제 시뮬레이션 코드를 참고하세요.

3. 하드웨어 모델 소멸자에서 다음 호출을 수행합니다:
```c
_uart_connection->close();
```

## 나만의 시뮬레이터 작성하기
다음 공식은 위의 방법들로 만든 하드웨어 모델(및 선택적으로 데이터 제공자)을 이용해 시뮬레이터를 만드는 방법을 설명합니다:
1. 표준 설정 파일(표준 설정 파일 이름은 `nos3-simulator.xml`)의 `<simulators></simulators>` 태그 안에 다음과 같은 XML을 추가합니다
```xml
<simulator>
   <name>foosim</name>
   <active>true</active>
   <library>libexample_sim.so</library>
   <hardware-model>
      <type>FOOHARDWARE</type>
      <connections>
         <connection>
            <connection-param1>cp1</connection-param1>
            <!-- ... -->
            <connection-paramN>cpN</connection-paramN>
         </connection>
      </connections>
      <data-provider>
         <type>FOOPROVIDER</type>
         <provider-param1>fpp1</provider-param1>
         <!-- ... -->
         <provider-paramN>fppN</provider-paramN>
      </data-provider>
      <other-hardware-parameter1>OTHER-FOO</other-hardware-parameter1>
      <!-- ... -->
      <other-hardware-parameterN>OTHER-FOO</other-hardware-parameterN>
   </hardware-model>
</simulator>
```
2. XML 커스터마이징하기:
   1. `simulator.name`은 실행할 때 `nos3-single-simulator`에 전달하는 이름이어야 합니다.
   2. `simulator.active` 태그는 시뮬레이터를 실행하지 않으려는 경우가 아니라면 true여야 합니다(그런 경우는 false).
   3. `simulator.library` 태그에는 예제 시뮬레이터 공유 객체 라이브러리 파일의 이름이 들어가야 합니다(보통 `lib<project>.so` 형태이며, 여기서 `<project>`는 `CMakeLists.txt` 파일에서 프로젝트에 지정한 프로젝트 이름입니다; 아래 참고)
   4. `simulator.hardware-model.type`은 위의 `REGISTER_HARDWARE_MODEL` 줄에서 사용한 문자열과 동일해야 합니다.
   5. `simulator.hardware-model.data-provider.type`은 위의 `REGISTER_DATA_PROVIDER` 줄에서 사용한 문자열과 동일해야 합니다.
   6. 그 밖의 모든 태그는 여러분의 자유입니다… 원하는 이름을 만들고, 위의 정보를 이용해 데이터에 접근하면 됩니다. UART, I2C, 명령 연결(시뮬레이터 터미널로 시뮬레이터를 제어하는 데 사용됨)과 같은 여러 일반적인 연결 유형을 사용하는 예시가 소스 코드에 있다는 점도 참고하세요. 또한 명령 연결은 `SimIHardwareModel` 기본 클래스에서 자동으로 설정된다는 점도 참고하세요. 명령 버스로 들어오는 명령에 시뮬레이터가 반응하도록 하려면, 하드웨어 모델 클래스에서 `SimIHardwareModel::command_callback` 메소드를 오버라이드하기만 하면 됩니다(기본 구현은 아무 것도 하지 않습니다).

## 예제 시뮬레이터
이 소개 글이 NOS3 시뮬레이터 개발에 사용된 유연하고 확장 가능한 프레임워크를 설명하는 데 도움이 되었기를 바랍니다. 이 소개 글은 NOS3 시뮬레이터 내부에서 사용되는 디자인 패턴을 설명하고, 하드웨어 모델(및 데이터 제공자와 그 밖의 지원 항목들)을 추가하는 방법과, 하드웨어 모델들을 조합해 NOS3 시뮬레이션 환경의 일부가 될 수 있는 독립적인 시뮬레이터로 만드는 방법을 설명하고자 했습니다.

완전한 예시를 보려면, `nos3` git 저장소의 `components/sample/sim/` 하위 디렉터리에 있는 소스 코드와 `CMakeLists.txt` 파일을 참고하고, `nos3` git 저장소의 `cfg/sims/nos3-simulator.xml` 설정 파일(이름이 `"sample_sim"`인 시뮬레이터 섹션 참고)을 참고하세요. 또한 새 시뮬레이터의 `CMakeLists.txt` 파일 시작 부분에 `"project(sample_sim)"`과 같은 프로젝트 이름 줄이 있다면, `nos3` git 저장소의 `sims/CMakeLists.txt` 파일 안 # NOS3 Sim Core 아래에 `"add_subdirectory(sample_sim)"` 줄을 추가하여 새 시뮬레이터가 빌드되도록 할 수 있습니다. 다만 `sims/CMakeLists.txt` 파일은 nos3/sims/ 안에서 부모 폴더가 `"<name-of-your-sim>_sim"` 형태를 따르는, 올바르게 구성되고 이름 붙여진 모든 디렉터리를 찾도록 작성되어 있습니다.
