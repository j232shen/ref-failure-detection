import pandas as pd
from tkinter import filedialog
from tkinter import messagebox

from test import create_test_list
from pipelines import run_short, run_long


def process_tests(f_signals, f_bubble_times):
    signals = pd.read_csv(f_signals)
    bubble_detect = pd.read_csv(f_bubble_times)

    if signals.empty or bubble_detect.empty:
        messagebox.showwarning("Notice", "One or more empty files. Please check input files and try again.")
        return None
    else:
        # expected columns per dataframe
        signals_expected_cols = ['TestID', 'Channel', '0.2']  # 0.2 need to be str for csv, int for xlsx
        bubble_detect_expected_cols = ['TestID', 'BubbleDetectTime']

        # bools
        signals_missing_cols = set(signals_expected_cols).issubset(signals.columns)
        bubble_detect_missing_cols = set(bubble_detect_expected_cols).issubset(bubble_detect.columns)

        # check for expected columns
        if not signals_missing_cols or not bubble_detect_missing_cols:
            messagebox.showwarning("Notice", "Unexpected file contents. Please check input files and try again.")
            return None
        else:
            # unique TestID lists must match across both dataframes
            signals_TestID = signals['TestID'].drop_duplicates(keep='first')
            if signals_TestID.tolist() != bubble_detect['TestID'].tolist():
                messagebox.showwarning("Notice", "TestIDs do not match. Please check input files and try again.")
                return None
            else:
                # create tests and store in list
                tests = create_test_list(signals, bubble_detect)

                # processing waveforms
                for test in tests:
                    test.offset_time()
                    test.trim_NaNs()

                # dataframe to hold predictions
                test_df = pd.DataFrame({'Test': tests, 'Predicted': '', 'Comments': ''})

                # make predictions for all tests in set
                for idx, test in enumerate(test_df['Test']):
                    # check length of test to run appropriate pipeline
                    if len(test.P4) < int(40 / 0.2):
                        run_short(idx, test, test_df)
                    else:
                        run_long(idx, test, test_df)

                # creating results dataframe
                results_df = pd.DataFrame({
                    'TestIDs': test_df['Test'].apply(lambda test: test.ID),
                    'Predicted': test_df['Predicted'],
                    'Comments': test_df['Comments']
                })

                return results_df


def export_results(results_df):
    # export to csv
    results_file = filedialog.asksaveasfilename(title="Save Results File",
                                                initialfile="results.csv",
                                                filetypes=(("Excel files", "*.csv"), ("All files", "*.*")))
    if results_file:
        results_df.to_csv(results_file, index=False)
