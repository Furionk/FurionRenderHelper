# Furion Render Helper

Advanced frame rendering with clipboard integration and keyframe detection for Blender.

## Features

- **Batch Frame Rendering**: Render specific frames or frame ranges with a simple comma-separated input
- **Smart Keyframe Detection**: Automatically suggest frames that contain keyframes across all animated objects
- **Windows Clipboard Integration**: Copy rendered images directly to clipboard with alpha channel support
- **Persistent Output Folder**: Save and remember your preferred output directory
- **Progress Tracking**: Real-time progress display with console output and cancellation support
- **Flexible Frame Input**: Support for both individual frames (1,5,10) and ranges (1-5,10-15)

## Usage

1. **Set Output Folder** (Optional): Configure where your rendered frames will be saved. If not set, uses the blend file directory.

2. **Choose Frames to Render**: 
   - Enter frame numbers manually: `1,5,10,25`
   - Use ranges: `1-5,10-15,30`
   - Mix both: `1,5-10,15,20-25`
   - Click the keyframe icon to auto-populate with frames containing keyframes

3. **Render**: Click "Render Specific Frames" to start batch rendering or "Render Current Frame" for single frame rendering.

## Panel Location

Properties Panel > Render Properties > Render Specific Frames

## File Naming Convention

Rendered files are named using the pattern:
`[blend_filename]_[camera_name]_frame_[frame_number].[extension]`

Example: `MyProject_Camera_frame_0001.png`

## System Requirements

- Blender 4.0 or later
- Windows OS (for clipboard functionality)

## Tips

- Use persistent data rendering for faster batch processing
- Press ESC during rendering to cancel the operation
- The extension remembers your output folder preference between sessions
- Supports all standard Blender image formats (PNG, JPEG, TIFF, EXR)

## Permissions

- **Files**: Creates a preferences file to remember your output folder setting
- **Clipboard**: Copies rendered images to Windows clipboard when enabled

## License

GPL-3.0-or-later