import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import firewall_manager

main_window = None

class PyFireApp(tb.Window):
    def __init__(self, app_state, config, **kwargs):
        super().__init__(**kwargs)
        global main_window
        main_window = self

        self.app_state = app_state
        self.config = config
        
        self.title("PyFire Dashboard")
        self.geometry("1000x650")
        
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        self.notebook = tb.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.f1 = tb.Frame(self.notebook)
        self.f2 = tb.Frame(self.notebook)
        self.f3 = tb.Frame(self.notebook)
        
        self.notebook.add(self.f1, text='Dashboard')
        self.notebook.add(self.f2, text='Rule Manager')
        self.notebook.add(self.f3, text='Live Alerts')
        
        self.create_dashboard_tab()
        self.create_rule_manager_tab()
        self.create_alerts_tab()

        self.after(1000, self.update_data)

    def update_data(self):
        self.update_dashboard_tab()
        self.update_rule_manager_tab()
        self.update_alerts_tab()
        self.after(2000, self.update_data)

    def create_dashboard_tab(self):
        stats, p_counts = self.app_state.get_stats()
        
        stats_frame = tb.Frame(self.f1)
        stats_frame.pack(pady=10, fill='x', padx=20)
        
        self.total_packets_label = tb.Label(stats_frame, text=f"Total Packets: {stats['total_packets']}", font=("Helvetica", 14))
        self.total_packets_label.pack(side='left', padx=20)
        
        self.blocked_conns_label = tb.Label(stats_frame, text=f"Blocked Connections: {stats['blocked_connections']}", font=("Helvetica", 14), bootstyle="danger")
        self.blocked_conns_label.pack(side='left', padx=20)
        
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_alpha(0.0)
        self.ax.set_facecolor('#222b32')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.f1)
        self.canvas.get_tk_widget().pack(pady=10, fill='both', expand=True)

    def update_dashboard_tab(self):
        stats, p_counts = self.app_state.get_stats()
        self.total_packets_label.config(text=f"Total Packets: {stats['total_packets']}")
        self.blocked_conns_label.config(text=f"Blocked Connections: {stats['blocked_connections']}")
        
        self.ax.clear()
        if sum(p_counts.values()) > 0:
            self.ax.pie(p_counts.values(), labels=p_counts.keys(), autopct='%1.1f%%', startangle=90, textprops={'color':"w"})
        else:
            self.ax.pie([1], labels=['No Data'], autopct='%1.1f%%', textprops={'color':"w"})
        self.ax.axis('equal')
        self.canvas.draw()
        
    def create_rule_manager_tab(self):
        manager_frame = tb.Frame(self.f2)
        manager_frame.pack(fill='x', padx=10, pady=10)

        ip_label = tb.Label(manager_frame, text="IP Address:")
        ip_label.pack(side='left', padx=(0, 5))

        self.ip_entry = tb.Entry(manager_frame, width=30)
        self.ip_entry.pack(side='left', padx=5)

        block_btn = tb.Button(manager_frame, text="Block IP", command=self.block_ip_action, bootstyle=DANGER)
        block_btn.pack(side='left', padx=5)

        unblock_btn = tb.Button(manager_frame, text="Unblock Selected", command=self.unblock_ip_action, bootstyle=SUCCESS)
        unblock_btn.pack(side='left', padx=5)

        self.blocked_ips_list = tb.Treeview(self.f2, columns=("Blocked IPs",), show="headings", bootstyle="primary")
        self.blocked_ips_list.heading("Blocked IPs", text="Currently Blocked IP Addresses")
        self.blocked_ips_list.pack(fill='both', expand=True, padx=10, pady=10)

    def update_rule_manager_tab(self):
        current_selection = self.blocked_ips_list.selection()
        
        for i in self.blocked_ips_list.get_children():
            self.blocked_ips_list.delete(i)
        
        blocked_ips = self.app_state.get_blocked_ips()
        for ip in blocked_ips:
            self.blocked_ips_list.insert("", "end", values=(ip,))
            
        if current_selection:
            self.blocked_ips_list.selection_set(current_selection)

    def block_ip_action(self):
        ip = self.ip_entry.get()
        if ip:
            firewall_manager.block_ip(ip)
            self.app_state.add_blocked_ip(ip)
            self.ip_entry.delete(0, END)
            self.update_rule_manager_tab()
    
    def unblock_ip_action(self):
        selected_items = self.blocked_ips_list.selection()
        for item in selected_items:
            ip = self.blocked_ips_list.item(item, 'values')[0]
            firewall_manager.unblock_ip(ip)
            self.app_state.remove_blocked_ip(ip)
        self.update_rule_manager_tab()

    def create_alerts_tab(self):
        self.alerts_list = tb.Treeview(self.f3, columns=("Time", "Message"), show="headings", bootstyle="info")
        self.alerts_list.heading("Time", text="Timestamp")
        self.alerts_list.heading("Message", text="Alert Message")
        self.alerts_list.column("Time", width=100, anchor='center')
        self.alerts_list.column("Message", width=600)
        self.alerts_list.pack(fill='both', expand=True, padx=10, pady=10)

    def update_alerts_tab(self):
        existing_alerts = {self.alerts_list.item(child)['values'][1] for child in self.alerts_list.get_children()}
        alerts = self.app_state.get_alerts()
        
        for timestamp, message in reversed(alerts):
            if message not in existing_alerts:
                self.alerts_list.insert("", 0, values=(timestamp, message))

def start_gui(app_state, config):
    app = PyFireApp(app_state, config, themename="cyborg")
    app.mainloop()
