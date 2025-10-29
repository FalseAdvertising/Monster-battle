import socket
import threading
import json
import time
from settings import *

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Game state
        self.players = {}  # {player_id: {'socket': socket, 'monster': None, 'ready': False}}
        self.game_state = 'waiting'  # 'waiting', 'selection', 'battle', 'finished'
        self.current_turn = 1
        self.moves = {}  # {player_id: move_name}
        self.running = True
        
        # Get and display local IP
        self.local_ip = self.get_local_ip()
        print(f"Server starting on {host}:{port}")
        print(f"Local IP address: {self.local_ip}")
        print(f"Other devices can connect using: {self.local_ip}:{port}")
        
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
        
    def start(self):
        """Start the server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(2)  # Only allow 2 players
            print("=" * 50)
            print(f"🚀 Monster Battle Server Started!")
            print(f"🌐 Listening on: {self.host}:{self.port}")
            print(f"🏠 Local IP: {self.local_ip}:{self.port}")
            print("=" * 50)
            print("📱 For other devices to connect, use:")
            print(f"   IP Address: {self.local_ip}")
            print(f"   Port: {self.port}")
            print("=" * 50)
            print("⏳ Waiting for players to connect...")
            
            while self.running and len(self.players) < 2:
                try:
                    client_socket, address = self.socket.accept()
                    
                    # Assign player ID based on current players
                    available_ids = [1, 2]
                    for existing_id in self.players.keys():
                        if existing_id in available_ids:
                            available_ids.remove(existing_id)
                    
                    if not available_ids:
                        print(f"⚠️ Connection from {address[0]}:{address[1]} rejected - server full")
                        client_socket.close()
                        continue
                    
                    player_id = available_ids[0]
                    
                    # Set socket options immediately
                    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    client_socket.settimeout(None)  # Remove timeout for normal operation
                    
                    self.players[player_id] = {
                        'socket': client_socket,
                        'address': address,
                        'monster': None,
                        'ready': False,
                        'health': 0,
                        'max_health': 0,
                        'shield_active': False,
                        'burn_turns': 0,
                        'special_used': False
                    }
                    
                    print(f"🎮 Player {player_id} connected from {address[0]}:{address[1]}")
                    
                    # Send player ID immediately
                    welcome_msg = {
                        'type': 'player_id',
                        'player_id': player_id,
                        'status': 'connected'
                    }
                    
                    if self.send_to_player(player_id, welcome_msg):
                        print(f"✅ Sent welcome message to Player {player_id}")
                        
                        # Start thread to handle this client AFTER successful welcome
                        thread = threading.Thread(target=self.handle_client, args=(player_id,))
                        thread.daemon = True
                        thread.start()
                        
                        if len(self.players) == 2:
                            print("🎯 Both players connected! Starting game...")
                            self.game_state = 'selection'
                            self.broadcast({
                                'type': 'game_start',
                                'message': 'Both players connected! Select your monsters.'
                            })
                    else:
                        print(f"❌ Failed to send welcome to Player {player_id}, disconnecting")
                        self.disconnect_player(player_id)
                        
                except Exception as e:
                    print(f"❌ Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.cleanup()
            
    def handle_client(self, player_id):
        """Handle messages from a specific client"""
        client_socket = self.players[player_id]['socket']
        
        try:
            # Set socket options for better connection stability
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            while self.running:
                try:
                    # Use a reasonable timeout to detect disconnections
                    client_socket.settimeout(60)  # 60 second timeout
                    data = client_socket.recv(1024).decode('utf-8')
                    
                    if not data:
                        print(f"Player {player_id} disconnected (no data)")
                        break
                        
                    try:
                        message = json.loads(data)
                        self.process_message(player_id, message)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from player {player_id}: {data}")
                        
                except socket.timeout:
                    # Check if client is still connected with a ping
                    try:
                        client_socket.send(b'{"type":"ping"}\n')
                        print(f"Sent ping to player {player_id}")
                    except:
                        print(f"Player {player_id} timed out and is unreachable")
                        break
                        
                except ConnectionResetError:
                    print(f"Player {player_id} connection was reset")
                    break
                except ConnectionAbortedError:
                    print(f"Player {player_id} connection was aborted")
                    break
                    
        except Exception as e:
            print(f"Error handling player {player_id}: {e}")
        finally:
            self.disconnect_player(player_id)
            
    def process_message(self, player_id, message):
        """Process incoming message from player"""
        msg_type = message.get('type')
        
        if msg_type == 'player_join':
            # Client is confirming connection
            print(f"✅ Player {player_id} confirmed connection with handshake")
            
        elif msg_type == 'ping':
            # Respond to client ping
            self.send_to_player(player_id, {'type': 'pong'})
            
        elif msg_type == 'pong':
            # Client responded to our ping
            print(f"Player {player_id} responded to ping")
            
        elif msg_type == 'monster_selection':
            monster_name = message.get('monster')
            if monster_name in MONSTER_DATA:
                self.players[player_id]['monster'] = monster_name
                monster_data = MONSTER_DATA[monster_name]
                self.players[player_id]['health'] = monster_data['health']
                self.players[player_id]['max_health'] = monster_data['health']
                self.players[player_id]['ready'] = True
                
                print(f"Player {player_id} selected {monster_name}")
                
                # Check if both players have selected
                if all(p['ready'] for p in self.players.values()):
                    self.start_battle()
                    
        elif msg_type == 'move_selection':
            if self.game_state == 'battle':
                move = message.get('move')
                self.moves[player_id] = move
                print(f"Player {player_id} selected move: {move}")
                
                # Check if both players have selected moves
                if len(self.moves) == 2:
                    self.execute_turn()
                    
        elif msg_type == 'ping':
            self.send_to_player(player_id, {'type': 'pong'})
            
    def start_battle(self):
        """Start the battle phase"""
        self.game_state = 'battle'
        
        # Send battle start info to both players
        battle_info = {
            'type': 'battle_start',
            'players': {}
        }
        
        for pid, player in self.players.items():
            battle_info['players'][pid] = {
                'monster': player['monster'],
                'health': player['health'],
                'max_health': player['max_health']
            }
            
        self.broadcast(battle_info)
        print("Battle started!")
        
    def execute_turn(self):
        """Execute a turn with both players' moves"""
        print(f"\n--- Turn {self.current_turn} ---")
        
        # Apply burn damage first
        for pid, player in self.players.items():
            if player['burn_turns'] > 0:
                burn_damage = max(1, player['max_health'] // 10)
                player['health'] -= burn_damage
                player['burn_turns'] -= 1
                print(f"Player {pid} takes {burn_damage} burn damage ({player['burn_turns']} turns left)")
                
                if player['health'] <= 0:
                    player['health'] = 0
                    self.end_battle(3 - pid)  # Other player wins
                    return
        
        # Determine turn order (alternating)
        if self.current_turn % 2 == 1:
            first_player, second_player = 1, 2
        else:
            first_player, second_player = 2, 1
            
        # Execute moves in order
        for attacker_id in [first_player, second_player]:
            if attacker_id not in self.moves:
                continue
                
            defender_id = 3 - attacker_id  # 1->2, 2->1
            move = self.moves[attacker_id]
            
            result = self.execute_move(attacker_id, defender_id, move)
            
            # Check for winner
            if self.players[defender_id]['health'] <= 0:
                self.end_battle(attacker_id)
                return
            elif self.players[attacker_id]['health'] <= 0:  # Reflected damage
                self.end_battle(defender_id)
                return
        
        # Send updated game state
        self.send_game_state()
        
        # Clear moves for next turn
        self.moves.clear()
        self.current_turn += 1
        
    def execute_move(self, attacker_id, defender_id, move):
        """Execute a single move"""
        if move not in ABILITIES_DATA:
            return
            
        move_data = ABILITIES_DATA[move]
        attacker = self.players[attacker_id]
        defender = self.players[defender_id]
        
        # Handle special moves
        if move_data.get('type') == 'special':
            if attacker['special_used']:
                print(f"Player {attacker_id} already used their special move!")
                return
                
            attacker['special_used'] = True
            
            if move == 'reflect_shield':
                attacker['shield_active'] = True
                print(f"Player {attacker_id} activates Reflect Shield!")
                
            elif move == 'healing_wave':
                heal_amount = abs(move_data['damage'])
                old_health = attacker['health']
                attacker['health'] = min(attacker['max_health'], attacker['health'] + heal_amount)
                healed = attacker['health'] - old_health
                print(f"Player {attacker_id} heals for {healed} HP!")
                
            elif move == 'burning_fury':
                damage = self.calculate_damage(attacker_id, defender_id, move_data)
                reflected = self.apply_damage(attacker_id, defender_id, damage)
                defender['burn_turns'] = 2
                print(f"Player {attacker_id} uses Burning Fury! Player {defender_id} is burned!")
                
        else:
            # Regular move
            damage = self.calculate_damage(attacker_id, defender_id, move_data)
            reflected = self.apply_damage(attacker_id, defender_id, damage)
            print(f"Player {attacker_id} uses {move} for {damage} damage!")
            
    def calculate_damage(self, attacker_id, defender_id, move_data):
        """Calculate damage with type effectiveness"""
        attacker_monster = self.players[attacker_id]['monster']
        defender_monster = self.players[defender_id]['monster']
        
        base_damage = move_data['damage']
        move_element = move_data['element']
        
        # Get type effectiveness
        attacker_element = MONSTER_DATA[attacker_monster]['element']
        defender_element = MONSTER_DATA[defender_monster]['element']
        
        effectiveness = 1.0
        if move_element in ELEMENT_DATA and defender_element in ELEMENT_DATA[move_element]:
            effectiveness = ELEMENT_DATA[move_element][defender_element]
        
        # Get stats
        attack_stat = MONSTER_DATA[attacker_monster]['attack']
        defense_stat = MONSTER_DATA[defender_monster]['defense']
        
        # Calculate final damage
        damage = int(base_damage * effectiveness * (attack_stat / defense_stat))
        return max(1, damage)
        
    def apply_damage(self, attacker_id, defender_id, damage):
        """Apply damage, handling shield reflection"""
        defender = self.players[defender_id]
        attacker = self.players[attacker_id]
        
        # Check shield
        if defender['shield_active'] and damage > 0:
            print(f"Player {defender_id}'s shield reflects {damage} damage!")
            defender['shield_active'] = False
            attacker['health'] -= damage
            if attacker['health'] < 0:
                attacker['health'] = 0
            return True
        else:
            defender['health'] -= damage
            if defender['health'] < 0:
                defender['health'] = 0
            return False
            
    def send_game_state(self):
        """Send current game state to both players"""
        state = {
            'type': 'game_state',
            'turn': self.current_turn,
            'players': {}
        }
        
        for pid, player in self.players.items():
            state['players'][pid] = {
                'health': player['health'],
                'max_health': player['max_health'],
                'shield_active': player['shield_active'],
                'burn_turns': player['burn_turns'],
                'special_used': player['special_used']
            }
            
        self.broadcast(state)
        
    def end_battle(self, winner_id):
        """End the battle"""
        self.game_state = 'finished'
        self.broadcast({
            'type': 'battle_end',
            'winner': winner_id,
            'winner_monster': self.players[winner_id]['monster']
        })
        print(f"Battle ended! Player {winner_id} wins!")
        
    def send_to_player(self, player_id, message):
        """Send message to specific player"""
        if player_id not in self.players:
            print(f"Cannot send to player {player_id}: player not found")
            return False
            
        try:
            data = json.dumps(message) + '\n'
            self.players[player_id]['socket'].send(data.encode('utf-8'))
            return True
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print(f"Player {player_id} connection lost while sending message")
            self.disconnect_player(player_id)
            return False
        except Exception as e:
            print(f"Error sending to player {player_id}: {e}")
            return False
            
    def broadcast(self, message):
        """Send message to all connected players"""
        disconnected_players = []
        for player_id in list(self.players.keys()):
            if not self.send_to_player(player_id, message):
                disconnected_players.append(player_id)
        
        # Clean up disconnected players
        for player_id in disconnected_players:
            if player_id in self.players:
                self.disconnect_player(player_id)
            
    def disconnect_player(self, player_id):
        """Handle player disconnection"""
        if player_id in self.players:
            print(f"Player {player_id} disconnected")
            try:
                self.players[player_id]['socket'].close()
            except:
                pass
            del self.players[player_id]
            
            # Notify other player
            if self.players:
                self.broadcast({
                    'type': 'player_disconnected',
                    'player_id': player_id
                })
                
    def cleanup(self):
        """Clean up server resources"""
        self.running = False
        for player in self.players.values():
            try:
                player['socket'].close()
            except:
                pass
        try:
            self.socket.close()
        except:
            pass
        print("Server shut down")

def start_server():
    """Start the game server"""
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.cleanup()

if __name__ == '__main__':
    start_server()