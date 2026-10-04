"""Tkinter dashboard. All widget operations occur in this main GUI thread."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collections import deque
from config import DEFAULT_CAPACITY, DEFAULT_CONSUMER_RATE, DEFAULT_PRODUCER_RATE, MAX_CAPACITY, MAX_RATE, SCENARIOS
from simulation import Simulation

BG, PANEL, TEXT, MUTED, ACCENT, GREEN, RED, ORANGE = "#101827", "#1d2939", "#f8fafc", "#9ca3af", "#38bdf8", "#34d399", "#fb7185", "#fbbf24"


class SimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Packet Transmission Simulator")
        self.geometry("1280x900")
        self.minsize(1100, 760)
        self.configure(bg=BG)
        self.simulation = Simulation()
        self.history = deque(maxlen=90)
        self.last_drop = 0
        self.capacity_var = tk.IntVar(value=DEFAULT_CAPACITY)
        self.producer_var = tk.DoubleVar(value=DEFAULT_PRODUCER_RATE)
        self.consumer_var = tk.DoubleVar(value=DEFAULT_CONSUMER_RATE)
        self.scenario_var = tk.StringVar(value="Choose scenario")
        self.stats_vars = {key: tk.StringVar(value="0") for key in ("generated", "processed", "dropped", "buffer_size", "capacity", "utilization", "overflows", "loss", "throughput")}
        self._style()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(150, self.refresh)

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground=TEXT)
        style.configure("Sub.TLabel", font=("Segoe UI", 11), foreground=MUTED)
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=ACCENT, font=("Segoe UI", 11, "bold"))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Metric.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 16, "bold"))
        style.configure("MetricName.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=7, background=ACCENT, foreground="#07101e")
        style.map("Accent.TButton", background=[("active", "#7dd3fc")])
        style.configure("TButton", padding=6)

    def _build(self):
        header = ttk.Frame(self, padding=(24, 18, 24, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Network Packet Transmission Simulator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Producer–Consumer Model  |  Online Competitive Gaming", style="Sub.TLabel").pack(anchor="w", pady=(2, 0))
        self.alert = tk.Label(header, text="READY", bg="#12334a", fg="#bae6fd", font=("Segoe UI", 10, "bold"), padx=10, pady=4)
        self.alert.pack(anchor="e", side="right", pady=6)

        controls = ttk.Frame(self, style="Panel.TFrame", padding=14)
        controls.pack(fill="x", padx=20, pady=8)
        ttk.Label(controls, text="SIMULATION CONTROLS", style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=12, sticky="w", pady=(0, 8))
        self._spin(controls, "Buffer Capacity", self.capacity_var, 1, MAX_CAPACITY, 1, 1)
        self._spin(controls, "Producer rate (pkt/s)", self.producer_var, 0.5, MAX_RATE, 0.5, 3)
        self._spin(controls, "Consumer rate (pkt/s)", self.consumer_var, 0.5, MAX_RATE, 0.5, 5)
        ttk.Combobox(controls, textvariable=self.scenario_var, values=["Choose scenario", *SCENARIOS], state="readonly", width=19).grid(row=1, column=7, padx=8, sticky="w")
        ttk.Button(controls, text="Apply preset", command=self.apply_scenario).grid(row=1, column=8, padx=3)
        ttk.Button(controls, text="Start", style="Accent.TButton", command=self.start).grid(row=1, column=9, padx=3)
        ttk.Button(controls, text="Pause", command=self.pause).grid(row=1, column=10, padx=3)
        ttk.Button(controls, text="Resume", command=self.resume).grid(row=1, column=11, padx=3)
        ttk.Button(controls, text="Reset", command=self.reset).grid(row=1, column=12, padx=3)

        body = ttk.Frame(self, padding=(20, 8))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3); body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=3); body.rowconfigure(1, weight=2)
        self.viz = ttk.Frame(body, style="Panel.TFrame", padding=16)
        self.viz.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self._build_visualization()
        self.right = ttk.Frame(body, style="Panel.TFrame", padding=14)
        self.right.grid(row=0, column=1, sticky="nsew", pady=(0, 8))
        self._build_right()
        bottom = ttk.Frame(body)
        bottom.grid(row=1, column=0, columnspan=2, sticky="nsew")
        bottom.columnconfigure(0, weight=1); bottom.columnconfigure(1, weight=1)
        self._build_log(bottom)
        self._build_graphs(bottom)

    def _spin(self, parent, label, variable, low, high, step, col):
        ttk.Label(parent, text=label, style="Panel.TLabel").grid(row=1, column=col, sticky="w")
        tk.Spinbox(parent, from_=low, to=high, increment=step, textvariable=variable, width=7, bg="#e5e7eb", relief="flat").grid(row=1, column=col + 1, padx=(5, 16))

    def _build_visualization(self):
        ttk.Label(self.viz, text="LIVE PACKET FLOW", style="PanelTitle.TLabel").pack(anchor="w")
        self.flow = tk.Canvas(self.viz, bg=PANEL, highlightthickness=0, height=320)
        self.flow.pack(fill="both", expand=True)
        self.flow.bind("<Configure>", lambda _e: self.draw_flow(self.simulation.snapshot()))

    def _build_right(self):
        ttk.Label(self.right, text="LIVE STATISTICS", style="PanelTitle.TLabel").pack(anchor="w")
        metric_grid = ttk.Frame(self.right, style="Panel.TFrame")
        metric_grid.pack(fill="x", pady=7)
        metrics = [("generated", "Generated"), ("processed", "Processed"), ("dropped", "Dropped"), ("buffer_size", "In Buffer"), ("capacity", "Capacity"), ("utilization", "Utilization"), ("overflows", "Overflows"), ("loss", "Packet Loss"), ("throughput", "Throughput")]
        for i, (key, name) in enumerate(metrics):
            cell = ttk.Frame(metric_grid, style="Panel.TFrame", padding=5)
            cell.grid(row=i // 3, column=i % 3, sticky="ew")
            ttk.Label(cell, textvariable=self.stats_vars[key], style="Metric.TLabel").pack(anchor="w")
            ttk.Label(cell, text=name, style="MetricName.TLabel").pack(anchor="w")
        ttk.Separator(self.right).pack(fill="x", pady=8)
        ttk.Label(self.right, text="SYNCHRONIZATION", style="PanelTitle.TLabel").pack(anchor="w")
        self.sync_label = ttk.Label(self.right, text="mutex: AVAILABLE\nempty: 10\nfull: 0", style="Panel.TLabel", font=("Consolas", 10))
        self.sync_label.pack(anchor="w", pady=5)
        ttk.Label(self.right, text="mutex protects the shared buffer\nempty counts available slots\nfull counts packets available to consume", style="Panel.TLabel", foreground=MUTED).pack(anchor="w")
        ttk.Separator(self.right).pack(fill="x", pady=8)
        self.status_label = ttk.Label(self.right, text="PRODUCER\nStatus: STOPPED\n\nCONSUMER\nStatus: STOPPED", style="Panel.TLabel", font=("Segoe UI", 10))
        self.status_label.pack(anchor="w")

    def _build_log(self, parent):
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(frame, text="REAL-TIME EVENT LOG", style="PanelTitle.TLabel").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(frame, height=12, bg="#0b1220", fg="#d1fae5", insertbackground=TEXT, relief="flat", font=("Consolas", 9), state="disabled")
        self.log.pack(fill="both", expand=True, pady=(7, 0))

    def _build_graphs(self, parent):
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(frame, text="REAL-TIME GRAPHS", style="PanelTitle.TLabel").pack(anchor="w")
        self.graph = tk.Canvas(frame, bg="#0b1220", highlightthickness=0, height=220)
        self.graph.pack(fill="both", expand=True, pady=(7, 0))
        self.graph.bind("<Configure>", lambda _e: self.draw_graphs())

    def start(self):
        try:
            capacity, p_rate, c_rate = self._values()
        except tk.TclError:
            messagebox.showerror("Invalid setting", "Use numeric values within the displayed limits."); return
        self.history.clear(); self.last_drop = 0
        self.simulation.start(capacity, p_rate, c_rate)

    def pause(self): self.simulation.pause()
    def resume(self): self.simulation.resume()

    def reset(self):
        self.simulation.stop()
        self.simulation = Simulation()
        self.capacity_var.set(DEFAULT_CAPACITY); self.producer_var.set(DEFAULT_PRODUCER_RATE); self.consumer_var.set(DEFAULT_CONSUMER_RATE)
        self.scenario_var.set("Choose scenario"); self.history.clear(); self.last_drop = 0
        self.log.configure(state="normal"); self.log.delete("1.0", "end"); self.log.configure(state="disabled")

    def apply_scenario(self):
        name = self.scenario_var.get()
        if name in SCENARIOS:
            cap, prod, cons = SCENARIOS[name]
            self.capacity_var.set(cap); self.producer_var.set(prod); self.consumer_var.set(cons)
            if self.simulation.is_alive(): self.simulation.set_rates(prod, cons)

    def _values(self):
        cap, prod, cons = self.capacity_var.get(), self.producer_var.get(), self.consumer_var.get()
        if not 1 <= cap <= MAX_CAPACITY or not 0 < prod <= MAX_RATE or not 0 < cons <= MAX_RATE: raise tk.TclError
        return cap, prod, cons

    def refresh(self):
        if self.simulation.is_alive():
            try: self.simulation.set_rates(self.producer_var.get(), self.consumer_var.get())
            except tk.TclError: pass
        snap = self.simulation.snapshot()
        self.update_dashboard(snap)
        while not self.simulation.events.empty():
            timestamp, text = self.simulation.events.get_nowait()
            self.log.configure(state="normal"); self.log.insert("end", f"{timestamp}  {text}\n"); self.log.see("end"); self.log.configure(state="disabled")
        self.after(150, self.refresh)

    def update_dashboard(self, s):
        formats = {"generated": str(s["generated"]), "processed": str(s["processed"]), "dropped": str(s["dropped"]), "buffer_size": str(s["buffer_size"]), "capacity": str(s["capacity"]), "utilization": f'{s["utilization"]:.0f}%', "overflows": str(s["overflows"]), "loss": f'{s["loss"]:.1f}%', "throughput": f'{s["throughput"]:.1f}/s'}
        for key, value in formats.items(): self.stats_vars[key].set(value)
        self.sync_label.configure(text=f'mutex: {"LOCKED" if s["mutex_locked"] else "AVAILABLE"}\nempty: {s["empty"]}\nfull: {s["full"]}')
        self.status_label.configure(text=f'PRODUCER\nStatus: {s["producer_status"]}\nRate: {s["producer_rate"]:.1f} packets/sec\n\nCONSUMER\nStatus: {s["consumer_status"]}\nRate: {s["consumer_rate"]:.1f} packets/sec')
        if s["dropped"] > self.last_drop:
            self.alert.configure(text="PACKET DROPPED / BUFFER OVERFLOW", bg="#7f1d1d", fg="#fee2e2")
        elif s["buffer_size"] == s["capacity"]:
            self.alert.configure(text="BUFFER FULL", bg="#78350f", fg="#fef3c7")
        else: self.alert.configure(text="RUNNING" if self.simulation.is_alive() else "READY", bg="#12334a", fg="#bae6fd")
        self.last_drop = s["dropped"]
        self.history.append((s["producer_rate"], s["consumer_rate"], s["buffer_size"], s["capacity"], s["dropped"]))
        self.draw_flow(s); self.draw_graphs()

    def draw_flow(self, s):
        c = self.flow; c.delete("all"); w, h = max(c.winfo_width(), 500), max(c.winfo_height(), 280)
        def box(x1, y1, x2, y2, title, subtitle, color=ACCENT):
            c.create_rectangle(x1,y1,x2,y2, outline=color, width=2, fill="#142033")
            c.create_text((x1+x2)/2, y1+20, text=title, fill=TEXT, font=("Segoe UI", 12, "bold"))
            c.create_text((x1+x2)/2, y1+43, text=subtitle, fill=MUTED, font=("Segoe UI", 9))
        mid = w/2
        c.create_text(mid, 18, text="GAME SERVER", fill=GREEN, font=("Segoe UI", 12, "bold")); c.create_text(mid, 38, text="Network packets", fill=MUTED)
        c.create_line(mid, 48, mid, 72, arrow="last", fill=ACCENT, width=2)
        box(mid-105, 75, mid+105, 135, "PRODUCER", "Packet Receiver")
        c.create_line(mid, 135, mid, 160, arrow="last", fill=ACCENT, width=2)
        bx1, bx2, by1, by2 = 25, w-25, 164, 248
        c.create_rectangle(bx1,by1,bx2,by2, outline=ACCENT, width=2, fill="#142033")
        c.create_text(mid, 179, text=f'PACKET BUFFER  —  Capacity: {s["capacity"]}   Utilization: {s["utilization"]:.0f}%', fill=TEXT, font=("Segoe UI", 10, "bold"))
        gap, y, slots = 6, 195, s["capacity"]
        slotw = min(68, (bx2-bx1-30-gap*(slots-1))/slots)
        start = (w - (slots*slotw+(slots-1)*gap))/2
        for i in range(slots):
            x = start+i*(slotw+gap); occupied = i < len(s["packets"])
            color = RED if s["buffer_size"] == slots else (GREEN if occupied else "#334155")
            c.create_rectangle(x,y,x+slotw,y+35, fill=color if occupied else "#1e293b", outline=color, width=2)
            txt = f'P{s["packets"][i].packet_id}' if occupied else "EMPTY"
            c.create_text(x+slotw/2,y+17,text=txt,fill=TEXT,font=("Segoe UI",8,"bold"))
        c.create_line(mid, 249, mid, 270, arrow="last", fill=ACCENT, width=2)
        box(mid-105, 274, mid+105, 334, "CONSUMER", "Game Engine", GREEN)

    def draw_graphs(self):
        c=self.graph; c.delete("all"); w,h=max(c.winfo_width(),350),max(c.winfo_height(),180)
        if not self.history: return
        data=list(self.history); left, right=38,w-10; section=h/3
        labels=["Rates (p/c)", "Buffer occupancy", "Dropped packets"]
        for idx,label in enumerate(labels):
            top=idx*section; c.create_text(4,top+10,text=label,anchor="w",fill=MUTED,font=("Segoe UI",8)); c.create_line(left,top+section-6,right,top+section-6,fill="#334155")
        def line(values, idx, color, scale):
            pts=[]; top=idx*section+14; bottom=(idx+1)*section-8
            for i,v in enumerate(values): pts.extend((left+(right-left)*i/max(1,len(values)-1), bottom-(bottom-top)*min(1,v/scale)))
            if len(pts)>=4:c.create_line(*pts,fill=color,width=2,smooth=True)
        line([x[0] for x in data],0,ACCENT,MAX_RATE); line([x[1] for x in data],0,GREEN,MAX_RATE)
        line([x[2] for x in data],1,ORANGE,max(1,max(x[3] for x in data)))
        line([x[4] for x in data],2,RED,max(1,max(x[4] for x in data)))

    def close(self):
        self.simulation.stop(); self.destroy()
