import tkinter as tk
from tkinter import font
import math
import re

# ══════════════════════════════════════════════════════
#  THEMES  –  dark (lavender-purple) + light (lilac)
# ══════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "BG":         "#1a1030",
        "PANEL":      "#221540",
        "DISPLAY_BG": "#130c25",
        "ACCENT":     "#c084fc",
        "ACCENT2":    "#f472b6",
        "ACCENT3":    "#a78bfa",
        "BTN_DARK":   "#2d1f52",
        "BTN_OP":     "#3b1f6e",
        "BTN_EQ":     "#9333ea",
        "BTN_FUNC":   "#2a1a4e",
        "TXT_MAIN":   "#f3e8ff",
        "TXT_DIM":    "#7c5fa8",
        "TXT_OP":     "#e879f9",
        "TXT_FUNC":   "#a78bfa",
        "TXT_EQ":     "#ffffff",
        "BORDER":     "#4c2d8a",
        "SETTINGS_BG":"#1e1238",
        "TOGGLE_ON":  "#9333ea",
        "TOGGLE_OFF": "#3b2a5a",
        "SEP":        "#3b2a6a",
    },
    "light": {
        "BG":         "#f3e8ff",
        "PANEL":      "#ede9fe",
        "DISPLAY_BG": "#faf5ff",
        "ACCENT":     "#7c3aed",
        "ACCENT2":    "#db2777",
        "ACCENT3":    "#8b5cf6",
        "BTN_DARK":   "#ddd6fe",
        "BTN_OP":     "#c4b5fd",
        "BTN_EQ":     "#7c3aed",
        "BTN_FUNC":   "#e9d5ff",
        "TXT_MAIN":   "#2e1065",
        "TXT_DIM":    "#7e22ce",
        "TXT_OP":     "#6d28d9",
        "TXT_FUNC":   "#5b21b6",
        "TXT_EQ":     "#ffffff",
        "BORDER":     "#a78bfa",
        "SETTINGS_BG":"#ede9fe",
        "TOGGLE_ON":  "#7c3aed",
        "TOGGLE_OFF": "#c4b5fd",
        "SEP":        "#c4b5fd",
    },
}

_app_theme = dict(THEMES["dark"])


def th(key):
    return _app_theme[key]


# ══════════════════════════════════════════════════════
#  ANIMATED BUTTON
# ══════════════════════════════════════════════════════
class AnimButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 bg_key="BTN_DARK", fg_key="TXT_MAIN",
                 radius=10, font_obj=None, **kw):
        super().__init__(parent, bd=0, highlightthickness=0, **kw)
        self.command  = command
        self.text_str = text
        self.bg_key   = bg_key
        self.fg_key   = fg_key
        self.radius   = radius
        self.font_obj = font_obj
        self._anim_id = None
        self._glow    = 0.0
        self._pressed = False

        self.bind("<Configure>",       self._draw)
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)

    def refresh_theme(self):
        self.config(bg=th("PANEL"))
        self._draw()

    def _hex_blend(self, c1, c2, t):
        r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(
            int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

    def _draw(self, *_):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return

        bg_col  = th(self.bg_key)
        acc_col = th("ACCENT")
        bdr_col = th("BORDER")
        fg_col  = th(self.fg_key)

        t   = self._glow
        pad = int((1 - (0.85 if self._pressed else 1.0)) * 4)
        r   = self.radius
        x0, y0, x1, y1 = pad, pad, w-pad, h-pad

        fill = self._hex_blend(bg_col, acc_col, t * 0.22)
        pts  = [x0+r,y0, x1-r,y0, x1,y0,   x1,y0+r,
                x1,y1-r, x1,y1,   x1-r,y1, x0+r,y1,
                x0,y1,   x0,y1-r, x0,y0+r, x0,y0]

        self.config(bg=th("PANEL"))
        self.create_polygon(pts, smooth=True, fill=fill, outline="")
        glow_col = self._hex_blend(bdr_col, acc_col, t*0.9) if t > 0 else bdr_col
        self.create_polygon(pts, smooth=True, fill="",
                            outline=glow_col, width=1+int(t*2))

        cy_off = 2 if self._pressed else 0
        self.create_text(w//2, h//2+cy_off, text=self.text_str,
                         fill=fg_col, font=self.font_obj, anchor="center")

    def _on_press(self, _):
        self._pressed = True
        self._draw()
        self.after(120, self._finish_press)

    def _finish_press(self):
        self._pressed = False
        self._draw()
        if self.command:
            self.command()

    def _on_release(self, _): pass
    def _on_enter(self, _): self._animate_glow(1.0)
    def _on_leave(self, _): self._animate_glow(0.0)

    def _animate_glow(self, target, steps=8):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        delta = (target - self._glow) / steps
        def step(n):
            self._glow = max(0.0, min(1.0, self._glow + delta))
            self._draw()
            if n > 1:
                self._anim_id = self.after(16, lambda: step(n-1))
        step(steps)


# ══════════════════════════════════════════════════════
#  TOGGLE SWITCH
# ══════════════════════════════════════════════════════
class ToggleSwitch(tk.Canvas):
    W, H = 70, 26

    def __init__(self, parent, on_text="DARK", off_text="LIGHT",
                 state=True, command=None, font_obj=None):
        super().__init__(parent, width=self.W, height=self.H,
                         bd=0, highlightthickness=0)
        self.on_text   = on_text
        self.off_text  = off_text
        self._state    = state
        self.command   = command
        self.font_obj  = font_obj
        self._knob_x   = self.W - 14 if state else 14
        self.bind("<ButtonPress-1>", self._toggle)
        self.bind("<Configure>", self._draw)
        self._draw()

    def _draw(self, *_):
        self.delete("all")
        bg  = th("SETTINGS_BG")
        col = th("TOGGLE_ON") if self._state else th("TOGGLE_OFF")
        self.config(bg=bg)
        r = self.H // 2
        # track
        self.create_oval(0, 0, self.H, self.H, fill=col, outline="")
        self.create_oval(self.W-self.H, 0, self.W, self.H, fill=col, outline="")
        self.create_rectangle(r, 0, self.W-r, self.H, fill=col, outline="")
        # knob
        kx = int(self._knob_x)
        self.create_oval(kx-10, 3, kx+10, self.H-3, fill="#ffffff", outline="")
        # label
        lbl = self.on_text if self._state else self.off_text
        lx  = kx - 20 if self._state else kx + 20
        self.create_text(lx, self.H//2, text=lbl, fill="#ffffff",
                         font=self.font_obj, anchor="center")

    def _toggle(self, _):
        self._state = not self._state
        target = self.W - 14 if self._state else 14
        self._animate_knob(target)
        if self.command:
            self.command(self._state)

    def _animate_knob(self, target, steps=8):
        dist = (target - self._knob_x) / steps
        def step(n):
            self._knob_x += dist
            self._draw()
            if n > 1:
                self.after(14, lambda: step(n-1))
            else:
                self._knob_x = target
                self._draw()
        step(steps)

    def refresh_theme(self):
        self._draw()


# ══════════════════════════════════════════════════════
#  SETTINGS PANEL (slide-in overlay)
# ══════════════════════════════════════════════════════
class SettingsPanel(tk.Frame):
    def __init__(self, parent, calculator, **kw):
        super().__init__(parent, **kw)
        self.calc     = calculator
        self._visible = False
        self._anim_y  = -280
        self._target  = 0
        self._anim_id = None
        self._build()

    def _build(self):
        self.config(bg=th("SETTINGS_BG"),
                    highlightbackground=th("ACCENT"),
                    highlightthickness=1)

        tk.Label(self, text="⚙   S E T T I N G S",
                 font=self.calc.f_btn_sm,
                 bg=th("SETTINGS_BG"), fg=th("ACCENT")).pack(pady=(16, 8))

        tk.Frame(self, bg=th("SEP"), height=1).pack(fill="x", padx=16)

        row = tk.Frame(self, bg=th("SETTINGS_BG"))
        row.pack(fill="x", padx=22, pady=14)
        tk.Label(row, text="Mode", font=self.calc.f_label,
                 bg=th("SETTINGS_BG"), fg=th("TXT_MAIN")).pack(side="left")

        self._toggle = ToggleSwitch(
            row, on_text="DARK", off_text="LIGHT",
            state=self.calc._dark_mode,
            command=self.calc._switch_theme,
            font_obj=self.calc.f_label)
        self._toggle.pack(side="right")

        tk.Frame(self, bg=th("SEP"), height=1).pack(fill="x", padx=16)

        close_btn = AnimButton(
            self, text="✕  Close", command=self.hide,
            bg_key="BTN_DARK", fg_key="ACCENT2",
            radius=8, font_obj=self.calc.f_btn_xs,
            width=120, height=36)
        close_btn.pack(pady=14)
        self._close_btn = close_btn

    def refresh_theme(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def show(self):
        if self._visible:
            return
        self._visible = True
        self._anim_y  = -280
        self._target  = 55
        self.place(x=8, y=int(self._anim_y), width=348)
        self.lift()
        self._animate()

    def hide(self):
        if not self._visible:
            return
        self._target = -280
        self._animate(on_done=self._do_hide)

    def _do_hide(self):
        self._visible = False
        self.place_forget()

    def _animate(self, on_done=None):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        dist = self._target - self._anim_y
        if abs(dist) < 1.5:
            self._anim_y = self._target
            self.place(x=8, y=int(self._anim_y), width=348)
            if on_done:
                on_done()
            return
        self._anim_y += dist * 0.2
        self.place(x=8, y=int(self._anim_y), width=348)
        self._anim_id = self.after(12, lambda: self._animate(on_done))


# ══════════════════════════════════════════════════════
#  MAIN CALCULATOR
# ══════════════════════════════════════════════════════
class ScientificCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✦ SCIENTIFIC CALC")
        self.resizable(False, False)

        self._expression  = ""
        self._just_result = False
        self._deg_mode    = True
        self._last_answer = None
        self._dark_mode   = True
        self._all_buttons = []

        self._build_fonts()

        self._root_frame = tk.Frame(self)
        self._root_frame.pack()

        self._build_ui()
        self._start_cursor_blink()

    # ── fonts ───────────────────────────────────────
    def _build_fonts(self):
        self.f_display = font.Font(family="Courier New", size=28, weight="bold")
        self.f_expr    = font.Font(family="Courier New", size=12)
        self.f_btn_lg  = font.Font(family="Courier New", size=15, weight="bold")
        self.f_btn_sm  = font.Font(family="Courier New", size=11, weight="bold")
        self.f_btn_xs  = font.Font(family="Courier New", size=9,  weight="bold")
        self.f_label   = font.Font(family="Courier New", size=9)

    # ── UI ──────────────────────────────────────────
    def _build_ui(self):
        panel = th("PANEL")
        bg    = th("BG")

        self.configure(bg=bg)
        self._root_frame.config(bg=bg)

        outer = tk.Frame(self._root_frame, bg=panel, padx=16, pady=16)
        outer.pack()
        self._outer = outer

        # ── title bar
        title_f = tk.Frame(outer, bg=panel)
        title_f.pack(fill="x", pady=(0, 8))

        self._title_lbl = tk.Label(
            title_f, text="✦ SCIENTIFIC",
            font=font.Font(family="Courier New", size=11, weight="bold"),
            bg=panel, fg=th("ACCENT"))
        self._title_lbl.pack(side="left")

        gear_btn = AnimButton(
            title_f, text="⚙", command=self._open_settings,
            bg_key="BTN_DARK", fg_key="ACCENT",
            radius=6, font_obj=self.f_btn_sm, width=30, height=22)
        gear_btn.pack(side="right", padx=(4, 0))
        self._all_buttons.append(gear_btn)

        self._mode_lbl = tk.Label(
            title_f, text="DEG", font=self.f_label,
            bg=panel, fg=th("ACCENT3"))
        self._mode_lbl.pack(side="right", padx=6)

        self._ans_lbl = tk.Label(
            title_f, text="ANS: —", font=self.f_label,
            bg=panel, fg=th("TXT_DIM"))
        self._ans_lbl.pack(side="right", padx=6)

        # ── display
        self._disp_frame = tk.Frame(
            outer, bg=th("DISPLAY_BG"),
            highlightbackground=th("ACCENT"), highlightthickness=1)
        self._disp_frame.pack(fill="x", pady=(0, 10))

        self.expr_var = tk.StringVar(value="")
        self._expr_lbl = tk.Label(
            self._disp_frame, textvariable=self.expr_var,
            font=self.f_expr, anchor="e", padx=10, height=1,
            bg=th("DISPLAY_BG"), fg=th("TXT_DIM"))
        self._expr_lbl.pack(fill="x", pady=(6, 0))

        result_row = tk.Frame(self._disp_frame, bg=th("DISPLAY_BG"))
        result_row.pack(fill="x")
        self._result_row = result_row

        self.result_var = tk.StringVar(value="0")
        self._result_lbl = tk.Label(
            result_row, textvariable=self.result_var,
            font=self.f_display, anchor="e", padx=10,
            bg=th("DISPLAY_BG"), fg=th("TXT_MAIN"))
        self._result_lbl.pack(side="left", fill="x", expand=True)

        self.cursor_lbl = tk.Label(
            result_row, text="▋", font=self.f_display,
            bg=th("DISPLAY_BG"), fg=th("ACCENT"))
        self.cursor_lbl.pack(side="right", padx=4)

        # ── divider
        self._divider = tk.Frame(outer, bg=th("ACCENT"), height=2)
        self._divider.pack(fill="x", pady=(0, 10))

        # ── buttons
        btn_frame = tk.Frame(outer, bg=panel)
        btn_frame.pack()
        self._btn_frame = btn_frame

        self._make_buttons(btn_frame)

        # ── settings overlay
        self._settings = SettingsPanel(
            self._root_frame, self,
            bg=th("SETTINGS_BG"), highlightthickness=1)

    # ── button factory ──────────────────────────────
    def _btn(self, parent, text, cmd, row, col,
             bg_key="BTN_DARK", fg_key="TXT_MAIN", fnt=None,
             rowspan=1, colspan=1, w=70, h=50):
        fnt = fnt or self.f_btn_sm
        b = AnimButton(parent, text=text, command=cmd,
                       bg_key=bg_key, fg_key=fg_key,
                       radius=8, font_obj=fnt, width=w, height=h)
        b.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
               padx=3, pady=3, sticky="nsew")
        self._all_buttons.append(b)
        return b

    def _make_buttons(self, f):
        P = lambda v: lambda: self._press(v)
        B = self._btn

        # row 0 – top utilities
        B(f,"DEG/RAD", self._toggle_deg,  0,0, bg_key="BTN_DARK", fg_key="ACCENT3", fnt=self.f_btn_xs)
        B(f,"(",        P("("),            0,1, bg_key="BTN_OP",   fg_key="TXT_OP",  fnt=self.f_btn_lg)
        B(f,")",        P(")"),            0,2, bg_key="BTN_OP",   fg_key="TXT_OP",  fnt=self.f_btn_lg)
        B(f,"⌫",        self._backspace,   0,3, bg_key="BTN_DARK", fg_key="ACCENT2", fnt=self.f_btn_lg)
        B(f,"AC",       self._clear_all,   0,4, bg_key="BTN_DARK", fg_key="ACCENT2", fnt=self.f_btn_lg)

        # row 1 – trig
        B(f,"sin",  P("sin("),  1,0, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"cos",  P("cos("),  1,1, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"tan",  P("tan("),  1,2, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"π",    P("π"),     1,3, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_sm)
        B(f,"e",    P("e"),     1,4, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_sm)

        # row 2 – inv trig + power
        B(f,"asin", P("asin("), 2,0, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"acos", P("acos("), 2,1, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"atan", P("atan("), 2,2, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"√",    P("sqrt("), 2,3, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_sm)
        B(f,"x²",   P("**2"),   2,4, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_sm)

        # row 3 – log + misc
        B(f,"log",  P("log("),  3,0, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"ln",   P("ln("),   3,1, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"xʸ",   P("**"),    3,2, bg_key="BTN_OP",   fg_key="TXT_OP",   fnt=self.f_btn_sm)
        B(f,"1/x",  P("1/("),   3,3, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)
        B(f,"|x|",  P("abs("),  3,4, bg_key="BTN_FUNC", fg_key="TXT_FUNC", fnt=self.f_btn_xs)

        # row 4 – ANS + 789 ÷
        B(f,"ANS", self._press_ans, 4,0, bg_key="BTN_OP", fg_key="ACCENT",  fnt=self.f_btn_xs)
        B(f,"7",   P("7"),          4,1, fnt=self.f_btn_lg)
        B(f,"8",   P("8"),          4,2, fnt=self.f_btn_lg)
        B(f,"9",   P("9"),          4,3, fnt=self.f_btn_lg)
        B(f,"÷",   P("/"),          4,4, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)

        # row 5 – % + 456 ×
        B(f,"%",   P("%"),  5,0, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)
        B(f,"4",   P("4"),  5,1, fnt=self.f_btn_lg)
        B(f,"5",   P("5"),  5,2, fnt=self.f_btn_lg)
        B(f,"6",   P("6"),  5,3, fnt=self.f_btn_lg)
        B(f,"×",   P("*"),  5,4, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)

        # row 6 – ! + 123 −
        B(f,"!",   P("!"),  6,0, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)
        B(f,"1",   P("1"),  6,1, fnt=self.f_btn_lg)
        B(f,"2",   P("2"),  6,2, fnt=self.f_btn_lg)
        B(f,"3",   P("3"),  6,3, fnt=self.f_btn_lg)
        B(f,"−",   P("-"),  6,4, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)

        # tall = button (rows 6-7, col 5)
        eq_btn = AnimButton(f, text="=", command=self._evaluate,
                            bg_key="BTN_EQ", fg_key="TXT_EQ",
                            radius=8, font_obj=self.f_btn_lg,
                            width=70, height=110)
        eq_btn.grid(row=6, column=5, rowspan=2, padx=3, pady=3, sticky="nsew")
        self._all_buttons.append(eq_btn)

        # row 7 – 0 00 . +
        B(f,"0",  P("0"),  7,0, fnt=self.f_btn_lg)
        B(f,"00", P("00"), 7,1, fnt=self.f_btn_sm)
        B(f,".",  P("."),  7,2, fnt=self.f_btn_lg)
        B(f,"+",  P("+"),  7,3, bg_key="BTN_OP", fg_key="TXT_OP",  fnt=self.f_btn_lg)

    # ── theme switching ─────────────────────────────
    def _switch_theme(self, dark_state):
        global _app_theme
        self._dark_mode = dark_state
        _app_theme.update(THEMES["dark"] if dark_state else THEMES["light"])
        self._apply_theme_colors()
        self._settings.refresh_theme()

    def _apply_theme_colors(self):
        bg   = th("BG")
        panel= th("PANEL")
        disp = th("DISPLAY_BG")
        acc  = th("ACCENT")
        acc3 = th("ACCENT3")
        tm   = th("TXT_MAIN")
        tdim = th("TXT_DIM")

        self.configure(bg=bg)
        self._root_frame.config(bg=bg)
        self._outer.config(bg=panel)

        # title row widgets
        for w in self._outer.winfo_children():
            try:
                w.config(bg=panel)
            except Exception:
                pass

        self._title_lbl.config(fg=acc,  bg=panel)
        self._mode_lbl.config( fg=acc3, bg=panel)
        self._ans_lbl.config(  fg=tdim, bg=panel)

        self._disp_frame.config(bg=disp,
                                highlightbackground=acc,
                                highlightthickness=1)
        self._expr_lbl.config(  fg=tdim, bg=disp)
        self._result_row.config(bg=disp)
        self._result_lbl.config(fg=tm,   bg=disp)
        self.cursor_lbl.config( fg=acc,  bg=disp)
        self._divider.config(   bg=acc)
        self._btn_frame.config( bg=panel)

        for b in self._all_buttons:
            b.refresh_theme()

    def _open_settings(self):
        if self._settings._visible:
            self._settings.hide()
        else:
            self._settings.show()

    # ── cursor blink ────────────────────────────────
    def _start_cursor_blink(self):
        self._cursor_on = True
        self._blink()

    def _blink(self):
        self._cursor_on = not self._cursor_on
        try:
            self.cursor_lbl.config(
                fg=th("ACCENT") if self._cursor_on else th("DISPLAY_BG"))
        except Exception:
            pass
        self.after(530, self._blink)

    # ── input handling ──────────────────────────────
    def _press(self, val):
        if self._just_result and val not in ("+", "-", "*", "/", "**", "%"):
            self._expression = ""
        self._just_result = False
        self._expression += str(val)
        self._update_display()

    def _press_ans(self):
        if self._last_answer is None:
            return
        if self._just_result:
            self._expression = ""
        self._just_result = False
        self._expression += str(self._last_answer)
        self._update_display()

    def _backspace(self):
        self._expression = self._expression[:-1]
        self._update_display()

    def _clear_all(self):
        self._expression  = ""
        self._just_result = False
        self.result_var.set("0")
        self.expr_var.set("")
        self._flash(th("ACCENT2"))

    def _toggle_deg(self):
        self._deg_mode = not self._deg_mode
        self._mode_lbl.config(text="DEG" if self._deg_mode else "RAD")
        self._flash(th("ACCENT3"))

    def _update_display(self):
        d = (self._expression
             .replace("*", "×").replace("/", "÷").replace("-", "−"))
        self.expr_var.set(d)
        self.result_var.set(d or "0")

    # ── evaluate ─────────────────────────────────────
    def _evaluate(self):
        expr = self._expression
        if not expr:
            return
        try:
            result = self._safe_eval(expr)
            show = (self._expression
                    .replace("*","×").replace("/","÷").replace("-","−"))
            self.expr_var.set(show)
            if (isinstance(result, float)
                    and result == int(result) and abs(result) < 1e15):
                result = int(result)
            self.result_var.set(str(result))
            self._last_answer = result
            self._ans_lbl.config(text=f"ANS: {result}")
            self._expression  = str(result)
            self._just_result = True
            self._flash(th("ACCENT"))
        except Exception:
            self.result_var.set("ERROR")
            self._flash(th("ACCENT2"))
            self._expression = ""

    def _flash(self, color, steps=10):
        orig = th("ACCENT")
        def pulse(n, col):
            try:
                self.cursor_lbl.config(fg=col)
            except Exception:
                return
            if n > 0:
                nxt = color if n % 2 == 0 else orig
                self.after(60, lambda: pulse(n-1, nxt))
            else:
                try:
                    self.cursor_lbl.config(fg=orig)
                except Exception:
                    pass
        pulse(steps, color)

    # ── safe eval ────────────────────────────────────
    def _safe_eval(self, expr):
        expr = expr.replace("π", str(math.pi))
        expr = expr.replace("÷", "/").replace("×", "*").replace("−", "-")
        # standalone e  (not part of a function name)
        expr = re.sub(r'(?<![a-zA-Z])e(?![a-zA-Z])', str(math.e), expr)

        # factorial
        def fact(m):
            return str(math.factorial(abs(int(m.group(1)))))
        expr = re.sub(r'(\d+)!', fact, expr)

        # deg trig wrapping
        if self._deg_mode:
            for fn in ("sin", "cos", "tan"):
                expr = re.sub(rf'\b{fn}\(', f'_d_{fn}(', expr)

        def _d_sin(x): return math.sin(math.radians(x))
        def _d_cos(x): return math.cos(math.radians(x))
        def _d_tan(x): return math.tan(math.radians(x))

        ns = {
            "__builtins__": {},
            "sin":  math.sin,  "cos": math.cos,  "tan": math.tan,
            "asin": math.asin, "acos":math.acos, "atan":math.atan,
            "sqrt": math.sqrt, "log": math.log10,"ln":  math.log,
            "abs":  abs,       "pow": pow,
            "pi":   math.pi,
            "_d_sin": _d_sin, "_d_cos": _d_cos, "_d_tan": _d_tan,
        }
        return eval(expr, ns)


if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()