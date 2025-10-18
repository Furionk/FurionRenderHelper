# Bug Fix: View Layer Access Error

## Issue
Users encountered an AttributeError when the extension tried to access `scene.view_layers.active`:

```
AttributeError: bpy_prop_collection: attribute "active" not found
```

## Root Cause
The Blender API doesn't have an `active` property on the `view_layers` collection. The correct way to access view layers is through indexing.

## Solution
Changed from:
```python
view_layer = scene.view_layers.active  # ❌ Incorrect
```

To:
```python
view_layer = scene.view_layers[0] if scene.view_layers else None  # ✅ Correct
```

## Additional Safety
Added fallback logic:
- If no view layers exist, defaults to Combined channel only
- Prevents crashes in edge cases
- Maintains functionality in all scenarios

## Status
✅ **Fixed in v1.3.0**  
📦 Updated package: `furion_render_helper_v1.3.0_20251018.zip`  
🔧 Build size: 19,837 bytes  

The extension now properly accesses view layers and should work without errors in all Blender scenes!