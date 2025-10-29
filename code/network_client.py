import socket
import threading
import json
import time
import pygame
from settings import *

class NetworkClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.player_id = None
        
        # Game state
        self.game_state = 'waiting'  # 'waiting', 'selection', 'battle', 'finished'
        self.players = {}
        self.my_monster = None
        self.opponent_monster = None
        self.turn = 1
        self.waiting_for_move = False
        
        # Message queue for main thread
        self.message_queue = []
        self.queue_lock = threading.Lock()
        
        # Heartbeat system
        self.last_heartbeat = threading.Event()
        self.heartbeat_thread = None
        
    def connect(self):
        """Connect to the game server"""
        try:
            print(f"Attempting to connect to {self.host}:{self.port}...")
            
            # First, try to resolve the hostname
            try:
                resolved_ip = socket.gethostbyname(self.host)
                print(f"Resolved {self.host} to {resolved_ip}")
            except socket.gaierror as e:
                print(f"DNS resolution failed for {self.host}: {e}")
                print("This could mean:")
                print("1. The hostname is incorrect")
                print("2. DNS is not working properly")
                print("3. Try using an IP address instead")
                return False
            
            # Test connection first with a timeout
            print(f"Testing connection to {resolved_ip}:{self.port}...")
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(5)
            result = test_socket.connect_ex((resolved_ip, self.port))
            test_socket.close()
            
            if result != 0:
                print(f"Cannot reach server at {resolved_ip}:{self.port}")
                print(f"Error code: {result}")
                print("Make sure:")
                print("1. The server is running")
                print("2. You're on the same network")
                print("3. Firewall isn't blocking the connection")
                return False
            
            # Now make the actual connection
            print(f"Connecting to {resolved_ip}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set socket options for stability
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set initial timeout for connection
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((resolved_ip, self.port))
            
            # Connection successful, remove timeout for normal operation
            self.socket.settimeout(None)
            self.connected = True
            
            # Send initial handshake message immediately
            try:
                handshake = {'type': 'player_join', 'timestamp': time.time()}
                self.send_message(handshake)
                print("Sent initial handshake to server")
            except Exception as e:
                print(f"Failed to send handshake: {e}")
                self.disconnect()
                return False
            
            # Start listening thread
            listen_thread = threading.Thread(target=self.listen_for_messages)
            listen_thread.daemon = True
            listen_thread.start()
            
            # Start heartbeat thread
            self.heartbeat_thread = threading.Thread(target=self.heartbeat_worker)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
            
            print(f"Successfully connected to server at {resolved_ip}:{self.port}")
            return True
            
        except socket.timeout:
            print(f"Connection timed out. Server at {self.host}:{self.port} may not be responding.")
            return False
        except ConnectionRefusedError:
            print(f"Connection refused. Server at {self.host}:{self.port} actively refused connection.")
            print("The server may not be running or may be full.")
            return False
        except socket.gaierror as e:
            print(f"Address resolution error: {e}")
            print(f"Could not resolve hostname: {self.host}")
            print("Try using an IP address instead of a hostname.")
            return False
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            print(f"Error type: {type(e).__name__}")
            return False
            
    def listen_for_messages(self):
        """Listen for messages from server"""
        buffer = ""
        
        try:
            # Remove timeout for continuous listening
            self.socket.settimeout(None)
            
            while self.connected:
                try:
                    data = self.socket.recv(1024).decode('utf-8')
                    if not data:
                        print("Server closed connection")
                        break
                        
                    buffer += data
                    
                    # Process complete messages (ending with newline)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                message = json.loads(line)
                                with self.queue_lock:
                                    self.message_queue.append(message)
                            except json.JSONDecodeError:
                                print(f"Invalid JSON received: {line}")
                                
                except socket.timeout:
                    # This shouldn't happen since we removed timeout, but just in case
                    continue
                except ConnectionResetError:
                    print("Connection was reset by server")
                    break
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    break
                            
        except Exception as e:
            print(f"Connection lost: {e}")
        finally:
            self.connected = False
            print("Disconnected from server")
            
    def heartbeat_worker(self):
        """Send periodic heartbeat to server"""
        import time
        
        while self.connected:
            try:
                time.sleep(30)  # Send heartbeat every 30 seconds
                if self.connected:
                    self.send_message({'type': 'ping'})
            except:
                break
            
    def process_messages(self):
        """Process messages from server (call from main thread)"""
        with self.queue_lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
            
        for message in messages:
            self.handle_message(message)
            
    def handle_message(self, message):
        """Handle incoming message from server"""
        msg_type = message.get('type')
        
        if msg_type == 'player_id':
            self.player_id = message.get('player_id')
            status = message.get('status', 'assigned')
            print(f"✅ Assigned as Player {self.player_id} (status: {status})")
            
        elif msg_type == 'game_start':
            self.game_state = 'selection'
            print("🎮 Game starting! Select your monster.")
            
        elif msg_type == 'battle_start':
            self.game_state = 'battle'
            self.players = message.get('players', {})
            
            # Determine my monster and opponent
            opponent_id = 3 - self.player_id
            self.my_monster = self.players.get(str(self.player_id), {}).get('monster')
            self.opponent_monster = self.players.get(str(opponent_id), {}).get('monster')
            
            print(f"Battle starting! You: {self.my_monster} vs Opponent: {self.opponent_monster}")
            self.waiting_for_move = True
            
        elif msg_type == 'game_state':
            self.players = message.get('players', {})
            self.turn = message.get('turn', 1)
            self.waiting_for_move = True
            print(f"Turn {self.turn} - Select your move!")
            
        elif msg_type == 'battle_end':
            winner_id = message.get('winner')
            winner_monster = message.get('winner_monster')
            self.game_state = 'finished'
            
            if winner_id == self.player_id:
                print(f"You win! {winner_monster} is victorious!")
            else:
                print(f"You lose! {winner_monster} defeated you!")
                
        elif msg_type == 'player_disconnected':
            disconnected_id = message.get('player_id')
            print(f"Player {disconnected_id} disconnected")
            
        elif msg_type == 'pong':
            pass  # Heartbeat response
            
    def send_monster_selection(self, monster_name):
        """Send monster selection to server"""
        if self.connected and self.game_state == 'selection':
            message = {
                'type': 'monster_selection',
                'monster': monster_name
            }
            self.send_message(message)
            
    def send_move_selection(self, move_name):
        """Send move selection to server"""
        if self.connected and self.game_state == 'battle' and self.waiting_for_move:
            message = {
                'type': 'move_selection',
                'move': move_name
            }
            self.send_message(message)
            self.waiting_for_move = False
            print(f"Sent move: {move_name}")
            
    def send_message(self, message):
        """Send message to server"""
        try:
            data = json.dumps(message) + '\n'
            self.socket.send(data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            
    def get_my_health(self):
        """Get my current health"""
        if str(self.player_id) in self.players:
            return self.players[str(self.player_id)].get('health', 0)
        return 0
        
    def get_my_max_health(self):
        """Get my max health"""
        if str(self.player_id) in self.players:
            return self.players[str(self.player_id)].get('max_health', 0)
        return 0
        
    def get_opponent_health(self):
        """Get opponent's current health"""
        opponent_id = str(3 - self.player_id) if self.player_id else '1'
        if opponent_id in self.players:
            return self.players[opponent_id].get('health', 0)
        return 0
        
    def get_opponent_max_health(self):
        """Get opponent's max health"""
        opponent_id = str(3 - self.player_id) if self.player_id else '1'
        if opponent_id in self.players:
            return self.players[opponent_id].get('max_health', 0)
        return 0
        
    def get_my_status_effects(self):
        """Get my status effects"""
        if str(self.player_id) in self.players:
            player = self.players[str(self.player_id)]
            return {
                'shield_active': player.get('shield_active', False),
                'burn_turns': player.get('burn_turns', 0),
                'special_used': player.get('special_used', False)
            }
        return {'shield_active': False, 'burn_turns': 0, 'special_used': False}
        
    def get_opponent_status_effects(self):
        """Get opponent's status effects"""
        opponent_id = str(3 - self.player_id) if self.player_id else '1'
        if opponent_id in self.players:
            player = self.players[opponent_id]
            return {
                'shield_active': player.get('shield_active', False),
                'burn_turns': player.get('burn_turns', 0),
                'special_used': player.get('special_used', False)
            }
        return {'shield_active': False, 'burn_turns': 0, 'special_used': False}
        
    def get_available_moves(self):
        """Get available moves for my monster"""
        if not self.my_monster:
            return []
            
        monster_data = MONSTER_DATA.get(self.my_monster, {})
        element = monster_data.get('element', 'normal')
        
        # Base moves
        moves = ['scratch']
        
        # Element-specific moves
        if element == 'fire':
            moves.extend(['spark', 'nuke'])
            if not self.get_my_status_effects()['special_used']:
                moves.append('burning_fury')
        elif element == 'water':
            moves.extend(['splash', 'shards'])
            if not self.get_my_status_effects()['special_used']:
                moves.append('healing_wave')
        elif element == 'plant':
            moves.extend(['spiral', 'earthquake'])
            if not self.get_my_status_effects()['special_used']:
                moves.append('reflect_shield')
                
        return moves
        
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Disconnected from server")