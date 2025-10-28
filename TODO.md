# TODO List for Monster Battle Updates

## 1. Remove Attack Sound Effects
- [ ] Comment out sound.play() in ui.py (around line 200)
- [ ] Comment out sound.play() in animation.py (around line 50)

## 2. Balance Abilities and Add Fighting Type
- [ ] Update ELEMENT_DATA in settings.py to add 'fighting' type (fighting weak to plant, strong vs normal)
- [ ] Balance ABILITIES_DATA damages in settings.py

## 3. Implement Team Selection
- [ ] Modify selection_screen.py to select 3 monsters each, alternating turns
- [ ] Update setup_cards to handle team selection

## 4. Update Battle Logic for Teams
- [ ] Modify battle_engine.py to handle lists of monsters instead of single monsters
- [ ] Add logic to switch to next monster when current HP <= 0
- [ ] End game when one player's team is exhausted

## 5. Update Main Game Logic
- [ ] Modify main.py to initialize teams (lists of 3 monsters each) instead of single monsters
- [ ] Update loading screen and game initialization for teams

## 6. Update UI for Teams
- [ ] Modify ui.py to show current active monster and team status
- [ ] Add team HP indicators or bars
- [ ] Update health display for current monster

## Followup Steps
- [ ] Test selection screen for team selection
- [ ] Test battle flow with monster switching
- [ ] Ensure UI updates correctly for teams
- [ ] Verify sound effects are removed
- [ ] Verify type balancing and fighting type
