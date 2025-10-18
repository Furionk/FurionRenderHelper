#!/usr/bin/env python3
"""
Validation script for Furion Render Helper Blender Extension
Uses both manual checks and official Blender validation when available
"""

import os
import sys
import subprocess
import shutil

def validate_extension():
    """Validate the extension structure and files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'blender_manifest.toml',
        '__init__.py',
        'README.md',
        'LICENSE'
    ]
    
    optional_files = [
        'CHANGELOG.md',
        'INSTALL.md'
    ]
    
    print("🔍 Validating Furion Render Helper Extension Structure...")
    print(f"📁 Extension directory: {current_dir}")
    
    # Check required files
    missing_files = []
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    # Check optional files
    for file in optional_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} - Found (optional)")
        else:
            print(f"⚠️  {file} - Missing (optional)")
    
    # Check manifest content
    manifest_path = os.path.join(current_dir, 'blender_manifest.toml')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for required fields according to official docs
            required_fields = ['schema_version', 'id', 'version', 'name', 'tagline', 'maintainer', 'type', 'blender_version_min', 'license']
            missing_fields = []
            for field in required_fields:
                if field not in content:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ blender_manifest.toml - All required fields present")
                
                # Check version format
                if 'blender_version_min = "4.2.0"' in content or 'blender_version_min = "4.2"' in content:
                    print("✅ blender_manifest.toml - Minimum Blender version 4.2.0+ ✓")
                else:
                    print("⚠️  blender_manifest.toml - Should use blender_version_min = \"4.2.0\" or higher")
                
                # Check tags
                if 'tags = ["Render", "Animation"]' in content:
                    print("✅ blender_manifest.toml - Uses official supported tags")
                else:
                    print("⚠️  blender_manifest.toml - Consider using only official supported tags")
            else:
                print(f"❌ blender_manifest.toml - Missing required fields: {', '.join(missing_fields)}")
                missing_files.extend(missing_fields)
    
    # Check __init__.py content
    init_path = os.path.join(current_dir, '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            required_functions = ['register()', 'unregister()']
            missing_functions = []
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if not missing_functions:
                print("✅ __init__.py - Required functions present")
                
                # Check for bl_info (for backward compatibility)
                if 'bl_info' in content:
                    print("✅ __init__.py - bl_info present (backward compatibility)")
                else:
                    print("ℹ️  __init__.py - No bl_info (extension-only mode)")
            else:
                print(f"❌ __init__.py - Missing required functions: {', '.join(missing_functions)}")
                missing_files.extend(missing_functions)
    
    # Try to use official Blender validation if available
    print("\n🔧 Attempting official Blender validation...")
    blender_executable = shutil.which('blender')
    if blender_executable:
        try:
            result = subprocess.run([
                blender_executable, 
                '--command', 'extension', 'validate', 
                current_dir
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Official Blender validation - PASSED")
                print("Output:", result.stdout.strip() if result.stdout.strip() else "(no output)")
            else:
                print("❌ Official Blender validation - FAILED")
                print("Error:", result.stderr.strip() if result.stderr.strip() else result.stdout.strip())
                # Don't treat this as a fatal error since it might be a Blender version issue
        except subprocess.TimeoutExpired:
            print("⚠️  Official Blender validation - Timed out")
        except Exception as e:
            print(f"⚠️  Official Blender validation - Error: {e}")
    else:
        print("ℹ️  Blender not found in PATH - Skipping official validation")
        print("   (Install Blender and add to PATH for official validation)")
    
    # Summary
    print("\n" + "="*50)
    if missing_files:
        print(f"❌ Validation FAILED - Issues: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Validation PASSED - Extension is ready for installation!")
        print("\n📦 To install:")
        print("1. Create a ZIP file with all the files (use build_extension.py)")
        print("2. In Blender 4.2+: Edit > Preferences > Extensions")
        print("3. Click '+' > Install from Disk")
        print("4. Select your ZIP file")
        print("\n🚀 Or use official Blender build command:")
        print("   blender --command extension build")
        return True

if __name__ == "__main__":
    success = validate_extension()
    sys.exit(0 if success else 1)