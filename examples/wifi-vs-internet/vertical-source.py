"""Original caption-led explainer; procedural geometry and installed DejaVu Sans.

The connection diagram is simplified, illustrative, and not a measurement.
Use PORTRAIT=1 for the independently laid-out 9:16 edition.
"""
import os
import numpy as np
from manim import *

VERTICAL = os.environ.get("PORTRAIT") == "1"
config.pixel_width, config.pixel_height = ((1080, 1920) if VERTICAL else (1920, 1080))
config.frame_width, config.frame_height = ((8, 128 / 9) if VERTICAL else (128 / 9, 8))
config.frame_rate = 30
BG = "#091820"
PANEL = "#102732"
TEXT = "#EFFAF7"
MUTED = "#A9C0C8"
TEAL = "#40E4C1"
BLUE = "#74BBFF"
WARN = "#FFC06C"


def txt(s, size=36, color=TEXT, width=None):
    m = Text(s, font="DejaVu Sans", font_size=size, color=color, line_spacing=.85)
    if width and m.width > width:
        m.scale_to_fit_width(width)
    return m


def phone(color=TEXT):
    body = RoundedRectangle(width=.77, height=1.32, corner_radius=.12,
                            stroke_color=color, stroke_width=3, fill_color=PANEL, fill_opacity=1)
    line = Line([-.15, .47, 0], [.15, .47, 0], stroke_width=3, color=color)
    dot = Dot([0, -.50, 0], radius=.035, color=color)
    return VGroup(body, line, dot)


def router(color=TEAL):
    body = RoundedRectangle(width=1.38, height=.52, corner_radius=.12,
                            stroke_width=3, stroke_color=color, fill_color=PANEL, fill_opacity=1)
    sticks = VGroup(Line([-.46, .24, 0], [-.63, .78, 0], color=color, stroke_width=3),
                    Line([.46, .24, 0], [.63, .78, 0], color=color, stroke_width=3))
    leds = VGroup(*[Dot([x, 0, 0], radius=.032, color=color) for x in [-.36, -.16, .04]])
    return VGroup(body, sticks, leds)


def globe(color=BLUE):
    outer = Circle(radius=.65, color=color, stroke_width=3, fill_color=PANEL, fill_opacity=1)
    el = Ellipse(width=.60, height=1.3, color=color, stroke_width=2)
    h = Line([-.65, 0, 0], [.65, 0, 0], color=color, stroke_width=2)
    return VGroup(outer, el, h)


def wifi_bars():
    return VGroup(*[RoundedRectangle(width=.24, height=.30 + i * .29, corner_radius=.055,
                                     stroke_width=0, fill_color=TEAL, fill_opacity=1)
                   .move_to([i * .42, (.30 + i * .29) / 2, 0]) for i in range(4)]).center()


class WifiVsInternet(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.v = VERTICAL
        self.safe_width = 6.7 if self.v else 12.3
        self.title_y = 4.45 if self.v else 2.25
        self.caption_y = -4.55 if self.v else -2.68
        self.label_size = 28 if self.v else 27
        self.clock = ValueTracker(0)
        self.add(self.clock)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.frame_decor()
        self.hook(5 if self.v else 6)
        self.two_links(8 if self.v else 10)
        self.interruption(7 if self.v else 9)
        self.checks(9 if self.v else 11)
        self.takeaway(9 if self.v else 10)

    def frame_decor(self):
        w = config.frame_width
        top = 5.95 if self.v else 3.48
        brand = txt("HOME TECH / EXPLAINED", 19, MUTED)
        brand.to_edge(LEFT, buff=.65).set_y(top)
        number = txt("01", 19, TEAL).to_edge(RIGHT, buff=.65).set_y(top)
        self.add(brand, number)
        self.add(Line([-.5 * w + .65, top - .36, 0], [.5 * w - .65, top - .36, 0],
                      color=MUTED, stroke_opacity=.23, stroke_width=1))
        # A small bottom label keeps the animation explicitly illustrative.
        self.add(txt("SIMPLIFIED ILLUSTRATION", 17, MUTED).set_y(-5.92 if self.v else -3.52))

    def heading(self, s):
        return txt(s, 45 if self.v else 48, width=self.safe_width).set_y(self.title_y)

    def caption(self, s, color=MUTED):
        return txt(s, 31 if self.v else 31, color, width=self.safe_width).set_y(self.caption_y)

    def enter(self, mobs, seconds=.7):
        self.play(*[FadeIn(m, shift=UP * .12) for m in mobs], run_time=seconds)

    def leave(self, mobs, seconds=.5):
        self.play(*[FadeOut(m) for m in mobs], run_time=seconds)

    def hold(self, seconds):
        # Avoid float rounding adding a frame at an exact 30 fps boundary.
        self.wait(seconds - 1e-6)

    def hook(self, duration):
        title = self.heading("Full Wi-Fi bars,\nbut nothing loads?")
        card = RoundedRectangle(width=5.9 if self.v else 9.0, height=3.5 if self.v else 2.9,
                                corner_radius=.25, stroke_width=1.4, stroke_color="#254654",
                                fill_color=PANEL, fill_opacity=1).set_y(.25 if self.v else -.05)
        bars = wifi_bars().scale(1.25).move_to([-.95 if self.v else -2.25, .45 if self.v else .10, 0])
        spinner = Arc(radius=.58, start_angle=.0, angle=PI * 1.4, color=WARN, stroke_width=6)
        spinner.move_to([1.55 if self.v else 2.25, .45 if self.v else .1, 0])
        spinner.add_updater(lambda m, dt: m.rotate(-dt * 1.35))
        labels = VGroup(txt("STRONG SIGNAL", 20 if self.v else 23, TEAL).next_to(bars, DOWN, buff=.38),
                        txt("STILL LOADING", 20 if self.v else 23, WARN).next_to(spinner, DOWN, buff=.48))
        caption = self.caption("Signal strength is only\npart of the story." if self.v else
                               "Signal strength is only part of the story.")
        objs = [title, card, bars, spinner, labels, caption]
        self.enter(objs)
        self.hold(duration - 1.2)
        spinner.clear_updaters()
        self.leave(objs)

    def make_diagram(self):
        positions = ([[-.25, 2.12, 0], [-.25, -.08, 0], [-.25, -2.35, 0]] if self.v else
                     [[-4.45, .1, 0], [0, .1, 0], [4.45, .1, 0]])
        icons = VGroup(phone().move_to(positions[0]), router().move_to(positions[1]),
                       globe().move_to(positions[2]))
        node_labels = VGroup()
        for icon, label in zip(icons, ["DEVICE", "ROUTER", "INTERNET"]):
            t = txt(label, self.label_size, MUTED)
            if self.v:
                t.next_to(icon, RIGHT, buff=.48)
            else:
                t.next_to(icon, DOWN, buff=.55)
            node_labels.add(t)
        if self.v:
            p1, q1 = [-.25, 1.38, 0], [-.25, .65, 0]
            p2, q2 = [-.25, -.61, 0], [-.25, -1.62, 0]
        else:
            p1, q1 = [-3.93, .1, 0], [-.85, .1, 0]
            p2, q2 = [.85, .1, 0], [3.66, .1, 0]
        lines = VGroup(Line(p1, q1, color=TEAL, stroke_width=4), Line(p2, q2, color=BLUE, stroke_width=4))
        packets = VGroup()
        for index, line in enumerate(lines):
            dot = Dot(radius=.085, color=TEXT)
            dot.add_updater(lambda m, p=line, i=index: m.move_to(
                p.point_from_proportion((self.clock.get_value() * .52 + i * .25) % 1)))
            packets.add(dot)
        l1 = txt("1  WI-FI", 26 if self.v else 28, TEAL)
        l2 = txt("2  INTERNET", 26 if self.v else 28, BLUE)
        if self.v:
            l1.next_to(lines[0], LEFT, buff=.43)
            l2.next_to(lines[1], LEFT, buff=.43)
        else:
            l1.set_x(-2.3).set_y(1.0)
            l2.set_x(2.3).set_y(1.0)
        labels = VGroup(l1, l2)
        return VGroup(icons, node_labels, lines, labels, packets), lines, packets

    def two_links(self, duration):
        self.diagram, self.lines, self.packets = self.make_diagram()
        self.h = self.heading("Two links.\nDifferent jobs." if self.v else "Two links. Different jobs.")
        self.c = self.caption("Wi-Fi connects to your router.\nThe router connects onward.")
        self.enter([self.h, self.diagram, self.c])
        self.hold(duration - .7)

    def interruption(self, duration):
        new_h = self.heading("Strong Wi-Fi.\nInternet interrupted.")
        new_c = self.caption("One possible failure:\nyour Wi-Fi signal stays strong.", WARN)
        center = self.lines[1].get_center()
        # The gap and X denote only the illustrated upstream failure.
        cover = Circle(radius=.22, stroke_width=0, fill_color=BG, fill_opacity=1).move_to(center)
        cross = VGroup(Line(center + [-.13, -.13, 0], center + [.13, .13, 0], color=WARN, stroke_width=4),
                       Line(center + [-.13, .13, 0], center + [.13, -.13, 0], color=WARN, stroke_width=4))
        self.packets[1].clear_updaters()
        self.play(Transform(self.h, new_h), Transform(self.c, new_c),
                  self.lines[1].animate.set_color(WARN).set_opacity(.65),
                  FadeOut(self.packets[1]), FadeIn(cover), Create(cross), run_time=.8)
        self.hold(duration - 1.3)
        self.packets[0].clear_updaters()
        self.leave([self.h, self.c, self.diagram, cover, cross])

    def test_card(self, number, title, body, icon, center, width, height):
        panel = RoundedRectangle(width=width, height=height, corner_radius=.20,
                                 stroke_color="#284653", stroke_width=1.5,
                                 fill_color=PANEL, fill_opacity=1).move_to(center)
        tag = txt(number, 23, TEAL).move_to(panel.get_top() + [0, -.36, 0])
        icon.move_to(panel.get_center() + [0, .45 if self.v else .35, 0])
        t = txt(title, 30 if self.v else 33, TEXT, width=width-.5).move_to(panel.get_center()+[0,-.30 if self.v else -.55,0])
        b = txt(body, 23 if self.v else 26, MUTED, width=width-.5).move_to(panel.get_bottom()+[0,.43 if self.v else .48,0])
        return VGroup(panel, tag, icon, t, b)

    def checks(self, duration):
        h = self.heading("Two quick checks")
        site = VGroup(RoundedRectangle(width=1.48, height=.9, corner_radius=.08, color=BLUE, stroke_width=2.5),
                      Line([-.74,.20,0],[.74,.20,0],color=BLUE,stroke_width=2.5),
                      Dot([-.53,.33,0],radius=.04,color=BLUE), Dot([-.36,.33,0],radius=.04,color=BLUE))
        devices = VGroup(phone().scale(.59).shift(LEFT*.38), phone(BLUE).scale(.59).shift(RIGHT*.38))
        if self.v:
            centers = [[0,1.65,0], [0,-1.75,0]]
            width, height = 6.5, 3.0
        else:
            centers = [[-3.0,-.1,0], [3.0,-.1,0]]
            width, height = 5.65, 3.75
        a = self.test_card("01", "Try another site or app", "Only one fails?\nIt may be that service.", site, centers[0], width, height)
        b = self.test_card("02", "Try a second device", "Use the same Wi-Fi.\nCompare what works.", devices, centers[1], width, height)
        c = self.caption("On phones: turn mobile data off\nfor the test, then restore it." if self.v else
                         "On phones: turn mobile data off for the test, then restore it.", WARN)
        self.enter([h,a])
        first_wait = round((duration - 1.9) * .42 * 30) / 30
        self.hold(first_wait)
        self.enter([b,c])
        self.hold(round(((duration - 1.9) - first_wait) * 30) / 30)
        self.leave([h,a,b,c])

    def takeaway(self, duration):
        h = self.heading("Still stuck?")
        card = RoundedRectangle(width=6.5 if self.v else 11.5,
                                height=3.75 if self.v else 2.65, corner_radius=.22,
                                stroke_color="#284653", stroke_width=1.5,
                                fill_color=PANEL, fill_opacity=1).set_y(.8 if self.v else .3)
        p = phone(TEAL).scale(.82).move_to([0 if self.v else -4.55, 1.92 if self.v else .3, 0])
        t = txt("Check your internet provider\nfor a reported outage.", 33 if self.v else 36,
                width=5.9 if self.v else 8.4).move_to([0 if self.v else .75, .58 if self.v else .60, 0])
        sub = txt("Use mobile data, if available.", 25 if self.v else 28, MUTED,
                  width=6).move_to([0 if self.v else .75, -.48 if self.v else -.37, 0])
        result = txt("Check which link fails\nbefore buying new gear.", 38 if self.v else 36, TEAL,
                     width=self.safe_width).set_y(-2.7 if self.v else -1.91)
        caption = txt("These checks narrow the cause.\nThey do not prove it.", 28 if self.v else 24,
                      MUTED, width=self.safe_width).set_y(-4.48 if self.v else -3.00)
        self.enter([h,card,p,t,sub,result,caption])
        self.hold(duration - .7)
