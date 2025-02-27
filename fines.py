import tkinter as tk
from tkinter import ttk
import sqlite3
import os
from datetime import datetime, timedelta
import random

class FinesChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Fines & Taxes Checker")
        self.root.geometry("800x600")
        
        # Connect to SQLite database
        self.conn = self.setup_database()
        
        # Create UI elements
        self.create_ui()
        
    def setup_database(self):
        # Ensure db directory exists
        os.makedirs("db", exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        
        # Create fines table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fines (
                id INTEGER PRIMARY KEY,
                iin TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                issue_date TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Check if we need to generate sample data
        cursor.execute("SELECT COUNT(*) FROM fines")
        if cursor.fetchone()[0] == 0:
            self.generate_sample_data(cursor)
            
        conn.commit()
        return conn
        
    def generate_sample_data(self, cursor):
        # Sample IINs
        iins = ['123456789012', '987654321098', '456789123045', '789123456078']
        
        # Sample fine types
        fine_types = [
            ('Traffic Violation', 'Speeding', 50, 250),
            ('Tax', 'Property Tax', 200, 1000),
            ('Administrative', 'Parking Violation', 30, 100),
            ('Tax', 'Income Tax', 500, 5000),
            ('Traffic Violation', 'Red Light', 80, 150),
            ('Administrative', 'Public Disturbance', 100, 300)
        ]
        
        # Generate sample fines
        current_date = datetime.now()
        sample_fines = []
        
        for iin in iins:
            # Decide how many fines this IIN has (0-5)
            num_fines = random.randint(0, 5)
            
            for _ in range(num_fines):
                fine_type = random.choice(fine_types)
                category = fine_type[0]
                details = fine_type[1]
                amount = random.uniform(fine_type[2], fine_type[3])
                
                # Random date within the last 2 years
                days_ago = random.randint(1, 730)
                issue_date = (current_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                # Status (80% chance of being unpaid for recent fines)
                if days_ago < 30 and random.random() < 0.8:
                    status = 'Unpaid'
                elif days_ago > 180 and random.random() < 0.7:
                    status = 'Paid'
                else:
                    status = random.choice(['Paid', 'Unpaid', 'In Process'])
                
                sample_fines.append((iin, category, round(amount, 2), issue_date, status, details))
        
        # Insert the sample data
        cursor.executemany('''
            INSERT INTO fines (iin, type, amount, issue_date, status, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_fines)
    
    def create_ui(self):
        # Top frame for input
        input_frame = ttk.Frame(self.root, padding="20 20 20 0")
        input_frame.pack(fill=tk.X)
        
        # IIN input
        ttk.Label(input_frame, text="Enter IIN:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.iin_var = tk.StringVar()
        iin_entry = ttk.Entry(input_frame, textvariable=self.iin_var, width=20, font=("Arial", 12))
        iin_entry.pack(side=tk.LEFT, padx=(0, 20))
        iin_entry.bind("<Return>", lambda event: self.check_fines())
        
        # Check button
        check_button = ttk.Button(input_frame, text="Check", command=self.check_fines, style="Check.TButton")
        check_button.pack(side=tk.LEFT)
        
        # Status frame
        self.status_frame = ttk.Frame(self.root, padding="20 10")
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="Enter an IIN and click Check", 
                                     font=("Arial", 12))
        self.status_label.pack(anchor=tk.W)
        
        # Create result frame
        self.result_frame = ttk.Frame(self.root, padding="20")
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable treeview for fines
        self.tree_frame = ttk.Frame(self.result_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        self.tree = ttk.Treeview(self.tree_frame, 
                                columns=("type", "amount", "date", "status", "details"),
                                show="headings",
                                yscrollcommand=self.tree_scroll.set)
        
        # Configure columns
        self.tree.column("type", width=150, anchor=tk.W)
        self.tree.column("amount", width=100, anchor=tk.E)
        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("details", width=250, anchor=tk.W)
        
        # Configure headings
        self.tree.heading("type", text="Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("date", text="Date")
        self.tree.heading("status", text="Status")
        self.tree.heading("details", text="Details")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # Define status colors
        self.root.option_add('*TFrame.background', '#f0f0f0')
        self.style = ttk.Style()
        self.style.configure('Green.TFrame', background='#d4edda')
        self.style.configure('Yellow.TFrame', background='#fff3cd')
        self.style.configure('Red.TFrame', background='#f8d7da')
        self.style.configure('Check.TButton', font=('Arial', 12))
        
        # Configure row tags
        self.tree.tag_configure('paid', background='#d4edda')
        self.tree.tag_configure('unpaid', background='#f8d7da')
        self.tree.tag_configure('processing', background='#fff3cd')
        
    def check_fines(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        iin = self.iin_var.get().strip()
        
        # Validate IIN
        if not iin:
            self.update_status("Please enter a valid IIN", "normal")
            return
            
        if not iin.isdigit() or len(iin) != 12:
            self.update_status("IIN must be a 12-digit number", "normal")
            return
        
        # Query database
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT type, amount, issue_date, status, details 
            FROM fines 
            WHERE iin = ? 
            ORDER BY issue_date DESC
        ''', (iin,))
        
        fines = cursor.fetchall()
        
        # Check results
        if not fines:
            self.update_status("No outstanding payments", "green")
            self.tree.insert("", tk.END, values=("No fines or taxes found", "", "", "", ""), tags=('paid',))
            return
        
        # Check for unpaid fines and taxes
        has_unpaid_fines = False
        has_unpaid_taxes = False
        
        for fine in fines:
            fine_type, amount, date, status, details = fine
            
            # Format amount
            formatted_amount = f"${amount:.2f}"
            
            # Determine row tag
            if status.lower() == 'paid':
                row_tag = 'paid'
            elif status.lower() == 'unpaid':
                row_tag = 'unpaid'
                if fine_type.lower() == 'tax':
                    has_unpaid_taxes = True
                else:
                    has_unpaid_fines = True
            else:
                row_tag = 'processing'
            
            # Add to tree
            self.tree.insert("", tk.END, values=(fine_type, formatted_amount, date, status, details), tags=(row_tag,))
        
        # Update status based on findings
        if has_unpaid_fines:
            self.update_status("Outstanding fines detected", "red")
        elif has_unpaid_taxes:
            self.update_status("Outstanding taxes detected", "yellow")
        else:
            self.update_status("No outstanding payments", "green")
    
    def update_status(self, message, level):
        self.status_label.config(text=message)
        
        if level == "green":
            self.status_frame.configure(style='Green.TFrame')
        elif level == "yellow":
            self.status_frame.configure(style='Yellow.TFrame')
        elif level == "red":
            self.status_frame.configure(style='Red.TFrame')
        else:
            self.status_frame.configure(style='')

if __name__ == "__main__":
    root = tk.Tk()
    app = FinesChecker(root)
    root.mainloop()