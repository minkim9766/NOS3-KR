
# 시나리오 - GDB를 이용한 Sample 디버깅

이 시나리오는 NOS3 환경 안에서 **sample 시뮬레이터**와 그 **체크아웃(checkout) 애플리케이션**을 디버깅을 위해 **GDB**와 함께 실행하는 방법을 보여줍니다.
이는 표준 sample 시뮬레이션 시나리오를 기반으로 하며, `sample_checkout` 애플리케이션을 실시간으로 점검하고, 중단점(breakpoint)을 설정하고, 한 줄씩 실행(step-through)하며 디버깅할 수 있도록 실행 과정에 `gdb`를 통합합니다.

> 💡 **초보자 가이드**: GDB(GNU Debugger)는 프로그램이 실행되는 도중 내부에서 무슨 일이 일어나고 있는지 자세히 들여다볼 수 있게 해주는 도구입니다. 프로그램을 특정 지점에서 잠깐 멈추게 하거나(중단점, breakpoint), 한 줄씩 천천히 실행하며 변수 값이 어떻게 바뀌는지 확인할 수 있어, 코드에 숨어 있는 버그를 찾는 데 매우 유용합니다.

이는 다음과 같은 목적에 유용합니다:
* Sample 페이로드(payload) 로직 디버깅하기
* 실행 중 메모리나 변수 값 점검하기
* 결함(fault)을 추적하거나 애플리케이션 동작을 검증하기

이 시나리오는 2025년 6월 10일에 마지막으로 업데이트되었으며, 당시 `dev` 브랜치(커밋 [a3e7c100])를 기반으로 작성되었습니다.

## 학습 목표

이 시나리오를 마치면 다음을 할 수 있게 됩니다:

* Docker 안에서 `gdb` 세션을 이용해 sample checkout 애플리케이션 실행하기.
* 중단점을 설정하고 애플리케이션을 대화형으로 실행하기.
* 실행 중 변수와 함수 호출 흐름 점검하기.
* NOS3 시뮬레이션 워크플로우에 저수준(low-level) 디버깅 통합하기.

## 사전 준비 사항

시나리오를 실행하기 전에 다음 단계를 완료하세요:
* [시작하기](./NOS3_Getting_Started.md)
  * {ref}`설치 <installation>`
  * {ref}`실행 <running>`
* 또한 NOS3 저장소의 최상위 경로에서 작업 중인지 확인하세요.

---

## 실습 과정

gdb, 즉 Gnu Debugger는 명령줄에서 프로세스를 디버깅하는 데 유용합니다. 이를 독립 실행형(standalone) 모드의 컴포넌트와 함께 실행하려면 다음 단계가 필요합니다:

### 1단계: NOS3 빌드하기

```bash
make
```

---
### 2단계: Sample Checkout 앱 빌드하기

```bash
./scripts/checkout.sh
make stop
make debug
cd components/sample/fsw/standalone/
mkdir build
cd build
cmake .. -DTGTNAME=cpu1
make
exit
```

이제 NOS3와 sample checkout 앱을 모두 빌드했으니, checkout 스크립트를 편집해야 합니다.

---
### 3단계: checkout 스크립트 편집하기

checkout 스크립트가 sample 시뮬레이터를 실행하기를 원합니다.
또한 sample checkout 앱을 GDB 아래에서 실행하기를 원합니다.
`./scripts/checkout.sh`를 다음과 같이 편집하세요:
* 165번째 줄(sample sim)과 166번째 줄(sample checkout)의 주석을 해제하세요
* 166번째 줄의 "$DBOX"와 "./components/sample/fsw/standalone/build/sample_checkout" 사이에 `gdb`를 삽입하세요

### 4단계: Sample Sim 실행 및 GDB에서 Sample Checkout 앱 실행하기

새 터미널을 열고 다음 `gnome-terminal` 명령을 실행하세요:

```bash
./scripts/checkout.sh
```

**참고: 이는 여러분의 환경 변수(예: `$DFLAGS`, `$BASE_DIR`, `$SC_NUM`, `$DBOX`, `$SC_NETNAME`)가 일반적인 NOS3 세션처럼 설정되어 있다고 가정합니다.
이는 `checkout.sh` 스크립트가 자동으로 처리해야 합니다.**

---
### 5단계: GDB 사용하기

GDB 세션 안에서는 다음을 할 수 있습니다:

* 중단점 설정하기:
  ```text
  break main
  ```
* 애플리케이션 실행하기:
  ```text
  run
  ```
* 코드를 한 줄씩 실행하기:
  ```text
  next
  step
  ```
* 변수 점검하기:
  ```text
  print variable_name
  info locals
  ```

GDB를 종료하고 Sample Simulator, NOS Engine 등을 종료하려면:
```text
quit
make stop
```

---
### 선택 사항: TUI 모드 활성화하기

여러분의 컨테이너가 `ncurses`를 지원한다면, `./scripts/checkout.sh`에 `-tui`를 추가하여 GDB의 텍스트 기반 UI를 활성화할 수 있습니다. 그러면 166번째 줄의 끝이 다음과 같아집니다:

```bash
gdb -tui ./components/sample/fsw/standalone/build/sample_checkout
```

---
### 결론

이제 여러분은 `gdb`가 연결된 NOS3 sample 컴포넌트를 성공적으로 실행하여, 실시간 대화형 디버깅을 할 수 있게 되었습니다. 이는 NOS3 개발 루프 안에서 직접 페이로드 로직을 테스트하고 예외 상황을 시뮬레이션하는 강력한 방법입니다.
