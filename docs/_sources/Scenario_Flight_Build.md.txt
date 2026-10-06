# 시나리오 - 비행용(Flight) 빌드

이 시나리오는 NOS3 환경에 비행용 툴체인(flight toolchain)을 통합하는 과정을 보여주기 위해 만들어졌습니다.
NOS3는 프로세서 에뮬레이션을 지원하지 않지만, NOS3용은 물론 다른 타겟(target)용으로도 빌드할 수 있습니다.

> 💡 **초보자 가이드**: "툴체인(Toolchain)"이란 소스 코드를 특정 하드웨어에서 실행 가능한 프로그램으로 변환해주는 컴파일러 등 도구들의 묶음을 말합니다. 예를 들어 컴퓨터에서 작성한 코드를 라즈베리파이 같은 다른 종류의 CPU에서 돌아가게 하려면, 그 CPU에 맞는 전용 컴파일러(교차 컴파일러, cross compiler)가 필요합니다.

이 시나리오는 2025년 5월 22일에 마지막으로 업데이트되었으며, 당시 `dev` 브랜치(커밋 [a3e7c100])를 기반으로 작성되었습니다.

## 학습 목표

이 시나리오를 마치면 다음을 할 수 있게 됩니다:
* 도커(docker)에 비행용 툴체인 통합하기.
* 개발용 도커 컨테이너를 빌드하고 사용하도록 선택하기.
* 다른 타겟용으로 빌드하기 위해 NOS3의 설정 파일 업데이트하기.
* 원하는 타겟을 위한 비행 소프트웨어 빌드하기.

## 사전 준비 사항

시나리오를 실행하기 전에 다음 단계를 완료하세요:
* [시작하기](./NOS3_Getting_Started.md)
  * {ref}`설치 <installation>`
  * {ref}`실행 <running>`
* [https://github.com/nasa-itc/deployment](https://github.com/nasa-itc/deployment) 클론하기
  * 작성 시점 기준 `main` 브랜치 커밋 [55f6b01]

## 실습 과정

시작하기 전에 몇 가지 용어를 명확히 해야 합니다:
* "타겟(target)"은 개발용 특정 설정을 가리킬 수도 있고, 비행용 프로세서를 가리킬 수도 있습니다.
  * 이 예제에서는 "타겟"을 비행용 프로세서를 가리키는 의미로 사용하겠습니다.
* 교차 컴파일을 가능하게 하려면 해당 타겟용 툴체인이 필요합니다.
  * 여러분의 특정 작업에 맞는 올바른 툴체인을 선택하는 것이 중요합니다!

---
### 타겟 툴체인

가장 먼저 해야 할 일은 비행용 타겟을 식별하는 것입니다.
이번 시나리오에서는 라즈베리파이(Raspberry Pi, 64비트 ARM) 타겟을 추가할 것입니다.
이를 위한 64비트 컴파일러 패키지는 `gcc-aarch64-linux-gnu`와 `g++-aarch64-linux-gnu` 툴체인이며, 둘 다 패키지 관리자를 통해 쉽게 설치할 수 있습니다.

위 툴체인을 VM이나 호스트 머신에 직접 설치하는 방식은 NOS3에서는 동작하지 않습니다. NOS3는 모든 것을 빌드하고 실행하기 위해 도커 컨테이너를 활용하기 때문입니다.
먼저 이 도커 파일(docker file)에 포함시킬 내용을 편집하는 것부터 시작해봅시다.
사전 준비 사항으로서 nasa-itc/deployment 저장소를 클론해달라고 요청드렸는데, 이제 `./deployment/Dockerfile`을 열어 편집해보세요.

[DockerFile](https://github.com/nasa-itc/deployment/blob/2ec5f5748cbca37e00e7b21b0b7084e50df077f7/Dockerfile)은 새로운 것을 추가할 때 테스트를 빠르게 하기 위해 단계별(staged) 빌드 방식을 사용합니다:
* 각 단계는 `FROM` 문으로 시작합니다.
* 작성 시점(위 링크 참고) 기준, 다음과 같이 구성되어 있습니다:
  * nos0 - apt-get과 pip3를 통해 초기 패키지 설치
  * nos1 - NOS3 미들웨어(NOS Engine, ITC Common) 설치
  * nos2 - CryptoLib 설치

이 기존 파일에 다음 단계를 추가로 확장해봅시다:
```
# Add the toolchain for the Raspberry Pi
FROM nos2 AS nos3
RUN apt-get update -y \
    && apt-get install -y \
        gcc-arm-linux-gnueabihf \
        g++-arm-linux-gnueabihf \
    && rm -rf /var/lib/apt/lists/*
```

위 내용을 추가하고 저장했다면, 이제 터미널에서 Dockerfile 상단의 단계들을 따라 이 컨테이너를 로컬에서 빌드할 수 있습니다:
* cd deployment
* docker build -t rpi_flight .

---
### NOS3 수정하기

컨테이너가 빌드되는 동안(시간이 좀 걸립니다) NOS3의 파일들을 편집하기 시작할 수 있습니다:
* NOS3 저장소에서 다음을 편집하세요:
  * [./scripts/env.sh](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/scripts/env.sh#L51)
    * `DBOX` 줄을 새로운 박스 이름과 버전을 사용하도록 업데이트하세요
    * `DBOX="rpi_flight:latest"`

이 시점부터는 기술적으로 다른 최상위 수준의 NOS3 수정은 필요하지 않다는 점에 유의하세요. 우리는 기반이 되는 FSW를 직접 수정하고 있는 것입니다.
이렇게 하면 지금까지처럼 NOS3를 빌드하고 실행할 수 있으면서, 동시에 원하는 비행용 타겟을 위한 FSW도 빌드할 수 있게 됩니다. 이를 통해 개발용 보드나 FlatSat(비행모델과 동일한 지상 시험용 시스템)을 이용할 수 있을 때 그것으로 테스트하면서도 NOS3를 계속 개발에 활용할 수 있습니다.

---
### cFS 수정하기

새로운 타겟을 설정하려면 몇 가지 cFS 수정이 필요합니다:
* [./cfg/nos3_defs/toolchain-amd64-posix.cmake](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/toolchain-amd64-posix.cmake)를 복사한 뒤 `toolchain-arm64-posix.cmake`라는 이름으로 저장하세요.
  * `CMAKE_C_COMPILER`를 `/usr/bin/arm-linux-gnueabihf-gcc`로 편집하세요.
  * `CMAKE_CXX_COMPILER`를 `/usr/bin/arm-linux-gnueabihf-g++`로 편집하세요.
  * 우리 예제의 RPI가 posix linux를 실행 중이기 때문에 이 파일에서 다른 것을 바꿀 필요는 없습니다.
    * 만약 여러분의 타겟이 그런 OS를 실행하지 않는다면, `OSAL_SYSTEM_OSTYPE`을 편집하고 이 파일의 추가 "Build Specific" 섹션을 검토해야 합니다.
* [./cfg/nos3_defs/arch_build_custom.cmake](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/arch_build_custom.cmake#L43)를 수정하세요:
  * `CMAKE_C_FLAGS` 문자열에서 `-Werror`를 제거하세요.
* 다음 테이블들을 삭제하세요. 이 파일들이 없으면 cFS는 각 애플리케이션에 저장된 기본값을 사용합니다:
  * `./cfg/nos3_defs/tables/sch_def_msgtbl.c`
  * `./cfg/nos3_defs/tables/sch_def_schtbl.c`
  * `./cfg/nos3_defs/tables/to_lab_sub.c`
* [./cfg/nos3_defs/targets.cmake](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/targets.cmake)
  * 이 파일은 빌드에 포함된 모든 라이브러리와 애플리케이션을 나열합니다.
  * NOS3 위성 설정 파일은 단순히 무엇을 실행할지를 바꿀 뿐이지만, 의존성 관리를 쉽게 하기 위해 매번 모든 것을 빌드합니다.
  * 아래에 재현된 파일로 교체하되, 비행용 타겟에 필요한 라이브러리가 없어서 여러 타겟이 주석 처리되어 있음에 유의하세요:
```
SET(MISSION_NAME "NOS3")

# SPACECRAFT_ID gets compiled into the build data structure and the PSP may use it.
# should be an integer.
SET(SPACECRAFT_ID 42)

# The "MISSION_GLOBAL_APPLIST" is a set of apps/libs that will be built
# for every defined target.  These are built as dynamic modules
# and must be loaded explicitly via startup script or command.
# This list is effectively appended to every TGTx_APPLIST in targets.cmake.
# Example:
list(APPEND MISSION_GLOBAL_APPLIST
    #
    # Libraries
    #
        #cryptolib
        #hwlib
        #io_lib
    #
    # cFS Apps
    #
        #cf
        #ci
        ci_lab
        #ds
        #fm
        #lc
        #sbn
        #sbn_tcp
        #sbn_client
        #sc
        sch
        #to
        to_lab
    #
    # Components
    #
        #arducam/fsw/cfs
        #generic_adcs/fsw/cfs
        #generic_css/fsw/cfs
        #generic_eps/fsw/cfs
        #generic_fss/fsw/cfs
        #generic_imu/fsw/cfs
        #generic_mag/fsw/cfs
        #generic_reaction_wheel/fsw/cfs
        #generic_radio/fsw/cfs
        #generic_star_tracker/fsw/cfs
        #generic_thruster/fsw/cfs
        #generic_torquer/fsw/cfs
        #mgr/fsw/cfs
        #novatel_oem615/fsw/cfs
        #onair
        #sample/fsw/cfs
        #syn/fsw/cfs
)

# Create Application Platform Include List
FOREACH(X ${MISSION_GLOBAL_APPLIST})
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/mission_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/cfs/mission_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/mission_inc)

    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/cfs/inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/inc)

    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/platform_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/cfs/platform_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/platform_inc)

    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/public_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/cfs/public_inc)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/public_inc)

    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/../shared)

    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/src)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/cfs/src)
    LIST(APPEND APPLICATION_PLATFORM_INC_LIST ${${X}_MISSION_DIR}/fsw/src)
ENDFOREACH(X)

# FT_INSTALL_SUBDIR indicates where the black box test data files (lua scripts) should
# be copied during the install process.
# Each target board can have its own HW arch selection and set of included apps
SET(MISSION_CPUNAMES cpu1 cpu2)

# NASA Operational Simulator for Space Systems (NOS3) - Host Linux
SET(cpu1_PROCESSORID 1)
SET(cpu1_APPLIST hwlib) # Note: Using all ${MISSION_GLOBAL_APPLIST} automatically
SET(cpu1_FILELIST cfe_es_startup.scr)
if (ENABLE_UNIT_TESTS)
    SET(cpu1_SYSTEM amd64-posix)
else() 
    SET(cpu1_SYSTEM amd64-nos3)
endif()

# RPI Flight Target
SET(cpu2_PROCESSORID 2)
SET(cpu2_APPLIST)
SET(cpu2_FILELIST cfe_es_startup.scr)
SET(cpu2_SYSTEM arm64-posix)
```

추가로 `./cfg/nos3_defs/cpu1*` 파일들을 같은 디렉토리에 `cpu2*` 접두사로 복사해야 합니다.
이렇게 이름을 바꾸면 우리의 NOS3 빌드(cpu1)와는 다를 비행용 타겟에 대해 별도로 추가 설정을 할 수 있습니다.

---
### 비행용 타겟 빌드하기

이 시점이면 여러분의 도커 컨테이너가 빌드되어 사용 준비가 되어 있을 것입니다.
우리가 편집해온 NOS3 저장소의 최상위 경로에 있는 터미널에서, 그저 다음을 실행하면 됩니다:
* make clean
* make

NOS3 빌드(cpu1)와 비행용 타겟(cpu2) 모두 FSW용으로 빌드되며, 시뮬레이터도 NOS3와 함께 사용할 수 있도록 빌드됩니다.
NOS3 파일은 `./fsw/build/exe/cpu1`에서, 비행용 타겟 파일은 `./fsw/build/exe/cpu2`에서 찾을 수 있습니다.
해당 위치에서 cFS를 실행하는 것 외에도 그 디렉토리와 하위 디렉토리에 있는 모든 것이 필요하다는 점에 유의하세요.

### 결론
이번 시나리오를 통해, 개발용으로도 계속 사용할 수 있게 유지하면서 동시에 비행용으로 NOS3를 빌드하는 방법을 배웠습니다.
