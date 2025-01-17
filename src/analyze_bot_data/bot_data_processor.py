import pandas as pd

from src.analyze_bot_data.paths_manager.paths_manager import PathsManager

class BotDataProcessor:
    """
    Processes data frames. We will create a new method to find the top
    MOST_DIFFERENT questions, each with best & worst attempts.
    """

    def get_worst_answer_per_question(self, df_worst: pd.DataFrame):
        # (Keep or remove this old method as needed)
        if df_worst.empty or "Grading" not in df_worst.columns:
            return pd.DataFrame()

        worst_df = df_worst.loc[df_worst.groupby("Question")["Grading"].idxmin()].copy()
        return worst_df

    def get_best_and_worst_with_biggest_difference(self, df_worst: pd.DataFrame, top_n: int):
        """
        For each question, find the best (max) and worst (min) rows by 'Grading'.
        Compute the difference (max - min). Keep only the top 'top_n' questions 
        with the largest difference. Return a DataFrame with 2*top_n rows 
        (the best and worst for each question).
        """
        if df_worst.empty or "Grading" not in df_worst.columns:
            return pd.DataFrame()

        # Group by question
        grouped = df_worst.groupby("Question")

        # For each group, find:
        #   * best_row (max Grading)
        #   * worst_row (min Grading)
        #   * difference = best_row.Grading - worst_row.Grading
        results = []
        for question, group_df in grouped:
            # If the group is empty or missing columns, skip
            if group_df.empty:
                continue

            max_idx = group_df["Grading"].idxmax()
            min_idx = group_df["Grading"].idxmin()

            best_row = group_df.loc[max_idx]
            worst_row = group_df.loc[min_idx]
            difference = best_row["Grading"] - worst_row["Grading"]

            results.append({
                "Question": question,
                "BestRow": best_row,
                "WorstRow": worst_row,
                "Difference": difference
            })

        # Sort by difference descending, keep top N
        sorted_results = sorted(results, key=lambda x: x["Difference"], reverse=True)
        top_results = sorted_results[:top_n]

        # Build a final DataFrame with both best & worst rows
        # We'll keep the original columns, plus a "Type" column 
        # so you know if it's "BEST" or "WORST" in the final table
        final_rows = []
        for item in top_results:
            best_row_data = item["BestRow"].to_dict()
            worst_row_data = item["WorstRow"].to_dict()

            # Tag them for clarity
            best_row_data["Type"] = "BEST"
            worst_row_data["Type"] = "WORST"

            # We might also store the difference if you want to see it in the HTML
            best_row_data["Difference"] = item["Difference"]
            worst_row_data["Difference"] = item["Difference"]

            final_rows.append(best_row_data)
            final_rows.append(worst_row_data)

        df_final = pd.DataFrame(final_rows)
        return df_final.reset_index(drop=True)

    def filter_single_assessment_top_and_bottom(self, df_single: pd.DataFrame, n: int, grading_col: str = "Grading"):
        # (This method stays the same if you still want top & bottom rows)
        if df_single.empty or grading_col not in df_single.columns:
            return df_single  
        df_single_sorted = df_single.sort_values(by=grading_col, ascending=False)
        top_n = df_single_sorted.head(n)
        bottom_n = df_single_sorted.tail(n)
        return pd.concat([top_n, bottom_n], axis=0).reset_index(drop=True)
    
    def get_top_n(self, df: pd.DataFrame, n: int, grading_col: str = "Grading") -> pd.DataFrame:
        """
        Return the top-n rows sorted by `grading_col` descending.
        """
        if df.empty or grading_col not in df.columns:
            return pd.DataFrame()  # Return an empty DataFrame if conditions are not met
        return df.sort_values(by=grading_col, ascending=False).head(n)

    def get_bottom_n(self, df: pd.DataFrame, n: int, grading_col: str = "Grading") -> pd.DataFrame:
        """
        Return the bottom-n rows sorted by `grading_col` ascending.
        """
        if df.empty or grading_col not in df.columns:
            return pd.DataFrame()  # Return an empty DataFrame if conditions are not met
        return df.sort_values(by=grading_col, ascending=False).tail(n)

class WorstOf4Saver:
    """
    Saves the entire worst-of-4 data (or any processed subset) to a CSV file (optional).
    """
    def save_worst_data(self, df_worst: pd.DataFrame, paths_manager: PathsManager, assistant_name: str):
        if df_worst.empty:
            print("No data to save for worst-of-4.")
            return
        output_file = paths_manager.processed_dir + f"/{assistant_name}_only_worst.csv"
        df_worst.to_csv(output_file, index=False, sep=';')
        print(f"Worst-of-4 data saved to: {output_file}")