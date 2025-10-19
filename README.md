# Furion Render Helper

This is just a blender plugin for me to batch render with multi-channel output and customizable filename patterns. 

![image](https://github.com/Furionk/FurionRenderHelper/blob/main/furion_render_helper.png)

## Key Features

- 🎯 **Batch Frame Rendering** - Batch render by typing frame ranges (e.g., `1,5,10-15,30`)
- 🔑 **Smart Keyframe Detection** - Auto-suggest keyframes for blocking stage renders. Extracts keyframes from the Dope Sheet Summary timeline, skipping interpolated frames. Respects your frame range: if you type `1-100`, only keyframes between 1 and 100 are included (keyframes at 100+ are filtered out). It is for reviewing animation blocking without rendering unnecessary in-between frames. Making it for reviewing animation blocking without rendering interpolated frames easier.


- 🎨 **Multi-Channel Output** - Render multiple passes (Combined, Depth, Mist, Normal, etc.) in a single batch
- 📝 **Customizable Filenames** - Use flexible token patterns with date/time support
- 💾 **Persistent Settings** - Output folder and filename patterns are saved between sessions

## Quick Start

1. **Set Output Folder** - Click "Set Output Folder" or leave blank to use blend file directory
2. **Enable Render Passes** - Go to View Layer Properties > Passes and enable desired outputs channels (optional)
3. **Configure Pattern** (Optional) - Use tokens like `(FileName)_(Frame)_(Channel)` for custom naming
4. **Enter Frames** - Type frame numbers: `1,5,10` or ranges: `1-5,10-15` or click keyframe icon
5. **Render** - Click "Render Specific Frames" or "Render Current Frame"

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

## Requirements

- Blender 4.0+
- Supports Windows, macOS, Linux

## Location

Properties > Render Properties > **Furion Render Helper**

---

**License:** MIT
