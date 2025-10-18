# Furion Render Helper

Batch render specific frames with multi-channel output and customizable filename patterns.

## Key Features

- 🎯 **Batch Frame Rendering** - Render specific frames or ranges (e.g., `1,5,10-15,30`)
- 🎨 **Multi-Channel Output** - Automatically exports all enabled render passes from View Layer
- 📝 **Custom Filename Patterns** - Token-based naming with live preview
- 🔑 **Smart Keyframe Detection** - Auto-suggest frames with keyframes
- 💾 **Persistent Settings** - Remembers output folder and patterns

## Quick Start

1. **Set Output Folder** - Click "Set Output Folder" or leave blank to use blend file directory
2. **Enable Render Passes** - Go to View Layer Properties > Passes and enable desired outputs
3. **Configure Pattern** (Optional) - Use tokens like `(FileName)_(Frame)_(Channel)` for custom naming
4. **Enter Frames** - Type frame numbers: `1,5,10` or ranges: `1-5,10-15` or click keyframe icon
5. **Render** - Click "Furion Render Helper"

## Filename Tokens

| Token | Output | Notes |
|-------|--------|-------|
| `(FileName)` | `MyProject` | Blend file name |
| `(Camera)` | `Camera` | Scene camera name |
| `(ViewLayer)` | `ViewLayer` | View layer name |
| `(Frame)` | `0001` | Frame with padding |
| `(Channel)` | `Combined`, `Depth`, `Mist` | Render pass name (required for multi-pass) |
| `(Start:yyyyMMdd)` | `20251018` | Render start date/time |
| `(End:HHmmss)` | `172118` | Render end time |

### Date/Time Format
- `yyyy` = year, `MM` = month, `dd` = day, `HH` = hour, `mm` = minute, `ss` = second

### Example Patterns

```
(FileName)_(Camera)_frame_(Frame)
→ MyProject_Camera_frame_0001.png

(FileName)_(Frame)_(Channel)
→ MyProject_0001_Combined.png
→ MyProject_0001_Depth.png

(FileName)_(ViewLayer)_(Frame)_(Start:yyyyMMdd)
→ MyProject_Beauty_0001_20251018.png
```

## Multi-Channel Rendering

**Enable passes in Blender:**  
Properties > View Layer Properties > Passes > Data/Light sections

**Add `(Channel)` token when rendering multiple passes:**
- ✅ With token: Each pass saves separately  
  `MyProject_0001_Combined.png`, `MyProject_0001_Depth.png`
- ⚠️ Without token: Passes overwrite each other  
  `MyProject_0001.png` (only last pass saved)

## Tips

- Press **ESC** during rendering to cancel
- Click **keyframe icon** to auto-populate animated frames
- **Open Folder** button quickly accesses output directory
- Settings are automatically saved between sessions

## Requirements

- Blender 4.0+
- Supports Windows, macOS, Linux

## Location

Properties > Render Properties > **Furion Render Helper**

---

**License:** MIT