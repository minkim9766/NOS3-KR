# STF - 빠른 참조 (Quick Look)

Simulation To Flight(STF) 임무는 우주선 운영자를 위한 빠른 참조 임무 문서가 필요합니다.
이 문서에는 필요한 정보가 어디에 있는지 빠르게 찾아갈 수 있도록 관련 문서와 코드에 대한 모든 링크가 담겨 있습니다.

## 전력 (Power)

전력 시스템(EPS)에는 우주선 전반에 걸쳐 전력 절약과 재순환(cycling)을 가능하게 하는 다양한 구성 요소용 스위치가 여럿 있습니다.
EPS 스위치는 다음과 같이 연결되어 있습니다:
* 스위치 0 - 샘플 계측기(Sample Instrument)
* 스위치 1 - 스타 트래커(Star Tracker)
* 스위치 2 - 미배정
* 스위치 3 - 미배정
* 스위치 4 - 미배정
* 스위치 5 - 미배정
* 스위치 6 - 미배정
* 스위치 7 - 미배정

## 데이터 (Data)

데이터 생성과 저장은 매우 중요합니다.
이상 징후를 신속히 식별하는 것과 과학 데이터 수집을 최대화하는 것 사이에서 균형을 맞춰야 합니다.

### 스케줄 (Schedule)

core Flight System(cFS)의 스케줄(SCH) 애플리케이션은 정해진 주기로 데이터 생성을 요청하거나 점검을 시작하는 데 사용됩니다.
STF 임무의 기본값이자 선택된 주기는 100Hz입니다.
이 100개의 슬롯 각각에 하나의 명령이 실행될 수 있습니다.
* [./cfg/nos3_defs/tables/sch_def_msgtbl.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/sch_def_msgtbl.c)
  * 실제 스케줄에서 사용할 수 있는 사전 정의된 명령들
  * 여기에는 완전한 명령 정의가 포함되며, 새 테이블을 업로드하지 않고서는 이를 변경할 로직이 없습니다
* [./cfg/nos3_defs/tables/sch_def_schtbl.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/sch_def_schtbl.c)
  * 100Hz 안에서 각각 자신만의 실행 구간(execution window)을 갖는 100개의 스케줄 슬롯
  * 초 단위의 주기, 스케줄 균형을 맞추기 위한 초 단위의 송신 구간 오프셋, 그리고 명령 참조를 정의합니다
    * 송신 구간 예시: 5초 주기로 두 개의 패킷이 있다고 가정하면, 하나는 구간 0초에, 다른 하나는 구간 2초 지점에 실행되도록 할 수 있습니다
  * 하나의 요청이 여러 슬롯에 걸쳐 나타날 수 있으며, 이는 보통 기본 최대 주기인 1Hz보다 더 빠르게 실행하기 위해 사용됩니다

### 데이터 저장 (Data Storage, DS)

데이터 저장 애플리케이션은 단순히 소프트웨어 버스 상의 메시지를 구독(subscribe)하며, 원하는 대로 다운샘플링(down sample)할 수 있는 기능을 갖고 있습니다.
이는 단순한 콘솔 출력(print)만 캡처하는 것이 아니라, 로그 메시지를 포함해 각 구성 요소에서 게시되고 이용 가능한 모든 텔레메트리를 캡처합니다.
* [./cfg/nos3_defs/tables/ds_file_tbl.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/ds_file_tbl.c)
  * 생성할 파일들을 설정하며 명명 규칙(시간 기준 또는 카운트 기준), 메모리 내 위치, 최대 크기와 보관 기간을 세부적으로 정합니다
* [./cfg/nos3_defs/tables/ds_filter_tbl.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/ds_filter_tbl.c)
  * 이상적으로는 우주선이 생성하는 각 패킷마다 하나의 인덱스를 가집니다
  * 정의된 각 파일 유형에 대해 (원하는 경우) 다운샘플링에 대한 세부 사항을 제공합니다

STF의 경우, ADCS와 컴포넌트 HK(health & keeping) 데이터는 0.1Hz로 다운샘플링되어 저장되는 반면, 모든 과학 데이터와 콘솔 로그는 그대로 저장됩니다.
운영의 단순함을 위해, 그리고 시간대별 데이터를 함께 캡처할 수 있도록, 모든 데이터는 단일 파일 유형으로 저장됩니다.

## 결함 감지 및 수정 (Fault Detection and Correction, FDC)

FDC는 cFS 안에서 서로 다른 두 애플리케이션을 짝지어 수행됩니다.
바로 리밋 체커(Limit Checker, LC)와 스토어드 커맨드(Stored Command, SC)입니다.

### 리밋 체커 (Limit Checker, LC)

LC 애플리케이션은 조치를 취할 패킷 내 특정 비트들을 모니터링할 수 있게 해주며, 이는 두 개의 테이블에서 설정됩니다:
* [./cfg/nos3_defs/tables/lc_def_adt.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/lc_def_adt.c)
  * 액션포인트(AP) 정의 테이블(ADT)은 워치포인트(WP) 상태를 평가하는 데 사용되는 수식과, 취해야 할 조치를 정의합니다
  * 취해야 할 조치는 상대 시간 시퀀스(RTS)에 저장되며 SC 애플리케이션에 의해 관리됩니다
* [./cfg/nos3_defs/tables/lc_def_wdt.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/lc_def_wdt.c)
  * 워치포인트 정의 테이블(WDT)은 평가할 데이터를 정의합니다

현재 워치포인트에 대한 요약은 아래와 같습니다:

| 워치포인트 (Watchpoint) | 로직 (Logic) |
| ------------ | ----- |
|WP #25 | MGR SPACECRAFT_MODE = Science_Reboot|
|WP #26 | MGR SPACECRAFT_MODE = Science|
|WP #27 | EPS BATTERY_VOLTAGE < 60% (24240mV)|
|WP #28 | EPS BATTERY_VOLTAGE > 90% (24960mV)|
|WP #29 | MGR SPACECRAFT_MODE = Safe Mode|
|WP #30 | AK 경계: GPS LAT < 71.35|
|WP #31 | AK 경계: GPS LAT > 51.22|
|WP #32 | AK 경계: GPS LON < -129.99|
|WP #33 | AK 경계: GPS LON > -179.15|
|WP #34 | MGR AK_STATUS = ENABLED|
|WP #35 | CONUS 경계: GPS LAT < 49.38|
|WP #36 | CONUS 경계: GPS LAT > 24.52|
|WP #37 | CONUS 경계: GPS LON < -66.95|
|WP #38 | CONUS 경계: GPS LON > -125|
|WP #39 | MGR CONUS_STATUS = ENABLED|
|WP #40 | HI 경계: GPS LAT < 28.4|
|WP #41 | HI 경계: GPS LAT > 18.9|
|WP #42 | HI 경계: GPS LON < -154.8|
|WP #43 | HI 경계: GPS LON > -178.7|
|WP #44 | MGR HI_STATUS = ENABLED|

현재 액션포인트와 그들이 모니터링하는 워치포인트에 대한 요약은 아래와 같습니다:
| 액션포인트 (Actionpoint) | 설명 | 워치포인트 로직 |
| ------------ | ----- | ------ |
| AP #25 Science_Reboot to Science | RTSId = 25| WP Equation = (WP_25)|
| AP #26 Enable Science Mode | RTSId = 26| WP Equation = (WP_26)|
| AP #27 Science Mode: Low Power | RTSId = 27 | WP Equation = (WP_27)|
| AP #28 Science Mode: Recharged | RTSId = 28 | WP Equation = (WP_28)|
| AP #29 Science Mode: EXIT Science Mode | RTSId = 29 | WP Equation = (WP_29)|
| AP #30 Science Mode: Entering AK Region | RTSId  = 30 | WP Equation = (WP_30) && (WP_31) && (WP_32) && (WP_33) && (WP_34)|
| AP #31 Science Mode: Entering CONUS Regiod | RTSID = 31 |WP Equation = (WP_35) && (WP_36) && (WP_37) && (WP_38) && (WP_39)|
| AP #32 Science Mode: Entering HI Region | RTSId = 32 | WP Equation = (WP_40) && (WP_41) && (WP_42) && (WP_43) && (WP_44)| 
| AP #33 Science Mode: Science Idle, Left AK Region | RTSId = 33 | WP Equation = !((WP_30) && (WP_31) && (WP_32) && (WP_33) && (WP_34))|
| AP #34 Science Mode: Science Idle, Left CONUS Region | RTSId  = 34 | WP Equation = !((WP_35) && (WP_36) && (WP_37) && (WP_38) && (WP_39))| 
| AP #35 Science Mode: Science Idle, Left HI Region | RTSId = 35 | WP Equation = !((WP_40) && (WP_41) && (WP_42) &&  (WP_43) && (WP_44))|

> 💡 **초보자 가이드**
> "워치포인트(Watchpoint)"는 감시할 값(예: 배터리 전압, GPS 위도)이고, "액션포인트(Actionpoint)"는 그 워치포인트들의 조합이 특정 조건(수식)을 만족했을 때 자동으로 실행할 명령 묶음(RTS)을 연결해주는 규칙이에요. 예를 들어 "배터리 전압이 60% 미만"이라는 워치포인트가 참이 되면, 그에 연결된 액션포인트가 발동해서 저전력 모드로 전환하는 RTS를 실행시키는 식입니다.

### 스토어드 커맨드 (Stored Command, SC)

SC에는 두 가지 유형이 있습니다:
* [./cfg/nos3_defs/tables/sc_ats1.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/sc_ats1.c)
  * 절대 시간 시퀀스 (Absolute Time Sequence, ATS)
  * 각 명령은 미리 정해진 특정 시점에 실행되도록 설정됩니다
  * STF 임무에서는 모드 전환을 기체 내부에서 처리하므로 사용을 피합니다
* [./cfg/nos3_defs/tables/sc_rts001.c](https://github.com/nasa/nos3/blob/900f0e9eb5754014cec1a43fb630adae6d93bec5/cfg/nos3_defs/tables/sc_rts001.c)
  * 상대 시간 시퀀스 (Relative Time Sequence, RTS)
  * 이는 우주선의 모드 전환, 패스 시작, 그리고 일반적인 설정/해제/유지보수 명령 시퀀스를 제어하는 데 사용됩니다

STF 임무의 현재 RTS 목록에 대한 요약은 아래와 같습니다:
* [sc_rts001.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts001.c) - 전원 인가 리셋 (Power On Reset, POR)
  * DS 활성화
  * 디버그 인터페이스 활성화
  * RTS 3-64 활성화
  * LC 활성화
  * RTS 3 시작 (안전 모드)
* [sc_rts003.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts003.c) - 안전 모드로 이동
  * CSS 활성화
  * FSS 활성화
  * IMU 활성화
  * MAG 활성화
  * 토커(Torquer) 활성화
  * GPS 활성화
  * ADCS를 SUNSAFE_MODE로 설정
* [sc_rts025.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts025.c) - 과학 모드 활성화
  * AP25 비활성화
  * MGR에서 과학 모드 설정
* [sc_rts026.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts026.c) - 과학 활동, 활성화
  * RTS27 - RTS32 활성화
  * AP27 - AP32 리셋
  * AP27 - AP32 활성 상태로 설정
* [sc_rts027.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts027.c) - 과학 활동, 저전력 일시 정지
  * MGR에서 전력을 낮춤, SS_NO_SCIENCE_LOW_POWER
  * AP30 - AP35 비활성화
  * 계측기 애플리케이션 비활성화
  * 계측기 EPS 스위치 비활성화
  * AP28 리셋
  * AP28 활성 상태로 설정
* [sc_rts028.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts028.c) - 과학 활동, 재충전 후 재개
  * MGR에서 과학 활동 재개, SS_NO_SCIENCE_RECHARGED
  * AP28 비활성화
  * AP27 - AP32 리셋
  * AP27 - AP32 활성 상태로 설정
* [sc_rts029.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts029.c) - 과학 활동, 종료
  * MGR에서 과학 활동 중단, SS_EXITED_SCIENCE_MODE
  * AP27 - AP35 비활성화
  * 계측기 애플리케이션 비활성화
  * 계측기 EPS 스위치 비활성화
  * AP26 리셋
  * AP26 활성 상태로 설정
* [sc_rts030.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts030.c) - 과학 활동, 알래스카(AK) 상공
  * MGR에서 과학 활동 시작, SS_SCIENCE_OVER_AK
  * 과학 활동 패스 카운터 증가
  * 계측기 EPS 스위치 활성화
  * 계측기 애플리케이션 활성화
  * AP33 리셋
  * AP33 활성 상태로 설정
* [sc_rts031.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts031.c) - 과학 활동, 미국 본토(CONUS) 상공
  * MGR에서 과학 활동 시작, SS_SCIENCE_OVER_CONUS
  * 과학 활동 패스 카운터 증가
  * 계측기 EPS 스위치 활성화
  * 계측기 애플리케이션 활성화
  * AP34 리셋
  * AP34 활성 상태로 설정
* [sc_rts032.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts032.c) - 과학 활동, 하와이(HI) 상공
  * MGR에서 과학 활동 시작, SS_SCIENCE_OVER_HI
  * 과학 활동 패스 카운터 증가
  * 계측기 EPS 스위치 활성화
  * 계측기 애플리케이션 활성화
  * AP35 리셋
  * AP35 활성 상태로 설정
* [sc_rts033.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts033.c) - 과학 활동 대기, 알래스카(AK) 이탈
  * MGR에서 과학 활동 중단, SS_NO_SCIENCE_LEFT_AK
  * 계측기 애플리케이션 비활성화
  * 계측기 EPS 스위치 비활성화
  * AP31 리셋
  * AP31 활성 상태로 설정
* [sc_rts034.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts034.c) - 과학 활동 대기, 미국 본토(CONUS) 이탈
  * MGR에서 과학 활동 중단, SS_NO_SCIENCE_LEFT_CONUS
  * 계측기 애플리케이션 비활성화
  * 계측기 EPS 스위치 비활성화
  * AP31 리셋
  * AP31 활성 상태로 설정
* [sc_rts035.c](https://github.com/nasa/nos3/blob/dev/cfg/nos3_defs/tables/sc_rts035.c) - 과학 활동 대기, 하와이(HI) 이탈
  * MGR에서 과학 활동 중단, SS_NO_SCIENCE_LEFT_HI
  * 계측기 애플리케이션 비활성화
  * 계측기 EPS 스위치 비활성화
  * AP31 리셋
  * AP31 활성 상태로 설정

RTS 번호가 위 목록에 없는 경우, 일반적으로 아무 동작도 하지 않는(NOOP) 명령을 수행하는 기본 테이블이 사용된다는 점에 유의하세요.

## 표준 운영 절차 (Standard Operating Procedures)

추후 결정 (TBD)

### 패스 로그 (Pass Logs)

### 표준 패스 (Standard Pass)

### 패칭 (Patching)
