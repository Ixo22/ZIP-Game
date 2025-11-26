import tkinter as tk
from tkinter import messagebox
import threading
import time
from collections import deque

class ZipGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZIP Game - V12 (IA Fix)")
        self.root.configure(bg="#f0f2f5") 

        # Configuración
        self.FILAS = 7
        self.COLS = 7
        self.CELL_SIZE = 50 

        # --- ESTADO INTERNO ---
        self.grid_content = [[0]*self.COLS for _ in range(self.FILAS)]
        self.walls_v = [[False]*self.COLS for _ in range(self.FILAS)]
        self.walls_h = [[False]*self.COLS for _ in range(self.FILAS)]
        self.next_number_to_place = 1

        # --- ESTADO JUEGO ---
        self.mode = "EDIT"
        self.user_path = [] 
        self.checkpoints = [] 
        self.target_cells_count = 0 
        self.start_time = 0
        self.timer_running = False

        # --- GUI WIDGETS ---
        self.widgets_cells = [[None]*self.COLS for _ in range(self.FILAS)]
        self.widgets_walls_v = [[None]*self.COLS for _ in range(self.FILAS)]
        self.widgets_walls_h = [[None]*self.COLS for _ in range(self.FILAS)]

        self.crear_interfaz()

    def crear_interfaz(self):
        # PANEL IZQUIERDO
        left_panel = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False) 

        self.lbl_title = tk.Label(left_panel, text="MODO EDITOR", font=("Arial", 14, "bold"), bg="#f0f2f5", fg="#555")
        self.lbl_title.pack(pady=(0, 10))

        self.lbl_timer = tk.Label(left_panel, text="00:00", font=("Consolas", 24, "bold"), bg="#f0f2f5", fg="#333")
        self.lbl_timer.pack(pady=5)

        self.btn_play = tk.Button(left_panel, text="▶ JUGAR", command=self.activar_modo_juego, 
                                  bg="#28a745", fg="white", font=('Arial', 12, 'bold'), cursor="hand2", pady=8)
        self.btn_play.pack(fill=tk.X, pady=(20, 5))

        self.btn_ai = tk.Button(left_panel, text="🤖 RESOLVER CON IA", command=self.activar_ia, 
                                bg="#6f42c1", fg="white", font=('Arial', 10, 'bold'), cursor="hand2", pady=8)
        self.btn_ai.pack(fill=tk.X, pady=5)

        self.btn_edit = tk.Button(left_panel, text="✏ VOLVER A EDITAR", command=self.activar_modo_editor, 
                                  bg="#ffc107", fg="black", font=('Arial', 10, 'bold'), cursor="hand2", pady=8)
        self.btn_edit.pack(fill=tk.X, pady=(20, 5))
        self.btn_edit.config(state="disabled") 

        self.btn_reset = tk.Button(left_panel, text="🗑 BORRAR TODO", command=self.reset_board,
                                   bg="#dce6f1", fg="#c00", font=('Arial', 10, 'bold'), cursor="hand2")
        self.btn_reset.pack(fill=tk.X, pady=20)

        # Instrucciones
        lbl_instr = tk.Label(left_panel, text="1. Pon números (Clic)\n2. Pon muros (Bordes)\n3. Dale a Jugar", 
                             font=("Arial", 9), bg="#f0f2f5", justify=tk.LEFT, fg="#666")
        lbl_instr.pack(side=tk.BOTTOM, pady=10)

        # PANEL DERECHO (GRID)
        grid_frame = tk.Frame(self.root, bg="white", padx=20, pady=20, bd=2, relief=tk.RIDGE)
        grid_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        for r in range(self.FILAS):
            for c in range(self.COLS):
                # CASILLA
                lbl = tk.Label(grid_frame, text="", width=4, height=2, 
                               font=('Arial', 16, 'bold'), bg="#f0f2f5", relief="flat")
                lbl.grid(row=r*2, column=c*2, padx=0, pady=0)
                
                # Bindings
                lbl.bind("<Button-1>", lambda e, row=r, col=c: self.gestionar_clic(row, col))
                lbl.bind("<B1-Motion>", lambda e, row=r, col=c: self.on_drag_cell(e))

                self.widgets_cells[r][c] = lbl

                # MUROS
                if c < self.COLS - 1:
                    btn_v = tk.Button(grid_frame, bg="#e0e0e0", bd=0, cursor="sb_h_double_arrow", width=1)
                    btn_v.grid(row=r*2, column=c*2+1, sticky="ns")
                    btn_v.config(command=lambda row=r, col=c: self.toggle_wall_v(row, col))
                    self.widgets_walls_v[r][c] = btn_v

                if r < self.FILAS - 1:
                    btn_h = tk.Button(grid_frame, bg="#e0e0e0", bd=0, cursor="sb_v_double_arrow", height=1)
                    btn_h.grid(row=r*2+1, column=c*2, sticky="ew")
                    btn_h.config(command=lambda row=r, col=c: self.toggle_wall_h(row, col))
                    self.widgets_walls_h[r][c] = btn_h
                
                # Decoración
                if c < self.COLS - 1 and r < self.FILAS - 1:
                    tk.Frame(grid_frame, bg="white", width=4, height=4).grid(row=r*2+1, column=c*2+1)

    # --- CONTROL ---
    def gestionar_clic(self, r, c):
        if self.mode == "EDIT":
            self.accion_editar_celda(r, c)
        elif self.mode == "PLAY":
            self.accion_empezar_juego(r, c)

    # ======================================================
    # MODO EDITOR
    # ======================================================

    def accion_editar_celda(self, r, c):
        val = self.grid_content[r][c]
        if val == 0:
            self.grid_content[r][c] = self.next_number_to_place
            self.widgets_cells[r][c].config(text=str(self.next_number_to_place), bg="white", fg="black")
            self.next_number_to_place += 1
        else:
            self.grid_content[r][c] = 0
            self.widgets_cells[r][c].config(text="", bg="#f0f2f5", fg="black")
            self.recalcular_secuencia(val)

    def recalcular_secuencia(self, deleted_val):
        for r in range(self.FILAS):
            for c in range(self.COLS):
                v = self.grid_content[r][c]
                if v > deleted_val:
                    self.grid_content[r][c] = v - 1
                    self.widgets_cells[r][c].config(text=str(v - 1))
        
        max_n = 0
        for r in range(self.FILAS):
            for c in range(self.COLS):
                v = self.grid_content[r][c]
                if v > max_n: max_n = v
        self.next_number_to_place = max_n + 1

    def toggle_wall_v(self, r, c):
        if self.mode != "EDIT": return
        self.walls_v[r][c] = not self.walls_v[r][c]
        self.widgets_walls_v[r][c].config(bg="black" if self.walls_v[r][c] else "#e0e0e0")

    def toggle_wall_h(self, r, c):
        if self.mode != "EDIT": return
        self.walls_h[r][c] = not self.walls_h[r][c]
        self.widgets_walls_h[r][c].config(bg="black" if self.walls_h[r][c] else "#e0e0e0")

    def reset_board(self):
        if self.mode != "EDIT": self.activar_modo_editor()
        self.grid_content = [[0]*self.COLS for _ in range(self.FILAS)]
        self.walls_v = [[False]*self.COLS for _ in range(self.FILAS)]
        self.walls_h = [[False]*self.COLS for _ in range(self.FILAS)]
        self.next_number_to_place = 1
        
        for r in range(self.FILAS):
            for c in range(self.COLS):
                self.widgets_cells[r][c].config(text="", bg="#f0f2f5", fg="black")
                if c < self.COLS - 1: self.widgets_walls_v[r][c].config(bg="#e0e0e0")
                if r < self.FILAS - 1: self.widgets_walls_h[r][c].config(bg="#e0e0e0")
        
        self.lbl_title.config(text="MODO EDITOR (Limpio)")

    # ======================================================
    # MODO JUEGO
    # ======================================================

    def activar_modo_juego(self):
        self.checkpoints = []
        start_pos = None
        for r in range(self.FILAS):
            for c in range(self.COLS):
                v = self.grid_content[r][c]
                if v > 0:
                    self.checkpoints.append(v)
                    if v == 1: start_pos = (r, c)
        self.checkpoints.sort()

        if not self.checkpoints or self.checkpoints[0] != 1:
            messagebox.showerror("Error", "Falta el número 1.")
            return
        
        for i, num in enumerate(self.checkpoints):
            if num != i + 1:
                messagebox.showerror("Error", f"Falta el número {i+1}.")
                return

        self.target_cells_count = self.calcular_area_accesible(start_pos)
        
        self.mode = "PLAY"
        self.lbl_title.config(text="¡JUGANDO!", fg="#28a745")
        self.btn_edit.config(state="normal")
        self.btn_play.config(state="disabled", bg="#cccccc")
        self.btn_ai.config(state="disabled", bg="#cccccc")
        self.btn_reset.config(state="disabled")
        
        self.clean_visuals_for_play()
        
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.lbl_timer.config(text=f"{mins:02}:{secs:02}")
            self.root.after(1000, self.update_timer)

    def accion_empezar_juego(self, r, c):
        if self.grid_content[r][c] == 1:
            self.user_path = [(r, c)]
            self.pintar_camino()

    def on_drag_cell(self, event):
        if self.mode != "PLAY": return
        if not self.user_path: return

        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        
        tr, tc = -1, -1
        found = False
        for r in range(self.FILAS):
            for c in range(self.COLS):
                if self.widgets_cells[r][c] == widget:
                    tr, tc = r, c
                    found = True
                    break
            if found: break
        
        if not found: return

        lr, lc = self.user_path[-1]
        if (tr, tc) == (lr, lc): return

        # Backtrack
        if len(self.user_path) > 1 and (tr, tc) == self.user_path[-2]:
            self.user_path.pop() 
            self.pintar_camino()
            return

        if (tr, tc) in self.user_path: return 
        if abs(tr - lr) + abs(tc - lc) != 1: return 

        # Muros
        blocked = False
        if tr == lr: 
            c_min = min(lc, tc)
            if self.walls_v[tr][c_min]: blocked = True
        elif tc == lc: 
            r_min = min(lr, tr)
            if self.walls_h[r_min][tc]: blocked = True
        
        if blocked: return

        # Checkpoints
        val_dest = self.grid_content[tr][tc]
        if val_dest > 0:
            last_chk = 0
            for pr, pc in reversed(self.user_path):
                v = self.grid_content[pr][pc]
                if v > 0:
                    last_chk = v
                    break
            if val_dest != last_chk + 1: return 

        self.user_path.append((tr, tc))
        self.pintar_camino()
        self.check_victory()

    def check_victory(self):
        if len(self.user_path) != self.target_cells_count: return
        lr, lc = self.user_path[-1]
        if self.grid_content[lr][lc] != self.checkpoints[-1]: return

        self.timer_running = False
        self.lbl_title.config(text="¡GANASTE!", fg="#d4af37")
        self.mode = "FINISHED"
        messagebox.showinfo("¡Felicidades!", f"Completado en {self.lbl_timer.cget('text')}")

    # ======================================================
    # IA Y UTILIDADES
    # ======================================================

    def activar_ia(self):
        self.activar_modo_juego()
        self.mode = "SOLVING_AI"
        self.lbl_title.config(text="IA PENSANDO...", fg="blue")
        threading.Thread(target=self.thread_ia, daemon=True).start()

    def thread_ia(self):
        # 1. Preparar datos
        grid = [fila[:] for fila in self.grid_content]
        wv = [fila[:] for fila in self.walls_v]
        wh = [fila[:] for fila in self.walls_h]
        
        # FIX: Buscar el 1 manualmente, no depender de self.user_path
        start = None
        for r in range(self.FILAS):
            for c in range(self.COLS):
                if grid[r][c] == 1:
                    start = (r, c)
                    break
        
        if not start: return # No debería pasar
        
        target = self.target_cells_count
        
        # 2. Ejecutar
        path = self.backtracking(grid, wv, wh, start[0], start[1], [start], target, self.checkpoints, 1)

        if path:
            self.root.after(0, lambda: self.finish_ia(path))
        else:
            self.root.after(0, lambda: self.fail_ia())

    def finish_ia(self, path):
        self.timer_running = False
        self.user_path = path
        self.pintar_camino() 
        self.lbl_title.config(text="RESUELTO POR IA", fg="purple")
    
    def fail_ia(self):
        self.timer_running = False
        self.lbl_title.config(text="IA FALLÓ", fg="red")
        messagebox.showinfo("IA", "Sin solución.")

    def activar_modo_editor(self):
        self.mode = "EDIT"
        self.timer_running = False
        self.lbl_timer.config(text="00:00")
        self.lbl_title.config(text="MODO EDITOR", fg="#555")
        
        self.btn_play.config(state="normal", bg="#28a745")
        self.btn_ai.config(state="normal", bg="#6f42c1")
        self.btn_edit.config(state="disabled")
        self.btn_reset.config(state="normal")
        
        self.clean_visuals_for_play()
        # Mostrar números en negro
        for r in range(self.FILAS):
            for c in range(self.COLS):
                v = self.grid_content[r][c]
                if v > 0: self.widgets_cells[r][c].config(text=str(v), fg="black")

    def clean_visuals_for_play(self):
        for r in range(self.FILAS):
            for c in range(self.COLS):
                v = self.grid_content[r][c]
                bg = "white" if v > 0 else "#f0f2f5"
                self.widgets_cells[r][c].config(bg=bg)

    def calcular_area_accesible(self, inicio):
        q = deque([inicio])
        visited = {inicio}
        count = 0
        while q:
            r, c = q.popleft()
            count += 1
            moves = [(-1, 0, 'h', -1, 0), (1, 0, 'h', 0, 0), (0, -1, 'v', 0, -1), (0, 1, 'v', 0, 0)]
            for dr, dc, wtype, wr, wc in moves:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.FILAS and 0 <= nc < self.COLS:
                    if (nr, nc) not in visited:
                        blocked = False
                        if wtype=='h': blocked = self.walls_h[r+wr][c+wc]
                        else: blocked = self.walls_v[r+wr][c+wc]
                        if not blocked:
                            visited.add((nr, nc))
                            q.append((nr, nc))
        return count

    def backtracking(self, grid, wv, wh, r, c, camino, meta, checkpoints, idx_obj):
        if len(camino) == meta:
            if grid[r][c] == checkpoints[-1]: return camino
            return None
        
        val_meta = checkpoints[idx_obj] if idx_obj < len(checkpoints) else 9999
        moves = [(-1, 0, 'h', -1, 0), (1, 0, 'h', 0, 0), (0, -1, 'v', 0, -1), (0, 1, 'v', 0, 0)]

        for dr, dc, wtype, wr, wc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.FILAS and 0 <= nc < self.COLS:
                blocked = False
                if wtype=='h': blocked = wh[r+wr][c+wc]
                else: blocked = wv[r+wr][c+wc]
                
                if not blocked and (nr, nc) not in camino:
                    v = grid[nr][nc]
                    can = False
                    n_idx = idx_obj
                    if v == 0: can=True
                    elif v == val_meta: can=True; n_idx+=1
                    if can:
                        res = self.backtracking(grid, wv, wh, nr, nc, camino+[(nr,nc)], meta, checkpoints, n_idx)
                        if res: return res
        return None

    def pintar_camino(self):
        total = max(len(self.user_path), 2)
        c1 = (0, 100, 255)
        c2 = (0, 255, 200)

        for r in range(self.FILAS):
            for c in range(self.COLS):
                if (r, c) not in self.user_path:
                    v = self.grid_content[r][c]
                    bg = "white" if v > 0 else "#f0f2f5"
                    fg = "black" 
                    self.widgets_cells[r][c].config(bg=bg, fg=fg)

        for i, (r, c) in enumerate(self.user_path):
            f = i / (total - 1)
            nr = int(c1[0] + (c2[0]-c1[0])*f)
            ng = int(c1[1] + (c2[1]-c1[1])*f)
            nb = int(c1[2] + (c2[2]-c1[2])*f)
            color = f'#{nr:02x}{ng:02x}{nb:02x}'
            
            v = self.grid_content[r][c]
            txt = str(v) if v > 0 else ""
            self.widgets_cells[r][c].config(bg=color, text=txt, fg="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = ZipGameApp(root)
    root.mainloop()