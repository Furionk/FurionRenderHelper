# SPDX-FileCopyrightText: 2024 Furion Mashiou
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Furion Render Helper - Advanced frame rendering with clipboard integration and keyframe detection

This extension provides tools for batch rendering specific frames with advanced features:
- Batch frame rendering with flexible input (individual frames and ranges)
- Smart keyframe detection across all animated objects
- Windows clipboard integration with alpha channel support
- Persistent output folder preferences
- Real-time progress tracking with cancellation support
"""

bl_info = {
    "name": "Furion Render Helper",
    "author": "Furion Mashiou",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Properties > Render Properties > Render Specific Frames",
    "description": "Advanced frame rendering with clipboard integration and keyframe detection",
    "warning": "Windows clipboard functionality requires Windows OS",
    "doc_url": "https://github.com/furion-mashiou/furion-render-helper",
    "tracker_url": "https://github.com/furion-mashiou/furion-render-helper/issues",
    "category": "Render",
}

import bpy
import bmesh
from bpy.props import StringProperty
from bpy.types import Operator, Panel
import os
import json
import sys
import struct
import ctypes

# Global variable to store the output folder
output_folder_path = ""

# Path to store user preferences
def get_preferences_file():
    """Get the path to the preferences file in Blender's user data folder"""
    user_data_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(user_data_dir, 'render_specific_frames_prefs.json')

def load_default_output_folder():
    """Load the default output folder from user preferences"""
    global output_folder_path
    prefs_file = get_preferences_file()
    try:
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                prefs = json.load(f)
                saved_folder = prefs.get('default_output_folder', '')
                if saved_folder and os.path.exists(saved_folder):
                    output_folder_path = saved_folder
                    print(f"Loaded default output folder: {output_folder_path}")
                else:
                    print("Saved output folder no longer exists, using default")
    except Exception as e:
        print(f"Could not load preferences: {e}")

def save_default_output_folder():
    """Save the current output folder as default to user preferences"""
    global output_folder_path
    prefs_file = get_preferences_file()
    try:
        # Ensure the config directory exists
        os.makedirs(os.path.dirname(prefs_file), exist_ok=True)
        
        # Load existing preferences or create new ones
        prefs = {}
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                prefs = json.load(f)
        
        # Update the output folder preference
        prefs['default_output_folder'] = output_folder_path
        
        # Save preferences
        with open(prefs_file, 'w') as f:
            json.dump(prefs, f, indent=2)
        
        print(f"Saved default output folder: {output_folder_path}")
    except Exception as e:
        print(f"Could not save preferences: {e}")

# Load default output folder on script load
load_default_output_folder()


def copy_render_result_to_windows_clipboard(context, fallback_path: str | None = None):
    """Copy the last render to the Windows clipboard with alpha (Windows only).

    Prefers loading from fallback_path (saved file), or tries the in-memory 'Render Result'.

    Returns True on success, False otherwise.
    """
    if sys.platform != 'win32':
        print("Copy to clipboard is only implemented on Windows in this script.")
        return False

    img = None
    use_loaded = False
    
    # Strategy 1: If we have a fallback file path, use that (most reliable)
    if fallback_path and os.path.exists(fallback_path):
        try:
            print(f"Loading image from disk: {fallback_path}")
            # Use check_existing=False to force a fresh load
            img = bpy.data.images.load(fallback_path, check_existing=False)
            use_loaded = True
            
            # Verify the loaded image has valid data
            if int(img.size[0]) <= 0 or int(img.size[1]) <= 0:
                print(f"Loaded image has invalid dimensions: {img.size[0]}x{img.size[1]}")
                bpy.data.images.remove(img)
                img = None
            else:
                print(f"Successfully loaded image from disk: {img.size[0]}x{img.size[1]}, {img.channels} channels")
        except Exception as e:
            print(f"Could not load fallback image: {e}")
            if img:
                try:
                    bpy.data.images.remove(img)
                except:
                    pass
            img = None
    
    # Strategy 2: Try to get pixels directly from render engine
    if not img:
        print("Attempting to access Render Result from render engine...")
        render_result = bpy.data.images.get('Render Result')
        if render_result:
            try:
                # Get the actual pixel data size from the render settings
                scene = context.scene
                width = int(scene.render.resolution_x * scene.render.resolution_percentage / 100)
                height = int(scene.render.resolution_y * scene.render.resolution_percentage / 100)
                
                print(f"Expected render size: {width}x{height}")
                
                # Try to access pixels - if this works, we can use it
                pixel_count = width * height * 4
                pixels = list(render_result.pixels)
                
                if len(pixels) == pixel_count:
                    print(f"Successfully accessed {len(pixels)} pixels from Render Result")
                    # Create a temporary image to hold the data
                    img = render_result
                    # Override the size with actual render size
                    class FakeImg:
                        def __init__(self, pixels_data, w, h, channels):
                            self.pixels = pixels_data
                            self.size = (w, h)
                            self.channels = channels
                    img = FakeImg(pixels, width, height, 4)
                else:
                    print(f"Pixel count mismatch: expected {pixel_count}, got {len(pixels)}")
                    img = None
            except Exception as e:
                print(f"Could not access Render Result pixels: {e}")
                img = None
    
    if not img:
        print("No valid image data available from any source.")
        return False

    # Get image properties (works for both real images and our FakeImg wrapper)
    channels = getattr(img, 'channels', 4)
    if channels < 4:
        print("Image has no alpha channel; proceeding without alpha.")

    width = int(img.size[0])
    height = int(img.size[1])
    if width <= 0 or height <= 0:
        print("Image has invalid dimensions.")
        if use_loaded and hasattr(img, 'name'):
            try:
                bpy.data.images.remove(img)
            except Exception:
                pass
        return False

    # Fetch pixel data (RGBA floats 0..1), Blender stores bottom-up which matches positive DIB height
    # Handle both list and property access
    if isinstance(img.pixels, list):
        pixels = img.pixels
    else:
        pixels = list(img.pixels)

    # Convert to BGRA 8-bit bytes (no premultiply)
    bgra = bytearray(width * height * 4)
    for i in range(0, len(pixels), 4):
        r = int(max(0, min(255, round(pixels[i + 0] * 255.0))))
        g = int(max(0, min(255, round(pixels[i + 1] * 255.0))))
        b = int(max(0, min(255, round(pixels[i + 2] * 255.0))))
        a = int(max(0, min(255, round(pixels[i + 3] * 255.0)))) if channels >= 4 else 255
        j = (i // 4) * 4
        bgra[j + 0] = b
        bgra[j + 1] = g
        bgra[j + 2] = r
        bgra[j + 3] = a

    # Build BITMAPINFOHEADER (40 bytes), 32bpp, BI_RGB, bottom-up (positive height)
    biSize = 40
    biWidth = width
    biHeight = height  # positive = bottom-up; matches Blender pixel order
    biPlanes = 1
    biBitCount = 32
    BI_RGB = 0
    biCompression = BI_RGB
    biSizeImage = len(bgra)
    biXPelsPerMeter = 0
    biYPelsPerMeter = 0
    biClrUsed = 0
    biClrImportant = 0

    header = struct.pack(
        '<IiiHHIIiiII',
        biSize, biWidth, biHeight, biPlanes, biBitCount,
        biCompression, biSizeImage, biXPelsPerMeter, biYPelsPerMeter,
        biClrUsed, biClrImportant
    )

    # Combine header + pixel data into a global memory block
    CF_DIB = 8
    GMEM_MOVEABLE = 0x0002
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    # Set return types for better error handling
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GetLastError.restype = ctypes.c_uint32

    total_size = len(header) + len(bgra)
    hGlobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, total_size)
    if not hGlobal:
        error_code = kernel32.GetLastError()
        print(f"GlobalAlloc failed with error code: {error_code}")
        return False

    pGlobal = kernel32.GlobalLock(hGlobal)
    if not pGlobal:
        error_code = kernel32.GetLastError()
        print(f"GlobalLock failed with error code: {error_code}")
        kernel32.GlobalFree(hGlobal)
        return False

    # Copy memory
    try:
        ctypes.memmove(ctypes.c_void_p(pGlobal), header, len(header))
        dest_ptr = ctypes.c_void_p(pGlobal + len(header))
        ctypes.memmove(dest_ptr, (ctypes.c_char * len(bgra)).from_buffer(bgra), len(bgra))
    except Exception as e:
        print(f"Memory copy failed: {e}")
        kernel32.GlobalUnlock(hGlobal)
        kernel32.GlobalFree(hGlobal)
        return False
    
    kernel32.GlobalUnlock(hGlobal)

    # Set clipboard data
    if not user32.OpenClipboard(0):
        error_code = kernel32.GetLastError()
        print(f"OpenClipboard failed with error code: {error_code}")
        kernel32.GlobalFree(hGlobal)
        return False
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_DIB, hGlobal):
            error_code = kernel32.GetLastError()
            print(f"SetClipboardData failed with error code: {error_code}")
            # If SetClipboardData fails, we must free the handle
            kernel32.GlobalFree(hGlobal)
            return False
        # On success, do not free hGlobal; clipboard owns it now
    finally:
        user32.CloseClipboard()

    print("✓ Image copied to Windows clipboard (BGRA 32-bit)")

    # If we loaded a temporary image from disk, free it
    if use_loaded and hasattr(img, 'name'):
        try:
            bpy.data.images.remove(img)
        except Exception:
            pass
    return True

class RENDER_OT_set_output_folder(Operator):
    """Set output folder for rendering specific frames"""
    bl_idname = "render.set_output_folder"
    bl_label = "Set Output Folder"
    bl_description = "Choose the folder where rendered frames will be saved"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Property to store output folder path
    folder_path: StringProperty(
        name="Output Folder",
        description="Choose the folder where rendered frames will be saved",
        default="",
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        global output_folder_path
        if self.folder_path.strip():
            output_folder_path = bpy.path.abspath(self.folder_path.strip())
            # Ensure the folder exists
            try:
                os.makedirs(output_folder_path, exist_ok=True)
                # Save as default preference
                save_default_output_folder()
                self.report({'INFO'}, f"Output folder set to: {output_folder_path}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to create/access folder: {str(e)}")
                return {'CANCELLED'}
        else:
            # Clear the output folder (use default)
            output_folder_path = ""
            # Save empty preference
            save_default_output_folder()
            self.report({'INFO'}, "Output folder cleared (will use blend file directory)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        global output_folder_path
        self.folder_path = output_folder_path
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "folder_path")
        layout.separator()
        layout.label(text="Leave empty to use blend file directory")
        layout.label(text="This folder will be saved as your default", icon='DISK_DRIVE')


class RENDER_OT_specific_frames(Operator):
    """Render specific frames based on user input"""
    bl_idname = "render.specific_frames"
    bl_label = "Render Specific Frames"
    bl_description = "Render specific frames entered by user (comma separated)"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Property to store frame numbers input
    frame_list: StringProperty(
        name="Frame Numbers",
        description="Enter frame numbers separated by commas (e.g., 1,5,10,25) or ranges (e.g., 1-5,10-15)",
        default="1,5,10-15"
    )
    
    # Internal properties for modal operation
    _timer = None
    _frame_numbers = []
    _current_frame_index = 0
    _original_frame = 0
    _original_filepath = ""
    _original_format = ""
    _format_switched = False
    _output_folder = ""
    _blend_filename = ""
    _last_saved_path = ""
    _original_use_persistent_data = False
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # Check if we're done rendering all frames
            if self._current_frame_index >= len(self._frame_numbers):
                return self.finish_rendering(context)
            
            # Render the current frame
            frame_num = self._frame_numbers[self._current_frame_index]
            scene = context.scene
            render = scene.render
            
            # Set current frame
            scene.frame_set(frame_num)
            
            # Get camera name for filename
            camera_name = "NoCamera"
            if scene.camera:
                camera_name = scene.camera.name
            
            # Create output filename with camera name
            filename = f"{self._blend_filename}_{camera_name}_frame_{frame_num:04d}"
            
            # Get file extension from render settings
            file_format = render.image_settings.file_format.lower()
            if file_format == 'png':
                extension = '.png'
            elif file_format == 'jpeg':
                extension = '.jpg'
            elif file_format == 'tiff':
                extension = '.tif'
            elif file_format == 'exr':
                extension = '.exr'
            else:
                extension = '.png'  # default
            
            # Set full output path
            full_output_path = os.path.join(self._output_folder, filename + extension)
            render.use_file_extension = True
            render.filepath = full_output_path
            self._last_saved_path = full_output_path
            
            # Console progress display
            progress_percent = ((self._current_frame_index + 1) / len(self._frame_numbers)) * 100
            progress_bar = "█" * int(progress_percent / 5) + "░" * (20 - int(progress_percent / 5))
            
            print("=" * 60)
            print(f"RENDERING PROGRESS: [{progress_bar}] {progress_percent:.1f}%")
            print(f"Frame {self._current_frame_index + 1} of {len(self._frame_numbers)}")
            print(f"Current Frame Number: {frame_num}")
            print(f"Output File: {filename}{extension}")
            print(f"Full Path: {full_output_path}")
            print(f"Render Format: {render.image_settings.file_format}")
            print(f"Resolution: {render.resolution_x}x{render.resolution_y}")
            print("=" * 60)
            
            # Update progress in UI
            progress_msg = f"Rendering frame {frame_num} ({self._current_frame_index + 1}/{len(self._frame_numbers)}) -> {filename}{extension}"
            self.report({'INFO'}, progress_msg)
            
            # Render the frame
            print(f"Starting render of frame {frame_num}...")
            bpy.ops.render.render(write_still=True)
            print(f"✓ Frame {frame_num} rendered successfully!")
            
            # Move to next frame
            self._current_frame_index += 1
            
            # Update UI
            for area in context.screen.areas:
                area.tag_redraw()
        
        elif event.type == 'ESC':
            return self.cancel_rendering(context)
        
        return {'PASS_THROUGH'}
    
    def finish_rendering(self, context):
        # Console completion message
        print("\n" + "=" * 60)
        print("🎉 RENDERING COMPLETED SUCCESSFULLY! 🎉")
        print(f"✓ Total frames rendered: {len(self._frame_numbers)}")
        print(f"✓ Output folder: {self._output_folder}")
        print(f"✓ Frame numbers: {self._frame_numbers}")
        print("=" * 60 + "\n")
        
        # Restore original frame and filepath
        scene = context.scene
        scene.frame_set(self._original_frame)
        scene.render.filepath = self._original_filepath
        if self._format_switched and self._original_format:
            try:
                scene.render.image_settings.file_format = self._original_format
            except Exception:
                pass
        
        # Restore original persistent data setting
        scene.render.use_persistent_data = self._original_use_persistent_data
        print(f"✓ Restored persistent data setting to: {self._original_use_persistent_data}")
        
        # Remove timer
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        # Optional: copy last rendered image to clipboard if toggle enabled
        if getattr(context.scene, 'copy_render_to_clipboard', False):
            ok = copy_render_result_to_windows_clipboard(context, fallback_path=self._last_saved_path or None)
            if ok:
                self.report({'INFO'}, "Copied rendered image to clipboard")
            else:
                self.report({'WARNING'}, "Could not copy image to clipboard")

        self.report({'INFO'}, f"Successfully rendered {len(self._frame_numbers)} frames")
        return {'FINISHED'}
    
    def cancel_rendering(self, context):
        # Console cancellation message
        print("\n" + "=" * 60)
        print("⚠️  RENDERING CANCELLED BY USER ⚠️")
        print(f"✓ Frames completed: {self._current_frame_index}/{len(self._frame_numbers)}")
        print(f"✓ Output folder: {self._output_folder}")
        print("=" * 60 + "\n")
        
        # Restore original frame and filepath
        scene = context.scene
        scene.frame_set(self._original_frame)
        scene.render.filepath = self._original_filepath
        if self._format_switched and self._original_format:
            try:
                scene.render.image_settings.file_format = self._original_format
            except Exception:
                pass
        
        # Restore original persistent data setting
        scene.render.use_persistent_data = self._original_use_persistent_data
        print(f"✓ Restored persistent data setting to: {self._original_use_persistent_data}")
        
        # Remove timer
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        self.report({'WARNING'}, f"Rendering cancelled. Completed {self._current_frame_index}/{len(self._frame_numbers)} frames")
        return {'CANCELLED'}
    
    def execute(self, context):
        global output_folder_path
        # Parse the frame list
        try:
            frame_string = self.frame_list.strip()
            if not frame_string:
                self.report({'ERROR'}, "Please enter frame numbers")
                return {'CANCELLED'}
            
            # Split by comma and convert to integers or ranges
            frame_numbers = []
            for frame_str in frame_string.split(','):
                frame_str = frame_str.strip()
                if frame_str:
                    try:
                        # Check if it's a range (contains hyphen)
                        if '-' in frame_str:
                            # Handle range like "1-5" or "10-20"
                            range_parts = frame_str.split('-')
                            if len(range_parts) == 2:
                                start_frame = int(range_parts[0].strip())
                                end_frame = int(range_parts[1].strip())
                                if start_frame <= end_frame:
                                    # Add all frames in range (inclusive)
                                    frame_numbers.extend(range(start_frame, end_frame + 1))
                                else:
                                    self.report({'ERROR'}, f"Invalid range: {frame_str} (start must be <= end)")
                                    return {'CANCELLED'}
                            else:
                                self.report({'ERROR'}, f"Invalid range format: {frame_str}")
                                return {'CANCELLED'}
                        else:
                            # Single frame number
                            frame_num = int(frame_str)
                            frame_numbers.append(frame_num)
                    except ValueError:
                        self.report({'ERROR'}, f"Invalid frame number or range: {frame_str}")
                        return {'CANCELLED'}
            
            if not frame_numbers:
                self.report({'ERROR'}, "No valid frame numbers found")
                return {'CANCELLED'}
            
            # Remove duplicates and sort
            frame_numbers = sorted(list(set(frame_numbers)))
            
            # Store frame numbers for modal operation
            self._frame_numbers = frame_numbers
            self._current_frame_index = 0
            
            # Get current scene
            scene = context.scene
            
            # Store original frame and filepath
            self._original_frame = scene.frame_current
            self._original_filepath = scene.render.filepath
            self._original_format = scene.render.image_settings.file_format
            self._format_switched = False
            
            # Store original persistent data setting and enable it for batch rendering
            self._original_use_persistent_data = scene.render.use_persistent_data
            scene.render.use_persistent_data = True
            print(f"✓ Enabled persistent data for batch rendering (was: {self._original_use_persistent_data})")

            # If current file format is a video/unsupported for still files, switch to PNG temporarily
            disallowed_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW", "FRAMESERVER"}
            if self._original_format in disallowed_formats:
                try:
                    scene.render.image_settings.file_format = 'PNG'
                    self._format_switched = True
                    print(f"ℹ️ Switched render format from {self._original_format} to PNG for still rendering")
                except Exception as e:
                    self.report({'WARNING'}, f"Could not switch format from {self._original_format}; output may not save correctly: {e}")
            
            # Get the blend file name (without extension)
            blend_filepath = bpy.data.filepath
            if blend_filepath:
                self._blend_filename = os.path.splitext(os.path.basename(blend_filepath))[0]
            else:
                self._blend_filename = "untitled"
            
            # Set up output folder
            if output_folder_path.strip():
                self._output_folder = output_folder_path
                # Ensure the folder exists
                os.makedirs(self._output_folder, exist_ok=True)
            else:
                # Use default blend file directory or current directory
                if blend_filepath:
                    self._output_folder = os.path.dirname(bpy.path.abspath(blend_filepath))
                else:
                    self._output_folder = os.getcwd()
            
            self.report({'INFO'}, f"Starting render of {len(frame_numbers)} frames: {frame_numbers}")
            self.report({'INFO'}, f"Output folder: {self._output_folder}")
            self.report({'INFO'}, "Press ESC to cancel rendering")
            
            # Console startup message
            print("\n" + "=" * 60)
            print("🚀 STARTING BATCH RENDER PROCESS 🚀")
            print(f"📁 Output folder: {self._output_folder}")
            print(f"🎬 Blend file: {self._blend_filename}")
            print(f"🎯 Total frames to render: {len(frame_numbers)}")
            print(f"📋 Frame list: {frame_numbers}")
            print(f"🖼️  Format: {context.scene.render.image_settings.file_format}")
            print(f"📐 Resolution: {context.scene.render.resolution_x}x{context.scene.render.resolution_y}")
            print(f"💾 Persistent data: ON (was {self._original_use_persistent_data})")
            print("💡 Press ESC to cancel rendering at any time")
            print("=" * 60 + "\n")
            
            # Start modal operation with timer
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error during rendering: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Show dialog box for user input
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        global output_folder_path
        layout = self.layout
        
        # Check if we have suggested keyframes to apply
        if hasattr(bpy.types.WindowManager, 'suggested_keyframes'):
            suggested = bpy.types.WindowManager.suggested_keyframes
            if suggested:
                self.frame_list = suggested
            # Clear the suggestion after applying
            delattr(bpy.types.WindowManager, 'suggested_keyframes')
        
        # Show current output folder
        box = layout.box()
        if output_folder_path:
            box.label(text=f"Output Folder: {output_folder_path}", icon='FOLDER_REDIRECT')
        else:
            box.label(text="Output Folder: (Blend file directory)", icon='FOLDER_REDIRECT')
        
        layout.separator()
        
        # Frame numbers input section with suggestion button
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "frame_list", text="Frame Numbers")
        
        # Suggest Keyframes button - pass current frame_list to the operator
        suggest_op = row.operator("render.suggest_keyframes", text="", icon='KEYFRAME_HLT')
        suggest_op.current_frames = self.frame_list
        
        col.label(text="Enter frame numbers separated by commas")
        col.label(text="Examples: 1,5,10,25 or 1-5,10-15,30")
        
        # Add keyframe suggestion info
        layout.separator()
        info_box = layout.box()
        info_box.label(text="💡 Click the keyframe icon to auto-populate frames with keyframes", icon='INFO')
        
        layout.separator()
        layout.label(text="Note: Press ESC during rendering to cancel", icon='INFO')


class RENDER_OT_current_frame(Operator):
    """Render the current frame to the configured output folder"""
    bl_idname = "render.current_frame"
    bl_label = "Render Current Frame"
    bl_description = "Render only the current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global output_folder_path
        try:
            scene = context.scene
            render = scene.render

            # Store original filepath to restore after rendering
            original_filepath = render.filepath
            original_format = render.image_settings.file_format
            format_switched = False

            # Determine output folder
            blend_filepath = bpy.data.filepath
            if output_folder_path.strip():
                output_folder = bpy.path.abspath(output_folder_path.strip())
                os.makedirs(output_folder, exist_ok=True)
            else:
                if blend_filepath:
                    output_folder = os.path.dirname(bpy.path.abspath(blend_filepath))
                else:
                    output_folder = os.getcwd()

            # Determine blend name and frame
            if blend_filepath:
                blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
            else:
                blend_name = "untitled"
            frame_num = scene.frame_current

            # File extension from render format
            # Ensure an image-capable format
            disallowed_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW", "FRAMESERVER"}
            if original_format in disallowed_formats:
                try:
                    render.image_settings.file_format = 'PNG'
                    format_switched = True
                    print(f"ℹ️ Switched render format from {original_format} to PNG for still rendering")
                except Exception as e:
                    self.report({'WARNING'}, f"Could not switch format from {original_format}; output may not save correctly: {e}")

            fmt = render.image_settings.file_format.lower()
            if fmt == 'png':
                extension = '.png'
            elif fmt == 'jpeg':
                extension = '.jpg'
            elif fmt == 'tiff':
                extension = '.tif'
            elif fmt == 'exr':
                extension = '.exr'
            else:
                extension = '.png'

            # Get camera name
            camera_name = "NoCamera"
            if scene.camera:
                camera_name = scene.camera.name
            
            # Build output path
            filename = f"{blend_name}_{camera_name}_frame_{frame_num:04d}"
            full_output_path = os.path.join(output_folder, filename + extension)

            # Console info
            print("\n" + "=" * 60)
            print("🎯 RENDER CURRENT FRAME")
            print(f"📁 Output folder: {output_folder}")
            print(f"🎬 Blend file: {blend_name}")
            print(f"📷 Camera: {camera_name}")
            print(f"🧭 Frame: {frame_num}")
            print(f"🖼️  Format: {render.image_settings.file_format}")
            print(f"➡️  Output: {full_output_path}")
            print("=" * 60 + "\n")

            # Set filepath and render
            render.filepath = full_output_path
            render.use_file_extension = True
            bpy.ops.render.render(write_still=True)

            # Determine where the image actually landed
            saved_path = full_output_path
            if not os.path.exists(saved_path):
                # Try Blender's computed frame path (handles extension/padding differences)
                try:
                    alt_path = bpy.path.abspath(render.frame_path(frame=frame_num))
                    if os.path.exists(alt_path):
                        saved_path = alt_path
                    else:
                        # Last resort: save the Render Result explicitly
                        img = bpy.data.images.get('Render Result')
                        if img:
                            img.save_render(filepath=full_output_path, scene=context.scene)
                            if os.path.exists(full_output_path):
                                saved_path = full_output_path
                except Exception:
                    pass

            # Restore original filepath
            render.filepath = original_filepath
            if format_switched:
                try:
                    render.image_settings.file_format = original_format
                except Exception:
                    pass

            if os.path.exists(saved_path):
                self.report({'INFO'}, f"Saved current frame to: {saved_path}")
                print(f"✓ Saved current frame to: {saved_path}")
                # Optional: copy to clipboard if toggle is enabled
                if getattr(context.scene, 'copy_render_to_clipboard', False):
                    ok = copy_render_result_to_windows_clipboard(context, fallback_path=saved_path)
                    if ok:
                        self.report({'INFO'}, "Copied rendered image to clipboard")
                    else:
                        self.report({'WARNING'}, "Could not copy image to clipboard")
                return {'FINISHED'}
            else:   
                self.report({'WARNING'}, "Rendered but could not confirm output file; check your default render output path.")
                print("⚠️  Render completed but file not found at expected paths:")
                print(f"  Expected: {full_output_path}")
                try:
                    print(f"  Alt: {bpy.path.abspath(render.frame_path(frame=frame_num))}")
                except Exception:
                    pass
                return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error rendering current frame: {str(e)}")
            return {'CANCELLED'}


class RENDER_OT_copy_to_clipboard(Operator):
    """Copy the Render Result to clipboard for debugging"""
    bl_idname = "render.copy_to_clipboard"
    bl_label = "Copy Render Result to Clipboard"
    bl_description = "Copy the current Render Result image to clipboard (for debugging)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            print("\n" + "=" * 60)
            print("📋 COPY RENDER RESULT TO CLIPBOARD (DEBUG)")
            print("=" * 60)
            
            # Check if Render Result exists
            img = bpy.data.images.get('Render Result')
            if not img:
                self.report({'WARNING'}, "No Render Result found. Please render something first.")
                print("⚠️  No Render Result found in bpy.data.images")
                return {'CANCELLED'}
            
            # Check initial state
            has_data = getattr(img, 'has_data', True)
            print(f"Render Result exists: Yes")
            print(f"Initial has_data: {has_data}")
            print(f"Initial size: {img.size[0]}x{img.size[1]}")
            print(f"Initial channels: {img.channels}")
            
            # Try to force update the pixel data
            print("Attempting to update pixel data...")
            try:
                img.update()
                if hasattr(img.pixels, 'update'):
                    img.pixels.update()
                print("✓ Pixel data update attempted")
            except Exception as e:
                print(f"⚠️  Update failed: {e}")
            
            # Check state after update
            has_data = getattr(img, 'has_data', True)
            print(f"After update has_data: {has_data}")
            print(f"After update size: {img.size[0]}x{img.size[1]}")
            print(f"After update channels: {img.channels}")
            
            # Check for valid data
            if not has_data or int(img.size[0]) <= 0 or int(img.size[1]) <= 0:
                self.report({'WARNING'}, "Render Result has no valid pixel data in memory")
                print("⚠️  Render Result still has no valid data after update")
                print("💡 Blender's Render Result doesn't store pixels in memory by default")
                print("💡 Will try to load from last saved render file...")
                
                # Try to find the last rendered file as fallback
                # Look for the last file that was actually saved
                global output_folder_path
                blend_filepath = bpy.data.filepath
                scene = context.scene
                
                # Determine what the last saved file should be
                if output_folder_path.strip():
                    output_folder = bpy.path.abspath(output_folder_path.strip())
                else:
                    if blend_filepath:
                        output_folder = os.path.dirname(bpy.path.abspath(blend_filepath))
                    else:
                        output_folder = os.getcwd()
                
                if blend_filepath:
                    blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
                else:
                    blend_name = "untitled"
                
                frame_num = scene.frame_current
                camera_name = "NoCamera"
                if scene.camera:
                    camera_name = scene.camera.name
                
                # Try different possible filenames
                fmt = scene.render.image_settings.file_format.lower()
                extensions = {
                    'png': '.png',
                    'jpeg': '.jpg',
                    'tiff': '.tif',
                    'exr': '.exr'
                }
                extension = extensions.get(fmt, '.png')
                
                possible_filename = f"{blend_name}_{camera_name}_frame_{frame_num:04d}{extension}"
                possible_path = os.path.join(output_folder, possible_filename)
                
                print(f"Looking for: {possible_path}")
                
                if os.path.exists(possible_path):
                    print(f"✓ Found render file: {possible_path}")
                    print("Attempting to copy from file instead...")
                    ok = copy_render_result_to_windows_clipboard(context, fallback_path=possible_path)
                    if ok:
                        self.report({'INFO'}, "✓ Copied from file to clipboard!")
                        print("=" * 60 + "\n")
                        return {'FINISHED'}
                else:
                    print(f"⚠️  File not found: {possible_path}")
                    print("💡 Please render the current frame first, then try copying")
                
                print("=" * 60 + "\n")
                return {'CANCELLED'}
            
            # Try to copy to clipboard
            print(f"Attempting to copy {img.size[0]}x{img.size[1]} image to clipboard...")
            ok = copy_render_result_to_windows_clipboard(context, fallback_path=None)
            
            if ok:
                self.report({'INFO'}, "✓ Successfully copied Render Result to clipboard!")
                print("✓ Successfully copied to clipboard!")
                print("=" * 60 + "\n")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Failed to copy to clipboard. Check console for details.")
                print("❌ Failed to copy to clipboard")
                print("=" * 60 + "\n")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error copying to clipboard: {str(e)}")
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 60 + "\n")
            return {'CANCELLED'}


class RENDER_OT_open_output_folder(Operator):
    """Open the rendered image file for the current frame"""
    bl_idname = "render.open_output_folder"
    bl_label = "Open Rendered Frame Result"
    bl_description = "Open the rendered image file for the current frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global output_folder_path
        try:
            scene = context.scene
            blend_filepath = bpy.data.filepath
            
            # Determine output folder
            if output_folder_path.strip():
                folder_to_open = bpy.path.abspath(output_folder_path.strip())
            else:
                if blend_filepath:
                    folder_to_open = os.path.dirname(bpy.path.abspath(blend_filepath))
                else:
                    folder_to_open = os.getcwd()

            # Check if folder exists
            if not os.path.exists(folder_to_open):
                self.report({'ERROR'}, f"Output folder does not exist: {folder_to_open}")
                return {'CANCELLED'}

            # Get current frame file info for better user feedback
            if blend_filepath:
                blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
            else:
                blend_name = "untitled"
            
            frame_num = scene.frame_current
            camera_name = "NoCamera"
            if scene.camera:
                camera_name = scene.camera.name

            # Determine file extension from render settings
            fmt = scene.render.image_settings.file_format.lower()
            if fmt == 'png':
                extension = '.png'
            elif fmt == 'jpeg':
                extension = '.jpg'
            elif fmt == 'tiff':
                extension = '.tif'
            elif fmt == 'exr':
                extension = '.exr'
            else:
                extension = '.png'

            expected_filename = f"{blend_name}_{camera_name}_frame_{frame_num:04d}{extension}"
            expected_filepath = os.path.join(folder_to_open, expected_filename)

            # Console info
            print("\n" + "=" * 60)
            print("�️  OPENING RENDERED FRAME RESULT")
            print(f"Current timeline frame: {frame_num}")
            print(f"Looking for file: {expected_filename}")
            print(f"Full path: {expected_filepath}")
            
            # Check if the rendered file exists
            if not os.path.exists(expected_filepath):
                # Try alternative extensions/formats that might exist
                alternative_files = []
                base_name = f"{blend_name}_{camera_name}_frame_{frame_num:04d}"
                common_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.bmp']
                
                for ext in common_extensions:
                    alt_path = os.path.join(folder_to_open, base_name + ext)
                    if os.path.exists(alt_path):
                        alternative_files.append(alt_path)
                
                if alternative_files:
                    expected_filepath = alternative_files[0]  # Use the first found file
                    expected_filename = os.path.basename(expected_filepath)
                    print(f"✓ Found alternative: {expected_filename}")
                else:
                    print(f"❌ File not found: {expected_filename}")
                    print("=" * 60 + "\n")
                    self.report({'ERROR'}, f"Rendered frame not found: {expected_filename}. Please render frame {frame_num} first.")
                    return {'CANCELLED'}
            else:
                print(f"✓ File exists: {expected_filename}")
            
            print("=" * 60 + "\n")

            # Open the specific image file using platform-specific method
            import subprocess
            import platform

            system = platform.system()
            try:
                if system == "Windows":
                    # Use the default program to open the image file
                    subprocess.run(['start', '', expected_filepath], shell=True, check=True)
                elif system == "Darwin":  # macOS
                    subprocess.run(['open', expected_filepath], check=True)
                elif system == "Linux":
                    subprocess.run(['xdg-open', expected_filepath], check=True)
                else:
                    self.report({'ERROR'}, f"Unsupported operating system: {system}")
                    return {'CANCELLED'}

                # Success message
                self.report({'INFO'}, f"Opened rendered frame: {expected_filename}")
                return {'FINISHED'}

            except subprocess.CalledProcessError as e:
                self.report({'ERROR'}, f"Failed to open image file: {e}")
                return {'CANCELLED'}
            except Exception as e:
                self.report({'ERROR'}, f"Error opening image file: {e}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error opening rendered frame result: {str(e)}")
            return {'CANCELLED'}


class RENDER_OT_suggest_keyframes(Operator):
    """Scan the dope sheet and suggest frames with keyframes"""
    bl_idname = "render.suggest_keyframes"
    bl_label = "Suggest Keyframes"
    bl_description = "Scan all objects' keyframes in the dope sheet and populate the frame numbers field"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Property to receive current frame list from the render operator
    current_frames: StringProperty(
        name="Current Frames",
        description="Current frame list to respect min/max values",
        default=""
    )
    
    def execute(self, context):
        scene = context.scene
        
        # Parse current_frames to get min and max values
        frame_range_min = None
        frame_range_max = None
        
        if self.current_frames.strip():
            try:
                frame_numbers = []
                frame_string = self.current_frames.strip()
                
                # Parse the frame list (same logic as the render operator)
                for frame_str in frame_string.split(','):
                    frame_str = frame_str.strip()
                    if frame_str:
                        try:
                            # Check if it's a range (contains hyphen)
                            if '-' in frame_str:
                                # Handle range like "1-5" or "10-20"
                                range_parts = frame_str.split('-')
                                if len(range_parts) == 2:
                                    start_frame = int(range_parts[0].strip())
                                    end_frame = int(range_parts[1].strip())
                                    if start_frame <= end_frame:
                                        frame_numbers.extend(range(start_frame, end_frame + 1))
                            else:
                                # Single frame number
                                frame_num = int(frame_str)
                                frame_numbers.append(frame_num)
                        except ValueError:
                            pass  # Skip invalid entries
                
                if frame_numbers:
                    frame_range_min = min(frame_numbers)
                    frame_range_max = max(frame_numbers)
                    print(f"Using existing frame range: {frame_range_min} - {frame_range_max}")
            except Exception as e:
                print(f"Could not parse current frames: {e}")
                # Continue without range limitation
        
        # Store original frame to restore later
        original_frame = scene.frame_current
        
        try:
            keyframes = set()
            
            # Collect keyframes from all objects in the scene
            def collect_keyframes_from_object(obj):
                """Recursively collect all keyframes from an object's animation data"""
                frames = set()
                
                # Check if object has animation data
                if obj.animation_data and obj.animation_data.action:
                    action = obj.animation_data.action
                    # Iterate through all fcurves in the action
                    for fcurve in action.fcurves:
                        # Get all keyframe points
                        for keyframe_point in fcurve.keyframe_points:
                            frame = int(keyframe_point.co[0])
                            frames.add(frame)
                
                # Check object data animation (e.g., shape keys, mesh animation)
                if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'animation_data') and obj.data.animation_data:
                    if obj.data.animation_data.action:
                        action = obj.data.animation_data.action
                        for fcurve in action.fcurves:
                            for keyframe_point in fcurve.keyframe_points:
                                frame = int(keyframe_point.co[0])
                                frames.add(frame)
                
                # Check material animation
                if hasattr(obj, 'material_slots'):
                    for mat_slot in obj.material_slots:
                        if mat_slot.material and mat_slot.material.animation_data:
                            if mat_slot.material.animation_data.action:
                                action = mat_slot.material.animation_data.action
                                for fcurve in action.fcurves:
                                    for keyframe_point in fcurve.keyframe_points:
                                        frame = int(keyframe_point.co[0])
                                        frames.add(frame)
                
                return frames
            
            # Collect keyframes from all objects
            object_keyframes = {}
            for obj in scene.objects:
                obj_frames = collect_keyframes_from_object(obj)
                if obj_frames:
                    object_keyframes[obj.name] = sorted(list(obj_frames))
                    keyframes.update(obj_frames)
            
            # Also check scene animation data (world, scene properties, etc.)
            if scene.animation_data and scene.animation_data.action:
                action = scene.animation_data.action
                for fcurve in action.fcurves:
                    for keyframe_point in fcurve.keyframe_points:
                        frame = int(keyframe_point.co[0])
                        keyframes.add(frame)
            
            # Check world animation
            if scene.world and scene.world.animation_data and scene.world.animation_data.action:
                action = scene.world.animation_data.action
                for fcurve in action.fcurves:
                    for keyframe_point in fcurve.keyframe_points:
                        frame = int(keyframe_point.co[0])
                        keyframes.add(frame)
            
            # Filter keyframes based on existing frame range or scene frame range
            if frame_range_min is not None and frame_range_max is not None:
                # Use the min/max from existing frame list
                frame_start = frame_range_min
                frame_end = frame_range_max
                filter_source = "existing frame list"
            else:
                # Use scene frame range as fallback
                frame_start = scene.frame_start
                frame_end = scene.frame_end
                filter_source = "scene frame range"
            
            filtered_keyframes = {frame for frame in keyframes if frame_start <= frame <= frame_end}
            
            # Debug output
            print(f"=== Keyframe Collection Debug Info ===")
            print(f"Filter source: {filter_source}")
            print(f"Filter range: {frame_start} - {frame_end}")
            print(f"Scene frame range: {scene.frame_start} - {scene.frame_end}")
            print(f"Objects with keyframes: {len(object_keyframes)}")
            for obj_name, frames in object_keyframes.items():
                print(f"  {obj_name}: {frames}")
            print(f"Total unique keyframes found: {len(keyframes)}")
            print(f"All keyframes: {sorted(list(keyframes))}")
            print(f"Filtered keyframes: {sorted(list(filtered_keyframes))}")
            
            if filtered_keyframes:
                # Sort keyframes and create comma-separated string
                sorted_keyframes = sorted(list(filtered_keyframes))
                keyframe_string = ','.join(map(str, sorted_keyframes))
                
                # Store keyframes in the window manager to persist across operator calls
                bpy.types.WindowManager.suggested_keyframes = keyframe_string
                
                range_info = f" (limited to range {frame_start}-{frame_end})" if filter_source == "existing frame list" else ""
                self.report({'INFO'}, f"Found {len(sorted_keyframes)} keyframes from {len(object_keyframes)} objects{range_info}: {keyframe_string[:80]}{'...' if len(keyframe_string) > 80 else ''}")
                
                return {'FINISHED'}
            else:
                range_info = f" in range {frame_start}-{frame_end}" if filter_source == "existing frame list" else ""
                self.report({'WARNING'}, f"No keyframes found{range_info}")
                return {'CANCELLED'}
        
        finally:
            # Restore original frame
            scene.frame_set(original_frame)


class RENDER_PT_specific_frames_panel(Panel):
    """Panel for rendering specific frames"""
    bl_label = "Render Specific Frames"
    bl_idname = "RENDER_PT_specific_frames"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw(self, context):
        global output_folder_path
        layout = self.layout

        # Header/info
        box = layout.box()
        box.label(text="Render Specific Frames Tool", icon='RENDER_ANIMATION')
        box.label(text="Step 1: Set output folder (optional)")
        box.label(text="Step 2: Choose frames to render")

        # Output folder section
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Output Folder Settings:")

        if output_folder_path:
            col.label(text=f"Current: {os.path.basename(output_folder_path)}", icon='FOLDER_REDIRECT')
            col.label(text=f"Path: {output_folder_path}")
            col.label(text="(Loaded from user preferences)", icon='DISK_DRIVE')
        else:
            col.label(text="Current: (Blend file directory)", icon='FOLDER_REDIRECT')
            col.label(text="(No default folder set)", icon='INFO')

        col.operator("render.set_output_folder", text="Set Output Folder", icon='FILE_FOLDER')

        # Rendering section
        layout.separator()
        layout.label(text="Render Frames:")
        layout.operator("render.specific_frames", text="Render Specific Frames", icon='RENDER_STILL')
        layout.operator("render.current_frame", text="Render Current Frame", icon='RENDER_STILL')
        layout.operator("render.open_output_folder", text="Open Rendered Frame Result", icon='IMAGE_DATA')
        layout.prop(context.scene, "copy_render_to_clipboard", text="Copy rendered image to clipboard (alpha)")
        
        # Debug section
        layout.separator()
        layout.label(text="Debug Tools:")
        layout.operator("render.copy_to_clipboard", text="Copy Render Result to Clipboard", icon='COPYDOWN')

        # Tips
        layout.separator()
        tips = layout.column(align=True)
        tips.label(text="Tips:")
        tips.label(text="• Default folder is automatically loaded from preferences")
        tips.label(text="• Set output folder to save as new default")
        tips.label(text="• Enter frames separated by commas")
        tips.label(text="• Single frames: 1,5,10,25,50")
        tips.label(text="• Ranges: 1-5,10-15,30 (inclusive)")
        tips.label(text="• Mixed: 1,5-10,15,20-25")
        tips.label(text="• Duplicates will be removed")
        tips.label(text="• Output format: [blendname]_frame_XXXX")


def register():
    bpy.utils.register_class(RENDER_OT_set_output_folder)
    bpy.utils.register_class(RENDER_OT_specific_frames)
    bpy.utils.register_class(RENDER_OT_current_frame)
    bpy.utils.register_class(RENDER_OT_copy_to_clipboard)
    bpy.utils.register_class(RENDER_OT_open_output_folder)
    bpy.utils.register_class(RENDER_OT_suggest_keyframes)
    bpy.utils.register_class(RENDER_PT_specific_frames_panel)
    # Scene property for clipboard toggle
    bpy.types.Scene.copy_render_to_clipboard = bpy.props.BoolProperty(
        name="Copy Render To Clipboard",
        description="After rendering, copy the Render Result to system clipboard (Windows only)",
        default=False,
    )


def unregister():
    bpy.utils.unregister_class(RENDER_OT_set_output_folder)
    bpy.utils.unregister_class(RENDER_OT_specific_frames)
    bpy.utils.unregister_class(RENDER_OT_current_frame)
    bpy.utils.unregister_class(RENDER_OT_copy_to_clipboard)
    bpy.utils.unregister_class(RENDER_OT_open_output_folder)
    bpy.utils.unregister_class(RENDER_OT_suggest_keyframes)
    bpy.utils.unregister_class(RENDER_PT_specific_frames_panel)
    # Remove Scene property
    if hasattr(bpy.types.Scene, 'copy_render_to_clipboard'):
        del bpy.types.Scene.copy_render_to_clipboard


if __name__ == "__main__":
    register()


