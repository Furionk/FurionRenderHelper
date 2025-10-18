#!/usr/bin/env python3
"""
Build script for Furion Render Helper Blender Extension
Uses official Blender build tools when available, falls back to manual ZIP creation
"""

import os
import zipfile
import sys
import subprocess
import shutil
from datetime import datetime

def create_extension_package():
    """Create a ZIP package of the extension using official tools or manual method"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🔧 Building Furion Render Helper Extension Package...")
    print(f"📁 Source directory: {current_dir}")
    
    # Try to use official Blender build command first
    blender_executable = shutil.which('blender')
    if blender_executable:
        print("🚀 Attempting to use official Blender build command...")
        try:
            result = subprocess.run([
                blender_executable, 
                '--command', 'extension', 'build',
                '--source-dir', current_dir
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Official Blender build - SUCCESS")
                print("Output:", result.stdout.strip() if result.stdout.strip() else "(no output)")
                
                # Look for the generated ZIP file
                for file in os.listdir(current_dir):
                    if file.endswith('.zip') and 'furion_render_helper' in file:
                        package_path = os.path.join(current_dir, file)
                        print(f"📦 Generated package: {file}")
                        print(f"📏 Package size: {os.path.getsize(package_path)} bytes")
                        print_installation_instructions(file)
                        return True
                
                print("⚠️  Build succeeded but couldn't find output ZIP file")
            else:
                print("❌ Official Blender build - FAILED")
                print("Error:", result.stderr.strip() if result.stderr.strip() else result.stdout.strip())
                print("⬇️  Falling back to manual ZIP creation...")
        except subprocess.TimeoutExpired:
            print("⚠️  Official Blender build - Timed out")
            print("⬇️  Falling back to manual ZIP creation...")
        except Exception as e:
            print(f"⚠️  Official Blender build - Error: {e}")
            print("⬇️  Falling back to manual ZIP creation...")
    else:
        print("ℹ️  Blender not found in PATH - Using manual ZIP creation")
        print("   (Install Blender and add to PATH for official build tools)")
    
    # Manual ZIP creation fallback
    print("\n🔧 Creating extension package manually...")
    
    # Files to include in the package (excluding build/validation scripts)
    files_to_include = [
        'blender_manifest.toml',
        '__init__.py',
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'INSTALL.md'
    ]
    
    # Create package name with version and date
    package_name = f"furion_render_helper_v1.0.0_{datetime.now().strftime('%Y%m%d')}.zip"
    package_path = os.path.join(current_dir, package_name)
    
    print(f"📦 Package name: {package_name}")
    
    try:
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_include:
                file_path = os.path.join(current_dir, file)
                if os.path.exists(file_path):
                    zipf.write(file_path, file)
                    print(f"✅ Added: {file}")
                else:
                    print(f"⚠️  Skipped: {file} (not found)")
        
        print(f"\n✅ Package created successfully: {package_path}")
        print(f"📏 Package size: {os.path.getsize(package_path)} bytes")
        print_installation_instructions(package_name)
        return True
        
    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return False

def print_installation_instructions(package_name):
    """Print installation instructions"""
    print("\n📦 Installation Instructions:")
    print("1. Open Blender 4.2 or later")
    print("2. Go to Edit > Preferences > Extensions")
    print("3. Click the '+' button dropdown > Install from Disk")
    print(f"4. Select the file: {package_name}")
    print("5. Enable the extension in the Extensions list")
    
    print("\n🚀 Alternative (Official Command):")
    print("If you have Blender in PATH, you can also install with:")
    print(f"   blender --command extension install-file {package_name}")

if __name__ == "__main__":
    success = create_extension_package()
    sys.exit(0 if success else 1)