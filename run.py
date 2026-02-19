import taptap
import requests
import re
from urllib.parse import unquote, urlparse
import os
from sys import exit

def download_file_minimal(url, filename=None, retry=False) -> str:
    """
    最简洁版本，只显示百分比进度
    """
    try:        
        # 下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        filename = re.search(r'filename="([^"]+)"',response.headers.get('content-disposition', '')).group(1)
        
        # 移除本地跳过逻辑，让GitHub Actions和本地行为一致
        # 无论retry参数如何，都重新下载
        with open(filename, 'wb') as file:
            percent_now = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        percent = f'{((downloaded_size / total_size) * 100):.1f}'
                        if(percent_now != percent):
                            print(f"\r{percent}%", end='', flush=True)
                            percent_now = percent
            return filename
    except Exception as e:
        raise e

try:
    apk_download_link = taptap.taptap(165287)
except Exception as e:
    print(e)
    exit(1)

# 预先提取文件名和版本号
try:
    # 使用HEAD请求获取文件名，不下载内容
    response = requests.head(apk_download_link)
    response.raise_for_status()
    content_disposition = response.headers.get('content-disposition', '')
    file_name_match = re.search(r'filename="([^"]+)"', content_disposition)
    
    if file_name_match:
        file_name = file_name_match.group(1)
    else:
        # 如果header中没有文件名，从URL路径中提取
        file_name = os.path.basename(urlparse(apk_download_link).path)
        if not file_name:
            file_name = "phigros.apk"
    
    # 提取版本号
    version = (file_name.split('-')[1]).split('.')[0]
    
except Exception as e:
    print(f"无法获取文件信息: {e}")
    exit(1)

# 检查是否需要下载
need_download = True

# 如果文件已存在且足够大，检查版本号
if os.path.exists(file_name) and os.stat(file_name).st_size >= 1500000000:
    try:
        if os.path.exists('VERSION'):
            with open('VERSION', 'r', encoding='UTF-8') as f:
                local_version = f.read().strip()
                if int(local_version) >= int(version):
                    print(f"文件 {file_name} (版本 {version}) 已存在且为最新版本，跳过下载")
                    need_download = False
    except Exception as e:
        print(f"版本检查失败: {e}")
        # 如果版本检查失败，继续下载

# 执行下载（如果需要）
if need_download:
    print(f"开始下载 {file_name} (版本 {version})...")
    try:
        file_name = download_file_minimal(apk_download_link)
        print(f"\n下载完成: {file_name}")
    except Exception as e:
        print(f"下载失败: {e}")
        exit(1)
else:
    print(f"使用现有文件: {file_name}")

# 更新版本文件到最新
try:
    with open("VERSION", "w", encoding='UTF-8') as f:
        f.write(version)
        f.close()
    print(f"版本信息已更新: {version}")
except Exception as e:
    print(f"更新版本文件失败: {e}")

# 执行处理任务
try:
    os.system(f"python gameInformation.py {file_name}")
    os.system(f"python resource.py {file_name}")
    os.system("python replaceAvatarName.py")
except Exception as e:
    print(f"执行处理任务时出错: {e}")
    exit(1)

print("所有任务完成！")