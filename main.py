
import os
import json
import csv

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


Window.clearcolor = (0.035, 0.055, 0.10, 1)


class HistoryChart(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = []

        self.message = Label(
            text="Enter at least 2 results to see your graph",
            color=(0.65, 0.75, 0.9, 1),
            font_size="13sp"
        )
        self.add_widget(self.message)

        self.bind(size=self.draw_chart, pos=self.draw_chart)

    def update_values(self, values):
        self.values = values[-20:]
        self.message.opacity = 1 if len(self.values) < 2 else 0
        self.draw_chart()

    def draw_chart(self, *args):
        self.canvas.clear()

        self.message.size = self.size
        self.message.pos = self.pos

        if len(self.values) < 2:
            return

        left = self.x + dp(20)
        right = self.right - dp(20)
        bottom = self.y + dp(25)
        top = self.top - dp(20)

        width = right - left
        height = top - bottom

        minimum = 0
        maximum = max(self.values) * 1.2

        if maximum <= 0:
            return

        with self.canvas:

            # Grid lines
            Color(0.18, 0.25, 0.36, 1)

            for i in range(5):
                y = bottom + height * i / 4
                Line(
                    points=[left, y, right, y],
                    width=1
                )

            # Graph line
            Color(0.1, 0.85, 0.65, 1)

            points = []

            for i, value in enumerate(self.values):
                x = left + width * i / (len(self.values) - 1)
                y = bottom + height * value / maximum
                points.extend([x, y])

            Line(points=points, width=2.5)

            # Graph points
            Color(0.2, 0.85, 1, 1)

            for i, value in enumerate(self.values):
                x = left + width * i / (len(self.values) - 1)
                y = bottom + height * value / maximum

                Ellipse(
                    pos=(x - dp(4), y - dp(4)),
                    size=(dp(8), dp(8))
                )


class WillyAV(App):

    def build(self):

        self.title = "WILLY AV PREDICTION"

        self.history = []

        self.file_path = os.path.join(
            self.user_data_dir,
            "aviator_history.json"
        )

        self.load_history()

        # Main scrolling layout
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(12),
            size_hint_y=None
        )

        root.bind(minimum_height=root.setter("height"))

        scroll.add_widget(root)

        # Header
        title = Label(
            text="[b]WILLY AV[/b]",
            markup=True,
            font_size="30sp",
            color=(0.1, 0.8, 1, 1),
            size_hint_y=None,
            height=dp(55)
        )
        root.add_widget(title)

        subtitle = Label(
            text="AVIATOR MULTIPLIER ANALYSIS",
            font_size="12sp",
            color=(0.7, 0.8, 0.9, 1),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(subtitle)

        # Dashboard
        self.dashboard_label = Label(
            text="Loading dashboard...",
            markup=True,
            font_size="14sp",
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(150)
        )

        self.dashboard_label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.dashboard_label.canvas.before.clear()

        root.add_widget(self.dashboard_label)

        # Latest result
        self.result_label = Label(
            text="Ready to analyse results",
            font_size="14sp",
            color=(0.2, 0.9, 0.7, 1),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(self.result_label)

        # Input
        self.multiplier_input = TextInput(
            hint_text="Enter multiplier e.g. 2.45",
            multiline=False,
            input_filter="float",
            font_size="18sp",
            size_hint_y=None,
            height=dp(55),
            padding=dp(12)
        )

        root.add_widget(self.multiplier_input)

        # Add result button
        add_button = self.make_button(
            "ADD MULTIPLIER",
            (0.05, 0.48, 0.38, 1)
        )

        add_button.bind(on_press=self.add_result)
        root.add_widget(add_button)

        # Graph heading
        graph_title = Label(
            text="[b]MULTIPLIER HISTORY GRAPH[/b]",
            markup=True,
            color=(0.2, 0.8, 1, 1),
            font_size="15sp",
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(graph_title)

        # Graph
        self.chart = HistoryChart(
            size_hint_y=None,
            height=dp(220)
        )

        root.add_widget(self.chart)

        # History heading
        history_title = Label(
            text="[b]RECENT RESULTS[/b]",
            markup=True,
            color=(0.2, 0.8, 1, 1),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(history_title)

        self.history_label = Label(
            text="No results yet",
            color=(1, 1, 1, 1),
            font_size="14sp",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(140)
        )

        self.history_label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        root.add_widget(self.history_label)

        # Export button
        export_button = self.make_button(
            "EXPORT HISTORY TO CSV",
            (0.12, 0.35, 0.65, 1)
        )

        export_button.bind(on_press=self.export_history)
        root.add_widget(export_button)

        # Clear button
        clear_button = self.make_button(
            "CLEAR HISTORY",
            (0.65, 0.12, 0.16, 1)
        )

        clear_button.bind(on_press=self.clear_history)
        root.add_widget(clear_button)

        # Disclaimer
        disclaimer = Label(
            text=(
                "IMPORTANT: Historical statistics only. "
                "Aviator outcomes are random and cannot "
                "be reliably predicted."
            ),
            color=(1, 0.75, 0.35, 1),
            font_size="11sp",
            halign="center",
            size_hint_y=None,
            height=dp(65)
        )

        disclaimer.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        root.add_widget(disclaimer)

        self.update_dashboard()

        return scroll

    def make_button(self, text, color):

        return Button(
            text=text,
            background_normal="",
            background_color=color,
            color=(1, 1, 1, 1),
            bold=True,
            font_size="14sp",
            size_hint_y=None,
            height=dp(52)
        )

    def load_history(self):

        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r") as file:
                    data = json.load(file)

                self.history = [
                    float(value)
                    for value in data
                    if float(value) > 0
                ]

        except Exception:
            self.history = []

    def save_history(self):

        with open(self.file_path, "w") as file:
            json.dump(self.history, file)

    def add_result(self, instance):

        entered = self.multiplier_input.text.strip().lower()
        entered = entered.replace("x", "")

        try:
            value = float(entered)

            if value <= 0:
                raise ValueError

        except ValueError:
            self.result_label.text = "Enter a valid multiplier!"
            return

        self.history.append(value)

        self.save_history()

        self.multiplier_input.text = ""

        self.result_label.text = (
            f"Saved successfully: {value:.2f}x"
        )

        self.update_dashboard()

    def update_dashboard(self):

        recent = self.history[-10:]

        if not hasattr(self, "dashboard_label"):
            return

        if not recent:
            self.dashboard_label.text = (
                "[b]WILLY AV DASHBOARD[/b]\n\n"
                "Total rounds: 0\n"
                "Average: --\n"
                "LOW: 0 | MEDIUM: 0 | HIGH: 0"
            )

        else:
            average = sum(recent) / len(recent)

            low = sum(1 for x in recent if x < 2)
            medium = sum(
                1 for x in recent if 2 <= x < 5
            )
            high = sum(1 for x in recent if x >= 5)

            self.dashboard_label.text = (
                "[b]WILLY AV DASHBOARD[/b]\n\n"
                f"Total saved rounds: {len(self.history)}\n"
                f"Latest multiplier: {self.history[-1]:.2f}x\n"
                f"Average of last 10: {average:.2f}x\n"
                f"LOW (<2x): {low}\n"
                f"MEDIUM (2-5x): {medium}\n"
                f"HIGH (5x+): {high}"
            )

        if hasattr(self, "chart"):
            self.chart.update_values(self.history)

        if hasattr(self, "history_label"):
            recent_history = self.history[-10:]

            if recent_history:
                lines = [
                    f"Round {i}: {value:.2f}x"
                    for i, value in enumerate(
                        recent_history,
                        start=max(1, len(self.history) - 9)
                    )
                ]

                self.history_label.text = "\n".join(
                    reversed(lines)
                )

            else:
                self.history_label.text = "No results yet"

    def export_history(self, instance):

        if not self.history:
            self.result_label.text = "No history to export!"
            return

        path = os.path.join(
            self.user_data_dir,
            "willy_av_history.csv"
        )

        with open(path, "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(["Round", "Multiplier"])

            for number, value in enumerate(
                self.history,
                start=1
            ):
                writer.writerow([number, value])

        self.result_label.text = (
            "CSV exported! Saved in app storage."
        )

    def clear_history(self, instance):

        self.history = []

        self.save_history()

        self.update_dashboard()

        self.result_label.text = "History cleared!"


if __name__ == "__main__":
    WillyAV().run()
