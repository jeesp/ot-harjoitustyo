import time
import random
import pygame
from entities.deck import Deck
from entities.player import Player
from repository.highscore_repository import HighscoreRepository
from database_connection import get_database_connection
from ui.gameplay_ui import draw_blanco_button, draw_continue_button, draw_chicago_button
from ui.gameplay_ui import trick_card_select, poker_card_select, print_round_ending_lines
from ui.ui import GUI

"""
Metodi luo pelaajat peliin.
"""
class App:
    def __init__(self):
        self.highscore_repository = HighscoreRepository(get_database_connection())
        self.players = []
        self.set_up_players()
        self.scoreboard = dict()
        self.set_up_scoreboard()
        self.chicago = dict()
        self.set_up_chicago()
        self.hand_values = {0: "Ei mitään", 1: "Pari", 2: "Kaksi paria", 3: "Kolmoset", 4: "Suora",
                       5: "Väri", 6: "Täyskäsi", 8: "Neloset", 10: "Värisuora"}
        self.deals = 0
        self.dealing_turn = 0
        self.starting_player = 0
        self.deck = Deck()
        self.turn = 0
        self.played_cards = []
        self.compare_card = None
        self.start = 0
        self.value_comparison = (0, 0, 0)
        self.winningtext = []
        self.chicago_on = False
        self.chicago_successful = False
        self.chicago_player = None
        self.blanco_is_on = False
        self.poker_hand_lines = []
        self.round_ending_lines = []
        self.points_reseted = False
        self.gui = GUI()
    """
    Metodi alustaa pelaajat.
    """
    def set_up_players(self):
        db_players = self.highscore_repository.get_players()
        if len(db_players) == 0:
            self.add_players(["Pelaaja 1", "Pelaaja 2", "Pelaaja 3", "Pelaaja 4"])
            db_players = self.highscore_repository.get_players()
        self.players = []
        for player in db_players:
            player_object = Player(player[1])
            self.players.append(player_object)
    """
    Metodi lisää pelaajat tietokantaan.
    """
    def add_players(self, names):
        game_objects = []
        for name in names:
            self.highscore_repository.add_name(name)
            player_id = self.highscore_repository.get_player_id(name)
            game_objects.append([player_id, 0, 0])
        self.highscore_repository.add_new_game(game_objects)
    """
    Metodi alustaa tulostaulun.
    """
    def set_up_scoreboard(self):
        self.scoreboard = dict()
        for player in self.players:
            self.scoreboard[player] = 0
    """
    Metodi laskee ja vertaa pokerikäsien arvot sekä lisää voittajalle pisteet. 
    Metodi myös palauttaa tulostettavat tekstit pokerikierrokselta.
    """
    def set_up_chicago(self):
        self.chicago = dict()
        for player in self.players:
            self.chicago[player] = 0
        self.chicago_on = False
        self.chicago_successful = False
        self.chicago_player = None
        self.blanco_is_on = False
    def poker_points(self):
        if self.deals < 2:
            hands = []
            self.poker_hand_lines = []
            for player in self.players:
                hand = player.hand_value()
                hands.append((player, hand))
            self.value_comparison = self.compare_hands(hands)
        if self.value_comparison[0] != 0:
            self.scoreboard[self.value_comparison[0]] += self.value_comparison[1]
            if self.value_comparison[2] == 0 or self.value_comparison[2] == 1:
                if self.deals == 3:
                    self.poker_hand_lines.append("Lopun pokeripisteet sai "
                                                 + self.value_comparison[0].name)
                else:
                    self.poker_hand_lines.append("Pisteet " + str(self.deals + 1)
                                                 + ". kierrokselta sai: "
                                                 + self.value_comparison[0].name)
                self.poker_hand_lines.append("Käsi: "
                                             + self.hand_values[self.value_comparison[1]].lower() + ".")
            if self.value_comparison[2] == 1:
                self.poker_hand_lines.append("Myös toisella pelaajalla oli "
                                             + self.hand_values[self.value_comparison[1]].lower() + ".")
            if self.value_comparison[1] == 8:
                if not self.points_reseted:
                    self.points_reseted = True
                    for player in self.scoreboard:
                        if player != self.value_comparison[0]:
                            self.scoreboard[player] = 0
                    line = ("Pelaajien pisteet nollattiin nelosten takia.")
                    self.poker_hand_lines.append(line)
            if self.value_comparison[1] == 52:
                for player in self.scoreboard:
                    if player != self.value_comparison[0]:
                        self.scoreboard[player] = 0
                line = ("Pelaajien pisteet värisuoran takia.")
        elif self.value_comparison[2] == 2:
            self.poker_hand_lines.append("Kahdella pelaajalla on sama käsi: "
                                         + self.hand_values[self.value_comparison[1]].lower() + ".")
            self.poker_hand_lines.append("Kukaan ei saanut pisteitä.")
        else:
            if self.deals == 3:
                self.poker_hand_lines.append("Kenelläkään ei ollut mitään.")
                self.poker_hand_lines.append(" Kukaan ei saanut lopun pokeripisteitä.")
            else:
                self.poker_hand_lines.append("Kenelläkään ei ollut mitään.")
                self.poker_hand_lines.append(" Kukaan ei saanut pokeripisteitä.")

    """
    Metodi pokerikierroksen pelaamiseen ja graafisen käyttöliittymän päivittämiseen.
    """
    def play_poker(self, event, players_cards, continue_button, blanco_object):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            poker_card_select(self.gui, players_cards)
            if blanco_object[0] != 0:
                if blanco_object[0].collidepoint(mouse_position):
                    if not blanco_object[1]:
                        color = (0, 200, 0)
                        draw_blanco_button(self.gui, color)
                        blanco_object[1] = True
                        print(blanco_object)
                    else:
                        color = (0, 0, 0)
                        draw_blanco_button(self.gui, color)
                        blanco_object[1] = False
                        print(blanco_object)
                pygame.display.update()
                self.gui.mode = 3
            if continue_button.collidepoint(mouse_position):
                if blanco_object[1]:
                    self.chicago[self.players[self.turn]] = 2
                    self.chicago_player = self.players[self.turn]
                cards_clicked = []
                pygame.display.flip()
                for card in players_cards:
                    if card[3]:
                        cards_clicked.append(card[0])
                    pygame.draw.rect(self.gui.screen, self.gui.POKER_GREEN, pygame.Rect(card[1].x-20,
                    card[1].y-20, self.gui.CARD_SIZE[0]+20, self.gui.CARD_SIZE[1]+40))
                pygame.display.update()
                self.change_card(self.players[self.turn], cards_clicked)
                self.turn += 1
                if self.turn == len(self.players):
                    self.turn = 0
                if self.turn == self.dealing_turn:
                    random.shuffle(self.deck.cards)
                    self.deck.deal_cards(self.players)
                    self.deals += 1
                    if self.deals < 2:
                        self.poker_points()
                    if self.deals == 2:
                        self.gui.game_to_play = 2
                        for player in self.chicago:
                            if self.chicago[player] != 0:
                                self.start = self.players.index(player)
                                self.gui.game_to_play = 2
                                self.chicago_successful = True
                                self.chicago_on = True
                                self.blanco_is_on = True
                        self.turn = self.start
                        self.deals = 3
                        print(self.players[self.turn].name)
                        hands = []
                        for player in self.players:
                            hand = player.hand_value()
                            hands.append((player, hand))
                        self.poker_hand_lines = []
                        self.value_comparison = self.compare_hands(hands)
                        print(self.value_comparison)
                        print("testi")
                self.gui.mode = 1
        draw_continue_button(self.gui)
        if blanco_object[0] != 0:
            if blanco_object[1]:
                color = (0, 200, 0)
                draw_blanco_button(self.gui, color)
            else:
                color = (0, 0, 0)
                draw_blanco_button(self.gui, color)
        pygame.display.update()
    """
    Metodi kortin vaihtoon.
    """
    def change_card(self, player, cards_clicked):
        for card in cards_clicked:
            self.deck.add_card_to_dealt_cards(card)
            player.remove_card(card)
    """
    Metodi tikkikierroksen pelaamiseen ja graafisen käyttöliittymän päivittämiseen.
    """
    def play_trick(self, event, players_cards, continue_button, chicago_object):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            trick_card_select(self.gui, players_cards)
            if chicago_object[0] != 0 and len(self.players[self.turn].hand) > 4:
                if chicago_object[0].collidepoint(mouse_position):
                    if not chicago_object[1]:
                        color = (0, 200, 0)
                        draw_chicago_button(self.gui, color)
                        chicago_object[1] = True
                        print(chicago_object)
                    else:
                        color = (0, 0, 0)
                        draw_chicago_button(self.gui, color)
                        chicago_object[1] = False
                        print(chicago_object)
                pygame.display.update()
                self.gui.mode = 3
            if continue_button.collidepoint(mouse_position) and chicago_object[1]:
                self.chicago[self.players[self.turn]] = 1
                self.gui.mode = 1
                self.start = self.players.index(self.players[self.turn])
                self.chicago_player = self.players[self.turn]
                self.chicago_successful = True
                self.chicago_on = True
                self.compare_card = None
                for card in self.played_cards:
                    card[0].hand.append(card[1])
            if continue_button.collidepoint(mouse_position) and self.gui.card_selected:
                played_card = (0, 0, 0)
                for card in players_cards:
                    if card[3]:
                        played_card = card[0]
                    pygame.draw.rect(self.gui.screen, self.gui.POKER_GREEN, pygame.Rect(card[1].x-20,
                    card[1].y-20, self.gui.CARD_SIZE[0]+20, self.gui.CARD_SIZE[1]+40))
                pygame.display.update()
                self.play_card(self.players[self.turn], played_card)
                if self.compare_card[2] != self.chicago_player:
                    self.chicago_successful = False
                self.turn += 1
                if self.turn == len(self.players):
                    self.turn = 0
                if self.turn == self.start:
                    if len(self.players[self.start].hand) == 0:
                        self.dealing_turn += 1
                        if self.dealing_turn == len(self.players):
                            self.dealing_turn = 0
                        self.gui.game_to_play = 1
                        self.deck = Deck()
                        self.start = self.dealing_turn
                        self.turn = self.dealing_turn
                        self.played_cards = []
                        self.round_ending_lines = []
                        random.shuffle(self.deck.cards)
                        self.deck.deal_cards(self.players)
                        self.end_trick()
                        self.compare_card = None
                        if self.round_ending():
                            self.highscore_repository.create_game_object(self)
                            self.gui.mode = 2
                            self.turn = 0
                            self.deals = 0
                            self.gui.card_selected = False
                            self.played_cards = []
                            self.start = 0
                            self.value_comparison = (0, 0, 0)
                            self.dealing_turn = 0
                            self.starting_player = 0
                            self.gui.game_to_play = 0
                            print_round_ending_lines(self.gui, self)
                            time.sleep(5)
                        else:
                            print_round_ending_lines(self.gui, self)
                            time.sleep(5)
                            self.deals = 0
                            self.poker_points()
                        self.set_up_chicago()
                    else:
                        self.start = self.players.index(self.compare_card[2])
                        self.compare_card = None
                        self.turn = self.start
                if self.gui.game_to_play == 2:
                    print(self.players[self.turn].name)
                if self.gui.mode == 3:
                    self.gui.mode = 1
                self.gui.card_selected = False
        draw_continue_button(self.gui)
        if chicago_object[0] != 0 and len(self.players[self.turn].hand) > 4:
            if chicago_object[1]:
                color = (0, 200, 0)
                draw_chicago_button(self.gui, color)
            else:
                color = (0, 0, 0)
                draw_chicago_button(self.gui, color)
        pygame.display.update()

    """
    Metodi tikkikierroksen päättämiseen.
    """
    def end_trick(self):
        if self.chicago_on:
            if self.chicago_successful:
                if self.blanco_is_on:
                    self.scoreboard[self.compare_card[2]] += 30
                    self.round_ending_lines.append(self.compare_card[2].name
                                                   + " sai läpi onnistuneesti blanco-chicagon.")
                else:
                    self.scoreboard[self.compare_card[2]] += 15
                    self.round_ending_lines.append(self.compare_card[2].name
                                                   + " sai läpi onnistuneesti chicagon.")
            else:
                self.scoreboard[self.compare_card[2]] += 5
                self.round_ending_lines.append(self.compare_card[2].name
                                               + " sai lopetuksen ja " + self.chicago_player.name
                                               + "n chicago meni pieleen.")
                if self.blanco_is_on:
                    self.scoreboard[self.chicago_player] -= 30
                else:
                    self.scoreboard[self.chicago_player] -= 15
        else:
            if self.compare_card[0] == 2:
                self.scoreboard[self.compare_card[2]] += 10
                self.round_ending_lines.append("Kierroksen lopetti " +
                      self.compare_card[2].name + " kakkoslopetuksella")
            else:
                self.scoreboard[self.compare_card[2]] += 5
                self.round_ending_lines.append("Kierroksen lopetti "
                                               + self.compare_card[2].name)
    """
    Metodi vertailukortin vaihtamiseen tikkiä varten.
    """
    def set_compare_card(self, player, card):
        compare_card_number = card[0]
        compare_card_suit = card[1]
        compare_card_player = player
        self.compare_card = (compare_card_number, compare_card_suit, compare_card_player)
    """
    Metodi kortin pelaamiseen tikissä.
    """
    def play_card(self, player, played_card):
        playable_cards = []
        for card in player.hand:
            if self.compare_card is not None:
                if card[1] == self.compare_card[1]:
                    playable_cards.append(card)
            else:
                playable_cards.append(card)
        if len(playable_cards) == 0:
            playable_cards = player.hand
        player.hand.remove(played_card)
        self.played_cards.append((player, played_card))
        if self.compare_card is None:
            self.set_compare_card(player, played_card)
        if played_card[1] == self.compare_card[1]:
            if played_card[0] > self.compare_card[0]:
                self.set_compare_card(player, played_card)
    """
    Metodi pokerikäsien vertailuun.
    """
    def compare_hands(self, hands):
        strongest_hand_object = (0, 0)
        strongest_hand = 0
        strongest_player = 0
        comparable_hands = [1, 3, 4, 5, 8, 52]
        same_hand = False
        same_value_but_different_numbers = False
        for hand in hands:
            if hand[1][0] > strongest_hand:
                same_hand = False
                same_value_but_different_numbers = False
                strongest_hand = hand[1][0]
                strongest_hand_object = hand[1]
                strongest_player = hand[0]
            elif hand[1][0] == strongest_hand:
                if hand[1][0] in comparable_hands:
                    same_value_but_different_numbers = True
                    if hand[1][1] > strongest_hand_object[1]:
                        strongest_hand = hand[1][0]
                        strongest_hand_object = hand[1]
                        strongest_player = hand[0]
                    elif hand[1][1] == strongest_hand_object[1]:
                        same_hand = True
                if hand[1][0] == 2 or hand[1][0] == 6:
                    same_hand = True
        if same_hand:
            return (0, strongest_hand, 2)
        if strongest_hand in comparable_hands and same_value_but_different_numbers:
            return (strongest_player, strongest_hand, 1)
        return (strongest_player, strongest_hand, 0)
    """
    Metodi kierroksen päättämiseen ja pisteiden tarkistukseen.
    """
    def round_ending(self):
        no_chicagos = True
        for player in self.chicago:
            if self.chicago[player] != 0:
                no_chicagos = False
        if no_chicagos:
            self.poker_points()
        else:
            self.poker_hand_lines.append("Kierroksella huudettiin chicago, ei pokeripisteitä.")
        points = []
        for player in self.players:
            points.append(self.scoreboard[player])
        points.sort()
        if self.points_check(points):
            return True
        print(self.value_comparison)
        print("")
        print("Uusi kierros.")
        print("")
        return False
    """
    Metodi pistetarkistukseen ja pelin päättämiseen jos pisteitä on tarpeeksi.
    """
    def points_check(self, points):
        if points[len(points)-1] >= 5:
            if points[len(points)-1] > points[len(points)-2]:
                for player in self.players:
                    if self.scoreboard[player] == points[len(points)-1]:
                        self.winningtext.append("Peli päättynyt!")
                        self.winningtext.append("Voittaja on: " + player.name + ". Pisteet: "
                              + str(points[len(points)-1]))
            if points[len(points)-1] == points[len(points)-2]:
                self.winningtext.append("Pisteraja ylitetty, mutta osalla pelaajista on tasatilanne.")
                self.winningtext.append("Pelaajat tasatilanteessa: ", end=" ")
                for player in self.players:
                    if self.scoreboard[player] == points[len(points)-1]:
                        self.winningtext.append(player.name + " ", end=" ")
                self.winningtext.append("Pisteillä: " + str(points[len(points)-1]))
            return True
        return False
    """
    Metodi alku- ja loppuvalikon toimintoja varten.
    """
    def menu_actions(self, event, start_button, reset_button):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_position):
                if self.gui.mode == 2:
                    self.winningtext = []
                    self.set_up_players()
                    self.set_up_scoreboard()
                    self.set_up_chicago()
                    self.poker_hand_lines = []
                self.gui.mode = 1
                self.gui.game_to_play = 1
                random.shuffle(self.deck.cards)
                self.deck.deal_cards(self.players)
                self.poker_points()
            if reset_button.collidepoint(mouse_position):
                self.highscore_repository.delete_all()
                self.set_up_players()
                self.set_up_scoreboard()
                self.set_up_chicago()
    def check_chicago(self):
        no_chicago = True
        chicago_player = 0
        blanco = False
        for chicago in self.chicago:
            if self.chicago[chicago] != 0:
                no_chicago = False
                chicago_player = chicago
                if self.chicago[chicago] == 2:
                    blanco = True
        return [no_chicago, chicago_player, blanco]