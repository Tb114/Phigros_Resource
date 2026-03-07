import taptap
import requests
import re
from urllib.parse import unquote, urlparse
import os
from sys import exit

def download_file_with_retry(url, filename, max_retries=3):
    """带重试机制的下载函数"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filename, 'wb') as file:
                percent_now = 0
                in_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            percent = ((downloaded_size / total_size) * 100)
                            percent_str = f'{percent:.1f}'
                            
                            if in_github_actions:
                                # 在GitHub Actions环境中，每隔1个整数百分比输出
                                if int(percent) != int(percent_now):
                                    print(f"{int(percent)}%")
                                    percent_now = percent
                            else:
                                # 原逻辑：只有百分比变化时才更新显示
                                if percent_str != percent_now:
                                    print(f"\r{percent_str}%", end='', flush=True)
                                    percent_now = percent_str
                        
            # 验证文件大小
            actual_size = os.path.getsize(filename)
            if total_size > 0 and actual_size != total_size:
                print(f"\n文件大小不匹配: 期望 {total_size}, 实际 {actual_size}")
                os.remove(filename)
                if attempt < max_retries - 1:
                    print(f"重试下载... ({attempt + 1}/{max_retries})")
                    continue
                else:
                    raise Exception(f"下载失败: 文件大小不匹配 ({actual_size}/{total_size})")
            
            print(f"\n下载完成: {filename}")
            return filename
            
        except Exception as e:
            print(f"\n下载失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if os.path.exists(filename):
                os.remove(filename)
            if attempt == max_retries - 1:
                raise e

def get_apk_filename(url):
    """尝试从URL获取APK文件名"""
    try:
        # 方法1: 从content-disposition获取
        response = requests.head(url, timeout=10, allow_redirects=True)
        content_disposition = response.headers.get('content-disposition', '')
        match = re.search(r'filename=["\']?([^"\'\s]+)["\']?', content_disposition, re.I)
        if match:
            return unquote(match.group(1))
        return "phigros.apk"
        
    except:
        return "phigros.apk"

try:
    print("获取APK下载链接...")
    apk_download_link = taptap.taptap(165287)
    print(f"下载链接: {apk_download_link}")
except Exception as e:
    print(f"获取下载链接失败: {e}")
    exit(1)

# 获取文件名
file_name = get_apk_filename(apk_download_link)
print(f"APK文件名: {file_name}")

# 从文件名提取版本号
try:
    # 尝试从文件名中提取版本号，例如: com.PigeonGames.Phigros-136.apk
    if '-' in file_name and '.apk' in file_name.lower():
        version_part = file_name.split('-')[1]
        version = version_part.split('.')[0]
        print(f"提取到版本号: {version}")
    else:
        version = "0"
        print(f"无法从文件名提取版本号，使用默认值: {version}")
except Exception as e:
    version = "0"
    print(f"提取版本号失败: {e}")

# 检查是否需要下载
need_download = True

if os.path.exists(file_name):
    file_size = os.path.getsize(file_name)
    print(f"本地文件存在: {file_name} ({file_size} bytes)")
    
    # 检查版本文件
    version_updated = False
    if os.path.exists('VERSION'):
        try:
            with open('VERSION', 'r', encoding='UTF-8') as f:
                local_version = f.read().strip()
                print(f"本地版本号: {local_version}")
                if local_version and version and int(local_version) >= int(version):
                    print(f"本地版本 {local_version} 已是最新或更高，跳过下载")
                    need_download = False
        except Exception as e:
            print(f"读取版本文件失败: {e}")
            need_download = True
    
    # 如果文件太小，也需要重新下载
    if file_size < 1000000:  # 小于1MB的文件肯定不完整
        print(f"文件大小 ({file_size} bytes) 太小，需要重新下载")
        need_download = True
else:
    print(f"本地文件不存在: {file_name}")

# 执行下载（如果需要）
if need_download:
    print(f"\n开始下载 {file_name} (版本 {version})...")
    try:
        # 删除可能存在的损坏文件
        if os.path.exists(file_name):
            os.remove(file_name)
            
        # 下载文件
        file_name = download_file_with_retry(apk_download_link, file_name, max_retries=3)
        
        # 验证文件完整性（简单检查文件大小）
        final_size = os.path.getsize(file_name)
        print(f"最终文件大小: {final_size} bytes")
        
        if final_size < 100000000:  # Phigros APK应该大于100MB
            print(f"警告: 文件大小 ({final_size} bytes) 可能不完整!")
        
    except Exception as e:
        print(f"下载失败: {e}")
        exit(1)
else:
    print(f"使用现有文件: {file_name}")

# 更新版本文件
try:
    with open("VERSION", "w", encoding='UTF-8') as f:
        f.write(version)
    print(f"版本信息已更新: {version}")
except Exception as e:
    print(f"更新版本文件失败: {e}")

# 执行处理任务
try:
    print("\n开始执行处理任务...")
    os.system(f"python gameInformation.py {file_name}")
    os.system(f"python resource.py {file_name}")
    os.system("python replaceAvatarName.py")
except Exception as e:
    print(f"执行处理任务时出错: {e}")
    exit(1)

print("\n所有任务完成！")