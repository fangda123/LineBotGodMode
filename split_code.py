import os
import re
import sys
import shutil
import subprocess
import time

def capitalize_first_letter(s):
    return s[0].upper() + s[1:] if s else s

def run_command(cmd, cwd=None):
    """รันคำสั่งและรอจนกว่าจะเสร็จ"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}: สำเร็จ")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}: ล้มเหลว")
        print(f"Error: {e.stderr}")
        return False

def fix_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # แยกส่วน package declaration และ imports
        package_line = None
        if 'package main' in content:
            package_line = 'package main\n'
            content = content.replace(package_line, '')
            
        # แก้ไข imports
        replacements = {
            'github.com/bashery/botline/thriftjos': 'github.com/apache/thrift/lib/go/thrift',
            './library/': 'linebotgodmode/library/',
            './library': 'linebotgodmode/library',
            'github.com/bashery/botline/oop': 'linebotgodmode/library/oop',
            'github.com/bashery/botline/SyncService': 'linebotgodmode/library/SyncService',
            'github.com/bashery/botline/hashmap': 'linebotgodmode/library/hashmap',
            'github.com/bashery/botline/linethrift': 'linebotgodmode/library/linethrift',
            'github.com/bashery/botline/channel': 'linebotgodmode/library/channel',
            'github.com/bashery/botline/newcrash': 'linebotgodmode/library/newcrash',
            'github.com/bashery/botline/modcompact': 'linebotgodmode/library/modcompact',
            'github.com/bashery/botline/difflib': 'linebotgodmode/library/difflib',
            'github.com/bashery/botline/secondaryqrcodeloginservice': 'linebotgodmode/library/secondaryqrcodeloginservice'
        }
        
        for old_path, new_path in replacements.items():
            content = content.replace(old_path, new_path)
            
        # จัดการ imports block
        import_block = None
        if 'import (' in content:
            import_start = content.find('import (')
            import_end = content.find(')', import_start) + 1
            import_block = content[import_start:import_end]
            content = content.replace(import_block, '')
            
            # ลบ imports ที่ไม่ได้ใช้
            unused_imports = ['"time"', '"fmt"', '"os"', '"strings"', '"syscall"']
            for unused in unused_imports:
                if unused in import_block and unused not in content:
                    import_block = import_block.replace('\n\t' + unused, '')
        
        # รวมกลับเข้าด้วยกันตามลำดับที่ถูกต้อง
        final_content = ''
        if package_line:
            final_content += package_line + '\n'
        if import_block:
            final_content += import_block + '\n\n'
        final_content += content.strip()
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(final_content)
            
        print(f'✅ แก้ไข imports ใน {file_path} สำเร็จ')
        return True
    except Exception as e:
        print(f'❌ แก้ไข imports ใน {file_path} ล้มเหลว: {str(e)}')
        return False

def copy_library():
    try:
        if os.path.exists('library'):
            shutil.copytree('library', os.path.join(target_dir, 'library'), dirs_exist_ok=True)
            return True
        else:
            print('❌ ไม่พบโฟลเดอร์ library')
            return False
    except Exception as e:
        print(f'❌ เกิดข้อผิดพลาดในการคัดลอก library: {str(e)}')
        return False

def copy_db_and_gomod():
    try:
        # คัดลอก db
        if os.path.exists('db'):
            shutil.copytree('db', os.path.join(target_dir, 'db'), dirs_exist_ok=True)
            print('✅ คัดลอก db สำเร็จ')
        
        # คัดลอก go.mod และ go.sum
        for file in ['go.mod', 'go.sum']:
            if os.path.exists(file):
                shutil.copy2(file, os.path.join(target_dir, file))
                print(f'✅ คัดลอก {file} สำเร็จ')
        
        return True
    except Exception as e:
        print(f'❌ เกิดข้อผิดพลาดในการคัดลอก db และ go.mod: {str(e)}')
        return False

def add_imports_to_main():
    try:
        main_file = os.path.join(target_dir, 'main.go')
        
        # รายชื่อไฟล์ที่ต้อง import
        import_files = [
            'package_import', 'constants_variables', 'types_structs', 
            'core', 'config', 'group_management', 'member_management', 
            'utils', 'logging_backup', 'qr_verification', 'array_list', 
            'purge_kick', 'bot_core', 'member_user', 'kick_protection', 
            'group_backup_invite', 'bot_contact', 'bot_main'
        ]
        
        # อ่านเนื้อหาเดิมของไฟล์
        with open(main_file, 'r') as file:
            content = file.read()
        
        # หาตำแหน่ง import block
        import_start = content.find('import (')
        import_end = content.find(')', import_start) + 1
        
        # สร้าง import block ใหม่
        new_imports = 'import (\n'
        new_imports += '\t"os"\n'
        new_imports += '\t"fmt"\n'
        
        # เพิ่ม import สำหรับทุกไฟล์
        for file_name in import_files:
            new_imports += f'\t"linebotgodmode/{file_name}"\n'
        
        new_imports += ')\n\n'
        
        # แทนที่ import block เดิม
        new_content = content[:import_start] + new_imports + content[import_end:]
        
        # เขียนไฟล์กลับ
        with open(main_file, 'w') as file:
            file.write(new_content)
            
        print('✅ เพิ่ม imports ใน main.go สำเร็จ')
        return True
    except Exception as e:
        print(f'❌ เพิ่ม imports ใน main.go ล้มเหลว: {str(e)}')
        return False

def setup_project():
    """ตั้งค่าโปรเจคหลังจากสร้างไฟล์เสร็จ"""
    try:
        # คัดลอก library
        print('\n📚 กำลังคัดลอก library...')
        if copy_library():
            print('✅ คัดลอก library สำเร็จ')
        else:
            print('❌ คัดลอก library ล้มเหลว')

        # คัดลอก db และ go.mod
        print('\n📚 กำลังคัดลอก db และ go.mod...')
        copy_db_and_gomod()

        # เพิ่ม imports ใน main.go
        print('\n🔧 กำลังเพิ่ม imports...')
        add_imports_to_main()

        # รันโปรแกรม
        print('\n🚀 กำลังรันโปรแกรม...')
        if run_command(f'cd {target_dir} && go run main.go zul'):
            print('✅ รันโปรแกรมสำเร็จ')
        else:
            print('❌ รันโปรแกรมล้มเหลว')

        return True
    except Exception as e:
        print(f'\n❌ เกิดข้อผิดพลาด: {str(e)}')
        return False

# Get current directory
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
module_name = "linebotgodmode"  # กำหนดค่าคงที่เป็น linebotgodmode
target_dir = os.path.join(current_dir, 'linebotgodmode')  # เปลี่ยนเป็น linebotgodmode

print("\n🗑️ กำลังลบโฟลเดอร์ linebotgodmode เดิม...")
# Remove existing target directory if exists
if os.path.exists(target_dir):
    try:
        shutil.rmtree(target_dir)
        print("✅ ลบโฟลเดอร์ linebotgodmode เดิมสำเร็จ")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการลบโฟลเดอร์ linebotgodmode: {e}")
        exit(1)

print("\n📁 กำลังสร้างโฟลเดอร์ linebotgodmode ใหม่...")
# Create the target directory
try:
    os.makedirs(target_dir)
    print("✅ สร้างโฟลเดอร์ linebotgodmode ใหม่สำเร็จ")
except OSError as e:
    print(f"❌ เกิดข้อผิดพลาดในการสร้างโฟลเดอร์: {e}")
    exit(1)

# Define the line ranges for each group
groups = [
     ('package_import.go', 1, 37),
    ('constants_variables.go', 37, 682),
    ('types_structs.go', 683, 741),
    ('core.go', 742, 967),
    ('main.go', 968, 1247),
    ('config.go', 1248, 1528),
    ('group_management.go', 1529, 2053),
    ('member_management.go', 2054, 2683),
    ('utils.go', 2684, 3604),
    ('logging_backup.go', 3605, 4162),
    ('qr_verification.go', 4163, 5113),
    ('array_list.go', 5114, 5718),
    ('purge_kick.go', 5719, 6208),
    ('bot_core.go', 6209, 7011),
    ('member_user.go', 7012, 7283),
    ('kick_protection.go', 7284, 7495),
    ('group_backup_invite.go', 7496, 7728),
    ('bot_contact.go', 7729, 7859),
    ('bot_main.go', 7860, 14853),
]

print("\n📝 กำลังแยกไฟล์...")
# Split the code into separate files
for file_name, start_line, end_line in groups:
    file_path = os.path.join(target_dir, file_name)
    try:
        with open('masterj.go', 'r') as source_file:
            lines = source_file.readlines()
            
        with open(file_path, 'w') as file:
            # กำหนด package name โดยพิเศษสำหรับบางไฟล์
            if file_name == 'package_import.go':
                package_name = 'package_import'
            elif file_name == 'main.go':
                # ข้ามการสร้างไฟล์ main.go เพื่อป้องกันการคัดลอกซ้ำ
                print(f"⏩ ข้ามการสร้างไฟล์ {file_name}")
                continue
            else:
                package_name = os.path.splitext(file_name)[0]
            
            # เขียน package declaration
            file.write(f'package {package_name}\n\n')
            
            # Write code content exactly as is
            for line in lines[start_line-1:end_line]:
                file.write(line)
                
        print(f"✅ สร้างไฟล์ {file_name} สำเร็จ")
    except IOError as e:
        print(f"❌ เกิดข้อผิดพลาดในการเขียนไฟล์ {file_path}: {e}")
        exit(1)

print("\n🎉 แยกไฟล์เสร็จสมบูรณ์!")

# เริ่มการตั้งค่าโปรเจคและรันทันที
setup_project() 