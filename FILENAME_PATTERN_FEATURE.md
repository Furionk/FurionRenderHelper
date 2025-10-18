# Furion Render Helper v1.1.0 - Filename Pattern Feature

## 🎉 New Feature: Customizable Filename Patterns

Just a tool for me to manage blender render easier, allows me complete control over how rendered files are named!

### ✨ Key Features Added

#### 🏷️ **Token System**
- `(FileName)` - Blend file name without extension
- `(Camera)` - Current scene camera name  
- `(Frame)` - Frame number with zero-padding (0001)
- `(Start:format)` - Render start date/time
- `(End:format)` - Render end date/time

#### 📅 **Date/Time Formatting**
- `yyyy` - 4-digit year → 2025
- `MM` - 2-digit month → 10  
- `dd` - 2-digit day → 18
- `HH` - 2-digit hour → 17
- `mm` - 2-digit minute → 21
- `ss` - 2-digit second → 18

#### 🎯 **Your Requested Examples Work Perfectly**

1. **`(FileName)_(Camera)_(Frame)_(Start:yyyyMM)`**
   → `blenderfile_maincamera_0001_202510`

2. **`(FileName)_(Frame)_(End:yyyyMMddHHmmss)`**  
   → `blenderfile_0001_20251018172118`

3. **`(FileName)_(End:yyyyMMdd_HH:mm:ss)`**
   → `blenderfile_20251018_17:21:18`

### 🎮 **User Interface Enhancements**

#### **New UI Section**: "Filename Pattern Settings"
- Shows current pattern with preview
- Live preview of generated filename
- One-click pattern customization

#### **Pattern Dialog Features**  
- Comprehensive help with all available tokens
- Date/time format examples
- Real pattern examples with outputs
- Input validation and error handling

#### **Persistent Settings**
- Patterns saved in user preferences
- Automatically loaded on Blender startup
- Works alongside existing output folder preferences

### 🔧 **Technical Implementation**

#### **Smart Pattern Processing**
- Regex-based token replacement
- Custom date/time format conversion
- Invalid character filtering for cross-platform compatibility
- Fallback handling for missing data

#### **Timeline Integration**  
- Records actual render start time for batch operations
- Uses current time for single frame renders
- Maintains timing accuracy across modal operations

#### **Backward Compatibility**
- Default pattern matches original naming: `(FileName)_(Camera)_frame_(Frame)`
- Existing users see no change until they customize
- All existing functionality preserved

### 📦 **Installation Package**

**Package**: `furion_render_helper_v1.1.0_20251018.zip` (20,482 bytes)

**Version**: 1.1.0 (updated from 1.0.0)

### 🚀 **Ready to Use**

The extension is now fully updated and ready for installation in Blender 4.2+. Users can:

1. Use default naming (unchanged behavior)
2. Customize patterns via intuitive UI
3. See live previews of their naming choices
4. Use complex date/time formatting
5. Save preferences for future sessions

### 📋 **Summary of Changes**

#### **Added Files/Functions**:
- `generate_filename_from_pattern()` - Core pattern processing
- `RENDER_OT_set_filename_pattern` - UI operator for pattern setting
- Enhanced preferences system for pattern storage

#### **Updated Functions**:
- All filename generation logic (batch render, single render, file opening)
- UI panel with new pattern section and preview
- Preferences loading/saving system
- Help text and documentation

#### **Documentation Updated**:
- README with pattern examples and format table
- CHANGELOG with detailed feature description  
- Comprehensive inline help in the UI

The extension now provides exactly the filename customization system you requested! 🎯