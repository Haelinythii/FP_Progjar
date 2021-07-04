from Command_wrapper import Command_Wrapper
import threading, time, random, pickle

class Matchroom:
    def __init__(self, roomId, playerOne, playerSocket) -> None:
        self.roomId = roomId
        self.playerOne = playerOne
        self.playerTwo = None
        self.playerSocket = {}
        self.playerSocket[playerOne.name] = playerSocket
        self.full = False
        self.end = False
        self.registered_attack = {}
        self.registered_attack[playerOne.name] = None
    
    def get_opposing_player(self, playerName):
        if playerName == self.playerOne.name:
            return self.playerTwo.name
        else:
            return self.playerOne.name

    def set_playerTwo(self, playerTwo, playerSocket):
        self.playerTwo = playerTwo
        self.playerSocket[playerTwo.name] = playerSocket
        self.full = True
        self.registered_attack[playerTwo.name] = None

    def start_thread(self):
        self.game_thread = threading.Thread(target=self.update)
        self.game_thread.start()
    
    def register_attack(self, attack_type, player):
        self.registered_attack[player.name] = attack_type

    def calculate_speed(self):
        playerOne_speed = self.playerOne.speed * random.randint(1, 3) / 2
        playerTwo_speed = self.playerTwo.speed * random.randint(1, 3) / 2
        if playerOne_speed > playerTwo_speed:
            return self.playerOne, self.playerTwo #first, second
        else:
            return self.playerTwo, self.playerOne

    def attack(self, player, player_to_be_hit):
        attacker_socket = self.playerSocket[player.name]
        defender_socket = self.playerSocket[player_to_be_hit.name]

        attack_type = self.registered_attack[player.name]
        damage = player.get_damage()
        accuracy = 0
        if attack_type == "Fist":
            accuracy = 100
        elif attack_type == "Kick":
            damage = damage * 2
            accuracy = 70
        elif attack_type == "Slash":
            damage = damage * 4
            accuracy = 40
        
        if random.randint(0, 99) < accuracy:
            is_player_dead = player_to_be_hit.take_damage_battle(damage)
            if is_player_dead[0]:
                #end
                self.game_end(player, player_to_be_hit)
            else:
                damage = is_player_dead[1]
                self.send_pickle("dealDamage", None, (damage, player_to_be_hit.hp), attacker_socket)
                self.send_pickle("takeDamage", None, (damage, player_to_be_hit.hp), defender_socket)
        else:
            self.send_pickle("missAttack", None, None, attacker_socket)
            self.send_pickle("evadeAttack", None, None, defender_socket)
            

    def game_end(self, winner, loser):
        self.end = True

        is_level_up, level = winner.add_experience(random.randint(50, 200))

        winner_socket = self.playerSocket[winner.name]
        loser_socket = self.playerSocket[loser.name]

        self.send_pickle("matchWinner", None, (loser.name, is_level_up, level), winner_socket)
        # command = Command_Wrapper("matchWinner", None, None)
        # winner_socket.send(pickle.dumps(command))

        self.send_pickle("matchLoser", None, (winner.name,), loser_socket)
        # command = Command_Wrapper("matchLoser", None, None)
        # loser_socket.send(pickle.dumps(command))

    def send_pickle(self, command, dest, args, socket):
        command_wrapper = Command_Wrapper(command, dest, args)
        p_command = pickle.dumps(command_wrapper)
        socket.send(p_command)

    def update(self):
        while True:
            time.sleep(0.1)
            if self.registered_attack[self.playerOne.name] is None or self.registered_attack[self.playerTwo.name] is None:
                continue
            else:
                first_player_to_move, second_player_to_move = self.calculate_speed()
                self.attack(first_player_to_move, second_player_to_move)

                if self.end == True:
                    break
                time.sleep(1)

                self.attack(second_player_to_move, first_player_to_move)

            if self.end == True:
                break

            self.registered_attack[self.playerOne.name] = None
            self.registered_attack[self.playerTwo.name] = None