from src.gather_bot_data import GatherBotData
from parameters import BOTS_NAMES

def main():
    gather_bot_data = GatherBotData()

    for bot_name in BOTS_NAMES:
        gather_bot_data.get_data(bot_name)

if __name__ == "__main__":
    main()