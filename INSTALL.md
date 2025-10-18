# Installation Guide

## Method 1: Installing from Extension Repository (Recommended)

1. Open Blender 4.2 or later
2. Go to `Edit > Preferences > Extensions`
3. Search for "Furion Render Helper"
4. Click "Install" next to the extension
5. Enable the extension by checking the checkbox

## Method 2: Installing from File

1. Download or clone this repository
2. Build the extension package:
   - **Option A (Recommended)**: Use official Blender tools:
     ```bash
     blender --command extension build --source-dir /path/to/FurionRenderHelper
     ```
   - **Option B**: Use the provided build script:
     ```bash
     python build_extension.py
     ```
   - **Option C**: Create a ZIP file manually containing:
     - `blender_manifest.toml`
     - `__init__.py`
     - `README.md`
     - `LICENSE`
     - `CHANGELOG.md` (optional)
     - `INSTALL.md` (optional)

3. Open Blender 4.2 or later
4. Go to `Edit > Preferences > Extensions`
5. Click the "+" button dropdown > "Install from Disk..."
6. Navigate to and select your ZIP file
7. Enable the extension by checking the checkbox

## Method 3: Development Installation

1. Clone or download this repository
2. Copy the entire `FurionRenderHelper` folder to your Blender extensions directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\[version]\extensions\user_default\`
   - **macOS**: `~/Library/Application Support/Blender/[version]/extensions/user_default/`
   - **Linux**: `~/.config/blender/[version]/extensions/user_default/`
3. Restart Blender
4. Go to `Edit > Preferences > Extensions`
5. Find "Furion Render Helper" in the list and enable it

## Command Line Installation (Advanced)

If you have Blender in your system PATH, you can install extensions via command line:

```bash
# Install from file
blender --command extension install-file /path/to/furion_render_helper.zip

# Build and install from source
blender --command extension build --source-dir /path/to/FurionRenderHelper
blender --command extension install-file furion_render_helper-1.0.0.zip
```

## Verification

After installation, you should see the "Furion Render Helper" panel in:
`Properties Panel > Render Properties > Furion Render Helper`

## Requirements

- **Blender**: Version 4.2.0 or later
- **Operating System**: All platforms supported
- **Clipboard Features**: Windows OS (for clipboard functionality)

## Uninstallation

1. Go to `Edit > Preferences > Extensions`
2. Find "Furion Render Helper" in the list
3. Click the dropdown arrow next to the extension
4. Select "Uninstall"

## Troubleshooting

- **Extension not appearing**: Make sure you're using Blender 4.2 or later
- **Cannot find Extensions panel**: Update to Blender 4.2+ (Extensions replaced Add-ons in 4.2)
- **Clipboard not working**: This feature only works on Windows OS
- **Output folder issues**: Ensure you have write permissions to the selected folder
- **Missing keyframes**: Make sure your objects have actual keyframe animation data
- **Build errors**: Use `python validate_extension.py` to check for issues

## Development and Validation

To validate the extension structure:
```bash
# Manual validation
python validate_extension.py

# Official Blender validation
blender --command extension validate /path/to/FurionRenderHelper
```

For support, please visit the project repository or create an issue.