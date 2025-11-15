import taptap
import resource
import gameInformation

import requests
import re
from urllib.parse import unquote, urlparse
import os

def download_file_minimal(url, filename=None):
    """
    最简洁版本，只显示百分比进度
    """
    try:        
        # return
        # 下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        filename = re.search(r'filename="([^"]+)"',response.headers.get('content-disposition', '')).group(1)
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        print(f"\r{percent:.1f}%", end='', flush=True)
        
    except Exception as e:
        raise e
try:
    apk_download_link = taptap.taptap(165287)
except Exception as e:
    print(e)
    exit(1)
try:
    # file_name = "com.PigeonGames.Phigros-136.apk"
    file_name = download_file_minimal(apk_download_link)
except Exception as e:
    print(e)
    exit(1)
    
os.system(f"python Resource.py {file_name}")
os.system(f"python gameInformation.py {file_name}")
os.system("python replaceAvatarName.py")