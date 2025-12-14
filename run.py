import argparse
import asyncio
import logging
import aiohttp
import os
import sys
import sc2
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.client import Client
from sc2.player import Bot, Computer
from sc2.protocol import ConnectionAlreadyClosed
import random

from bot import ZergBot, TerranBot, ProtossBot, BotSettings, BotPersonality
from config import BOT_NAME, BOT_RACE, MAP_POOL, MAP_PATH, OPPONENT_RACE, OPPONENT_DIFFICULTY, REALTIME

# Run ladder game
def run_ladder_game(args, bot):
    if args.LadderServer == None:
        host = "127.0.0.1"
    else:
        host = args.LadderServer

    host_port = args.GamePort
    lan_port = args.StartPort

    # Port config
    ports = [lan_port + p for p in range(1, 6)]

    portconfig = sc2.portconfig.Portconfig()
    portconfig.shared = ports[0]  # Not used
    portconfig.server = [ports[1], ports[2]]
    portconfig.players = [[ports[3], ports[4]]]

    # Join ladder game
    g = join_ladder_game(host=host, port=host_port, players=[bot], realtime=args.Realtime, portconfig=portconfig)

    # Run the game
    result = asyncio.get_event_loop().run_until_complete(g)
    return result, args.OpponentId


async def join_ladder_game(
        host, port, players, realtime, portconfig, save_replay_as=None, step_time_limit=None, game_time_limit=None
):
    ws_url = "ws://{}:{}/sc2api".format(host, port)
    ws_connection = await aiohttp.ClientSession().ws_connect(ws_url, timeout=120)
    client = Client(ws_connection)
    try:
        result = await sc2.main._play_game(players[0], client, realtime, portconfig, step_time_limit, game_time_limit)
        if save_replay_as is not None:
            await client.save_replay(save_replay_as)
    except ConnectionAlreadyClosed:
        logging.error(f"Connection was closed before the game ended")
        return None
    finally:
        await ws_connection.close()

    return result


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Ladder play arguments
    parser.add_argument("--GamePort", type=int, help="Game port.")
    parser.add_argument("--StartPort", type=int, help="Start port.")
    parser.add_argument("--LadderServer", type=str, help="Ladder server.")

    # Bot settings
    parser.add_argument("--bot-name", type=str, default=BOT_NAME, help="Name of your bot.")
    parser.add_argument("--bot-race", type=str, default=BOT_RACE, help="Bot race (Terran, Zerg, Protoss, Random).")
    parser.add_argument("--mmr", type=int, default=3000, help="Bot MMR (Skill Level).")
    parser.add_argument("--personality", type=str, default="Standard", help="Bot Personality (Standard, Economic, Aggressive, Cheese).")
    
    # Game settings
    parser.add_argument("--map", type=str, default=None, help="Map to play on.")
    parser.add_argument("--opponent-race", type=str, default=OPPONENT_RACE, help="Computer race.")
    parser.add_argument("--difficulty", type=str, default=OPPONENT_DIFFICULTY, help="Computer difficulty.")
    parser.add_argument("--realtime", action='store_true', default=REALTIME, help="Play in realtime.")
    parser.add_argument("--sc2-path", type=str, help="Path to StarCraft II installation.")
    parser.add_argument("--sc2-version", type=str, help="Starcraft 2 game version.")

    args, unknown_args = parser.parse_known_args()

    # Handle SC2 Path
    if args.sc2_path and os.path.exists(args.sc2_path):
        os.environ["SC2PATH"] = args.sc2_path

    # Set default opponent ID
    if not hasattr(args, 'OpponentId') or not args.OpponentId:
        args.OpponentId = f"{args.opponent_race}_{args.difficulty}"

    return args


def load_bot(args):
    """Initialize and configure the bot."""
    # Settings
    try:
        personality = BotPersonality(args.personality)
    except ValueError:
        print(f"Invalid personality: {args.personality}. Using Standard.")
        personality = BotPersonality.STANDARD

    settings = BotSettings(mmr=args.mmr, personality=personality)

    # Race
    try:
        bot_race = Race[args.bot_race.capitalize()]
    except KeyError:
        print(f"Invalid bot race: {args.bot_race}. Using Zerg.")
        bot_race = Race.Zerg

    # Select Bot Class
    if bot_race == Race.Zerg:
        bot_logic = ZergBot(settings)
    elif bot_race == Race.Terran:
        bot_logic = TerranBot(settings)
    elif bot_race == Race.Protoss:
        bot_logic = ProtossBot(settings)
    else:
        bot_logic = ZergBot(settings) # Fallback for Random?

    return Bot(bot_race, bot_logic)


def main():
    args = parse_arguments()
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    bot_name = getattr(args, 'bot_name', BOT_NAME)
    bot_race = getattr(args, 'bot_race', BOT_RACE)
    
    # Check if running in Ladder mode (GamePort provided)
    if args.GamePort:
        print(f"Starting Ladder Game for {bot_name}...")
        bot = load_bot(args)
        run_ladder_game(args, bot)
        return 0

    # Local Play
    print(f"===== {bot_name} ({bot_race}) =====")
    print(f"MMR: {args.mmr}, Personality: {args.personality}")
    print(f"Available maps: {', '.join(MAP_POOL)}")
    
    try:
        bot = load_bot(args)

        # Opponent Setup
        try:
            opponent_race = Race[args.opponent_race.capitalize()]
        except KeyError:
            opponent_race = Race.Random

        try:
            difficulty = Difficulty[args.difficulty]
        except KeyError:
            difficulty = Difficulty.VeryHard

        # Map Setup
        map_name = args.map if args.map else random.choice(MAP_POOL)

        # Resolve Map Path
        # Logic: If map arg is a full path, use it? Or assume it's a name in MAP_PATH?
        # sc2.maps.get() looks in MAP_DIR.
        # If MAP_PATH is set in config, use it.

        print(f"\nStarting game on {map_name}...")
        run_game(
            sc2.maps.get(map_name),
            [bot, Computer(opponent_race, difficulty)],
            realtime=args.realtime,
            sc2_version=args.sc2_version
        )
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if __debug__:
            import traceback
            traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
