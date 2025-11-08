import os

mp:map = {}
with open('./info/tmp.tsv','r', encoding='utf-8') as f:
    content = f.read()
    lst:list[str] = content.split('\n')
    
    for each in lst:
        try:
            each.split('\t')[1]
        except:
            continue
        mp[each.split('\t')[1]] = each.split('\t')[0]

for key, value in mp.items():
    old_file = os.path.join('avatar/', f"{key}.png")
    new_file = os.path.join('avatar/', f"{value}.png")
    # 检查原文件是否存在
    if os.path.exists(old_file):
        if key == 'Cipher1':
            continue
        try:
            os.rename(old_file, new_file)
        except:
            pass