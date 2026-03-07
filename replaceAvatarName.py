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
# print(mp)
for key, value in mp.items():
    old_file = os.path.join('avatar/', f"{key}.png")
    new_file = os.path.join('avatar/', f"{value}.png")
    # 检查原文件是否存在
    if os.path.exists(old_file):
        if old_file == 'avatar/Cipher1.png':
            continue
        try:
            if(os.path.isfile(new_file)):
                os.remove(new_file)
            os.rename(old_file, new_file)
            print(f'Rename {old_file} into {new_file}')
        except:
            print(old_file,new_file)
            pass
    else:
        print(old_file)
        