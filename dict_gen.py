import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import random

class DictionaryProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Dictionary Processor Tool v2.0")
        self.root.geometry("650x500")

        # --- UI Elements ---
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", padding=6, font=("Helvetica", 10))
        style.configure("TButton", padding=6, font=("Helvetica", 10, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        header_label = ttk.Label(main_frame, text="Generate Final Dictionary JSON", style="Header.TLabel")
        header_label.pack(pady=(0, 15))

        # --- Variables ---
        self.source_path = tk.StringVar()
        self.profanity_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.min_len_var = tk.IntVar(value=4)
        self.max_len_var = tk.IntVar(value=9)
        self.reduction_var = tk.DoubleVar(value=80.0)
        self.minify_var = tk.BooleanVar(value=True)

        # --- UI Layout ---
        ttk.Label(main_frame, text="1. Select Source Dictionary File (.json or .jsonl):").pack(anchor=tk.W)
        source_frame = ttk.Frame(main_frame); source_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(source_frame, textvariable=self.source_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).pack(side=tk.RIGHT)

        ttk.Label(main_frame, text="2. Select Profanity/Exclusion File (.txt):").pack(anchor=tk.W)
        profanity_frame = ttk.Frame(main_frame); profanity_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(profanity_frame, textvariable=self.profanity_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(profanity_frame, text="Browse...", command=self.browse_profanity).pack(side=tk.RIGHT)

        options_frame = ttk.LabelFrame(main_frame, text="3. Filtering and Sizing Options", padding=10)
        options_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(options_frame, text="Word Length:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Spinbox(options_frame, from_=3, to=8, textvariable=self.min_len_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(options_frame, text="to").grid(row=0, column=2)
        ttk.Spinbox(options_frame, from_=9, to=15, textvariable=self.max_len_var, width=5).grid(row=0, column=3, padx=5)

        ttk.Label(options_frame, text="Random Reduction %:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        reduction_slider = ttk.Scale(options_frame, from_=0, to=95, orient=tk.HORIZONTAL, variable=self.reduction_var, length=200, command=lambda s:self.reduction_var.set(float(f"{float(s):.0f}")))
        reduction_slider.grid(row=1, column=1, columnspan=3, sticky=tk.EW)
        ttk.Label(options_frame, textvariable=self.reduction_var).grid(row=1, column=4, padx=5)

        ttk.Checkbutton(options_frame, text="Generate Minified (Smaller File)", variable=self.minify_var).grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="4. Select Output Location and Name:").pack(anchor=tk.W)
        output_frame = ttk.Frame(main_frame); output_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.RIGHT)

        generate_button = ttk.Button(main_frame, text="Generate JSON File", command=self.process_files)
        generate_button.pack(pady=20, ipady=10)

    def browse_source(self): path = filedialog.askopenfilename(title="Select Source File", filetypes=(("JSON files", "*.json*"), ("All files", "*.*"))); self.source_path.set(path) if path else None
    def browse_profanity(self): path = filedialog.askopenfilename(title="Select Profanity TXT", filetypes=(("Text Files", "*.txt"),)); self.profanity_path.set(path) if path else None
    def browse_output(self): path = filedialog.asksaveasfilename(title="Save JSON As", defaultextension=".json", filetypes=(("JSON Files", "*.json"),)); self.output_path.set(path) if path else None
    def clean_romanian_html(self, raw_html):
        clean_text = re.sub(r'<[^>]+>', '', raw_html)
        clean_text = re.sub(r'^[A-ZĂÂÎȘȚ,\s]+,', '', clean_text, count=1)
        clean_text = re.split(r'-\s+Din\s+', clean_text)[0]
        clean_text = clean_text.strip()
        return clean_text[0].upper() + clean_text[1:] if clean_text else ""

    def process_files(self):
        source_file, profanity_file, output_file = self.source_path.get(), self.profanity_path.get(), self.output_path.get()
        min_len, max_len, reduction_percent = self.min_len_var.get(), self.max_len_var.get(), self.reduction_var.get()
        if not source_file or not output_file: messagebox.showerror("Error", "Source file and Output location are required."); return

        profanity_set = set()
        if profanity_file:
            with open(profanity_file, 'r', encoding='utf-8') as f: profanity_set = {line.strip().lower() for line in f}
        
        print(f"Starting to process '{source_file}'...")
        initial_dictionary = {}
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                if source_file.endswith('.jsonl'):
                    print(f"Phase 1: Reading English Wiktionary (.jsonl)... Settings: Length {min_len}-{max_len}")
                    for i, line in enumerate(f):
                        if i % 200000 == 0 and i > 0: print(f"  ...scanned {i} lines...")
                        try:
                            entry = json.loads(line)
                            if entry.get("lang_code") != "en": continue
                            word = entry.get("word", "").upper()
                            if not (min_len <= len(word) <= max_len and word.isalpha() and word.lower() not in profanity_set and word not in initial_dictionary): continue
                            senses = entry.get("senses", [])
                            if senses and senses[0].get("glosses"):
                                definition = senses[0]["glosses"][0]
                                definition = re.sub(r'\(.+?\)', '', definition).strip()
                                if definition: initial_dictionary[word] = definition[0].upper() + definition[1:]
                        except (json.JSONDecodeError, AttributeError): continue
                else:
                    print(f"Phase 1: Reading Romanian DEX (.json)... Settings: Length {min_len}-{max_len}")
                    data = json.load(f)
                    for word_raw, def_raw in data.items():
                        word = word_raw.upper()
                        if not (min_len <= len(word) <= max_len and all('A' <= char <= 'Z' or char in 'ĂÂÎȘȚ' for char in word) and word.lower() not in profanity_set and word not in initial_dictionary): continue
                        definition = self.clean_romanian_html(def_raw)
                        if definition: initial_dictionary[word] = definition
            
            print(f"\nPhase 1 Complete. Found {len(initial_dictionary)} total valid words matching criteria.")

            # --- NEW: Check if any words were found before proceeding ---
            if not initial_dictionary:
                messagebox.showwarning("Processing Warning", f"Found 0 words matching your criteria (Length: {min_len}-{max_len}).\n\nPlease check your source file or relax the filtering options.\nNo output file was generated.")
                return

            print(f"Phase 2: Reducing dictionary by {reduction_percent:.0f}%...")
            all_words = list(initial_dictionary.keys())
            random.shuffle(all_words)
            keep_percentage = 1.0 - (reduction_percent / 100.0)
            num_to_keep = int(len(all_words) * keep_percentage)
            final_words = all_words[:num_to_keep]
            final_dictionary = {word: initial_dictionary[word] for word in final_words}
            
            print(f"Phase 2 Complete. Final dictionary size: {len(final_dictionary)} words.")

            with open(output_file, 'w', encoding='utf-8') as f:
                if self.minify_var.get():
                    json.dump(final_dictionary, f, ensure_ascii=False, separators=(',', ':'))
                else:
                    json.dump(final_dictionary, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Success", f"Successfully generated '{output_file}' with {len(final_dictionary)} words.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryProcessor(root)
    root.mainloop()