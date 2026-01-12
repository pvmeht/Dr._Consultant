import tkinter as tk
from tkinter import messagebox, ttk
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/"
AUTH_URL = "http://127.0.0.1:8000/api/api-token-auth/"

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        
        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            
    def _add_placeholder(self, e):
        if not self.get():
            self.insert(0, self.placeholder)

    def get_value(self):
        val = self.get()
        return "" if val == self.placeholder else val

class HealthCOApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HealthCO Hospital Management System")
        self.geometry("1200x800")
        
        # Colors
        self.colors = {
            'bg_dark': '#0f172a',      # Sidebar BG
            'bg_main': '#f1f5f9',      # Main Content BG
            'card': '#ffffff',         # Card BG
            'primary': '#3b82f6',      # Accent Blue
            'text_light': '#e2e8f0',   # Sidebar Text
            'text_dark': '#0f172a',    # Main Text
            'success': '#10b981',
            'danger': '#ef4444'
        }
        
        self.setup_styles()
        self.configure(bg=self.colors['bg_main'])
        
        self.token = None
        self.user_role = None
        
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Auto-Login Check
        import os
        if os.path.exists("token.txt"):
            try:
                with open("token.txt", "r") as f:
                    saved_token = f.read().strip()
                self.token = saved_token
                self.show_dashboard_layout()
                self.start_auto_refresh()
            except:
                self.show_login_page()
        else:
            self.show_login_page()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Sidebar Button Style
        style.configure("Sidebar.TButton", 
                        background=self.colors['bg_dark'], 
                        foreground=self.colors['text_light'], 
                        font=("Segoe UI", 11), 
                        anchor="w", 
                        padding=15, 
                        borderwidth=0)
        style.map("Sidebar.TButton", 
                  background=[('active', self.colors['primary'])],
                  foreground=[('active', 'white')])
        
        # Main Styles
        style.configure("TFrame", background=self.colors['bg_main'])
        style.configure("Sidebar.TFrame", background=self.colors['bg_dark'])
        style.configure("Card.TFrame", background=self.colors['card'], relief="solid", borderwidth=0)
        
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), background=self.colors['bg_main'], foreground=self.colors['text_dark'])
        style.configure("CardTitle.TLabel", font=("Segoe UI", 14, "bold"), background=self.colors['card'], foreground=self.colors['text_dark'])
        
        style.configure("Primary.TButton", background=self.colors['primary'], foreground='white', font=("Segoe UI", 10, "bold"), padding=10, borderwidth=0)
        style.map("Primary.TButton", background=[('active', '#2563eb')])

        style.configure("Success.TButton", background=self.colors['success'], foreground='white', padding=8)
        style.configure("Danger.TButton", background=self.colors['danger'], foreground='white', padding=8)

        # Treeview
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground=self.colors['text_dark'], padding=10)

    def show_login_page(self):
        self.clear_frame()
        self.configure(bg=self.colors['bg_main'])
        
        frame = ttk.Frame(self.container, style="TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Login Card
        card = ttk.Frame(frame, style="Card.TFrame", padding=40)
        card.pack()
        
        ttk.Label(card, text="HealthCO System", font=("Segoe UI", 28, "bold"), background=self.colors['card'], foreground=self.colors['primary']).pack(pady=(0, 10))
        ttk.Label(card, text="Hospital Login", font=("Segoe UI", 12), background=self.colors['card'], foreground="#64748b").pack(pady=(0, 30))
        
        ttk.Label(card, text="Username", background=self.colors['card']).pack(anchor="w")
        self.username_entry = ttk.Entry(card, width=35, font=("Segoe UI", 11))
        self.username_entry.pack(pady=(5, 15))
        
        ttk.Label(card, text="Password", background=self.colors['card']).pack(anchor="w")
        self.password_entry = ttk.Entry(card, show="*", width=35, font=("Segoe UI", 11))
        self.password_entry.pack(pady=(5, 10))
        
        self.remember_var = tk.BooleanVar()
        self.show_pass_var = tk.BooleanVar()
        
        def toggle_password():
            if self.show_pass_var.get():
                self.password_entry.config(show="")
            else:
                self.password_entry.config(show="*")

        ttk.Checkbutton(card, text="Show Password", variable=self.show_pass_var, command=toggle_password).pack(anchor="w", pady=(0, 5))
        ttk.Checkbutton(card, text="Remember Me", variable=self.remember_var).pack(anchor="w", pady=(0, 20))
        
        ttk.Button(card, text="Login to Dashboard", style="Primary.TButton", command=self.login, cursor="hand2").pack(fill="x")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            response = requests.post(AUTH_URL, data={'username': username, 'password': password})
            if response.status_code == 200:
                self.token = response.json()['token']
                
                # Remember Me Logic
                if self.remember_var.get():
                    with open("token.txt", "w") as f:
                        f.write(self.token)
                
                self.show_dashboard_layout()
                self.start_auto_refresh()
            else:
                messagebox.showerror("Login Failed", f"Invalid credentials (Status: {response.status_code})")
        except Exception as e:
            messagebox.showerror("Error", f"Server Connection Failed: {str(e)}")

    def logout(self):
        self.token = None
        import os
        if os.path.exists("token.txt"):
             os.remove("token.txt")
        self.show_login_page()


# Update init and show_login_page to handle persistence
# This is handled by modifying those methods directly or ensuring they call each other correctly.
# Ideally I should have edited show_login_page earlier too. 
# Let's do a multi-replace for cleanliness or just accept I need to edit show_login_page separately.
# I'll edit show_login_page and __init__ logic in a separate block if I can't fit it here.
# Actually I'll create a `check_token` method and call it in __init__

    def show_dashboard_layout(self):
        self.clear_frame()
        
        # Sidebar
        sidebar = ttk.Frame(self.container, style="Sidebar.TFrame", width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        ttk.Label(sidebar, text="HealthCO", font=("Segoe UI", 22, "bold"), background=self.colors['bg_dark'], foreground='white').pack(pady=40, padx=20, anchor="w")
        
        menus = [
            ("Dashboard", self.load_data), 
            ("Hospital Info", self.show_hospital_info),
            ("Staff Management", self.show_staff_management),
            ("Bed Management", self.show_bed_management)
        ]
        
        for text, cmd in menus:
            btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=cmd, cursor="hand2")
            btn.pack(fill="x", pady=2)
            
        ttk.Button(sidebar, text="Logout", style="Sidebar.TButton", command=self.logout).pack(side="bottom", fill="x", pady=20)

        # Main Content Area
        self.main_area = ttk.Frame(self.container, style="TFrame", padding=30)
        self.main_area.pack(side="right", fill="both", expand=True)
        
        # Load default view
        self.load_data()

    def show_hospital_info(self):
        self.clear_main_area()
        ttk.Label(self.main_area, text="Hospital Details", style="Title.TLabel").pack(anchor="w", pady=(0, 20))
        
        card = ttk.Frame(self.main_area, style="Card.TFrame", padding=20)
        card.pack(fill="x")
        
        self.entries = {}
        fields = ['name', 'address', 'phone', 'email']
        
        for field in fields:
            frame = ttk.Frame(card, style="Card.TFrame")
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=field.title(), width=15, style="CardTitle.TLabel", font=("Segoe UI", 10)).pack(side="left")
            entry = ttk.Entry(frame, width=40)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[field] = entry
            
        ttk.Button(card, text="Update Details", style="Primary.TButton", command=self.update_hospital_details).pack(pady=20)
        self.load_hospital_details()

    def load_hospital_details(self):
        headers = {'Authorization': f'Token {self.token}'}
        try:
            # Assuming first hospital linked to user
            response = requests.get(API_URL + "hospital-details/", headers=headers)
            if response.status_code == 200 and len(response.json()) > 0:
                data = response.json()[0]
                self.hospital_id = data['id']
                for field in self.entries:
                    self.entries[field].insert(0, data.get(field, ''))
        except: pass

    def update_hospital_details(self):
        if not hasattr(self, 'hospital_id'): return
        data = {k: v.get() for k, v in self.entries.items()}
        headers = {'Authorization': f'Token {self.token}'}
        requests.patch(API_URL + f"hospital-details/{self.hospital_id}/", json=data, headers=headers)
        messagebox.showinfo("Success", "Hospital Details Updated")


    def show_staff_management(self):
        self.clear_main_area()
        ttk.Label(self.main_area, text="Staff Management", style="Title.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Add Staff Form
        form_frame = ttk.Frame(self.main_area, style="Card.TFrame", padding=10)
        form_frame.pack(fill="x", pady=(0, 20))
        
        self.staff_name = PlaceholderEntry(form_frame, "Staff Name", width=20)
        self.staff_name.pack(side="left", padx=5)
        
        # Role Dropdown
        self.staff_role = ttk.Combobox(form_frame, width=15, state="readonly")
        self.staff_role.set("Select Role")
        self.staff_role.pack(side="left", padx=5)
        self.fetch_staff_roles()
        
        self.staff_phone = PlaceholderEntry(form_frame, "Phone Number", width=15)
        self.staff_phone.pack(side="left", padx=5)
        
        ttk.Button(form_frame, text="Add Staff", style="Primary.TButton", command=self.add_staff).pack(side="left", padx=5)
        
        # List
        tree_frame = ttk.Frame(self.main_area, style="Card.TFrame", padding=2)
        tree_frame.pack(fill="both", expand=True)
        
        self.staff_tree = ttk.Treeview(tree_frame, columns=('id', 'name', 'role', 'phone'), show='headings', style="Treeview")
        self.staff_tree.heading('name', text='Name')
        self.staff_tree.heading('role', text='Role')
        self.staff_tree.heading('phone', text='Phone')
        self.staff_tree.column('id', width=0, stretch=False)
        self.staff_tree.pack(fill="both", expand=True)
        
        self.load_staff()

    def fetch_staff_roles(self):
        try:
            headers = {'Authorization': f'Token {self.token}'}
            response = requests.get(API_URL + "staff-roles/", headers=headers)
            if response.status_code == 200:
                self.staff_role['values'] = response.json()
                if self.staff_role['values']:
                    self.staff_role.current(0)
        except:
             self.staff_role['values'] = ['Other']

    def add_staff(self):
        name = self.staff_name.get_value()
        role = self.staff_role.get()
        phone = self.staff_phone.get_value()
        
        if not name or not phone or role == "Select Role":
             messagebox.showwarning("Warning", "Please fill all fields")
             return

        data = {
            'name': name,
            'role': role,
            'phone': phone
        }
        headers = {'Authorization': f'Token {self.token}'}
        requests.post(API_URL + "staff/", json=data, headers=headers)
        self.load_staff()
        # Reset
        self.staff_name.delete(0, 'end'); self.staff_name._add_placeholder(None)
        self.staff_phone.delete(0, 'end'); self.staff_phone._add_placeholder(None)

    def load_staff(self):
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(API_URL + "staff/", headers=headers)
        if response.status_code == 200:
            self.staff_tree.delete(*self.staff_tree.get_children())
            for s in response.json():
                self.staff_tree.insert('', 'end', values=(s['id'], s['name'], s['role'], s['phone']))

    def show_bed_management(self):
        self.clear_main_area()
        ttk.Label(self.main_area, text="Bed Management", style="Title.TLabel").pack(anchor="w", pady=(0, 20))

        # Add Bed
        form = ttk.Frame(self.main_area, style="TFrame")
        form.pack(fill="x", pady=(0,20))
        self.bed_ward = PlaceholderEntry(form, "Ward Name", width=15); self.bed_ward.pack(side="left", padx=5)
        self.bed_num = PlaceholderEntry(form, "Bed Number", width=10); self.bed_num.pack(side="left", padx=5)
        ttk.Button(form, text="Add Bed", style="Primary.TButton", command=self.add_bed).pack(side="left")

        # Bed Grid
        self.bed_frame = ttk.Frame(self.main_area, style="TFrame")
        self.bed_frame.pack(fill="both", expand=True)
        self.load_beds()

    def add_bed(self):
        ward = self.bed_ward.get_value()
        num = self.bed_num.get_value()
        if not ward or not num: return

        data = {'ward': ward, 'number': num}
        headers = {'Authorization': f'Token {self.token}'}
        requests.post(API_URL + "beds/", json=data, headers=headers)
        self.load_beds()
        # Reset
        self.bed_ward.delete(0, 'end'); self.bed_ward._add_placeholder(None)
        self.bed_num.delete(0, 'end'); self.bed_num._add_placeholder(None)

    def load_beds(self):
        for w in self.bed_frame.winfo_children(): w.destroy()
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(API_URL + "beds/", headers=headers)
        
        if response.status_code == 200:
            row, col = 0, 0
            for bed in response.json():
                color = self.colors['danger'] if bed['is_occupied'] else self.colors['success']
                card = tk.Frame(self.bed_frame, bg="white", padx=10, pady=10)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                tk.Label(card, text=f"{bed['ward']} - {bed['number']}", font=("Segoe UI", 12, "bold"), bg="white").pack()
                tk.Label(card, text="Occupied" if bed['is_occupied'] else "Available", fg=color, bg="white").pack()
                
                btn_text = "Free" if bed['is_occupied'] else "Occupy"
                tk.Button(card, text=btn_text, bg=self.colors['primary'], fg="white", 
                          command=lambda b=bed: self.toggle_bed(b)).pack(pady=5)
                
                col += 1
                if col > 3: col=0; row+=1

    def toggle_bed(self, bed):
        headers = {'Authorization': f'Token {self.token}'}
        new_status = not bed['is_occupied']
        requests.patch(API_URL + f"beds/{bed['id']}/", json={'is_occupied': new_status}, headers=headers)
        self.load_beds()

    def load_data(self):
        self.clear_main_area()
        ttk.Label(self.main_area, text="Appointment Management", style="Title.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Tabs
        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        self.tab_pending = ttk.Frame(self.notebook)
        self.tab_confirmed = ttk.Frame(self.notebook)
        self.tab_completed = ttk.Frame(self.notebook)
        self.tab_cancelled = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_pending, text='Pending')
        self.notebook.add(self.tab_confirmed, text='Confirmed')
        self.notebook.add(self.tab_completed, text='Completed')
        self.notebook.add(self.tab_cancelled, text='Cancelled')
        
        # Setup tables for each tab
        self.trees = {}
        for status, tab in [('PENDING', self.tab_pending), ('CONFIRMED', self.tab_confirmed), 
                            ('COMPLETED', self.tab_completed), ('CANCELLED', self.tab_cancelled)]:
            self.create_tree(tab, status)
            
        self.start_auto_refresh()

    def create_tree(self, parent, status):
        # Actions Frame
        action_frame = ttk.Frame(parent, padding=10)
        action_frame.pack(fill='x')
        
        if status == 'PENDING':
            ttk.Button(action_frame, text="Confirm", style="Success.TButton", command=lambda: self.update_status(status, 'CONFIRMED')).pack(side='left', padx=5)
            ttk.Button(action_frame, text="Cancel", style="Danger.TButton", command=lambda: self.update_status(status, 'CANCELLED')).pack(side='left', padx=5)
        elif status == 'CONFIRMED':
            ttk.Button(action_frame, text="Proceed to Consultation", style="Primary.TButton", command=self.open_consultation).pack(side='left', padx=5)
            ttk.Button(action_frame, text="Cancel", style="Danger.TButton", command=lambda: self.update_status(status, 'CANCELLED')).pack(side='left', padx=5)
        elif status == 'COMPLETED':
            ttk.Button(action_frame, text="View Details", command=self.view_details).pack(side='left', padx=5)
            
        # Tree
        cols = ('id', 'patient', 'doctor', 'date', 'time')
        tree = ttk.Treeview(parent, columns=cols, show='headings', style="Treeview")
        for c in cols: tree.heading(c, text=c.capitalize())
        tree.column('id', width=50); tree.column('time', width=100)
        tree.pack(fill='both', expand=True)
        self.trees[status] = tree
        
    def refresh_all_tables(self):
        headers = {'Authorization': f'Token {self.token}'}
        try:
            response = requests.get(API_URL + "appointments/", headers=headers)
            if response.status_code == 200:
                # Store selection to restore later? For now just clear/reload
                for t in self.trees.values(): t.delete(*t.get_children())
                
                for apt in response.json():
                    status = apt['status']
                    if(status in self.trees):
                        self.trees[status].insert('', 'end', values=(
                            apt['id'], apt['patient_name'], apt['doctor_name'], apt['date'], apt['time']
                        ))
        except Exception as e:
            print(e)
            
    def start_auto_refresh(self):
        self.refresh_all_tables()
        self.after(30000, self.start_auto_refresh) # 30 seconds

    def update_status(self, current_status, new_status):
        tree = self.trees[current_status]
        sel = tree.selection()
        if not sel: return
        apt_id = tree.item(sel[0])['values'][0]
        
        try:
            requests.patch(API_URL + f"appointments/{apt_id}/", json={'status': new_status}, headers={'Authorization': f'Token {self.token}'})
            self.refresh_all_tables()
        except: pass

    def open_consultation(self):
        tree = self.trees['CONFIRMED']
        sel = tree.selection()
        if not sel: return
        apt_id = tree.item(sel[0])['values'][0]
        
        ConsultationWindow(self, apt_id, self.token)
        
    def view_details(self):
        tree = self.trees['COMPLETED']
        sel = tree.selection()
        if not sel: return
        apt_id = tree.item(sel[0])['values'][0]
        
        DetailsWindow(self, apt_id, self.token)

    def create_stat_card(self, parent, title, value, color):
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(side="left", fill="x", expand=True, padx=10)
        
        ttk.Label(card, text=title, font=("Segoe UI", 10, "bold"), foreground="#64748b", background="white").pack(anchor="w")
        ttk.Label(card, text=value, font=("Segoe UI", 24, "bold"), foreground=color, background="white").pack(anchor="w")

    def logout(self):
        self.token = None
        self.show_login_page()

    def clear_frame(self):
        for widget in self.container.winfo_children(): widget.destroy()

    def clear_main_area(self):
        for widget in self.main_area.winfo_children(): widget.destroy()

class ConsultationWindow(tk.Toplevel):
    def __init__(self, parent, apt_id, token):
        super().__init__(parent)
        self.title("Clinical Consultation")
        self.geometry("900x750")
        self.apt_id = apt_id
        self.token = token
        self.parent_app = parent
        
        self.setup_ui()
        
    def setup_ui(self):
        # Scrollable Layout
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main = ttk.Frame(scrollable_frame, padding=20)
        main.pack(fill='both', expand=True)
        
        # Ensure scrollable frame width matches canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.create_window((0,0), window=scrollable_frame, anchor="nw"), width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Header
        ttk.Label(main, text="New Consultation", font=("Segoe UI", 18, "bold"), foreground="#3b82f6").pack(anchor='w', pady=(0,10))

        # Section: Patient Info (New)
        pat_frame = ttk.LabelFrame(main, text="Patient Details", padding=10)
        pat_frame.pack(fill='x', pady=5)
        
        self.pat_info_label = ttk.Label(pat_frame, text="Loading...", font=("Segoe UI", 10))
        self.pat_info_label.pack(anchor='w')
        
        # Fetch Patient Data
        self.fetch_patient_data()

        # Section 0: Session Info
        info_frame = ttk.LabelFrame(main, text="Session Details", padding=10)
        info_frame.pack(fill='x', pady=5)
        
        self.nurse_name = PlaceholderEntry(info_frame, "Nurse Name", width=30)
        self.nurse_name.pack(side='left', padx=5)
        
        # Section 1: Vitals
        v_frame = ttk.LabelFrame(main, text="Vitals", padding=10)
        v_frame.pack(fill='x', pady=5)
        
        self.bp = PlaceholderEntry(v_frame, "BP (120/80)", width=15); self.bp.pack(side='left', padx=5)
        self.pulse = PlaceholderEntry(v_frame, "Pulse", width=10); self.pulse.pack(side='left', padx=5)
        self.temp = PlaceholderEntry(v_frame, "Temp (C)", width=10); self.temp.pack(side='left', padx=5)
        self.weight = PlaceholderEntry(v_frame, "Weight (kg)", width=10); self.weight.pack(side='left', padx=5)
        self.height = PlaceholderEntry(v_frame, "Height (ft)", width=10); self.height.pack(side='left', padx=5)
        
        # Section 2: Clinical
        c_frame = ttk.LabelFrame(main, text="Clinical Assessment", padding=10)
        c_frame.pack(fill='both', expand=True, pady=5)
        
        grid_frame = ttk.Frame(c_frame)
        grid_frame.pack(fill='x')
        
        ttk.Label(grid_frame, text="Symptoms").grid(row=0, column=0, sticky='w')
        self.symptoms = tk.Text(grid_frame, height=3, width=40); self.symptoms.grid(row=1, column=0, padx=5, pady=2)
        
        ttk.Label(grid_frame, text="Diagnosis").grid(row=0, column=1, sticky='w')
        self.diagnosis = tk.Text(grid_frame, height=3, width=40); self.diagnosis.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(c_frame, text="Advice / Plan").pack(anchor='w', pady=(5,0))
        self.advice = tk.Text(c_frame, height=2, width=80); self.advice.pack(fill='x', pady=2)
        
        # Section 3: Prescription
        p_frame = ttk.LabelFrame(main, text="Prescription", padding=10)
        p_frame.pack(fill='x', pady=5)
        
        
        input_row = ttk.Frame(p_frame); input_row.pack(fill='x')
        self.med_name = PlaceholderEntry(input_row, "Medicine Name", width=20); self.med_name.pack(side='left', padx=2)
        self.med_dose = PlaceholderEntry(input_row, "Dosage (1-0-1)", width=12); self.med_dose.pack(side='left', padx=2)
        self.med_dur = PlaceholderEntry(input_row, "Duration", width=12); self.med_dur.pack(side='left', padx=2)
        self.med_instr = PlaceholderEntry(input_row, "Instruction (e.g. After Food)", width=20); self.med_instr.pack(side='left', padx=2)
        ttk.Button(input_row, text="Add", command=self.add_med).pack(side='left', padx=5)
        
        self.med_tree = ttk.Treeview(p_frame, columns=('name', 'dose', 'dur', 'instr'), show='headings', height=4)
        self.med_tree.heading('name', text='Medicine'); self.med_tree.heading('dose', text='Dosage')
        self.med_tree.heading('dur', text='Duration'); self.med_tree.heading('instr', text='Instruction')
        self.med_tree.column('name', width=150); self.med_tree.column('dose', width=80)
        self.med_tree.column('dur', width=80); self.med_tree.column('instr', width=150)
        self.med_tree.pack(fill='x', pady=5)
        
        # Submit
        ttk.Button(main, text="Complete Consultation", style="Success.TButton", command=self.submit).pack(pady=10)
        
        self.load_existing()

    def fetch_patient_data(self):
        headers = {'Authorization': f'Token {self.token}'}
        try:
            r = requests.get(API_URL + f"appointments/{self.apt_id}/", headers=headers)
            if r.status_code == 200:
                apt = r.json()
                p = apt.get('patient_details', {})
                name = f"{p.get('first_name','')} {p.get('last_name','')}".strip() or p.get('username','Unknown')
                info = f"Name: {name}   |   Age: {p.get('age', 'N/A')}   |   Gender: {p.get('gender', '-')}   |   Blood Group: {p.get('blood_group', '-')}   |   Phone: {p.get('phone', '-')}"
                self.pat_info_label.config(text=info)
        except Exception as e:
            self.pat_info_label.config(text=f"Error fetching details: {e}")

    def load_existing(self):
        self.existing_id = None
        headers = {'Authorization': f'Token {self.token}'}
        try:
            # Filter API by appointment ID manually or check list
            # Ideally API should support ?appointment=ID
            r = requests.get(API_URL + "consultations/", headers=headers)
            if r.status_code == 200:
                data = r.json()
                found = next((c for c in data if c['appointment'] == self.apt_id), None)
                if found:
                    self.existing_id = found['id']
                    self.nurse_name.insert(0, found.get('nurse_name', ''))
                    
                    self.bp.insert(0, found.get('bp', ''))
                    self.pulse.insert(0, found.get('pulse', ''))
                    self.temp.insert(0, found.get('temperature', ''))
                    self.weight.insert(0, found.get('weight', ''))
                    self.height.insert(0, found.get('height', ''))
                    
                    self.symptoms.insert("1.0", found.get('symptoms', ''))
                    self.diagnosis.insert("1.0", found.get('diagnosis', ''))
                    self.advice.insert("1.0", found.get('advice', ''))
                    
                    # Clear placeholders if data exists
                    for w in [self.nurse_name, self.bp, self.pulse, self.temp, self.weight, self.height]:
                        w._clear_placeholder(None)

                    # Load Meds
                    for p in found.get('prescriptions', []):
                         self.med_tree.insert('', 'end', values=(p['medicine_name'], p['dosage'], p['duration'], p.get('instructions', '')))
                         
        except Exception as e: print(e)

    def add_med(self):
        n = self.med_name.get_value()
        d = self.med_dose.get_value()
        dur = self.med_dur.get_value()
        instr = self.med_instr.get_value()
        if n and d:
            self.med_tree.insert('', 'end', values=(n, d, dur, instr))
            
    def submit(self):
        data = {
            'appointment': self.apt_id,
            'nurse_name': self.nurse_name.get_value(), # Added Nurse
            'bp': self.bp.get_value(),
            'pulse': self.pulse.get_value(),
            'temperature': self.temp.get_value(),
            'weight': self.weight.get_value(),
            'height': self.height.get_value(),
            'symptoms': self.symptoms.get("1.0", "end-1c"),
            'diagnosis': self.diagnosis.get("1.0", "end-1c"),
            'advice': self.advice.get("1.0", "end-1c"),
            'completed_at': datetime.now().isoformat(),
            'prescriptions_data': []
        }
        
        for item in self.med_tree.get_children():
            v = self.med_tree.item(item)['values']
            data['prescriptions_data'].append({
                'medicine_name': v[0],
                'dosage': v[1],
                'duration': v[2],
                'instructions': v[3]
            })
            
        headers = {'Authorization': f'Token {self.token}'}
        try:
            if self.existing_id:
                r = requests.patch(API_URL + f"consultations/{self.existing_id}/", json=data, headers=headers)
                success_code = 200
            else:
                r = requests.post(API_URL + "consultations/", json=data, headers=headers)
                success_code = 201
                
            if r.status_code == success_code:
                requests.patch(API_URL + f"appointments/{self.apt_id}/", json={'status': 'COMPLETED'}, headers=headers)
                messagebox.showinfo("Success", "Consultation Completed")
                self.parent_app.refresh_all_tables()
                self.destroy()
            else:
                 messagebox.showerror("Error", f"Failed: {r.text}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class DetailsWindow(tk.Toplevel):
    def __init__(self, parent, apt_id, token):
        super().__init__(parent)
        self.title("Appointment Report")
        self.geometry("850x700")
        self.apt_id = apt_id
        self.token = token
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Scrollable Frame
        canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="white")
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        self.header_label = tk.Label(self.scroll_frame, text="Medical Consultation Report", font=("Segoe UI", 22, "bold"), bg="white", fg="#0f172a")
        self.header_label.pack(pady=20, padx=30, anchor="center")
        
        self.session_frame = tk.LabelFrame(self.scroll_frame, text="Session Details", font=("Segoe UI", 12, "bold"), bg="white", padx=20, pady=10)
        self.session_frame.pack(fill="x", padx=30, pady=10)
        
        self.vitals_frame = tk.LabelFrame(self.scroll_frame, text="Vitals", font=("Segoe UI", 12, "bold"), bg="white", padx=20, pady=10)
        self.vitals_frame.pack(fill="x", padx=30, pady=10)
        
        self.clinical_frame = tk.LabelFrame(self.scroll_frame, text="Clinical Assessment", font=("Segoe UI", 12, "bold"), bg="white", padx=20, pady=10)
        self.clinical_frame.pack(fill="x", padx=30, pady=10)
        
        self.pres_frame = tk.LabelFrame(self.scroll_frame, text="Prescription", font=("Segoe UI", 12, "bold"), bg="white", padx=20, pady=10)
        self.pres_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Button(self.scroll_frame, text="Close Report", bg="#ef4444", fg="white", font=("Segoe UI", 10), command=self.destroy).pack(pady=30)

    def add_field(self, parent, label, value):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=15, anchor="w").pack(side="left")
        tk.Label(f, text=value, font=("Segoe UI", 10), bg="white", wraplength=500, justify="left").pack(side="left", fill="x")

    def load_data(self):
        headers = {'Authorization': f'Token {self.token}'}
        try:
            r = requests.get(API_URL + "consultations/", headers=headers)
            if r.status_code == 200:
                data = r.json()
                found = next((c for c in data if c['appointment'] == self.apt_id), None)
                if found:
                    self.display_data(found)
                else:
                    tk.Label(self.scroll_frame, text="No Record Found", fg="red", bg="white").pack()
        except Exception as e:
            tk.Label(self.scroll_frame, text=f"Error: {e}", fg="red", bg="white").pack()

    def display_data(self, data):
        # Session
        self.add_field(self.session_frame, "Start Time:", data['started_at'])
        self.add_field(self.session_frame, "Nurse:", data.get('nurse_name', '-'))
        
        # Vitals
        v_txt = f"BP: {data['bp']}   Pulse: {data['pulse']}   Temp: {data['temperature']}   Weight: {data['weight']}"
        tk.Label(self.vitals_frame, text=v_txt, font=("Segoe UI", 11), bg="#f1f5f9", padx=10, pady=5, width=60).pack()
        
        # Clinical
        self.add_field(self.clinical_frame, "Symptoms:", data['symptoms'])
        self.add_field(self.clinical_frame, "Diagnosis:", data['diagnosis'])
        self.add_field(self.clinical_frame, "Advice:", data['advice'])
        
        # Prescription
        if data['prescriptions']:
            # Header
            h = tk.Frame(self.pres_frame, bg="#e2e8f0", padx=5, pady=5)
            h.pack(fill="x")
            tk.Label(h, text="Medicine", width=25, bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(h, text="Dosage", width=10, bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(h, text="Duration", width=10, bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(h, text="Instruction", width=20, bg="#e2e8f0", font=("Segoe UI", 9, "bold")).pack(side="left")
            
            for p in data['prescriptions']:
                row = tk.Frame(self.pres_frame, bg="white", borderwidth=1, relief="solid")
                row.pack(fill="x", pady=2)
                tk.Label(row, text=p['medicine_name'], width=25, bg="white").pack(side="left")
                tk.Label(row, text=p['dosage'], width=10, bg="white").pack(side="left")
                tk.Label(row, text=p['duration'], width=10, bg="white").pack(side="left")
                tk.Label(row, text=p.get('instructions', '-'), width=20, bg="white").pack(side="left")
        else:
             tk.Label(self.pres_frame, text="No medicines prescribed", bg="white").pack()

if __name__ == "__main__":
    app = HealthCOApp()
    app.mainloop()
