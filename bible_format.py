import tkinter as tk
from tkinter import filedialog, messagebox
import os

def format_niv_bible_text(input_text):
    """
    Formats NIV Bible text by adding chapter and verse numbers.

    Args:
        input_text (str): The raw text content of the NIV Bible file,
                          where each line is a verse and book names are
                          headings.

    Returns:
        tuple: A tuple containing:
               - str: The formatted text with chapter and verse numbers.
               - list: A list of strings, each representing a book-level status or warning.
    """

    # Comprehensive NIV Bible chapter and verse counts
    # Each entry now includes a list of chapter verse counts and the total verses for the book.
    niv_book_data = {
        "GENESIS": {"chapters": [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26], "total_verses": 1533},
        "EXODUS": {"chapters": [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38], "total_verses": 1213},
        "LEVITICUS": {"chapters": [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34], "total_verses": 859},
        "NUMBERS": {"chapters": [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13], "total_verses": 1288},
        "DEUTERONOMY": {"chapters": [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12], "total_verses": 959},
        "JOSHUA": {"chapters": [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33], "total_verses": 658},
        "JUDGES": {"chapters": [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25], "total_verses": 618},
        "RUTH": {"chapters": [22, 23, 18, 22], "total_verses": 85},
        "1 SAMUEL": {"chapters": [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13], "total_verses": 810},
        "2 SAMUEL": {"chapters": [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25], "total_verses": 695},
        "1 KINGS": {"chapters": [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53], "total_verses": 816},
        "2 KINGS": {"chapters": [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30], "total_verses": 719},
        "1 CHRONICLES": {"chapters": [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30], "total_verses": 942},
        "2 CHRONICLES": {"chapters": [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23], "total_verses": 822},
        "EZRA": {"chapters": [11, 70, 13, 24, 17, 22, 28, 36, 15, 44], "total_verses": 280},
        "NEHEMIAH": {"chapters": [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31], "total_verses": 406},
        "ESTHER": {"chapters": [22, 23, 15, 17, 14, 14, 10, 17, 32, 3], "total_verses": 167},
        "JOB": {"chapters": [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17], "total_verses": 1070},
        "PSALMS": {"chapters": [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6], "total_verses": 2461},
        "PROVERBS": {"chapters": [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31], "total_verses": 915},
        "ECCLESIASTES": {"chapters": [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14], "total_verses": 222},
        "SONG OF SONGS": {"chapters": [17, 17, 11, 16, 16, 13, 13, 14], "total_verses": 117},
        "ISAIAH": {"chapters": [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 12, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24], "total_verses": 1292},
        "JEREMIAH": {"chapters": [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34], "total_verses": 1364},
        "LAMENTATIONS": {"chapters": [22, 22, 66, 22, 22], "total_verses": 154},
        "EZEKIEL": {"chapters": [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 17, 24, 23, 35], "total_verses": 1273},
        "DANIEL": {"chapters": [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13], "total_verses": 357},
        "HOSEA": {"chapters": [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9], "total_verses": 197},
        "JOEL": {"chapters": [20, 32, 21], "total_verses": 73},
        "AMOS": {"chapters": [15, 16, 15, 13, 27, 14, 17, 14, 15], "total_verses": 146},
        "OBADIAH": {"chapters": [21], "total_verses": 21},
        "JONAH": {"chapters": [17, 10, 10, 11], "total_verses": 48},
        "MICAH": {"chapters": [16, 13, 12, 13, 15, 16, 20], "total_verses": 105},
        "NAHUM": {"chapters": [15, 13, 19], "total_verses": 47},
        "HABAKKUK": {"chapters": [17, 20, 19], "total_verses": 56},
        "ZEPHANIAH": {"chapters": [18, 15, 20], "total_verses": 53},
        "HAGGAI": {"chapters": [15, 23], "total_verses": 38},
        "ZECHARIAH": {"chapters": [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21], "total_verses": 211},
        "MALACHI": {"chapters": [14, 17, 18, 6], "total_verses": 55},
        "MATTHEW": {"chapters": [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20], "total_verses": 1071},
        "MARK": {"chapters": [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20], "total_verses": 678},
        "LUKE": {"chapters": [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53], "total_verses": 1151},
        "JOHN": {"chapters": [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25], "total_verses": 879},
        "ACTS": {"chapters": [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31], "total_verses": 1007},
        "ROMANS": {"chapters": [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27], "total_verses": 433},
        "1 CORINTHIANS": {"chapters": [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24], "total_verses": 437},
        "2 CORINTHIANS": {"chapters": [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14], "total_verses": 257},
        "GALATIANS": {"chapters": [24, 21, 29, 31, 26, 18], "total_verses": 149},
        "EPHESIANS": {"chapters": [23, 22, 21, 32, 33, 24], "total_verses": 155},
        "PHILIPPIANS": {"chapters": [30, 30, 21, 23], "total_verses": 104},
        "COLOSSIANS": {"chapters": [29, 23, 25, 18], "total_verses": 95},
        "1 THESSALONIANS": {"chapters": [10, 20, 13, 18, 28], "total_verses": 89},
        "2 THESSALONIANS": {"chapters": [12, 17, 18], "total_verses": 47},
        "1 TIMOTHY": {"chapters": [20, 15, 16, 16, 25, 21], "total_verses": 113},
        "2 TIMOTHY": {"chapters": [18, 26, 17, 22], "total_verses": 83},
        "TITUS": {"chapters": [16, 15, 15], "total_verses": 46},
        "PHILEMON": {"chapters": [25], "total_verses": 25},
        "HEBREWS": {"chapters": [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25], "total_verses": 303},
        "JAMES": {"chapters": [27, 26, 18, 17, 20], "total_verses": 108},
        "1 PETER": {"chapters": [25, 25, 22, 19, 14], "total_verses": 105},
        "2 PETER": {"chapters": [21, 22, 18], "total_verses": 61},
        "1 JOHN": {"chapters": [10, 29, 24, 21, 21], "total_verses": 105},
        "2 JOHN": {"chapters": [13], "total_verses": 13},
        "3 JOHN": {"chapters": [14], "total_verses": 14},
        "JUDE": {"chapters": [25], "total_verses": 25},
        "REVELATION": {"chapters": [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21], "total_verses": 404}
    }

    # List of all book names in canonical order for checking missing books
    expected_book_order = list(niv_book_data.keys())

    output_lines = []
    book_summary_log = []
    
    current_book_name = None
    current_chapter_index = 0 # 0-indexed for list access
    verses_found_in_current_book = 0
    verses_found_in_current_chapter = 0
    
    processed_books_set = set() # To track which books were found in the input file

    lines = input_text.strip().split('\n')

    def finalize_previous_book_summary():
        nonlocal current_book_name, verses_found_in_book, book_summary_log
        if current_book_name:
            expected_total = niv_book_data[current_book_name]["total_verses"]
            if verses_found_in_book == expected_total:
                book_summary_log.append(f"{current_book_name} - Good")
            else:
                book_summary_log.append(
                    f"{current_book_name} overall expected {expected_total} verses but found {verses_found_in_book} verses."
                )
            processed_books_set.add(current_book_name)

    for line_num, line in enumerate(lines, 1):
        cleaned_line = line.lstrip('\ufeff').strip()
        if not cleaned_line:
            continue

        if cleaned_line.upper() in niv_book_data:
            finalize_previous_book_summary()

            current_book_name = cleaned_line.upper()
            output_lines.append(f"\n{current_book_name}\n")
            chapter_number = 1
            verse_number = 1
            verses_found_in_book = 0
            output_lines.append(f"Chapter {chapter_number}")
            continue

        if current_book_name:
            # Get chapter definitions for the current book
            chapter_definitions = niv_book_data[current_book_name]["chapters"]

            # Check if we need to roll over to the next chapter
            # This must happen BEFORE processing the current verse
            if chapter_number <= len(chapter_definitions) and verse_number > chapter_definitions[chapter_number - 1]:
                chapter_number += 1
                verse_number = 1
                if chapter_number <= len(chapter_definitions):
                    output_lines.append(f"\nChapter {chapter_number}")

            output_lines.append(f"{verse_number} {cleaned_line}")
            verse_number += 1
            verses_found_in_book += 1
            
    finalize_previous_book_summary()

    for expected_book in expected_book_order:
        if expected_book not in processed_books_set:
            book_summary_log.append(f"{expected_book} - Missing")

    return "\n".join(output_lines).strip(), book_summary_log

class BibleFormatterApp:
    def __init__(self, master):
        self.master = master
        master.title("NIV Bible Formatter")
        master.geometry("600x450") # Set a default window size
        master.resizable(True, True) # Allow resizing

        self.input_file_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()
        self.output_file_name = tk.StringVar(value="formatted_bible_niv.txt") # Default output filename
        self.mismatch_log_file_name = tk.StringVar(value="niv_summary_log.txt") # Default mismatch log filename

        # Input File Selection
        self.input_frame = tk.LabelFrame(master, text="Input File", padx=10, pady=10)
        self.input_frame.pack(padx=10, pady=5, fill="x")

        self.input_label = tk.Label(self.input_frame, textvariable=self.input_file_path, wraplength=450, justify="left")
        self.input_label.pack(side="left", fill="x", expand=True)

        self.input_button = tk.Button(self.input_frame, text="Select File", command=self.select_input_file)
        self.input_button.pack(side="right")

        # Output Location Selection
        self.output_frame = tk.LabelFrame(master, text="Output Location", padx=10, pady=10)
        self.output_frame.pack(padx=10, pady=5, fill="x")

        self.output_folder_label = tk.Label(self.output_frame, textvariable=self.output_folder_path, wraplength=450, justify="left")
        self.output_folder_label.pack(side="left", fill="x", expand=True)

        self.output_folder_button = tk.Button(self.output_frame, text="Select Folder", command=self.select_output_folder)
        self.output_folder_button.pack(side="right")

        # Output Filename
        self.output_name_label_frame = tk.Frame(self.output_frame)
        self.output_name_label_frame.pack(fill="x", pady=(5,0))
        self.output_name_label = tk.Label(self.output_name_label_frame, text="Formatted Bible Filename:")
        self.output_name_label.pack(side="left", padx=(0, 5))
        self.output_name_entry = tk.Entry(self.output_name_label_frame, textvariable=self.output_file_name, width=30)
        self.output_name_entry.pack(side="left", fill="x", expand=True)

        # Mismatch Log Filename
        self.mismatch_name_label_frame = tk.Frame(self.output_frame)
        self.mismatch_name_label_frame.pack(fill="x", pady=(5,0))
        self.mismatch_name_label = tk.Label(self.mismatch_name_label_frame, text="Summary Log Filename:")
        self.mismatch_name_label.pack(side="left", padx=(0, 5))
        self.mismatch_name_entry = tk.Entry(self.mismatch_name_label_frame, textvariable=self.mismatch_log_file_name, width=30)
        self.mismatch_name_entry.pack(side="left", fill="x", expand=True)


        # Process Button
        self.process_button = tk.Button(master, text="Format Bible Text", command=self.process_files)
        self.process_button.pack(pady=20)

        # Status Message
        self.status_label = tk.Label(master, text="", fg="blue", wraplength=580, justify="center")
        self.status_label.pack(pady=10)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select NIV Bible Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.status_label.config(text="") # Clear previous status

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if folder_path:
            self.output_folder_path.set(folder_path)
            self.status_label.config(text="") # Clear previous status

    def process_files(self):
        input_path = self.input_file_path.get()
        output_folder = self.output_folder_path.get()
        output_name = self.output_file_name.get()
        mismatch_log_name = self.mismatch_log_file_name.get()

        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        if not output_name:
            messagebox.showerror("Error", "Please enter a filename for the formatted Bible text.")
            return
        if not mismatch_log_name:
            messagebox.showerror("Error", "Please enter a filename for the summary log.")
            return

        output_full_path = os.path.join(output_folder, output_name)
        mismatch_full_path = os.path.join(output_folder, mismatch_log_name)

        try:
            with open(input_path, 'r', encoding='utf-8') as infile:
                input_content = infile.read()

            formatted_content, book_summary_log = format_niv_bible_text(input_content)

            with open(output_full_path, 'w', encoding='utf-8') as outfile:
                outfile.write(formatted_content)

            status_message = f"Successfully formatted and saved to:\n{output_full_path}"
            if book_summary_log:
                with open(mismatch_full_path, 'w', encoding='utf-8') as logfile:
                    for entry in book_summary_log:
                        logfile.write(entry + "\n")
                status_message += f"\n\nBook summaries/warnings logged to:\n{mismatch_full_path}"
                messagebox.showwarning("Formatting Complete with Summaries/Warnings", status_message)
            else:
                messagebox.showinfo("Success", status_message)

            self.status_label.config(text=status_message, fg="green")

        except FileNotFoundError:
            messagebox.showerror("Error", "Input file not found. Please check the path.")
            self.status_label.config(text="Error: Input file not found.", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {e}")
            self.status_label.config(text=f"Error: {e}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = BibleFormatterApp(root)
    root.mainloop()
