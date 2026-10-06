import os
import re
import subprocess
import sys
import shutil

def sphinx_jobs():
    """Return the Sphinx worker count, defaulting to a memory-safe limit."""
    value = os.environ.get("SPHINX_JOBS", "2")
    try:
        jobs = int(value)
    except ValueError as error:
        raise ValueError("SPHINX_JOBS must be a positive integer") from error
    if jobs < 1:
        raise ValueError("SPHINX_JOBS must be a positive integer")
    return jobs

def fix_rst_underlines():
    """ .rst 파일들의 'Title underline too short' 경고를 자동 교정합니다. """
    print("🔧 [1/2] Checking and fixing RST title underlines...")
    current_dir = os.getcwd()
    
    for root, dirs, files in os.walk(current_dir):
        # 가상환경, 빌드, 숨김 폴더는 RST 검사 대상에서 완전히 제외
        if any(x in root for x in ['.venv', 'venv', '_build', '.git', '__pycache__', '.github']):
            continue
            
        for file in files:
            if file.endswith('.rst'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    modified = False
                    for i in range(len(lines) - 1):
                        line = lines[i].rstrip()
                        next_line = lines[i+1].rstrip()
                        
                        # 다음 줄이 = 기호로만 이루어져 있고, 제목 길이보다 짧은 경우 처리
                        if line and next_line and re.match(r'^=+$', next_line):
                            if len(next_line) < len(line):
                                lines[i+1] = ("=" * len(line)) + "\n"
                                modified = True
                    
                    if modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        print(f"  └─ Fixed underline in: {file}")
                except Exception:
                    pass

def run_sphinx_build_fast():
    """ 원본 소스는 유지하되, 무거운 찌꺼기 폴더를 차단 및 격리하여 초고속으로 빌드합니다. """
    print("\n🚀 [2/2] Running Fast Sphinx build (Isolating Junk Folders)...")
    
    tmp_source = os.path.join("_build", "tmp_source")
    output_dir = os.path.join("_build", "html")
    
    # 매번 신선한 빌드를 위해 임시 소스 보관소 초기화
    if os.path.exists(tmp_source):
        shutil.rmtree(tmp_source)
    os.makedirs(tmp_source, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # 복사 대상 파일 확장자 정의
    valid_extensions = ('.md', '.rst', '.py', '.png', '.jpg', '.jpeg', '.gif', '.json')
    
    # 🚨 변환 엔진을 느리게 만드는 주범인 시스템/생성 찌꺼기 폴더 목록
    ignored_patterns = [
        '.venv', 'venv', '_build', '.git', '__pycache__', 
        '.github', 'for_build', 'opengl_builder'
    ]
    
    # 순수 문서 파일들만 임시 공간으로 복사
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ignored_patterns):
            continue
            
        # 하위 디렉토리 순회 목록 자체를 필터링하여 탐색 속도 극대화
        dirs[:] = [d for d in dirs if d not in ignored_patterns]
            
        for file in files:
            if file.lower().endswith(valid_extensions):
                rel_dir = os.path.relpath(root, ".")
                target_dir = os.path.join(tmp_source, rel_dir) if rel_dir != "." else tmp_source
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))

    # Sphinx 빌드 명령어 구성
    jobs = sphinx_jobs()
    print(f"Using {jobs} Sphinx worker(s). Set SPHINX_JOBS to override.")
    cmd = [
        sys.executable, "-m", "sphinx",
        "-T",
        "-j", str(jobs),
        "-b", "html",
        "-d", os.path.join("_build", "doctrees"),
        "-D", "language=ko",
        # 💡 유효하지 않은 목차(toc)로 인한 예외 처리 탐색 딜레이 강제 억제 옵션
        "-D", "suppress_warnings=toc.not_readable,toc.not_included",
        tmp_source, output_dir
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✨ Build Successful! Result saved in: {output_dir}")
        print(f"👉 Local preview link: file://{os.path.abspath(output_dir)}/index.html")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Sphinx Build Failed with exit code {e.returncode}")

if __name__ == "__main__":
    fix_rst_underlines()
    run_sphinx_build_fast()
