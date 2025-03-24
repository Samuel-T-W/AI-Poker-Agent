from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.card import Card
from pypokerengine.engine.game_evaluator import GameEvaluator
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.players import BasePokerPlayer
import random as rand
from pypokerengine.engine.poker_constants import PokerConstants as Const
import pprint

from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.utils.game_state_utils import deepcopy_game_state

class CustomPlayer(BasePokerPlayer):
  def __init__(self):
    self.is_first_player = None
    self.player_pos = None


  def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_pp = pprint.PrettyPrinter(indent=2)
    pp = pprint.PrettyPrinter(indent=2)
    print("------------ROUND_STATE(RANDOM)--------")
    pp.pprint(round_state)
    # print("------------HOLE_CARD----------")
    # pp.pprint(hole_card)
    # print("------------VALID_ACTIONS----------")
    # pp.pprint(valid_actions)
    # print("-------------------------------")
    # print("------------VALID_ACTIONS----------")
    # estimate_hole_card_win_rate_timed(1000, 2, hole_card, round_state["community_card"])
    # print("------------VALID_ACTIONS----------")

    if self.is_first_player == None:
      self.is_first_player = round_state["next_player"] == 0
      self.player_pos = round_state["next_player"]
    
    game_state_copy = deepcopy_game_state(round_state)
    _, action = tree_search(hole_card, round_state, 3, self.is_first_player)

    # action = rand.choice(valid_actions)  # Choose a random action from valid actions

    return action  # action returned here is sent to the poker engine


  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

  def tree_search(self, hole_card, round_state, depth, is_maximizing_player=True):
    # Base case for when depth stops at terminal nodes
    if is_last_round(round_state, round_state["game_rule"]):
      winners, _, prize_map = GameEvaluator.judge(round_state["table"])
      if len(winners) == 2:
        return 0 # since they are splitting the pot 

      if prize_map[self.player_pos] == 0:
        pot_size = round_state["pot"]["main"]["amount"]
        return -1 * pot_size if self.is_first_player else pot_size # -1 if we ae the maximizing player 1 otherwise
      else:
        pot_size = round_state["pot"]["main"]["amount"]
        return -1 * pot_size if self.is_first_player else pot_size # -1 if we ae the maximizing player 1 otherwise
      
    # Base case for when depth stops at intermediary nodes
    if depth == 0 or round_state["street"] == Const.Street.FINISHED:
      sign = -1 if is_maximizing_player else 1 # reverse since the player is before is the one to choose
      return sign * estimate_hole_card_win_rate_timed(30, 2, hole_card, round_state["community_card"])

def setup_ai():
  return CustomPlayer()



# ------- ------- ------- ------- ------- utils ------- ------- ------- ------- ------- ------- ------- 
import functools
import inspect
import time
# A decorator to measure the execution time of a function and print its parameters
def debug_timer(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
      # Get parameter names
      sig = inspect.signature(func)
      param_names = list(sig.parameters.keys())
      
      # Print function name
      print(f"Executing function: {func.__name__}")
      
      # Print parameters
      for i, arg in enumerate(args):
          if i < len(param_names):
              print(f"  {param_names[i]} = {arg}")
          else:
              print(f"  *args[{i}] = {arg}")
      
      for key, value in kwargs.items():
          print(f"  {key} = {value}")
      
      # Measure execution time
      start_time = time.time()
      result = func(*args, **kwargs)
      end_time = time.time()
      
      # Print execution time
      print(f"Function {func.__name__} executed in {(end_time - start_time)*1000 :.6f} milliseconds")
      
      return result
  
  return wrapper

def apply_action(self, game_state, action, bet_amount=0):
        if game_state["street"] == Const.Street.FINISHED:
            game_state, events = self._start_next_round(game_state)
        updated_state, messages = RoundManager.apply_action(game_state, action, bet_amount)
        return updated_state

def generate_possible_actions(self, game_state):
        players = game_state["table"].seats.players
        player_pos = game_state["next_player"]
        sb_amount = game_state["small_blind_amount"]
        return ActionChecker.legal_actions(players, player_pos, sb_amount)

@debug_timer
def estimate_hole_card_win_rate_timed(nb_simulation, nb_player, hole_card, community_card=None):
    hole_card = [Card.from_str(card) for card in hole_card]
    if community_card:
        community_card = [Card.from_str(card) for card in community_card]
    return estimate_hole_card_win_rate(nb_simulation, nb_player, hole_card, community_card)

def is_last_round(game_state, game_rule):
        is_round_finished = game_state["street"] == Const.Street.FINISHED
        is_final_round = game_state["round_count"] == game_rule["max_round"]
        is_winner_decided = len([1 for p in game_state["table"].seats.players if p.stack!=0])==1
        return is_round_finished and (is_final_round or is_winner_decided)


@debug_timer
def tree_search(hole_card, round_state, depth, is_maximizing_player=True):
  # Base case for when depth stops at terminal nodes
  if is_last_round(round_state, round_state["game_rule"]):
    
    winners, _, prize_map = GameEvaluator.judge(round_state["table"])
    if len(winners) == 2:
      return 0 # since they are splitting the pot 
    
  #  if prize_map[]

    sign = -1 if is_maximizing_player else 1 # reverse since the player is before is the one to choose
    return sign * (1 if winners[0]["uuid"] == round_state["next_player"] else -1)
    
  # Base case for when depth stops at intermediary nodes
  if depth == 0 or round_state["street"] == Const.Street.FINISHED:
    sign = -1 if is_maximizing_player else 1 # reverse since the player is before is the one to choose
    return sign * estimate_hole_card_win_rate_timed(30, 2, hole_card, round_state["community_card"])



  valid_actions = generate_possible_actions(round_state)
  val_and_action = None
  for action in valid_actions:
    value = apply_action(round_state, action, bet_amount=10)
    if value is None:
       val_and_action = [value, action]
    elif is_maximizing_player and value > val_and_action[0]:
      val_and_action = [value, action]
    elif not is_maximizing_player and value < val_and_action[0]:
      val_and_action = [value, action]
  return val_and_action
  
   