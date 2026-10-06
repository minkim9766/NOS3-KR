# 구성 요소(Components)

NOS3는 공통 코어 코드 세트와 커스텀 애플리케이션/시뮬레이터 세트로 구성되어 있습니다. 이러한 코어와 커스텀 사이의 분리를 촉진하기 위해, NOS3는 특정한 디렉토리 구조를 가지고 있으며 git 서브모듈(submodule)을 폭넓게 활용합니다.

## 커스터마이징의 기반이 되는 구성 요소

NOS3는 구성 요소라는 기본 개념을 중심으로 재구성되었습니다. 우주선은 공통 기능으로 이루어진 핵심 집합과, 커스텀 구성 요소 집합으로 이루어지도록 의도되었습니다. 각 구성 요소는 해당 구성 요소의 `fsw` 하위 디렉토리에 배치되는 cFS 애플리케이션으로 표현됩니다. COSMOS 지상 소프트웨어가 구성 요소 애플리케이션을 제어할 수 있도록, 각 구성 요소는 해당 구성 요소의 `gsw` 하위 디렉토리에 배치되는 COSMOS 명령 및 원격측정 테이블 모음을 갖습니다. 많은 경우(전부는 아니지만) 구성 요소는 우주선의 하드웨어 부품이므로, 그 구성 요소를 위한 NOS3 하드웨어 시뮬레이터를 해당 구성 요소의 `sims` 하위 디렉토리에 두는 것이 적절합니다.

### 빌드가 구성 요소를 찾는 방법(How the build finds components)
1. 비행 소프트웨어: 각 구성 요소는 cfg/nos3_defs/targets.cmake 파일에 나열되어 있습니다. 구성 요소 디렉토리의 위치는 최상위 Makefile의 CFS_APP_PATH 환경 변수로 지정됩니다.
2. 시뮬레이터: sims/CMakeLists.txt 파일에는 구성 요소 디렉토리에서 템플릿이 아닌 모든 시뮬레이터를 포함시키는 로직이 있습니다.

### 실행(launch)이 구성 요소를 찾는 방법(How launch finds components)
1. 비행 소프트웨어: 비행 소프트웨어는 fsw/build/exe/cpuN/core-cpuN에 위치합니다. cf 하위 디렉토리에는 빌드된 각 비행 소프트웨어 앱에 대한 공유 오브젝트 라이브러리가 들어 있습니다. cf 하위 디렉토리에는 또한 비행 소프트웨어의 일부로 실행할 앱과 구성 요소 목록을 나열하는 cfe_es_startup.scr 시작 스크립트가 들어 있으며, 이 스크립트는 빌드 과정 중에 cfg/nos3_defs 디렉토리 안의 시작 스크립트로부터 생성됩니다.
2. 시뮬레이터: gsw/scripts/launch.sh 스크립트에는 실행할 시뮬레이터 목록이 하드코딩되어 있습니다.

### COSMOS가 구성 요소를 찾는 방법(How COSMOS finds components)
gsw/cosmos/config/system/MISSION_system.txt 파일에 상대 경로가 추가되어, 각 구성 요소의 COSMOS 명령 및 원격측정 정의 파일을 찾을 수 있게 합니다.

## 커스터마이징 대상(What to customize)

NOS3 저장소의 대부분의 하위 디렉토리/서브모듈은 수정해서는 안 되는 공통 코어 코드입니다. 다음은 여러분의 우주선이 사용하는 구성 요소 애플리케이션/시뮬레이터에 맞게 커스터마이징해야 하는 커스텀 하위 디렉토리/서브모듈 목록입니다.

1. components
    1. 여러분의 우주선에 필요한 각 구성 요소마다 저장소 서브모듈을 추가하세요
2. cfg/nos3_defs
    1. targets.cmake - 비행 소프트웨어의 일부로 빌드할 구성 요소 목록을 이 파일에 추가하세요
    2. cpuN_cfe_es_startup.scr - 비행 소프트웨어의 일부로 실행할 구성 요소 앱 목록을 이 파일에 추가하세요
    3. 필요에 따라 이 디렉토리의 다른 파일들도 커스터마이징하세요
3. gsw/scripts/launch.sh - 실행할 각 시뮬레이터마다 한 줄씩 추가하세요
4. sims/cfg
    1. nos3-simulator.xml - 실행할 각 시뮬레이터마다 시뮬레이터 블록을 추가하세요 (truth42sim, 시간 드라이버, 터미널 같은 코어 시뮬레이터를 위한 블록도 있어야 합니다)
    2. InOut - 42 동역학 시뮬레이터를 제어하고, 42 동역학 시뮬레이터를 하드웨어 시뮬레이터에 연결하기 위해 이 디렉토리 안의 파일들을 커스터마이징하세요 (Inp_IPC.txt)
5. gsw/cosmos/config/
    1. system/MISSION_system.txt - 구성 요소 gsw 디렉토리에 대한 타겟을 선언하세요


## 가상 머신(The Virtual Machine)

NOS3 저장소에는 NOS3 가상 머신을 프로비저닝하기 위한 Vagrantfile이 들어 있습니다. 이 Vagrantfile은 매우 단순하며, 미리 빌드된 가상 머신을 사용합니다. 이 미리 빌드된 가상 머신들은 커뮤니티가 제공하는 Ubuntu Linux, Oracle Linux, Rocky Linux 베이스박스(basebox)로부터 방대한 프로비저닝 과정을 거쳐 만들어지지만, 이 저장소에서 손쉽게 프로비저닝할 수 있도록 별도로 저장되어 있습니다. 이 방대한 프로비저닝 과정에 대한 자세한 내용은 [NOS3 배포 저장소](https://github.com/nasa-itc/deployment)를 참고하세요. 이 저장소는 한때 메인 NOS3 저장소의 서브모듈이었지만, 이제는 미리 빌드된 가상 머신을 사용하기 때문에 더 이상 서브모듈이 아닙니다.


## 디렉토리 구조(Directory Structure)

위의 _커스터마이징 대상_에서 명시한 것 외에는 이 파일/디렉토리/서브모듈들을 수정하지 마세요.

* Vagrantfile - Vagrant와 VirtualBox를 이용해 NOS3 가상 머신을 만들기 위한 파일
* Makefile - 빌드 준비, 빌드, 클린, 실행, 중지를 위한 편의 타겟들이 담긴 최상위 Makefile
* components
  * ComponentSettings.cmake - 공통 빌드 설정
  * 우주선/미션의 일부인 각 구성 요소마다 서브모듈 1개씩; 각 구성 요소는 다음과 같은 하위 디렉토리를 갖습니다:
    * fsw - 애플리케이션 비행 소프트웨어
    * gsw - COSMOS 명령 및 원격측정 테이블
    * sim - 하드웨어 시뮬레이션 소프트웨어
* fsw
  * apps - core Flight Software 애플리케이션
  * build - 비행 소프트웨어 빌드 산출물 위치
  * cfe - core Flight Executive
  * fprime - JPL Flight Executive
  * nos3_defs - 미션에 특화된 정의. (nos3/cfg/nos3_defs 아래에서 찾을 수 있으며) 커스터마이징해야 합니다.
  * osal - 운영체제 추상화 레이어(Operating System Abstraction Layer)
  * psp - 플랫폼 지원 패키지(Platform Support Package)
  * tools - 그 외 각종 cFS 도구
* gsw
  * ait - AIT 설정 파일
  * cosmos - COSMOS 설정 파일. 이 안에서 커스터마이징해야 할 파일은 하나뿐입니다.
  * OrbitInviewPowerPrediction
  * yamcs - YAMCS( /jæmz/ ) - Yet Another Mission Control System
    * yamcs_studio - 명령/원격측정 사용자 레이아웃 설계, 원격측정 표시 등을 위한 애드인
    * openmct - 원격측정 표시를 위한 애드인
* scripts - 편의용 스크립트
  * cfg - 설정 스크립트
  * fsw - 비행 소프트웨어 스크립트
  * gsw - 지상 소프트웨어 스크립트
* sims
  * build - 시뮬레이션 빌드 산출물 위치
  * nos_time_driver - 비행 소프트웨어, 시뮬레이터, 42 전반에 걸쳐 시간을 구동하는 핵심 기능
  * sim_common - 플러그인 시스템 구현 및 시뮬레이터의 여러 핵심 기능을 위한 공통 코어 프레임워크 코드
  * sim_terminal - 하드웨어 시뮬레이터를 대역외(out of band)로 제어하기 위한 터미널을 제공하는 핵심 기능
  * truth_42_sim - 42의 실제(truth) 동역학 데이터를 원격측정 디스플레이용으로 COSMOS에 전달하는 핵심 기능


