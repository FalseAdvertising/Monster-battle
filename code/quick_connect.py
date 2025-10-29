#!/usr/bin/env python3
"""
Quick launcher that automatically opens the game window and connects
"""

import pygame
import sys
from network_game import NetworkGame, get_server_ip, check_server_running

def quick_connect():
    """Quick connect with automatic window opening"""
    print("=== Monster Battle - Quick Connect ===")
    print()
    
    # Initialize pygame early to show window
    pygame.init()
    
    # Get server info
    while True:
        print("Quick connect options:")
        print("1. Connect to localhost")
        print("2. Enter custom IP")
        print("3. Exit")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == '1':
            server_ip = 'localhost'
            break
        elif choice == '2':
            server_ip = input("Enter server IP: ").strip()
            if server_ip:
                break
        elif choice == '3':
            return
        else:
            print("Invalid choice!")
            continue
    
    # Check server before starting pygame
    print(f"Checking server at {server_ip}:12345...")
    if not check_server_running(server_ip, 12345):
        print(f"❌ No server found at {server_ip}:12345")
        print("Make sure the server is running first!")
        input("Press Enter to exit...")
        return
    
    print("✅ Server found! Opening game...")
    
    # Start the game immediately
    try:
        game = NetworkGame(server_ip)
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        input("Press Enter to exit...")
    finally:
        pygame.quit()

if __name__ == '__main__':
    try:
        quick_connect()
    except KeyboardInterrupt:
        print("\nCancelled by user")
        pygame.quit()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        pygame.quit()