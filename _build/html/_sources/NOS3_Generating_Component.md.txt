# 새 구성 요소 생성하기(Generating a New Component)

NOS3는 구성 요소라는 기본 개념을 중심으로 구성되어 있습니다.
우주선은 공통 기능으로 이루어진 핵심 집합과, 커스텀 구성 요소 집합으로 이루어지도록 의도되었습니다.
각 구성 요소는 해당 구성 요소의 `fsw` 하위 디렉토리에 배치되는 FSW 애플리케이션으로 표현됩니다.
지상 소프트웨어가 구성 요소 애플리케이션을 제어할 수 있도록, 각 구성 요소는 해당 구성 요소의 `gsw` 하위 디렉토리에 배치되는 명령 및 원격측정 테이블 모음을 갖습니다.
많은 경우(전부는 아니지만) 구성 요소는 우주선의 하드웨어 부품이므로, 그 구성 요소를 위한 NOS3 하드웨어 시뮬레이터를 해당 구성 요소의 `sims` 하위 디렉토리에 두는 것이 적절합니다.

아래는 새로운 구성 요소를 생성하는 방법에 대한 단계별 가이드입니다. 이 가이드는 NOS3에서 만들어진 Sample 구성 요소를 기준으로 설명한다는 점에 유의하세요. 자신만의 cFS 앱과 특정 하드웨어 모델을 자신의 애플리케이션에 맞게 구현하는 것은 사용자의 몫입니다. 아래 단계는 새로운 사용자가 NOS3에 새로운 구성 요소를 통합하는 과정을 안내하기 위한 것입니다.

## 단계별 가이드(Step-by-Step Guide)

**참고: 이 가이드는 cFS FSW와 Cosmos GSW를 사용해 NOS3에서 새로운 구성 요소를 만드는 방법을 설명합니다.**

1. 먼저, sample 구성 요소에 있는 generate_template.sh 스크립트를 실행합니다. 이 스크립트는 사용자가 입력한 이름으로 /nos3/components 디렉토리에 새로운 구성 요소를 만듭니다. 스크립트를 실행하려면 nos3 저장소에서 터미널을 열고 components/sample/로 디렉토리를 옮긴 뒤 아래처럼 실행하세요. 새 구성 요소의 이름을 지정해야 합니다. 참고로, 스크립트에 실행 권한이 없다면 다음 명령을 입력하세요:
```
chmod +x generate_template.sh
```
   ![generate_template](./_static/adding_nos3_component/generate_template.png)

구성 요소를 만들고 나면, /nos3/components에 스크립트에 입력한 이름으로 폴더가 생성된 것을 확인할 수 있습니다. 다음은 여러분의 특정 구성 요소를 위해 편집해야 할 구성 요소 파일들입니다. 다음 단계에서는 여러분의 구성 요소를 cFS와 cosmos에 추가하는 데 필요한 내용을 자세히 설명합니다. 새로 생성된 구성 요소는 sample 구성 요소와 동일하므로, 이 가이드의 나머지 부분에서는 새로 생성한 구성 요소를 nos3에 통합하기 위해 sample 구성 요소의 어떤 코드를 추가/수정해야 하는지 살펴볼 것입니다. 따라서 각 단계에서 "sample"이 보이면, 그것을 여러분의 새 구성 요소 이름으로 바꾸면 됩니다.

구성 요소의 세부 구현(fidelity) 정도는 최종적으로 사용자에게 달려 있으며, 새 구성 요소에 특화되어 사용자가 수정해야 할 부분에는 구성 요소 파일 안에 "TODO" 표시가 되어 있습니다. 서로 다른 수준의 세부 구현 예시를 보려면, NOS3의 다양한 generic_components, Arducam, Novatel GPS 등을 비교해 볼 수 있습니다.

2. 이제 구성 요소 파일을 고유하게 편집해야 합니다. **nos3/compoments/name_of_your_component/fsw/cfs**에서 찾을 수 있는 cFS 앱을 편집하는 것부터 시작하세요. 먼저, **name_of_your_component_perfids.h**에 있는 perfid 값을 NOS3에 이미 정의된 값과 다르게 수정해야 합니다. 이미 정의되어 있는 값이 무엇인지는 이 문서 앞부분의 Component Information(구성 요소 정보)을 참고하세요.

    ![perf_ids](./_static/adding_nos3_component/perf_ids.png)

3. perf_ID를 변경한 뒤, 여러분 구성 요소의 명령들에 대한 메시지 ID를 수정해야 합니다. 이는 **name_of_your_component_msgids.h**에서 찾을 수 있습니다. 참고로, 이 튜토리얼에서는 sample 구성 요소의 세부 구현에서 벗어나지 않으므로 명령 자체는 변경하지 않습니다. 이미 정의된 msg_id가 무엇인지는 이 문서 앞부분의 Component Information을 참고하세요.

    ![msg_ids](./_static/adding_nos3_component/msg_ids.png)

4. 다음으로, **name_of_your_component_platform_cfg.h**를 편집하면서 통신 인터페이스를 변경해야 합니다. 이 예시에서는 Uart 통신 인터페이스를 사용한다고 가정해 봅시다. Uart 16번은 이미 sample이 사용하고 있으므로 아래의 Uart 번호를 수정해야 합니다. **nos3/cfg/sims/**에 있는 nos3-simulator.xml을 참고하면 어떤 통신 장치가 정의되어 있고 어떤 포트 번호를 사용하고 있는지 확인할 수 있습니다. 이 파일은 이 가이드의 뒷부분에서 편집할 것입니다. 사용자가 Uart가 아닌 spi나 I2C 같은 다른 것을 사용하려는 경우, 다른 통신 인터페이스가 정의된 예시를 다른 NOS3 구성 요소들에서 참고할 수 있습니다.

    ![platform_cfg](./_static/adding_nos3_component/platform_cfg.png)

5. 이제 cosmos Command 및 TLM 정의의 opcode를 **xxxx.msgids.h**에 정의된 opcode와 일치하도록 수정합니다. cosmos를 위한 이러한 command 및 tlm 정의는 **nos3/components/name_of_your_component/gsw/name_of_your_component/cmd_tlm/**에서 찾을 수 있습니다. 여러분이 정의한 opcode로 아래에 보이는 두 파일을 편집하세요.

    ![Sample_cmd](./_static/adding_nos3_component/Sample_cmd_opcodes.png)

    ![sample_tlm](./_static/adding_nos3_component/Sample_tlm_opcodes.png)


6. NOS3 시스템이 여러분의 새 구성 요소 시뮬레이터를 찾고 설정하는 방법을 알 수 있도록, nos3-Simulator.xml에 구성 요소를 추가하는 것이 필요합니다. Uart 장치를 사용하는 구성 요소의 경우, Sample의 코드 블록을 복사한 뒤 여러분이 platform_cfg.h에 정의한 내용을 기반으로 수정하세요.

    ![nos3-simulator](./_static/adding_nos3_component/nos3_simulator_sample_xml.png)

7. 다음으로, 새로 정의한 구성 요소를 **nos3/cfg/tables**에 있는 TO 테이블에 추가합니다. to_config.c에서, 새 구성 요소를 include하고 아래 그림과 같은 문법으로 MID config 테이블에 구성 요소를 추가하세요. 참고로, 정리를 위해 TLM_MID들을 정의된 코드 블록 안에서 순서대로 추가하세요. sample에는 Sample_HK_TLM_MID와 Sample_Device_TLM_MID가 있으니, 그 줄들을 복사해서 테이블/코드 블록 끝에 추가하고 이름을 여러분의 구성 요소에 맞게 수정하세요.

    ![to_config_include_msgids](./_static/adding_nos3_component/to_config_include_msgIds.png)


    ![to_config_table](./_static/adding_nos3_component/To_config_toConfigTable.png)


8. 다음으로, to_lab_sub.c에서 여러분의 구성 요소를 include하고 MID들을 테이블에 추가해야 합니다. sample의 문법을 참고하여 두 줄을 테이블 끝에 복사하세요.

    ![to_lab_sub_include](./_static/adding_nos3_component/to_lab_sub_includeMsgIds.png)


    ![to_lab_sub_table](./_static/adding_nos3_component/to_lab_sub_toLabSubsTable.png)

9. **cfg/nos3_defs/**에서 구성 요소 앱을 **cpu1_cfe_es_startup_scr**에 추가합니다. sample의 문법을 복사하고, 여러분의 구성 요소에 적절한 우선순위 번호를 지정하세요. sample의 우선순위 번호는 71입니다. 숫자가 낮을수록 우선순위가 높습니다. 이 필드들은 cpu1_cfe_es_startup_scr에 문서화되어 있습니다.

    ![cpu1_cfe_es_startup_scr](./_static/adding_nos3_component/cpu1_cfe_es_startup_scr_cfeAppTable.png)

10. 다음으로, **cfg/nos3_defs/**에 있는 targets.cmake에 여러분의 구성 요소의 cfs 디렉토리를 추가합니다. sample의 문법을 복사하세요.

    ![targets_cmake](./_static/adding_nos3_component/targets_cmake_nos3Defs.png)

11. nos3/cfg/spacecraft/ 디렉토리 아래에는 우주선 설정을 위한 활성화(enable) 플래그를 추가해야 하는 여러 파일들이 있습니다. 예를 들어 그중 하나가 **sc-research-config.xml**입니다. 참고로, 각 파일에 동일한 플래그를 추가할 수 있으며, 여러분의 nos3-mission.xml이 사용하고 싶은 우주선 설정을 참조하고 있는지만 확인하면 됩니다. 파일의 components 섹션에서 sample의 문법을 복사하고 여러분의 구성 요소에 맞게 이름을 바꾸세요.

    ![SC_config](./_static/adding_nos3_component/research_cfg_xml.png)

12. 다음으로 Cosmos에서 새 구성 요소를 위한 타겟을 선언합니다. 이를 위해 **nos3/gsw/cosmos/config/system/stash**에 있는 system.txt 파일을 수정합니다. 아래 sample처럼 구성 요소와 라디오 모두에 대해 타겟을 선언하세요. 아래 문법을 참고하세요.

    ![Cosmos_config_system_txt](./_static/adding_nos3_component/cosmos_system_txt_declare_target.png)

13. 타겟을 선언했으니, 이제 cosmos에서 정의한 인터페이스를 위한 타겟을 cmd_tlm_server에 추가합니다. cmd_tlm_server.txt는 **nos3/gsw/cosmos/config/tools/cmd_tlm_server/stash**에서 찾을 수 있습니다. 아래 sample처럼 debug 인터페이스와 radio 인터페이스 모두에 타겟을 추가하세요.

    ![Cosmos_cmd_tlm_server](./_static/adding_nos3_component/cosmos_cmd_tlm_server_target_interface.png)

14. 이제 구성 요소 점검(checkout)을 실행하거나 일반적인 NOS3 운영과 함께 실행하도록 NOS3 스크립트를 수정할 준비가 되었습니다. 먼저 독립형 점검을 checkout 스크립트에 추가합시다. checkout.sh 스크립트는 **nos3/scripts/**에서 찾을 수 있습니다. 여기서 아래 sample처럼 독립형 점검을 실행하기 위한 타겟을 추가하세요. 단순히 문법을 복사해서 sample을 여러분의 구성 요소 이름으로 바꾸면 됩니다. 참고로, "make checkout"으로 점검을 빌드하고 실행하려면 독립형 점검 문서를 따라야 합니다.

    ![checkout_script_sample](./_static/adding_nos3_component/checkout_script_sample.png)

15. 다음으로, **nos3/scripts/fsw/**에 있는 fsw_cfs_launch.sh 스크립트에 구성 요소 시뮬레이터 실행을 추가합니다. 아래 sample의 문법을 복사해서 여러분의 구성 요소 이름으로 수정하세요.

    ![cfs_launch_script](./_static/adding_nos3_component/fsw_cfs_launch_adding_component_simulator.png)

16. 마지막으로, 새 구성 요소로 NOS3 시스템을 제대로 설정하기 위해, xml에서 이전 단계들에서 추가한 구성 요소들을 기반으로 적절한 파일 파싱을 추가하도록 configure 스크립트를 수정해야 합니다. **nos3/scripts/cfg/**에 있는 configure.py 스크립트를 편집해야 합니다. 아래는 새 구성 요소를 위해 복사하고 추가해야 할 코드 줄들입니다. 일부 줄은 주석 처리되어 있으며 42 설정에 필요한 것들입니다. sample은 42에 연결되어 있지 않으므로 그 줄들은 주석 처리되어 있지만, 다른 구성 요소들은 42에 연결되어 있는 것을 볼 수 있습니다. 아래에서 sample을 기반으로 파이썬 스크립트에 필요한 줄들을 추가하세요.

    ![configurePY_1](./_static/adding_nos3_component/configurePY_1.png)

    ![configurePY_2](./_static/adding_nos3_component/configurePY_2.png)

    ![configurePY_3](./_static/adding_nos3_component/configurePY_3.png)

    ![configurePY_4](./_static/adding_nos3_component/configurePY_4.png)

    ![configurePY_5](./_static/adding_nos3_component/configurePY_5_only42.png)

    ![configurePY_6](./_static/adding_nos3_component/configurePY_6_only42.png)

    ![configurePY_7](./_static/adding_nos3_component/configurePY_7_only42.png)

    ![configurePY_8](./_static/adding_nos3_component/configurePY_8.png)

    ![configurePY_9](./_static/adding_nos3_component/configurePY_9.png)

    ![configurePY_10](./_static/adding_nos3_component/configurePY_10.png)



## 핵심 요약(Key Takeaways)

이제 NOS3에서 새로 생성된 구성 요소를 빌드하고 실행하는 데 필요한 파일과 수정 사항을 모두 추가했습니다!

이제 새 구성 요소로 NOS3를 빌드하고 실행할 수 있습니다. NOS3 전체와 함께 실행하기 전에, 항상 먼저 해당 구성 요소의 독립형 점검을 빌드하고 실행해 보는 것이 권장됩니다. 다시 말하지만, 이 단계별 가이드는 참고용이며, 사용자는 자신의 새 구성 요소가 실제로 사용될 사례에 맞게 cFS 앱과 하드웨어 모델 시뮬레이터(**nos3/components/name_of_your_component/sim/**에서 찾을 수 있음)를 수정해야 합니다. 하지만 이 가이드를 따르면 템플릿 생성으로부터 새로 만들어진 구성 요소의 기본적인 sample 기능을 검증할 수 있습니다.

