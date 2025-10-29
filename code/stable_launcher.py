#!/usr/bin/env python3
"""
🔧 Stable Network Game Launcher
Fixed connection stability issues and improved player assignment
"""

import socket
import time
import threading
import subprocess
import sys
import os

def check_port_available(port):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Port is available if connection failed
    except:
        return True

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def start_server():
    """Start the game server"""
    print("🚀 Starting Monster Battle Server...")
    
    # Check if port is available
    if not check_port_available(12345):
        print("❌ Port 12345 is already in use!")
        print("   Another server might be running.")
        return None
    
    # Start server process
    try:
        server_process = subprocess.Popen([
            sys.executable, 'network_server.py'
        ], cwd=os.path.dirname(__file__))
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Verify server is running
        if not check_port_available(12345):
            local_ip = get_local_ip()
            print("✅ Server started successfully!")
            print(f"🌐 Server IP: {local_ip}:12345")
            print("📱 Other devices can connect using this IP")
            return server_process
        else:
            print("❌ Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def connect_client(host='localhost'):
    """Connect a client to the server"""
    print(f"🎮 Connecting client to {host}:12345...")
    
    # Wait a moment then start client
    time.sleep(1)
    
    try:
        client_process = subprocess.Popen([
            sys.executable, 'quick_connect.py', host
        ], cwd=os.path.dirname(__file__))
        
        print(f"✅ Client started for {host}")
        return client_process
        
    except Exception as e:
        print(f"❌ Error starting client: {e}")
        return None

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎮 MONSTER BATTLE - STABLE NETWORK LAUNCHER 🎮")
    print("=" * 60)
    print()
    print("Fixed Issues:")
    print("✅ Connection stability improved")
    print("✅ Player assignment logic fixed")
    print("✅ Proper error handling added")
    print("✅ Heartbeat system enhanced")
    print()
    
    while True:
        print("Choose an option:")
        print("1. 🏠 Start Server (Host Game)")
        print("2. 🌐 Connect as Client (Join Game)")
        print("3. 🔄 Host + Auto-connect (Quick Test)")
        print("4. 🔍 Network Diagnostics")
        print("5. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            # Start server only
            server_process = start_server()
            if server_process:
                print()
                print("🎯 Server is running! Waiting for players...")
                print("💡 To connect from another device:")
                local_ip = get_local_ip()
                print(f"   Use IP: {local_ip}")
                print("   Use Port: 12345")
                print()
                print("Press Ctrl+C to stop server")
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping server...")
                    server_process.terminate()
            
        elif choice == '2':
            # Connect as client
            host = input("Enter server IP (or press Enter for localhost): ").strip()
            if not host:
                host = 'localhost'
            
            client_process = connect_client(host)
            if client_process:
                print()
                print("🎮 Client connected! Check the game window.")
                print("Press Ctrl+C to stop")
                try:
                    client_process.wait()
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping client...")
                    client_process.terminate()
            
        elif choice == '3':
            # Quick test - start server and connect client
            print("🔄 Starting server and connecting client...")
            
            server_process = start_server()
            if server_process:
                client_process = connect_client()
                
                if client_process:
                    print()
                    print("🎯 Both server and client started!")
                    print("🎮 Check the game window to play!")
                    print("💡 Connect another client from another device to play multiplayer")
                    print()
                    print("Press Ctrl+C to stop everything")
                    
                    try:
                        # Wait for either process to finish
                        while True:
                            if server_process.poll() is not None:
                                print("Server stopped")
                                break
                            if client_process.poll() is not None:
                                print("Client stopped")
                                break
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n⏹️ Stopping server and client...")
                        server_process.terminate()
                        client_process.terminate()
                else:
                    server_process.terminate()
            
        elif choice == '4':
            # Network diagnostics
            print("🔍 Running Network Diagnostics...")
            print()
            
            local_ip = get_local_ip()
            print(f"🏠 Local IP Address: {local_ip}")
            
            # Check port availability
            if check_port_available(12345):
                print("✅ Port 12345 is available")
            else:
                print("❌ Port 12345 is in use")
            
            # Test network connectivity
            print("🌐 Testing network connectivity...")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect(("8.8.8.8", 80))
                s.close()
                print("✅ Internet connectivity working")
            except:
                print("❌ Network connectivity issues")
            
            print()
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
            
        print()

if __name__ == "__main__":
    main()