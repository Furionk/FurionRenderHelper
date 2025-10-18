# Furion Render Helper

Advanced frame rendering with keyframe detection for Blender.

## Features

- **Batch Frame Rendering**: Render specific frames or frame ranges with a simple comma-separated input
- **Customizable Filename Patterns**: Token-based system for flexible filename generation
- **Smart Keyframe Detection**: Automatically suggest frames that contain keyframes across all animated objects
- **Persistent Settings**: Save and remember your preferred output directory and filename patterns
- **Progress Tracking**: Real-time progress display with console output and cancellation support
- **Flexible Frame Input**: Support for both individual frames (1,5,10) and ranges (1-5,10-15)
- **Live Preview**: Real-time filename preview showing what your files will be named

## Usage

1. **Set Output Folder** (Optional): Configure where your rendered frames will be saved. If not set, uses the blend file directory.

2. **Customize Filename Pattern** (Optional): 
   - Use tokens like `(FileName)`, `(Camera)`, `(Frame)`, `(Channel)` for naming
   - Add date/time with `(Start:yyyyMMdd)`, `(End:HHmmss)` for time-stamped files
   - Preview shows exactly how your files will be named

3. **Select Render Channels/Passes**: 
   - Choose which render passes to output: Combined, Depth, Mist, Normal, etc.
   - Multiple channels require `(Channel)` token in filename pattern
   - Extension automatically enables selected passes in render settings

4. **Choose Frames to Render**: 
   - Enter frame numbers manually: `1,5,10,25`
   - Use ranges: `1-5,10-15,30`
   - Mix both: `1,5-10,15,20-25`
   - Click the keyframe icon to auto-populate with frames containing keyframes

5. **Render**: Click "Render Specific Frames" to start batch rendering or "Render Current Frame" for single frame rendering.

## Filename Pattern System

The extension supports a powerful token-based filename pattern system:

### Available Tokens
- `(FileName)` - Blend file name without .blend extension
- `(Camera)` - Current scene camera name
- `(Frame)` - Frame number with zero-padding (0001, 0002, etc.)
- `(Channel)` - Render pass/channel name (Combined, Depth, Mist, etc.) - **Required for multi-channel rendering**
- `(Start:format)` - Render batch start date/time
- `(End:format)` - Render completion date/time (or current time for single frames)

### Date/Time Formats
- `yyyy` - 4-digit year (2025)
- `MM` - 2-digit month (01-12)
- `dd` - 2-digit day (01-31)
- `HH` - 2-digit hour (00-23)
- `mm` - 2-digit minute (00-59)
- `ss` - 2-digit second (00-59)

### Pattern Examples
| Pattern | Output Example |
|---------|----------------|
| `(FileName)_(Camera)_frame_(Frame)` | `MyProject_Camera_frame_0001` |
| `(FileName)_(Camera)_(Frame)_(Channel)` | `MyProject_Camera_0001_Combined` |
| `(FileName)_(Frame)_(Channel)` | `MyProject_0001_Depth` |
| `(FileName)_(Camera)_(Frame)_(Start:yyyyMM)` | `MyProject_Camera_0001_202510` |
| `(FileName)_(Frame)_(End:yyyyMMddHHmmss)` | `MyProject_0001_20251018172118` |
| `(FileName)_(End:yyyyMMdd_HH:mm:ss)` | `MyProject_20251018_17:21:18` |
| `render_(Start:yyyy-MM-dd)_(Frame)` | `render_2025-10-18_0001` |

### Multi-Channel Output Examples
When multiple render passes are selected with pattern `(FileName)_(Camera)_(Frame)_(Channel)`:
- `MyProject_Camera_0001_Combined.png`
- `MyProject_Camera_0001_Depth.png`
- `MyProject_Camera_0001_Mist.png`
- `MyProject_Camera_0001_Normal.png`

## Panel Location

Properties Panel > Render Properties > Render Specific Frames

## File Naming Convention

Rendered files are named using the pattern:
`[blend_filename]_[camera_name]_frame_[frame_number].[extension]`

Example: `MyProject_Camera_frame_0001.png`

## System Requirements

- Blender 4.0 or later
- All operating systems supported

## Tips

- Use persistent data rendering for faster batch processing
- Press ESC during rendering to cancel the operation
- The extension remembers your output folder preference between sessions
- Supports all standard Blender image formats (PNG, JPEG, TIFF, EXR)

## Permissions

- **Files**: Creates a preferences file to remember your output folder and filename pattern settings

## License

GPL-3.0-or-later