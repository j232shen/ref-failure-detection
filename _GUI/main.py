# third-party library imports
import os
import time
import tkinter as tk
import threading
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from ttkthemes import ThemedTk

# importing test_processing module
from test_processing import process_tests, export_results

# global file path dict
file_path_list = {}


class HeaderFrame(ttk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)

        self.heading = ttk.Label(self, text="Import files", font=("Helvetica", 14, "bold"))
        self.heading.grid(padx=10, pady=(10, 0), sticky="w")

        self.subtext = ttk.Label(
            self,
            text="Please input files containing 1) Potassium waveforms, and \n"
                 "2) BubbleDetectTime for TestIDs of interest.",
            font=("Helvetica", 9)
        )
        self.subtext.grid(padx=10, pady=(5, 10), sticky="w")


class BodyFrame(ttk.Frame):
    def __init__(self, parent_frame, frame_id):
        super().__init__(parent_frame)
        self.frame_id = frame_id

        label_text = ""
        if frame_id == "signals":
            label_text = "Upload waveforms file"
        elif frame_id == "bubble times":
            label_text = "Upload bubble detect times file"

        heading = ttk.Label(self, text=label_text, font=("Helvetica", 10, "bold"))
        heading.grid(column=0, row=0, padx=10, pady=(10, 0), sticky="w")

        self.file_selector = FileSelectorFrame(self, self.frame_id)
        self.file_selector.grid(column=0, row=1, padx=5, pady=(0, 10))


class FileSelectorFrame(ttk.Frame):
    def __init__(self, parent_frame, frame_id):
        super().__init__(parent_frame)
        self.frame_id = frame_id

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)

        self.label = tk.Label(
            self,
            text="No file selected*",
            font=("Helvetica", 9),
            width=40, anchor="w",
            background="white"
        )
        self.label.grid(column=0, row=0, sticky="ns")

        self.button = ttk.Button(
            self,
            text="Browse",
            command=self.select_file
        )
        self.button.grid(column=1, row=0)

        for widget in self.winfo_children():
            widget.grid(padx=5, pady=5)

    def select_file(self):
        global file_path_list
        if len(file_path_list) < 2:
            filename = filedialog.askopenfilename(title="Select File",
                                                  filetypes=(("Excel files", "*.csv"), ("All files", "*.*")))
            if filename:
                file_path_list[self.frame_id] = filename
                filename = filename.split('/')[len(filename.split('/')) - 1]
                self.label['text'] = filename
        else:
            messagebox.showwarning("Notice", "Please reset first.")


class Timer(ttk.Label):
    def __init__(self, parent_frame):
        super().__init__(parent_frame, text="0s", font=("Helvetica", 9))
        self.elapsed_time = 0
        self.start_time = None

        self.timer_thread = None
        self.is_running = False

    def start_timer(self):
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.start()

    def update_timer(self):
        while self.is_running:
            if self.start_time is not None:
                self.elapsed_time = int(time.time() - self.start_time)
            self['text'] = f"{self.elapsed_time}s"
            time.sleep(1)  # update every second

    def stop_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_time = None
            self.timer_thread.join()


class ExecutionFrame(ttk.Frame):
    def __init__(self, parent_frame, app_instance):
        super().__init__(parent_frame)
        self.app_instance = app_instance

        self.columnconfigure(0, weight=2)  # weight=2 for 3 column grid, weight=4 for 2 column grid
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)  # for 3 column grid

        # widgets that need to dynamically change
        self.label = ttk.Label(self, text="Press Run to classify tests", font=("Helvetica", 10, "bold"))
        self.label.grid(column=0, row=0, padx=5, pady=(10, 0), sticky="w")

        self.timerLabel = ttk.Label(self, text="Elapsed time:", font=("Helvetica", 9))
        self.timerLabel.grid(column=0, row=1, padx=5, pady=(0, 0), sticky="w")

        # 3 column grid
        self.timer = Timer(self)
        self.timer.grid(column=1, row=1, padx=5, pady=(0, 0), sticky="e")

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='indeterminate', length=286)
        self.progress.grid(column=0, row=2, columnspan=2, padx=5, pady=5)  # add columnspan=2 for 3 column grid

        self.button = ttk.Button(self, text="Run", command=self.start_file_reading)
        self.button.grid(column=2, row=2, padx=5, pady=5)  # column=2 for 3 column grid

    def update_label(self, text):
        self.label['text'] = text
        # parent_frame.update_idletasks()

    def start_file_reading(self):
        global file_path_list
        file_reading_thread = threading.Thread(target=self.read_files)
        if len(file_path_list) == 2:
            file_reading_thread.start()
        else:
            messagebox.showwarning("Notice", "File(s) missing.")

    def read_files(self):
        global file_path_list
        f_signals = file_path_list["signals"]
        f_bubble_times = file_path_list["bubble times"]

        # disable buttons
        self.app_instance.lock_buttons()

        # start progress bar and timer
        self.timer.start_timer()
        self.progress.start()

        # process files
        self.update_label(f"Reading files...")
        results_df = process_tests(f_signals, f_bubble_times)

        # stop progress bar and timer
        self.timer.stop_timer()
        self.progress.stop()

        # export results if they exist
        if results_df is not None:
            self.update_label("Predictions done.")
            export_results(results_df)
            self.update_label("Results exported.")
        else:
            self.update_label("Processing interrupted.")

        # change Run button to Reset button
        self.button.config(state=tk.NORMAL)
        self.button['text'] = "Reset"
        self.button['command'] = self.app_instance.reset_gui


class App:
    def __init__(self):
        self.root = ThemedTk(theme="breeze")  # ThemedTk is already inherited from tk.Tk, so can't inherit from it
        # self.root.iconbitmap('logo.ico')
        self.root.title("epoc Waveform Classifier")
        self.root.resizable(False, False)

        self.file_paths = {}

        self.upper_body = None
        self.mid_body = None
        self.exec_frame = None

        self.create_header_frame()
        self.create_body_frame()

        self.root.mainloop()

    def create_header_frame(self):
        header = HeaderFrame(self.root)
        header.grid(column=0, row=0, padx=10, pady=(10, 0), sticky="w")

    def create_body_frame(self):
        # signals file selection
        self.upper_body = BodyFrame(self.root, "signals")
        self.upper_body.grid(column=0, row=1, padx=10, pady=(10, 0))

        # bubble detect times file selection
        self.mid_body = BodyFrame(self.root, "bubble times")
        self.mid_body.grid(column=0, row=2, padx=10, pady=(10, 0))

        # progress bar
        lower_body = ttk.Frame(self.root)
        lower_body.grid(column=0, row=3, padx=10, pady=10)

        self.exec_frame = ExecutionFrame(lower_body, self)
        self.exec_frame.grid(column=0, row=0, padx=5, pady=(0, 10))

    def reset_gui(self):
        # empty dict
        global file_path_list
        file_path_list = {}

        # reset file selectors
        self.upper_body.file_selector.label['text'] = "No file selected*"
        self.mid_body.file_selector.label['text'] = "No file selected*"
        self.unlock_buttons()

        # reset execution frame
        self.exec_frame.update_label("Press Run to classify tests")
        self.exec_frame.timer['text'] = "0s"
        self.exec_frame.button['text'] = "Run"
        self.exec_frame.button['command'] = self.exec_frame.start_file_reading

    def lock_buttons(self):
        self.upper_body.file_selector.button.config(state=tk.DISABLED)
        self.mid_body.file_selector.button.config(state=tk.DISABLED)
        self.exec_frame.button.config(state=tk.DISABLED)

    def unlock_buttons(self):
        self.upper_body.file_selector.button.config(state=tk.NORMAL)
        self.mid_body.file_selector.button.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = App()
