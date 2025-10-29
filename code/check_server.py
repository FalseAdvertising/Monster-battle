#!/usr/bin/env python3
import socket
import sys

def check_server(host='localhost', port=12345):
    """Check if the Monster Battle server is running"""
    print(f"Checking server at {host}:{port}...")
    
    try:
        # Create a socket and try to connect
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(5)  # 5 second timeout
        
        result = test_socket.connect_ex((host, port))
        test_socket.close()
        
        if result == 0:
            print(f"✅ Server is running at {host}:{port}")
            return True
        else:
            print(f"❌ No server found at {host}:{port}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    print("=== Monster Battle Server Checker ===")
    print()
    
    # Check localhost first
    if check_server():
        print("Server is ready for connections!")
    else:
        print("Server is not running.")
        print()
        print("To start the server:")
        print("1. Run: python network_server.py")
        print("2. Or use the Network Launcher")
        print()
        
        # Ask for custom IP to check
        try:
            custom_ip = input("Enter IP to check (or press Enter to exit): ").strip()
            if custom_ip:
                check_server(custom_ip)
        except KeyboardInterrupt:
            print("\nExiting...")
    
    print()
    input("Press Enter to exit...")

if __name__ == '__main__':
    main()