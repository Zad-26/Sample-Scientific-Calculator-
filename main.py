"""
Scientific Calculator — Kivy/Android
Clean minimal design | White light mode | Dark dark mode | Purple accents
"""

import math
import re

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

# Only set fixed size on desktop for testing; on Android use full screen
if platform not in ("android", "ios"):
    Window.size = (400, 800)

# ══════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════
THEMES = {
    "dark": {
        # backgrounds
        "bg":           (0.08, 0.08, 0.10, 1),   # near black
        "display_bg":   (0.12, 0.12, 0.16, 1),   # dark grey
        "panel":        (0.10, 0.10, 0.13, 1),

        # buttons
        "btn_num":      (0.18, 0.18, 0.22, 1),   # dark grey
        "btn_op":       (0.28, 0.16, 0.45, 1),   # dark purple
        "btn_func":     (0.15, 0.15, 0.20, 1),   # slightly lighter grey
        "btn_eq":       (0.55, 0.20, 0.90, 1),   # vivid purple
        "btn_clear":    (0.35, 0.10, 0.10, 1),   # dark red

        # text
        "txt_main":     (1.00, 1.00, 1.00, 1),   # white
        "txt_dim":      (0.60, 0.60, 0.65, 1),   # grey
        "txt_num":      (1.00, 1.00, 1.00, 1),   # white
        "txt_op":       (0.80, 0.55, 1.00, 1),   # light purple
        "txt_func":     (0.75, 0.75, 0.80, 1),   # light grey
        "txt_eq":       (1.00, 1.00, 1.00, 1),   # white
        "txt_clear":    (1.00, 0.45, 0.45, 1),   # red

        # accents
        "accent":       (0.70, 0.40, 1.00, 1),   # purple
        "accent2":      (1.00, 0.45, 0.45, 1),   # red
        "accent3":      (0.60, 0.80, 1.00, 1),   # blue
        "divider":      (0.25, 0.25, 0.30, 1),
        "border":       (0.25, 0.25, 0.30, 1),
    },
    "light": {
        # backgrounds
        "bg":           (1.00, 1.00, 1.00, 1),   # pure white
        "display_bg":   (0.96, 0.96, 0.98, 1),   # off white
        "panel":        (1.00, 1.00, 1.00, 1),

        # buttons
        "btn_num":      (0.94, 0.94, 0.96, 1),   # light grey
        "btn_op":       (0.90, 0.82, 1.00, 1),   # light purple
        "btn_func":     (0.90, 0.90, 0.93, 1),   # very light grey
        "btn_eq":       (0.55, 0.20, 0.90, 1),   # vivid purple
        "btn_clear":    (1.00, 0.90, 0.90, 1),   # light red

        # text
        "txt_main":     (0.10, 0.10, 0.10, 1),   # near black
        "txt_dim":      (0.50, 0.50, 0.55, 1),   # grey
        "txt_num":      (0.10, 0.10, 0.10, 1),   # near black
        "txt_op":       (0.45, 0.10, 0.80, 1),   # dark purple
        "txt_func":     (0.30, 0.30, 0.35, 1),   # dark grey
        "txt_eq":       (1.00, 1.00, 1.00, 1),   # white
        "txt_clear":    (0.80, 0.10, 0.10, 1),   # red

        # accents
        "accent":       (0.55, 0.20, 0.90, 1),   # purple
        "accent2":      (0.80, 0.10, 0.10, 1),   # red
        "accent3":      (0.20, 0.50, 0.90, 1),   # blue
        "divider":      (0.88, 0.88, 0.90, 1),
        "border":       (0.85, 0.85, 0.88, 1),
    },
}


# ══════════════════════════════════════════════════════
#  CALCULATOR BUTTON
# ══════════════════════════════════════════════════════
class CalcButton(Button):
    def __init__(self, bg_color, fg_color, accent_color, **kwargs):
        super().__init__(**kwargs)
        self._bg     = list(bg_color)
        self._fg     = list(fg_color)
        self._accent = list(accent_color)

        self.background_normal = ""
        self.background_down   = ""
        self.background_color  = (0, 0, 0, 0)
        self.color             = fg_color
        self.bold              = True
        self.font_size         = sp(14)

        with self.canvas.before:
            self._rect_col  = Color(*bg_color)
            self._rect      = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(10)])

        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._rect.pos  = self.pos
        self._rect.size = self.size

    def on_press(self):
        # lighten/darken on press
        factor = 1.18 if self._bg[0] < 0.5 else 0.88
        pressed = [min(1, c * factor) for c in self._bg[:3]] + [1]
        self._rect_col.rgba = pressed

    def on_release(self):
        Clock.schedule_once(lambda dt: self._restore(), 0.10)

    def _restore(self):
        self._rect_col.rgba = self._bg

    def update_theme(self, bg, fg, accent):
        self._bg     = list(bg)
        self._fg     = list(fg)
        self._accent = list(accent)
        self.color   = fg
        self._rect_col.rgba = bg


# ══════════════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════════════
class DisplayWidget(BoxLayout):
    def __init__(self, theme, **kwargs):
        super().__init__(orientation="vertical",
                         padding=[dp(16), dp(10), dp(16), dp(10)],
                         **kwargs)
        self.size_hint_y = None
        self.height      = dp(160)

        with self.canvas.before:
            self._bg_col  = Color(*theme["display_bg"])
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(16)])

        self.bind(pos=self._upd, size=self._upd)

        # ANS label top-left (small, shows previous answer)
        self.ans_lbl = Label(
            text="", font_size=sp(11),
            color=theme["txt_dim"],
            halign="left", valign="middle",
            size_hint_y=None, height=dp(22))
        self.ans_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.add_widget(self.ans_lbl)

        # Expression label (what user typed, small, right-aligned)
        self.expr_lbl = Label(
            text="", font_size=sp(15),
            color=theme["txt_dim"],
            halign="right", valign="middle",
            size_hint_y=None, height=dp(30))
        self.expr_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.add_widget(self.expr_lbl)

        # Result label — full answer, large, auto-shrinks for long numbers
        self.result_lbl = Label(
            text="0", font_size=sp(46),
            color=theme["txt_main"],
            halign="right", valign="bottom",
            bold=True)
        self.result_lbl.bind(size=self._update_font)
        self.add_widget(self.result_lbl)

    def _update_font(self, widget, size):
        widget.text_size = size
        n = len(widget.text or "0")
        if n <= 9:
            widget.font_size = sp(46)
        elif n <= 13:
            widget.font_size = sp(36)
        elif n <= 18:
            widget.font_size = sp(26)
        else:
            widget.font_size = sp(19)

    def set_result(self, text):
        self.result_lbl.text = text
        self._update_font(self.result_lbl, self.result_lbl.size)

    def _upd(self, *_):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def update_theme(self, theme):
        self._bg_col.rgba     = theme["display_bg"]
        self.expr_lbl.color   = theme["txt_dim"]
        self.result_lbl.color = theme["txt_main"]
        self.ans_lbl.color    = theme["txt_dim"]

    def flash(self, color):
        orig = list(self.result_lbl.color)
        self.result_lbl.color = color
        Clock.schedule_once(
            lambda dt: setattr(self.result_lbl, 'color', orig), 0.15)


# ══════════════════════════════════════════════════════
#  SETTINGS POPUP
# ══════════════════════════════════════════════════════
class SettingsPopup(Popup):
    def __init__(self, calc_layout, **kwargs):
        self._calc = calc_layout
        t = calc_layout.theme

        # ── content box
        content = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(20), dp(24), dp(20)],
            spacing=dp(18))

        with content.canvas.before:
            Color(*t["bg"])
            self._pop_bg = RoundedRectangle(
                pos=content.pos, size=content.size, radius=[dp(20)])
        content.bind(
            pos =lambda w,v: setattr(self._pop_bg,'pos',v),
            size=lambda w,s: setattr(self._pop_bg,'size',s))

        # title row
        title_row = BoxLayout(size_hint_y=None, height=dp(36))
        title_lbl = Label(
            text="Settings", font_size=sp(18), bold=True,
            color=t["accent"], halign="left", valign="middle")
        title_lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        title_row.add_widget(title_lbl)
        content.add_widget(title_row)

        # divider
        div = Widget(size_hint_y=None, height=dp(1))
        with div.canvas:
            Color(*t["divider"])
            Rectangle(size=div.size, pos=div.pos)
        div.bind(pos =lambda w,v: self._upd_div(w),
                 size=lambda w,s: self._upd_div(w))
        self._div = div
        content.add_widget(div)

        # dark mode row
        mode_row = BoxLayout(size_hint_y=None, height=dp(52),
                             spacing=dp(12))

        # moon / sun icon label
        icon_lbl = Label(
            text="🌙  Dark Mode", font_size=sp(15),
            color=t["txt_main"], halign="left", valign="middle")
        icon_lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        mode_row.add_widget(icon_lbl)
        self._icon_lbl = icon_lbl

        sw = Switch(active=calc_layout._dark_mode,
                    size_hint_x=None, width=dp(80))
        sw.bind(active=lambda w, val: self._on_toggle(val))
        mode_row.add_widget(sw)
        content.add_widget(mode_row)

        # DEG / RAD row
        deg_row = BoxLayout(size_hint_y=None, height=dp(52),
                            spacing=dp(12))
        deg_lbl = Label(
            text="📐  Angle Mode", font_size=sp(15),
            color=t["txt_main"], halign="left", valign="middle")
        deg_lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        deg_row.add_widget(deg_lbl)
        self._deg_lbl = deg_lbl

        deg_sw = Switch(active=calc_layout._deg_mode,
                        size_hint_x=None, width=dp(80))
        deg_sw.bind(active=lambda w, val: self._on_deg_toggle(val))
        deg_row.add_widget(deg_sw)
        content.add_widget(deg_row)

        # DEG label
        self._deg_state_lbl = Label(
            text="DEG (ON)  =  degrees   |   RAD (OFF)  =  radians",
            font_size=sp(10), color=t["txt_dim"],
            halign="center", valign="middle",
            size_hint_y=None, height=dp(20))
        self._deg_state_lbl.bind(
            size=lambda w,s: setattr(w,'text_size',s))
        content.add_widget(self._deg_state_lbl)

        # close button
        close_btn = Button(
            text="  Close",
            font_size=sp(14), bold=True,
            size_hint_y=None, height=dp(48),
            background_normal="",
            background_color=(0,0,0,0),
            color=t["txt_eq"])
        with close_btn.canvas.before:
            Color(*t["btn_eq"])
            self._close_rect = RoundedRectangle(
                pos=close_btn.pos, size=close_btn.size,
                radius=[dp(10)])
        close_btn.bind(
            pos =lambda w,v: setattr(self._close_rect,'pos',v),
            size=lambda w,s: setattr(self._close_rect,'size',s))
        close_btn.bind(on_press=self.dismiss)
        content.add_widget(close_btn)

        super().__init__(
            title="", content=content,
            size_hint=(0.88, None), height=dp(360),
            background="",
            background_color=(0, 0, 0, 0.5),
            separator_height=0,
            **kwargs)

    def _upd_div(self, w):
        w.canvas.clear()
        with w.canvas:
            Color(*self._calc.theme["divider"])
            Rectangle(size=w.size, pos=w.pos)

    def _on_toggle(self, val):
        self._calc._switch_theme(val)
        t = self._calc.theme
        self._icon_lbl.text  = "🌙  Dark Mode" if val else "☀️  Light Mode"
        self._icon_lbl.color = t["txt_main"]
        self._deg_lbl.color  = t["txt_main"]
        self._deg_state_lbl.color = t["txt_dim"]
        with self.content.canvas.before:
            Color(*t["bg"])

    def _on_deg_toggle(self, val):
        self._calc._deg_mode = val
        self._calc._mode_lbl.text = "DEG" if val else "RAD"


# ══════════════════════════════════════════════════════
#  MAIN LAYOUT
# ══════════════════════════════════════════════════════
class CalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            **kwargs)

        self._expression  = ""
        self._just_result = False
        self._last_answer = None
        self._deg_mode    = True
        self._dark_mode   = True
        self.theme        = dict(THEMES["dark"])
        self._all_buttons = []

        with self.canvas.before:
            self._bg_col  = Color(*self.theme["bg"])
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self._build_ui()

    def _upd_bg(self, *_):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    # ── UI ────────────────────────────────────────────
    def _build_ui(self):
        t = self.theme

        # ── top bar ─────────────────────────────────
        top = BoxLayout(
            size_hint_y=None, height=dp(48),
            spacing=dp(8), padding=[dp(4), 0, dp(4), 0])

        self._title_lbl = Label(
            text="Scientific Calculator",
            font_size=sp(15), bold=True,
            color=t["accent"],
            halign="left", valign="middle")
        self._title_lbl.bind(
            size=lambda w,s: setattr(w,'text_size',s))
        top.add_widget(self._title_lbl)

        self._mode_lbl = Label(
            text="DEG", font_size=sp(12),
            color=t["accent3"],
            halign="right", valign="middle",
            size_hint_x=None, width=dp(40))
        top.add_widget(self._mode_lbl)

        # settings button — gear icon ⚙
        settings_btn = Button(
            text="⚙",
            font_size=sp(22), bold=False,
            size_hint_x=None, width=dp(48),
            background_normal="",
            background_color=(0,0,0,0),
            color=t["txt_eq"])
        with settings_btn.canvas.before:
            self._set_btn_col = Color(*t["btn_eq"])
            self._set_btn_rect = RoundedRectangle(
                pos=settings_btn.pos,
                size=settings_btn.size,
                radius=[dp(12)])
        settings_btn.bind(
            pos =lambda w,v: setattr(self._set_btn_rect,'pos',v),
            size=lambda w,s: setattr(self._set_btn_rect,'size',s))
        settings_btn.bind(on_press=lambda x: self._open_settings())
        top.add_widget(settings_btn)
        self._settings_btn = settings_btn

        self.add_widget(top)

        # ── display ─────────────────────────────────
        self._display = DisplayWidget(t)
        self.add_widget(self._display)

        # ── thin divider ────────────────────────────
        div = Widget(size_hint_y=None, height=dp(1))
        with div.canvas:
            self._div_col  = Color(*t["divider"])
            self._div_rect = Rectangle(pos=div.pos, size=div.size)
        div.bind(
            pos =lambda w,v: setattr(self._div_rect,'pos',v),
            size=lambda w,s: setattr(self._div_rect,'size',s))
        self.add_widget(div)

        # ── button grid ─────────────────────────────
        grid = GridLayout(cols=5, spacing=dp(6))
        self._grid = grid
        self._build_buttons(grid)
        self.add_widget(grid)

    # ── buttons ───────────────────────────────────────
    def _mk(self, parent, text, bg_k, fg_k, action,
            h=dp(56), font_size=None):
        t   = self.theme
        btn = CalcButton(
            bg_color     = t[bg_k],
            fg_color     = t[fg_k],
            accent_color = t["accent"],
            text         = text,
            size_hint    = (1, None),
            height       = h,
            font_size    = sp(font_size or 14))
        btn._bg_key = bg_k
        btn._fg_key = fg_k
        btn.bind(on_press=lambda x: action())
        parent.add_widget(btn)
        self._all_buttons.append(btn)
        return btn

    def _build_buttons(self, g):
        P  = lambda v: lambda: self._press(v)
        h  = dp(54)
        hb = dp(54)   # same height for all rows

        # ── row 0: utilities
        self._mk(g,"DEG/RAD","btn_func","txt_func", self._toggle_deg, h=hb, font_size=11)
        self._mk(g,"(",      "btn_op",  "txt_op",   P("("),  h=hb)
        self._mk(g,")",      "btn_op",  "txt_op",   P(")"),  h=hb)
        self._mk(g,"⟵",      "btn_func","txt_clear", self._backspace, h=hb, font_size=20)
        self._mk(g,"AC",     "btn_clear","txt_clear", self._clear_all, h=hb)

        # ── row 1: trig
        self._mk(g,"sin",  "btn_func","txt_func", P("sin("), h=hb, font_size=13)
        self._mk(g,"cos",  "btn_func","txt_func", P("cos("), h=hb, font_size=13)
        self._mk(g,"tan",  "btn_func","txt_func", P("tan("), h=hb, font_size=13)
        self._mk(g,"π",    "btn_func","txt_op",   P("π"),    h=hb, font_size=16)
        self._mk(g,"e",    "btn_func","txt_op",   P("e"),    h=hb, font_size=16)

        # ── row 2: inverse trig + power
        self._mk(g,"asin", "btn_func","txt_func", P("asin("), h=hb, font_size=11)
        self._mk(g,"acos", "btn_func","txt_func", P("acos("), h=hb, font_size=11)
        self._mk(g,"atan", "btn_func","txt_func", P("atan("), h=hb, font_size=11)
        self._mk(g,"√",    "btn_func","txt_op",   P("sqrt("),h=hb, font_size=18)
        self._mk(g,"x²",   "btn_func","txt_op",   P("**2"),  h=hb, font_size=13)

        # ── row 3: log + misc
        self._mk(g,"log",  "btn_func","txt_func", P("log("), h=hb, font_size=13)
        self._mk(g,"ln",   "btn_func","txt_func", P("ln("),  h=hb, font_size=13)
        self._mk(g,"xʸ",   "btn_op",  "txt_op",   P("**"),   h=hb, font_size=13)
        self._mk(g,"1/x",  "btn_func","txt_func", P("1/("),  h=hb, font_size=11)
        self._mk(g,"|x|",  "btn_func","txt_func", P("abs("), h=hb, font_size=11)

        # ── row 4: ANS + 7 8 9 ÷
        self._mk(g,"ANS",  "btn_op",  "txt_op",   self._press_ans, h=hb, font_size=12)
        self._mk(g,"7",    "btn_num", "txt_num",  P("7"),    h=hb, font_size=18)
        self._mk(g,"8",    "btn_num", "txt_num",  P("8"),    h=hb, font_size=18)
        self._mk(g,"9",    "btn_num", "txt_num",  P("9"),    h=hb, font_size=18)
        self._mk(g,"÷",    "btn_op",  "txt_op",   P("/"),    h=hb, font_size=20)

        # ── row 5: % + 4 5 6 ×
        self._mk(g,"%",    "btn_op",  "txt_op",   P("%"),    h=hb, font_size=18)
        self._mk(g,"4",    "btn_num", "txt_num",  P("4"),    h=hb, font_size=18)
        self._mk(g,"5",    "btn_num", "txt_num",  P("5"),    h=hb, font_size=18)
        self._mk(g,"6",    "btn_num", "txt_num",  P("6"),    h=hb, font_size=18)
        self._mk(g,"×",    "btn_op",  "txt_op",   P("*"),    h=hb, font_size=20)

        # ── row 6: ! + 1 2 3 −
        self._mk(g,"!",    "btn_op",  "txt_op",   P("!"),    h=hb, font_size=18)
        self._mk(g,"1",    "btn_num", "txt_num",  P("1"),    h=hb, font_size=18)
        self._mk(g,"2",    "btn_num", "txt_num",  P("2"),    h=hb, font_size=18)
        self._mk(g,"3",    "btn_num", "txt_num",  P("3"),    h=hb, font_size=18)
        self._mk(g,"−",    "btn_op",  "txt_op",   P("-"),    h=hb, font_size=22)

        # ── row 7: 0  00  .  +  =
        self._mk(g,"0",    "btn_num", "txt_num",  P("0"),    h=hb, font_size=18)
        self._mk(g,"00",   "btn_num", "txt_num",  P("00"),   h=hb, font_size=14)
        self._mk(g,".",    "btn_num", "txt_num",  P("."),    h=hb, font_size=22)
        self._mk(g,"+",    "btn_op",  "txt_op",   P("+"),    h=hb, font_size=22)
        self._mk(g,"=",    "btn_eq",  "txt_eq",   self._evaluate, h=hb, font_size=22)

    # ── theme ─────────────────────────────────────────
    def _switch_theme(self, dark):
        self._dark_mode = dark
        self.theme = dict(THEMES["dark"] if dark else THEMES["light"])
        t = self.theme

        self._bg_col.rgba          = t["bg"]
        self._div_col.rgba         = t["divider"]
        self._title_lbl.color      = t["accent"]
        self._mode_lbl.color       = t["accent3"]
        self._set_btn_col.rgba     = t["btn_eq"]
        self._settings_btn.color   = t["txt_eq"]

        self._display.update_theme(t)

        for btn in self._all_buttons:
            btn.update_theme(
                bg     = t[btn._bg_key],
                fg     = t[btn._fg_key],
                accent = t["accent"])

    def _open_settings(self):
        SettingsPopup(self).open()

    # ── input ─────────────────────────────────────────
    def _press(self, val):
        if self._just_result and val not in ("+","-","*","/","**","%"):
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
        self._display.expr_lbl.text = ""
        self._display.ans_lbl.text  = ""
        self._display.set_result("0")
        self._display.flash(self.theme["accent2"])

    def _toggle_deg(self):
        self._deg_mode = not self._deg_mode
        self._mode_lbl.text = "DEG" if self._deg_mode else "RAD"

    def _update_display(self):
        d = (self._expression
             .replace("*","×").replace("/","÷").replace("-","−"))
        self._display.expr_lbl.text = ""
        self._display.set_result(d or "0")

    # ── evaluate ──────────────────────────────────────
    def _evaluate(self):
        expr = self._expression
        if not expr:
            return
        try:
            result = self._safe_eval(expr)
            show = (expr.replace("*","×")
                        .replace("/","÷")
                        .replace("-","−"))
            self._display.expr_lbl.text = show
            if (isinstance(result, float)
                    and result == int(result)
                    and abs(result) < 1e15):
                result = int(result)
            result_str = str(result)
            self._display.set_result(result_str)
            self._last_answer  = result
            self._display.ans_lbl.text = f"ANS = {result_str}"
            self._expression   = str(result)
            self._just_result  = True
            self._display.flash(self.theme["accent"])
        except Exception:
            self._display.set_result("Error")
            self._display.flash(self.theme["accent2"])
            self._expression = ""

    # ── safe eval ─────────────────────────────────────
    def _safe_eval(self, expr):
        expr = expr.replace("π", str(math.pi))
        expr = expr.replace("÷","/").replace("×","*").replace("−","-")
        expr = re.sub(r'(?<![a-zA-Z])e(?![a-zA-Z])', str(math.e), expr)

        def fact(m):
            return str(math.factorial(abs(int(m.group(1)))))
        expr = re.sub(r'(\d+)!', fact, expr)

        if self._deg_mode:
            for fn in ("sin","cos","tan"):
                expr = re.sub(rf'\b{fn}\(', f'_d_{fn}(', expr)

        def _d_sin(x): return math.sin(math.radians(x))
        def _d_cos(x): return math.cos(math.radians(x))
        def _d_tan(x): return math.tan(math.radians(x))

        ns = {
            "__builtins__": {},
            "sin":  math.sin,  "cos": math.cos,  "tan": math.tan,
            "asin": math.asin, "acos":math.acos, "atan":math.atan,
            "sqrt": math.sqrt, "log": math.log10,"ln":  math.log,
            "abs":  abs,       "pow": pow,        "pi":  math.pi,
            "_d_sin":_d_sin, "_d_cos":_d_cos, "_d_tan":_d_tan,
        }
        return eval(expr, ns)


# ══════════════════════════════════════════════════════
#  APP
# ══════════════════════════════════════════════════════
class ScientificCalculatorApp(App):
    def build(self):
        self.title = "Scientific Calculator"
        return CalculatorLayout()


if __name__ == "__main__":
    ScientificCalculatorApp().run()
