# Monster Battle Game Enhancements TODO

## Dynamic Sprite Positioning
- [x] Modify main.py to add dynamic scaling logic after UI creation
- [x] Check if sprite height exceeds panel_top - threshold
- [x] Scale down sprites proportionally if needed
- [x] Adjust midbottom position for both players

## Loading Animation
- [x] Create LoadingScreen class in main.py
- [x] Implement fading monster sprites animation
- [x] Add spooky audio playback during loading
- [x] Stop audio when battle starts
- [x] Integrate loading screen between selection and battle

## UI Background Textures
- [x] Update ui.py to load Player-Select-BG.jpg for UI panel backgrounds
- [x] Keep Wood_sign2.png for ability buttons
- [x] Enhance player label visibility (increase font size to 48, add glow effect)

## Testing
- [x] Test dynamic scaling and positioning for both player sprites
- [x] Verify loading animation plays with audio and transitions to battle
- [x] Confirm UI background changes and improved label visibility
- [x] Test turn execution animation and state transitions
