# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2024-10-18

### Added
- **Multi-channel Render Pass Output**: Select and render multiple passes simultaneously
  - Combined, Depth (Z), Mist, Normal, Diffuse Direct, Glossy Direct, Emission passes
  - Automatic render pass enablement when selected
  - Individual file output for each selected pass
- **Enhanced Filename Patterns**: New `(Channel)` token for multi-pass workflows
  - Required when multiple render passes are selected
  - Generates unique filenames per channel/pass
- **Advanced Validation**: Smart filename pattern checking
  - Warns when multiple channels selected without `(Channel)` token
  - Prevents rendering with invalid patterns
- **Enhanced Progress Tracking**: 
  - Total render count (frames × channels)
  - Per-channel progress display in console and UI
  - Detailed rendering information with channel names

### Updated
- **UI Enhancements**: New render channels selection section with checkboxes
- **Progress Reporting**: More detailed console output and progress messages
- **Documentation**: Updated with multi-channel workflow information

### Fixed
- **View Layer Access**: Fixed AttributeError when accessing scene view layers (used proper collection indexing)
- **Render Pass Extraction**: Implemented proper render pass extraction using compositor setup
  - Each render pass now outputs correct data instead of Combined pass
  - Automatic compositor configuration for specific passes (Depth, Mist, Normal, etc.)
  - Proper cleanup and restoration of original compositor state
- **Single Channel Rendering**: Fixed "could not confirm output files" error when using Combined channel only
  - Properly handles filename patterns without (Channel) token for single channel rendering
  - Improved file validation and manual save fallback for robust file output

## [1.2.0] - 2024-10-18

### Removed
- **Windows Clipboard Integration**: Removed all clipboard functionality to simplify the extension
- **Copy to Clipboard Toggle**: Removed UI toggle for clipboard copying
- **Debug Clipboard Tool**: Removed debug clipboard operator
- **Windows-specific Dependencies**: Removed ctypes, struct, and bmesh imports used only for clipboard

### Updated
- **Cross-platform Compatibility**: Extension now works identically on all operating systems
- **Simplified UI**: Cleaner interface without clipboard options
- **Reduced Complexity**: Focused purely on file-based rendering workflow
- **Documentation**: Updated to reflect removal of clipboard features

## [1.1.0] - 2024-10-18

### Added
- **Customizable Filename Patterns**: Token-based filename generation system
  - `(FileName)` - Blend file name without extension
  - `(Camera)` - Current scene camera name  
  - `(Frame)` - Frame number with padding (0001)
  - `(Start:format)` - Render start date/time with custom formatting
  - `(End:format)` - Render end date/time with custom formatting
- **Date/Time Format Support**: Custom date/time formatting (e.g., yyyyMMdd, HH:mm:ss)
- **Live Preview**: Real-time filename preview in UI showing generated filename
- **Pattern Persistence**: Filename patterns saved in user preferences
- **Comprehensive Help**: Built-in help with examples and format guides

### Examples
- `(FileName)_(Camera)_(Frame)_(Start:yyyyMM)` → `blenderfile_maincamera_0001_202510`
- `(FileName)_(Frame)_(End:yyyyMMddHHmmss)` → `blenderfile_0001_20251018172118`
- `(FileName)_(End:yyyyMMdd_HH:mm:ss)` → `blenderfile_20251018_17:21:18`

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