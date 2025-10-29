# Monster Battle - Network Multiplayer

## Overview
This Monster Battle game now supports network multiplayer, allowing two players to connect from separate devices on the same local network (LAN).

## How to Play Network Multiplayer

### Option 1: Using the Network Launcher (Recommended)
1. Run `start_network.bat` or `python code/network_launcher.py`
2. Choose your option:
   - **Host Game**: Start a server and automatically connect as Player 1
   - **Join Game**: Connect to an existing server as Player 2
   - **Local Game**: Play the original single-computer version

### Option 2: Manual Setup

#### For the Host (Player 1):
1. Open Command Prompt/Terminal
2. Navigate to the game folder
3. Run: `python code/network_server.py`
4. Note the IP address shown (e.g., 192.168.1.100:12345)
5. In another terminal, run: `python code/network_game.py`
6. Enter "localhost" when prompted for server IP

#### For the Guest (Player 2):
1. Get the host's IP address
2. Run: `python code/network_game.py`
3. Enter the host's IP address when prompted

## Network Features

### Special Moves (Balanced for Network Play)
- **Plant Monsters**: Reflect Shield - Creates a shield that reflects the next attack back to the attacker
- **Water Monsters**: Healing Wave - Heals the monster for 80 HP
- **Fire Monsters**: Burning Fury - Deals damage and applies burn effect for 2 turns

### Status Effects
- **Shield**: Shows with 🛡️ icon, reflects one attack
- **Burn**: Shows with 🔥 icon, deals damage each turn

### Game Flow
1. **Connection**: Both players connect to the server
2. **Monster Selection**: Each player selects their monster
3. **Battle**: Turn-based combat with move selection
4. **Results**: Winner announcement

## Technical Requirements
- Python 3.6+
- Pygame library
- Network connection (same LAN/WiFi network)

## Network Configuration
- Default port: 12345
- Server binds to all interfaces (0.0.0.0)
- Supports exactly 2 players
- Automatic disconnection handling

## Troubleshooting

### Connection Issues
- Ensure both devices are on the same network
- Check if port 12345 is blocked by firewall
- Try using IP address instead of hostname

### Firewall Settings
If having connection issues, you may need to allow Python through your firewall:
- Windows: Windows Defender Firewall → Allow an app
- Add Python.exe to allowed applications

### Finding Your IP Address
- Windows: `ipconfig` in Command Prompt
- Mac/Linux: `ifconfig` in Terminal
- Look for your local network IP (usually 192.168.x.x or 10.x.x.x)

## Files Added for Network Play
- `network_server.py` - Game server handling both players
- `network_client.py` - Client connection handling
- `network_game.py` - Network version of the game
- `network_launcher.py` - GUI launcher for easy setup
- `start_network.bat` - Quick launch script for Windows

## Game Balance Changes
- Special moves are one-time use only
- Burn damage is 10% of max health per turn
- Shield reflects full damage once
- Healing restores 80 HP (balanced across monster types)

Enjoy battling with your friends across the network! 🎮