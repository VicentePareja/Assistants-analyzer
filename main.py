from src.gather_bot_data.gather_bot_data import GatherBotData
from src.analyze_bot_data.analyze_bot_data import BotDataAnalyzer
import time
from parameters import BOTS_NAMES

def gather_bot_data():
    gather_bot_data = GatherBotData()

    print("Gathering data for all bots\n")

    starting_time = time.time()

    for bot_name in BOTS_NAMES:
        try:
            gather_bot_data.get_data(bot_name)
        except Exception as e:
            print(f"Error for {bot_name}: {str(e)}")

    print(f"Finished gathering data for all bots in {time.time() - starting_time:.2f} seconds.")

def analyze_bot_data():
    analyze_bot_data = BotDataAnalyzer()

    print("Analysing all bots\n")

    starting_time = time.time()

    for bot_name in BOTS_NAMES:
        try:
            analyze_bot_data.run_analysis(bot_name)
        except Exception as e:
            print(f"Error for {bot_name}: {str(e)}")

    print(f"Finished analysing all bots in {time.time() - starting_time:.2f} seconds.")

def main():
    user_input = input("Do you want to gather bot data? (yes/no, default: no): ").strip().lower()

    # Default to 'no' if no input is provided
    if user_input == "yes":
        gather_bot_data()
    else:
        print("Skipping data gathering.\n")

    analyze_bot_data()

if __name__ == "__main__":
    main()
