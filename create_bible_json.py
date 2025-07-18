import json
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk # Import ttk for Combobox

def parse_bible_text(filepath, lang_key, bible_data, status_callback):
    """
    Parses a plain text Bible file according to the specified format
    and adds it to the main data dictionary. Handles multi-line verses.
    Applies unified book name detection logic (first non-blank line before Chapter 1)
    and reduces output verbosity.

    Args:
        filepath (str): The path to the input text file.
        lang_key (str): The language key (e.g., 'english', 'romanian')
                        to use as the top-level key in the JSON.
        bible_data (dict): The main dictionary to which parsed data will be added.
                            This dictionary will be modified in place.
        status_callback (function): A function to update the GUI status.
    """
    status_callback(f"Starting to parse '{os.path.basename(filepath)}' for language '{lang_key}'...")

    # Initialize counters for summary within this parsing run
    book_count = 0
    chapter_count = 0
    verse_count = 0
    
    # Ensure the language key exists in the bible_data dictionary
    if lang_key not in bible_data:
        bible_data[lang_key] = {}

    current_book = None
    current_chapter = None
    current_verse_num = None
    current_verse_text_lines = [] # Buffer to collect lines of a single verse
    
    # Regex patterns for identifying different parts of the text file
    chapter_pattern_en = re.compile(r"^\s*Chapter\s+(\d+)\s*$")
    chapter_pattern_ro = re.compile(r"^\s*Capitolul\s+(\d+)\s*$")
    verse_start_pattern = re.compile(r"^\s*(\d+)\s+(.*)$") # Matches "NUMBER TEXT"
    
    # Buffer to store the last few non-blank lines and their numbers
    # This is crucial for the "line before Chapter 1" logic.
    non_blank_line_buffer = [] # Stores (line_content, line_num)
    BUFFER_SIZE = 2 # We need at least the immediate preceding non-blank line

    # Helper function to finalize and store the current verse
    def finalize_current_verse():
        nonlocal current_verse_num, current_verse_text_lines, verse_count
        if current_book and current_chapter and current_verse_num and current_verse_text_lines:
            full_verse_text = " ".join(current_verse_text_lines).strip()
            # Ensure the nested structure exists before assigning the verse text
            if current_book not in bible_data[lang_key]:
                bible_data[lang_key][current_book] = {}
            if current_chapter not in bible_data[lang_key][current_book]:
                bible_data[lang_key][current_book][current_chapter] = {}
            bible_data[lang_key][current_book][current_chapter][current_verse_num] = full_verse_text
            # Reduced output: No status_callback for every stored verse
        current_verse_num = None
        current_verse_text_lines = []

    try:
        # Use 'utf-8-sig' to handle Byte Order Mark (BOM) if present, common in text files
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.strip()

                # Add current non-blank line to buffer before processing it.
                # This ensures the buffer always contains the most recent non-blank lines
                # needed for look-behind logic (e.g., for book names).
                if line: # Only add non-blank lines to the buffer
                    non_blank_line_buffer.append((line, line_num))
                    if len(non_blank_line_buffer) > BUFFER_SIZE:
                        non_blank_line_buffer.pop(0) # Keep buffer size limited to BUFFER_SIZE

                if not line:
                    continue # Skip blank lines

                # 1. Check if the line is a chapter declaration (English or Romanian)
                match_chapter_en = chapter_pattern_en.match(line)
                match_chapter_ro = chapter_pattern_ro.match(line)

                if match_chapter_en or match_chapter_ro:
                    # If we were collecting a verse, finalize it before moving to a new chapter
                    finalize_current_verse() 

                    chapter_num = match_chapter_en.group(1) if match_chapter_en else match_chapter_ro.group(1)
                    
                    # Unified logic for identifying book name when Chapter 1 is encountered
                    if int(chapter_num) == 1:
                        preceding_line_info = None
                        # The current chapter line is non_blank_line_buffer[-1] (if it was added to buffer)
                        # The line before it is non_blank_line_buffer[-2]
                        if len(non_blank_line_buffer) >= 2:
                            preceding_line_info = non_blank_line_buffer[-2]
                        
                        if preceding_line_info:
                            preceding_content, preceding_num = preceding_line_info[0].strip(), preceding_line_info[1]
                            if current_book != preceding_content: # Only update if it's a new book
                                current_book = preceding_content
                                book_count += 1
                                status_callback(f"Found book: '{current_book}' (from Line {preceding_num})")
                        else:
                            # This handles cases where Chapter 1 is the very first line, or no non-blank line preceded it.
                            status_callback(f"WARNING: Chapter 1 found without a preceding non-blank line to identify as book (Line {line_num}).")

                    # General chapter processing
                    if current_book is None:
                        status_callback(f"ERROR: Chapter '{line}' found before any book name (Line {line_num}). Aborting parse.")
                        return False # Abort parsing if no book context
                    
                    current_chapter = chapter_num
                    
                    # Initialize the chapter's dictionary within the current book if it doesn't exist
                    if current_book not in bible_data[lang_key]:
                        bible_data[lang_key][current_book] = {} 
                    bible_data[lang_key][current_book][current_chapter] = {}
                    status_callback(f"Found chapter: {current_chapter} (Book: {current_book})")
                    chapter_count += 1
                    continue # Move to next line

                # 2. Check if the line starts a new verse
                match_verse_start = verse_start_pattern.match(line)
                if match_verse_start:
                    # If we were collecting a previous verse, finalize it now
                    finalize_current_verse()

                    verse_num, verse_text = match_verse_start.groups()
                    
                    if current_book is None or current_chapter is None:
                        status_callback(f"WARNING: Skipping verse: '{line}' (No book/chapter context, Line {line_num}).")
                        continue # Skip this verse if context is missing
                    
                    current_verse_num = verse_num
                    current_verse_text_lines.append(verse_text)
                    verse_count += 1 # Increment verse count
                    # Reduced output: No status_callback for every started verse
                    continue # Move to next line
                
                # 3. If we are currently parsing a verse, this line is its continuation
                if current_verse_num is not None:
                    current_verse_text_lines.append(line)
                    # Reduced output: No status_callback for every continued verse
                    continue # Move to next line
                
                # 4. If none of the above, and it's not a book name identified by Chapter 1 rule,
                # then it's an unrecognized line. The general `book_name_pattern` is no longer used
                # as the primary book identification method.
                status_callback(f"WARNING: Unrecognized line: '{line}' (Line {line_num}).")
                
        # After the loop, finalize any remaining verse that was being collected
        finalize_current_verse()

        status_callback(f"Successfully finished parsing '{os.path.basename(filepath)}'.")
        status_callback(f"Summary for '{lang_key}': Books found: {book_count}, Chapters found: {chapter_count}, Verses found: {verse_count}")
        status_callback("--------------------------")
        return True

    except FileNotFoundError:
        status_callback(f"ERROR: File not found at {filepath}.")
        return False
    except Exception as e:
        status_callback(f"An error occurred while parsing {filepath}: {e}")
        return False

class BibleParserApp:
    def __init__(self, master):
        """
        Initializes the GUI application.

        Args:
            master (tk.Tk): The root Tkinter window.
        """
        self.master = master
        master.title("Bible Text to JSON Converter")
        master.geometry("600x700") # Set initial window size
        master.resizable(False, False) # Prevent resizing for simplicity

        # Variables to store file paths and data
        self.filepath = ""
        self.output_dir = ""
        self.output_filename = "bible_data.json" # Default output filename

        # The main dictionary that will hold all parsed Bible data (can accumulate multiple files)
        # This will be populated with data for the *current* parsing operation.
        # The merge logic handles combining it with existing file data.
        self.current_parsed_data = {} 

        # --- GUI Elements ---

        # 1. Source Text File Selection
        tk.Label(master, text="1. Select Source Text File:", font=('Arial', 10, 'bold')).pack(pady=5)
        
        self.file_path_label = tk.Label(master, text="No file selected", wraplength=500, fg="blue")
        self.file_path_label.pack()
        
        self.select_file_button = tk.Button(master, text="Browse Text File", command=self.select_source_file,
                                             bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'), relief="raised")
        self.select_file_button.pack(pady=5)

        # 2. Language Key Input (now a Combobox)
        tk.Label(master, text="2. Select Language Key:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.language_options = ["english", "romanian", "french", "spanish", "german", "portuguese", "italian"]
        self.lang_key_combobox = ttk.Combobox(master, values=self.language_options, width=58, state="readonly", font=('Arial', 10))
        self.lang_key_combobox.set("english") # Set default value
        self.lang_key_combobox.pack(pady=5)

        # 3. Output Folder and Filename
        tk.Label(master, text="3. Select Output Folder and Name JSON File:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.output_path_label = tk.Label(master, text="No output folder selected", wraplength=500, fg="blue")
        self.output_path_label.pack()
        
        self.select_output_button = tk.Button(master, text="Select Output Folder", command=self.select_output_folder,
                                             bg="#2196F3", fg="white", font=('Arial', 10, 'bold'), relief="raised")
        self.select_output_button.pack(pady=5)

        tk.Label(master, text="JSON Output Filename:", font=('Arial', 10)).pack(pady=5)
        self.output_filename_entry = tk.Entry(master, width=60, bd=2, relief="groove", font=('Arial', 10))
        self.output_filename_entry.insert(0, self.output_filename)
        self.output_filename_entry.pack(pady=5)

        # 4. Process Button
        self.process_button = tk.Button(master, text="Parse and Convert to JSON", command=self.process_files,
                                        bg="#FF9800", fg="white", font=('Arial', 12, 'bold'), relief="raised", padx=10, pady=5)
        self.process_button.pack(pady=20)

        # 5. Status Display Area
        tk.Label(master, text="Status / Log:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.status_text = scrolledtext.ScrolledText(master, height=10, width=70, state='disabled', wrap='word',
                                                     bg="#f0f0f0", fg="#333", font=('Consolas', 9))
        self.status_text.pack(pady=10)

    def update_status(self, message):
        """
        Updates the status text area in the GUI.

        Args:
            message (str): The message to display.
        """
        self.status_text.config(state='normal') # Enable editing
        self.status_text.insert(tk.END, message + "\n") # Insert message at the end
        self.status_text.see(tk.END) # Scroll to the end to show the latest message
        self.status_text.config(state='disabled') # Disable editing
        self.master.update_idletasks() # Force GUI update immediately

    def select_source_file(self):
        """
        Opens a file dialog for the user to select the input text file.
        """
        filepath = filedialog.askopenfilename(
            title="Select Bible Text File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            self.filepath = filepath
            self.file_path_label.config(text=f"Selected: {os.path.basename(filepath)}")
            self.update_status(f"Source file selected: {filepath}")

    def select_output_folder(self):
        """
        Opens a directory dialog for the user to select the output folder.
        """
        output_dir = filedialog.askdirectory(title="Select Output Folder for JSON")
        if output_dir:
            self.output_dir = output_dir
            self.output_path_label.config(text=f"Selected: {output_dir}")
            self.update_status(f"Output folder selected: {output_dir}")

    def process_files(self):
        """
        Initiates the parsing and JSON conversion process based on user selections.
        Handles loading/updating existing JSON files.
        """
        self.update_status("--- Starting Processing ---")
        
        # Clear previous parsing data to ensure only current file's data is processed
        self.current_parsed_data = {} 

        # Validate inputs
        if not self.filepath:
            messagebox.showerror("Error", "Please select a source text file.")
            self.update_status("Error: No source file selected.")
            return

        lang_key = self.lang_key_combobox.get().strip() # Get value from Combobox
        if not lang_key:
            messagebox.showerror("Error", "Please select a language key.")
            self.update_status("Error: No language key selected.")
            return

        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output folder.")
            self.update_status("Error: No output folder selected.")
            return

        self.output_filename = self.output_filename_entry.get().strip()
        if not self.output_filename:
            messagebox.showerror("Error", "Please enter a filename for the JSON output.")
            self.update_status("Error: No output filename entered.")
            return
        # Ensure the filename ends with .json
        if not self.output_filename.endswith(".json"):
            self.output_filename += ".json"
            self.output_filename_entry.delete(0, tk.END)
            self.output_filename_entry.insert(0, self.output_filename)
            self.update_status(f"Appended .json extension to filename: {self.output_filename}")

        output_full_path = os.path.join(self.output_dir, self.output_filename)

        # Call the parsing function to populate self.current_parsed_data with the new language's data
        success = parse_bible_text(self.filepath, lang_key, self.current_parsed_data, self.update_status)

        if success:
            combined_data = {}
            # Check if the output file already exists and load its content
            if os.path.exists(output_full_path):
                self.update_status(f"Loading existing JSON data from {output_full_path}...")
                try:
                    with open(output_full_path, 'r', encoding='utf-8') as f:
                        combined_data = json.load(f)
                    self.update_status("Existing JSON data loaded.")
                except json.JSONDecodeError:
                    self.update_status(f"WARNING: Existing file '{self.output_filename}' is not valid JSON. Overwriting.")
                    combined_data = {} # Start fresh if file is corrupt
                except Exception as e:
                    self.update_status(f"WARNING: Could not read existing JSON file: {e}. Starting with new data.")

            # --- START OF MODIFIED MERGE LOGIC ---
            # self.current_parsed_data will only contain data for the single lang_key just parsed.
            newly_parsed_lang_data = self.current_parsed_data.get(lang_key, {})

            if lang_key in combined_data:
                # If the language already exists in combined_data, we need to merge its books.
                # This is a deep merge for the books and their content.
                existing_lang_data = combined_data[lang_key]
                for book_name, book_content in newly_parsed_lang_data.items():
                    if book_name in existing_lang_data:
                        # If book exists, merge chapters (assuming chapters are unique per book)
                        existing_lang_data[book_name].update(book_content)
                    else:
                        # If book is new, just add it
                        existing_lang_data[book_name] = book_content
                self.update_status(f"Deep merging new data for existing language '{lang_key}'.")
            else:
                # If the language does not exist, simply add it.
                combined_data[lang_key] = newly_parsed_lang_data
                self.update_status(f"Adding new language '{lang_key}' to combined data.")
            # --- END OF MODIFIED MERGE LOGIC ---
            
            self.update_status(f"Writing all combined data to {output_full_path}...")
            try:
                # Write the combined dictionary to the JSON file
                with open(output_full_path, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, ensure_ascii=False, indent=2)
                self.update_status(f"SUCCESS! Your '{self.output_filename}' has been created/updated at:\n{self.output_dir}.")
                messagebox.showinfo("Success", f"JSON file created/updated successfully at:\n{output_full_path}")
            except Exception as e:
                self.update_status(f"An error occurred while writing the JSON file: {e}")
                messagebox.showerror("Error", f"An error occurred while writing the JSON file: {e}")
        else:
            messagebox.showerror("Parsing Failed", "Failed to parse the text file. Check the 'Status / Log' for details.")

# Main entry point for the application
if __name__ == "__main__":
    root = tk.Tk() # Create the main Tkinter window
    app = BibleParserApp(root) # Create an instance of the application
    root.mainloop() # Start the Tkinter event loop
