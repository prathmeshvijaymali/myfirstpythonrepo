"""A polished, responsive desktop clock built with Tkinter."""

from __future__ import annotations

import math
import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont


BACKGROUND_TOP = (10, 14, 30)
BACKGROUND_BOTTOM = (18, 25, 47)
TEXT = "#F5F7FF"
MUTED = "#8994B3"
ACCENT = "#8B7CFF"
CYAN = "#54D9E8"


def blend(start: tuple[int, int, int], end: tuple[int, int, int], amount: float) -> str:
    """Interpolate two RGB colors and return a Tk-compatible hex color."""
    amount = max(0.0, min(1.0, amount))
    channels = tuple(round(a + (b - a) * amount) for a, b in zip(start, end))
    return "#{:02x}{:02x}{:02x}".format(*channels)


class ClockApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Luma — A better sense of time")
        self.root.geometry("1120x760")
        self.root.minsize(360, 600)
        self.root.configure(bg="#0A0E1E")

        self.is_24_hour = False
        self.canvas = tk.Canvas(
            root,
            bg="#0A0E1E",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)
        self.canvas.tag_bind("format_toggle", "<Button-1>", self._toggle_format)
        self.canvas.tag_bind("format_toggle", "<Enter>", self._on_toggle_enter)
        self.canvas.tag_bind("format_toggle", "<Leave>", self._on_leave)

        self._background_size = (0, 0)
        self._background_items: list[int] = []
        self._hovering_toggle = False
        self._tick()

    def _on_resize(self, _event: tk.Event) -> None:
        self._draw_background()
        self._render()

    def _on_motion(self, event: tk.Event) -> None:
        if self._hovering_toggle:
            return
        self.canvas.configure(cursor="hand2" if "format_toggle" in self.canvas.gettags("current") else "")

    def _on_toggle_enter(self, _event: tk.Event) -> None:
        self._hovering_toggle = True
        self.canvas.configure(cursor="hand2")

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovering_toggle = False
        self.canvas.configure(cursor="")

    def _toggle_format(self, _event: tk.Event) -> None:
        self.is_24_hour = not self.is_24_hour
        self._render()

    def _draw_background(self) -> None:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 2 or height < 2 or (width, height) == self._background_size:
            return

        for item in self._background_items:
            self.canvas.delete(item)
        self._background_items.clear()
        self._background_size = (width, height)

        strips = max(2, min(160, height // 5))
        strip_height = height / strips
        for index in range(strips):
            color = blend(BACKGROUND_TOP, BACKGROUND_BOTTOM, index / max(1, strips - 1))
            item = self.canvas.create_rectangle(
                0,
                index * strip_height,
                width,
                (index + 1) * strip_height + 1,
                fill=color,
                outline=color,
                tags=("background",),
            )
            self._background_items.append(item)

        self._background_items.append(
            self.canvas.create_oval(
                width * 0.55,
                -height * 0.5,
                width * 1.15,
                height * 0.48,
                fill="#151B3B",
                outline="",
                stipple="gray50",
                tags=("background",),
            )
        )
        self._background_items.append(
            self.canvas.create_oval(
                -width * 0.4,
                height * 0.48,
                width * 0.42,
                height * 1.3,
                fill="#102B43",
                outline="",
                stipple="gray50",
                tags=("background",),
            )
        )
        self.canvas.tag_lower("background")

    def _render(self) -> None:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 2 or height < 2:
            return

        self.canvas.delete("scene")
        now = datetime.now()
        compact = width < 820
        pad = max(20, min(54, int(width * 0.052)))
        header_y = max(34, int(height * 0.065))

        self._draw_brand(pad, header_y, compact)

        if compact:
            self._draw_compact(width, height, pad, header_y, now)
        else:
            self._draw_wide(width, height, pad, header_y, now)

    def _draw_brand(self, x: int, y: int, compact: bool) -> None:
        self.canvas.create_oval(
            x,
            y - 15,
            x + 30,
            y + 15,
            fill="#29264D",
            outline="#49437A",
            width=1,
            tags=("scene",),
        )
        self.canvas.create_arc(
            x + 8,
            y - 8,
            x + 22,
            y + 8,
            start=35,
            extent=290,
            style="arc",
            outline=CYAN,
            width=2,
            tags=("scene",),
        )
        self.canvas.create_line(
            x + 15,
            y,
            x + 20,
            y - 5,
            fill=TEXT,
            width=2,
            capstyle=tk.ROUND,
            tags=("scene",),
        )
        self.canvas.create_text(
            x + 42,
            y - 3,
            text="LUMA",
            fill=TEXT,
            anchor="w",
            font=("Segoe UI", 13, "bold"),
            tags=("scene",),
        )
        if not compact:
            self.canvas.create_text(
                x + 43,
                y + 14,
                text="A BETTER SENSE OF TIME",
                fill=MUTED,
                anchor="w",
                font=("Segoe UI", 7, "bold"),
                tags=("scene",),
            )

        self.canvas.create_text(
            self.canvas.winfo_width() - x,
            y,
            text="LOCAL TIME",
            fill="#AEB7D1",
            anchor="e",
            font=("Segoe UI", 9, "bold"),
            tags=("scene",),
        )
        self.canvas.create_oval(
            self.canvas.winfo_width() - x - 12,
            y - 3,
            self.canvas.winfo_width() - x - 6,
            y + 3,
            fill="#61E7BF",
            outline="",
            tags=("scene",),
        )

    def _draw_wide(
        self, width: int, height: int, pad: int, header_y: int, now: datetime
    ) -> None:
        top = max(header_y + 58, 112)
        date_top = height - max(94, int(height * 0.16))
        gap = 20
        card_bottom = max(top + 210, date_top - gap)
        available_width = width - 2 * pad - gap
        digital_width = int(available_width * 0.53)
        digital = (pad, top, pad + digital_width, card_bottom)
        analog = (pad + digital_width + gap, top, width - pad, card_bottom)

        self._panel(*digital)
        self._panel(*analog)
        self._draw_digital(digital, now, compact=False)
        self._draw_analog(analog, now)
        self._draw_date(pad, date_top, width - pad, height - pad)

    def _draw_compact(
        self, width: int, height: int, pad: int, header_y: int, now: datetime
    ) -> None:
        content_top = max(header_y + 38, 82)
        date_height = max(60, min(78, int(height * 0.13)))
        date_top = height - pad - date_height
        gap = max(12, int(pad * 0.55))
        main_height = max(300, date_top - content_top - gap * 2)
        digital_height = max(145, int(main_height * 0.42))
        digital_bottom = content_top + digital_height
        analog_bottom = min(date_top - gap, digital_bottom + gap + (main_height - digital_height))

        digital = (pad, content_top, width - pad, digital_bottom)
        analog = (pad, digital_bottom + gap, width - pad, analog_bottom)
        self._panel(*digital)
        self._panel(*analog)
        self._draw_digital(digital, now, compact=True)
        self._draw_analog(analog, now)
        self._draw_date(pad, date_top, width - pad, height - pad)

    def _panel(self, left: int, top: int, right: int, bottom: int) -> None:
        self._rounded_rectangle(
            left,
            top,
            right,
            bottom,
            radius=22,
            fill="#141A2D",
            outline="#303750",
            width=1,
            tags=("scene",),
        )
        self.canvas.create_line(
            left + 24,
            top + 1,
            right - 24,
            top + 1,
            fill="#393B60",
            width=1,
            tags=("scene",),
        )

    def _draw_digital(
        self, box: tuple[int, int, int, int], now: datetime, compact: bool
    ) -> None:
        left, top, right, bottom = box
        width = right - left
        height = bottom - top
        self.canvas.create_text(
            left + 30,
            top + 29,
            text="DIGITAL DISPLAY",
            anchor="w",
            fill=MUTED,
            font=("Segoe UI", 8, "bold"),
            tags=("scene",),
        )
        self.canvas.create_oval(
            right - 44,
            top + 24,
            right - 38,
            top + 30,
            fill=ACCENT,
            outline="",
            tags=("scene",),
        )

        time_value = now.strftime("%H:%M" if self.is_24_hour else "%I:%M")
        time_value = time_value.lstrip("0") if not self.is_24_hour else time_value
        time_size = int(min(105, width * (0.18 if compact else 0.17), height * 0.40))
        time_size = max(39, time_size)
        mid_y = top + height * (0.49 if compact else 0.50)

        if self.is_24_hour:
            self.canvas.create_text(
                (left + right) / 2,
                mid_y,
                text=time_value,
                fill=TEXT,
                font=("Segoe UI", time_size, "light"),
                tags=("scene",),
            )
        else:
            time_x = (left + right) / 2 - (10 if compact else 15)
            self.canvas.create_text(
                time_x,
                mid_y,
                text=time_value,
                fill=TEXT,
                font=("Segoe UI", time_size, "light"),
                tags=("scene",),
            )
            self.canvas.create_text(
                time_x + time_size * 1.78,
                mid_y + time_size * 0.17,
                text=now.strftime("%p"),
                fill=CYAN,
                anchor="w",
                font=("Segoe UI", max(11, int(time_size * 0.20)), "bold"),
                tags=("scene",),
            )

        self.canvas.create_line(
            left + 30,
            top + height * 0.72,
            right - 30,
            top + height * 0.72,
            fill="#2A3149",
            tags=("scene",),
        )
        self.canvas.create_text(
            left + 30,
            top + height * 0.79,
            text="TIME FORMAT",
            anchor="w",
            fill=MUTED,
            font=("Segoe UI", 8, "bold"),
            tags=("scene",),
        )
        self._draw_format_toggle(right - 115, top + height * 0.77)

    def _draw_format_toggle(self, center_x: float, center_y: float) -> None:
        label = "24H" if self.is_24_hour else "12H"
        self._rounded_rectangle(
            center_x - 37,
            center_y - 16,
            center_x + 37,
            center_y + 16,
            radius=14,
            fill="#222A43" if not self._hovering_toggle else "#2D3552",
            outline="#3C4562",
            width=1,
            tags=("scene", "format_toggle"),
        )
        knob_x = center_x + (17 if self.is_24_hour else -17)
        self.canvas.create_oval(
            knob_x - 12,
            center_y - 12,
            knob_x + 12,
            center_y + 12,
            fill=ACCENT,
            outline="",
            tags=("scene", "format_toggle"),
        )
        self.canvas.create_text(
            center_x,
            center_y,
            text=label,
            fill=TEXT,
            font=("Segoe UI", 8, "bold"),
            tags=("scene", "format_toggle"),
        )

    def _draw_analog(self, box: tuple[int, int, int, int], now: datetime) -> None:
        left, top, right, bottom = box
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2 + 5
        radius = min((right - left) * 0.32, (bottom - top) * 0.37)
        radius = max(62, radius)
        radius = min(radius, (bottom - top) / 2 - 46)

        self.canvas.create_text(
            left + 30,
            top + 29,
            text="ANALOG MOVEMENT",
            anchor="w",
            fill=MUTED,
            font=("Segoe UI", 8, "bold"),
            tags=("scene",),
        )
        self.canvas.create_oval(
            center_x - radius - 12,
            center_y - radius - 12,
            center_x + radius + 12,
            center_y + radius + 12,
            fill="#171E34",
            outline="#303953",
            width=1,
            tags=("scene",),
        )
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill="#11182B",
            outline="#4A5270",
            width=1,
            tags=("scene",),
        )

        for tick in range(60):
            angle = math.radians(tick * 6 - 90)
            outer = radius - 8
            inner = radius - (17 if tick % 5 == 0 else 11)
            color = "#C7CEE3" if tick % 5 == 0 else "#59637E"
            self.canvas.create_line(
                center_x + math.cos(angle) * inner,
                center_y + math.sin(angle) * inner,
                center_x + math.cos(angle) * outer,
                center_y + math.sin(angle) * outer,
                fill=color,
                width=2 if tick % 5 == 0 else 1,
                capstyle=tk.ROUND,
                tags=("scene",),
            )

        numeral_radius = radius - 29
        for number in range(1, 13):
            angle = math.radians(number * 30 - 90)
            self.canvas.create_text(
                center_x + math.cos(angle) * numeral_radius,
                center_y + math.sin(angle) * numeral_radius,
                text=str(number),
                fill="#C5CBE0",
                font=("Segoe UI", max(8, int(radius * 0.105)), "normal"),
                tags=("scene",),
            )

        seconds = now.second + now.microsecond / 1_000_000
        minutes = now.minute + seconds / 60
        hours = (now.hour % 12) + minutes / 60
        self._hand(center_x, center_y, radius * 0.47, hours * 30, "#F3F4FC", 5)
        self._hand(center_x, center_y, radius * 0.68, minutes * 6, CYAN, 3)
        self._hand(center_x, center_y, radius * 0.77, seconds * 6, ACCENT, 1)
        self.canvas.create_oval(
            center_x - 6,
            center_y - 6,
            center_x + 6,
            center_y + 6,
            fill=ACCENT,
            outline="#D5D0FF",
            width=1,
            tags=("scene",),
        )

    def _hand(
        self,
        center_x: float,
        center_y: float,
        length: float,
        degrees: float,
        color: str,
        width: int,
    ) -> None:
        angle = math.radians(degrees - 90)
        end_x = center_x + math.cos(angle) * length
        end_y = center_y + math.sin(angle) * length
        self.canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill=color,
            width=width,
            capstyle=tk.ROUND,
            tags=("scene",),
        )

    def _draw_date(self, left: int, top: int, right: int, bottom: int) -> None:
        self._panel(left, top, right, bottom)
        now = datetime.now()
        center_y = (top + bottom) / 2
        self.canvas.create_text(
            left + 24,
            center_y - 11,
            text="TODAY",
            anchor="w",
            fill=MUTED,
            font=("Segoe UI", 8, "bold"),
            tags=("scene",),
        )
        self.canvas.create_text(
            left + 24,
            center_y + 12,
            text=now.strftime("%A"),
            anchor="w",
            fill=CYAN,
            font=("Segoe UI", 11, "bold"),
            tags=("scene",),
        )
        date_text = now.strftime("%B %d, %Y")
        self.canvas.create_text(
            right - 24,
            center_y,
            text=date_text,
            anchor="e",
            fill=TEXT,
            font=("Segoe UI", 14 if right - left > 500 else 12, "normal"),
            tags=("scene",),
        )
        self.canvas.create_text(
            (left + right) / 2,
            bottom - 13,
            text="MAKE EVERY MOMENT COUNT",
            fill="#69738F",
            font=("Segoe UI", 7, "bold"),
            tags=("scene",),
        )

    def _rounded_rectangle(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
        radius: float,
        **options: object,
    ) -> int:
        radius = min(radius, (right - left) / 2, (bottom - top) / 2)
        points = [
            left + radius, top,
            right - radius, top,
            right, top,
            right, top + radius,
            right, bottom - radius,
            right, bottom,
            right - radius, bottom,
            left + radius, bottom,
            left, bottom,
            left, bottom - radius,
            left, top + radius,
            left, top,
        ]
        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=12,
            **options,
        )

    def _tick(self) -> None:
        self._render()
        self.root.after(80, self._tick)


def main() -> None:
    root = tk.Tk()
    ClockApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()