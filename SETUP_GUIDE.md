# Monster Battle - Setup Instructions

## 🎮 Quick Start for Network Play

### First-Time Setup (Required on BOTH devices):

#### Option A: Automatic Setup (Windows)
1. Double-click `setup.bat`
2. Follow the installation prompts

#### Option B: Manual Setup (Any OS)
1. Make sure Python 3.6+ is installed
2. Open terminal/command prompt
3. Run: `python -m pip install pygame`

### Playing the Game:

#### Device 1 (Host):
1. Run `start_game.bat`
2. Choose option `1` (Start Server)
3. Note the IP address shown (e.g., 192.168.1.100)
4. Share this IP with the other player

#### Device 2 (Guest):
1. Run `start_game.bat` 
2. Choose option `2` (Start Client)
3. Enter the host's IP address when prompted

## 🔧 Troubleshooting

### "No module named pygame" Error:
- **Solution**: Run `setup.bat` or manually install pygame:
  ```
  python -m pip install pygame
  ```

### "getaddrinfo failed" Error:
- **Solution**: Use IP address instead of hostname
- Run option `4` (Network Diagnostics) to find the correct IP

### Connection Refused:
- Make sure the server is running first
- Check both devices are on the same WiFi network
- Try disabling Windows Firewall temporarily

### Finding the Server:
- Run option `4` (Network Diagnostics) - it will scan for servers
- Server shows its IP when it starts
- Use `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to find IP

## 📁 File Structure

```
Monster-battle/
├── setup.bat              # Windows setup script
├── setup.py               # Cross-platform setup  
├── start_game.bat         # Main launcher
├── requirements.txt       # Python dependencies
└── code/
    ├── network_server.py  # Game server
    ├── network_game.py    # Network client
    ├── network_diagnostics.py # Network tools
    ├── check_dependencies.py # Dependency checker
    └── [other game files]
```

## 🎯 Game Features

### Special Moves (One-time use):
- 🌱 **Plant**: Reflect Shield - reflects next attack
- 💧 **Water**: Healing Wave - heals 80 HP
- 🔥 **Fire**: Burning Fury - damage + burn effect

### Status Effects:
- 🛡️ **Shield**: Reflects one attack
- 🔥 **Burn**: Damage over time (2 turns)

## 💡 Tips

1. **Always start the server first** before connecting clients
2. **Use the actual IP address** shown by the server
3. **Keep the server window open** during the game
4. **Both players need pygame installed**
5. **Use Network Diagnostics** to troubleshoot connection issues

Need help? Check the console output for error messages and solutions!