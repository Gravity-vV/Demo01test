import os
import re
import stat
import subprocess
import requests
from pathlib import Path
from tqdm import tqdm

def extract_versions():
    dataset_dir = Path("/home/zzh/code/research/idea_1_SmartAuditFlow_SolEvo/EmpiricalSCST/mainnet")
    versions = set()
    version_pattern = re.compile(r"0\.\d+\.\d+")

    for filepath in dataset_dir.glob("*.sol"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r"pragma\s+solidity\s+([^;]+);", content)
                for match in matches:
                    v_matches = version_pattern.findall(match)
                    versions.update(v_matches)
        except Exception as e:
            pass
    return sorted(list(versions))

def get_installed():
    try:
        res = subprocess.run(
            ["/home/zzh/code/research/idea_1_SmartAuditFlow_SolEvo/SmartAuditFlow/smart-contract-audit/venv/bin/solc-select", "versions"], 
            capture_output=True, 
            text=True, 
            env=dict(os.environ, VIRTUAL_ENV="/home/zzh/code/research/idea_1_SmartAuditFlow_SolEvo/SmartAuditFlow/smart-contract-audit/venv")
        )
        installed = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if line:
                if line.endswith("(current)"):
                    line = line.replace("(current)", "").strip()
                installed.append(line)
        return installed
    except Exception:
        return []

def main():
    print("正在扫描数据集并检测缺失版本，请稍候...")
    needed = extract_versions()
    installed = get_installed()
    missing = [v for v in needed if v not in installed]
    
    print(f"总计需求版本: {len(needed)} 个 | 仍需下载安装: {len(missing)} 个")
    if not missing:
        print("所有缺失版本均已安装完毕！")
        return

    print("\n获取官方 Solidity 版本清单...")
    list_url = "https://binaries.soliditylang.org/linux-amd64/list.json"
    try:
        releases_data = requests.get(list_url, timeout=10).json()
        releases = releases_data.get('releases', {})
    except Exception as e:
        print(f"获取版本清单失败: {e}")
        return

    artifacts_dir = Path("/home/zzh/code/research/idea_1_SmartAuditFlow_SolEvo/SmartAuditFlow/smart-contract-audit/venv/.solc-select/artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    # 我们使用顺序下载，每个文件带有单独的速度和进度条
    for i, v in enumerate(missing, 1):
        print(f"\n[{i}/{len(missing)}] 正在处理 solc {v}...")
        
        if v not in releases:
            print(f"[-] {v} 不是一个有效的或已发布的官方 Linux 编译版本，跳过。")
            continue
            
        artifact_filename = releases[v]
        download_url = f"https://binaries.soliditylang.org/linux-amd64/{artifact_filename}"
        
        # 准备存放路径
        target_dir = artifacts_dir / f"solc-{v}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_filepath = target_dir / f"solc-{v}"

        try:
            response = requests.get(download_url, stream=True, timeout=15)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # 使用 tqdm 实现该文件的具体下载进度条展示（包含速率）
            with open(target_filepath, "wb") as f, tqdm(
                desc=f"下载 {v}",
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=65536):
                    size = f.write(data)
                    pbar.update(size)
                    
            # 赋予可执行权限
            st = os.stat(target_filepath)
            os.chmod(target_filepath, st.st_mode | stat.S_IEXEC)
            success_count += 1
            print(f"[✓] {v} 安装就绪")
            
        except requests.exceptions.Timeout:
            print(f"[x] 下载 {v} 超时，请稍后重跑重试。")
        except Exception as e:
            print(f"[x] 下载 {v} 发生错误: {e}")

    print("\n" + "="*50)
    print(f"执行结束！本次成功下载/安装了 {success_count} 个版本。")
    print("您可以随时再次运行此脚本来补充遗漏的任何缺失版本。")

if __name__ == "__main__":
    main()
