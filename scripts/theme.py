"""Shared weekly visual themes.

Rotates the *decorative* chrome (page background, header banner, header
subtitle color) across a small set of curated, high-contrast palettes so the
cards look different week to week — without touching the semantic colors
used elsewhere (red = alert, green = good, gold = score), which must stay
consistent for the report to remain readable at a glance.
"""
from datetime import date

PALETTES = [
    {
        "name": "Forest",
        "bg": "#F6F3EA",
        "header_bg": "#1F5C45",
        "header_sub": "#DCEFE4",
        "accent": "#46A36F",
    },
    {
        "name": "Ocean",
        "bg": "#F4F8FB",
        "header_bg": "#023E8A",
        "header_sub": "#CFE8FF",
        "accent": "#0077B6",
    },
    {
        "name": "Plum",
        "bg": "#FBF6FA",
        "header_bg": "#6A0572",
        "header_sub": "#F1D6F5",
        "accent": "#AB4B9C",
    },
    {
        "name": "Rust",
        "bg": "#FFF8F0",
        "header_bg": "#9D0208",
        "header_sub": "#FBD7C6",
        "accent": "#E76F51",
    },
]


def get_theme(week_number=None):
    """Return this week's palette. All five card scripts call this so the
    whole report set stays visually consistent within a given week."""
    if week_number is None:
        week_number = date.today().isocalendar()[1]
    return PALETTES[week_number % len(PALETTES)]
