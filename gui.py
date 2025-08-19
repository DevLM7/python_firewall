import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def start_gui(app_state, config):
    app = tb.Window(themename="cyborg")
    app.title("Python UTM Dashboard")
    app.geometry("900x600")

    notebook = tb.Notebook(app)
    notebook.pack(pady=10, padx=10, fill="both", expand=True)

    f1 = tb.Frame(notebook)
    f2 = tb.Frame(notebook)
    f3 = tb.Frame(notebook)
    
    notebook.add(f1, text='Dashboard')
    notebook.add(f2, text='Rule Manager')
    notebook.add(f3, text='Live Alerts')
    
    create_dashboard_tab(f1, app_state)
    create_rule_manager_tab(f2, app_state)
    create_alerts_tab(f3, app_state)

    def update_data():
        update_dashboard_tab(f1, app_state)
        update_alerts_tab(f3, app_state)
        app.after(2000, update_data)
        
    update_data()
    app.mainloop()

def create_dashboard_tab(tab, app_state):
    stats = app_state.get_stats()
    
    stats_frame = tb.Frame(tab)
    stats_frame.pack(pady=10, fill='x', padx=20)
    
    tab.total_packets_label = tb.Label(stats_frame, text=f"Total Packets: {stats['total_packets']}", font=("Helvetica", 14))
    tab.total_packets_label.pack(side='left', padx=10)
    
    tab.blocked_packets_label = tb.Label(stats_frame, text=f"Blocked Connections: {stats['blocked_packets']}", font=("Helvetica", 14), bootstyle="danger")
    tab.blocked_packets_label.pack(side='left', padx=10)
    
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.pie(stats['protocol_counts'].values(), labels=stats['protocol_counts'].keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    fig.patch.set_alpha(0)
    
    tab.canvas = FigureCanvasTkAgg(fig, master=tab)
    tab.canvas.get_tk_widget().pack(pady=10)

def update_dashboard_tab(tab, app_state):
    stats = app_state.get_stats()
    tab.total_packets_label.config(text=f"Total Packets: {stats['total_packets']}")
    tab.blocked_packets_label.config(text=f"Blocked Connections: {stats['blocked_packets']}")
    
    ax = tab.canvas.figure.axes[0]
    ax.clear()
    
    if sum(stats['protocol_counts'].values()) > 0:
        ax.pie(stats['protocol_counts'].values(), labels=stats['protocol_counts'].keys(), autopct='%1.1f%%', startangle=90)
    else:
        ax.pie([1], labels=['No Data'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    tab.canvas.draw()
    
def create_rule_manager_tab(tab, app_state):
    pass

def create_alerts_tab(tab, app_state):
    tab.alerts_list = tb.Treeview(tab, columns=("Time", "Message"), show="headings", bootstyle="info")
    tab.alerts_list.heading("Time", text="Timestamp")
    tab.alerts_list.heading("Message", text="Alert")
    tab.alerts_list.pack(fill='both', expand=True, padx=10, pady=10)

def update_alerts_tab(tab, app_state):
    for i in tab.alerts_list.get_children():
        tab.alerts_list.delete(i)
    
    alerts = app_state.alerts
    for alert in alerts:
        tab.alerts_list.insert("", "end", values=alert)
