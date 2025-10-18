# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-18

### Added
- Initial release as Blender Extension following official Blender 4.2+ standards
- Batch frame rendering with flexible input support (individual frames and ranges)
- Smart keyframe detection across all animated objects in the scene
- Windows clipboard integration with alpha channel support
- Persistent output folder preferences stored in user config
- Real-time progress tracking with console output
- Cancellation support (ESC key during rendering)
- Automatic file naming with blend file, camera, and frame information
- Support for multiple image formats (PNG, JPEG, TIFF, EXR)
- Render current frame functionality
- Open rendered frame result functionality
- Debug tools for clipboard testing
- Comprehensive error handling and user feedback
- Modal rendering operation for non-blocking UI
- Persistent data optimization for faster batch rendering
- Automatic format switching for unsupported video formats

### Technical Features
- **Official Blender Extension Compliance**: Follows Blender 4.2+ extension standards
- **Proper Manifest**: `blender_manifest.toml` with all required fields per official documentation
- **Official Tags**: Uses only officially supported tags ("Render", "Animation")
- **Minimum Version**: Requires Blender 4.2.0 as per extension guidelines
- **SPDX License Headers**: Proper licensing with GPL-3.0-or-later
- **Permissions Declaration**: Properly declared "files" and "clipboard" permissions
- **Build Integration**: Compatible with official Blender build and validation tools
- **Cross-platform path handling** with Windows-specific clipboard features
- **Memory-efficient image processing** for clipboard operations
- **Robust keyframe detection** across objects, materials, and scene data

### Documentation
- **Comprehensive README** with usage instructions
- **Installation guide** with multiple installation methods including official tools
- **License file** (GPL-3.0-or-later)
- **Changelog** following semantic versioning
- **Validation and build scripts** with official Blender tool integration
- **Inline code documentation** and comments

### Extension Structure
- `blender_manifest.toml` - Official extension manifest
- `__init__.py` - Main extension code with bl_info for backward compatibility
- `README.md` - User documentation
- `LICENSE` - GPL-3.0-or-later license
- `CHANGELOG.md` - Version history
- `INSTALL.md` - Installation instructions
- `validate_extension.py` - Validation tool with official Blender integration
- `build_extension.py` - Build tool with official Blender integration

### Fixed
- Updated minimum Blender version to 4.2.0 per extension requirements
- Corrected manifest format to match official documentation exactly
- Improved permission descriptions to be concise and clear
- Enhanced build exclusion patterns to prevent development files in packages
- Updated all documentation to reference Blender 4.2+ requirements