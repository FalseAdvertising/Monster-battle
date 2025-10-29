#!/usr/bin/env python3
import socket
import subprocess
import sys
import platform

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unknown"

def ping_host(host):
    """Ping a host to see if it's reachable"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '1', '-w', '3000', host], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                  capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_port(host, port):
    """Check if a specific port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def resolve_hostname(hostname):
    """Try to resolve a hostname to IP"""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror as e:
        return None, str(e)

def scan_local_network():
    """Scan for Monster Battle servers on local network"""
    local_ip = get_local_ip()
    if local_ip == "Unknown":
        return []
        
    # Get network prefix (e.g., 192.168.1.)
    ip_parts = local_ip.split('.')
    network_prefix = '.'.join(ip_parts[:3]) + '.'
    
    print(f"Scanning network {network_prefix}x for servers...")
    servers_found = []
    
    for i in range(1, 255):
        test_ip = network_prefix + str(i)
        if check_port(test_ip, 12345):
            servers_found.append(test_ip)
            print(f"Found server at: {test_ip}")
    
    return servers_found

def main():
    print("=== Monster Battle Network Diagnostics ===")
    print()
    
    # Show local network info
    local_ip = get_local_ip()
    print(f"Your IP address: {local_ip}")
    print()
    
    # Test common scenarios
    print("Testing network connectivity...")
    print()
    
    # Test localhost
    print("1. Testing localhost...")
    localhost_works = check_port('localhost', 12345)
    print(f"   localhost:12345 - {'✅ OPEN' if localhost_works else '❌ CLOSED'}")
    
    # Test 127.0.0.1
    print("2. Testing 127.0.0.1...")
    loopback_works = check_port('127.0.0.1', 12345)
    print(f"   127.0.0.1:12345 - {'✅ OPEN' if loopback_works else '❌ CLOSED'}")
    
    # Test local IP
    print(f"3. Testing your local IP ({local_ip})...")
    local_ip_works = check_port(local_ip, 12345)
    print(f"   {local_ip}:12345 - {'✅ OPEN' if local_ip_works else '❌ CLOSED'}")
    
    print()
    
    if localhost_works or loopback_works or local_ip_works:
        print("✅ Local server is running!")
        print(f"Other devices can connect using: {local_ip}")
    else:
        print("❌ No local server found.")
        print("Make sure the server is running first.")
        print()
        
        # Scan for servers on network
        print("Scanning for servers on your network...")
        servers = scan_local_network()
        
        if servers:
            print("Found Monster Battle servers at:")
            for server in servers:
                print(f"  - {server}:12345")
        else:
            print("No servers found on your network.")
    
    print()
    
    # Get user input for custom testing
    while True:
        try:
            test_host = input("Enter hostname/IP to test (or press Enter to exit): ").strip()
            if not test_host:
                break
                
            print(f"\nTesting {test_host}...")
            
            # Try to resolve hostname
            if not test_host.replace('.', '').isdigit():  # If it's not an IP
                resolved_ip, error = resolve_hostname(test_host)
                if resolved_ip:
                    print(f"   Resolved to: {resolved_ip}")
                    test_host = resolved_ip
                else:
                    print(f"   ❌ DNS resolution failed: {error}")
                    continue
            
            # Test ping
            if ping_host(test_host):
                print(f"   ✅ Ping successful")
            else:
                print(f"   ❌ Ping failed")
            
            # Test port
            if check_port(test_host, 12345):
                print(f"   ✅ Port 12345 is open")
                print(f"   You can connect using: {test_host}")
            else:
                print(f"   ❌ Port 12345 is closed/blocked")
            
            print()
            
        except KeyboardInterrupt:
            break
    
    print("Diagnostics complete!")

if __name__ == '__main__':
    main()