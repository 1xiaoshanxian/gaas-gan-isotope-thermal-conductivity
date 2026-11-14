# -*- coding: utf-8 -*-
"""Shared physical geometry for Fig. 1(a) and Fig. 2(a,b)."""

FIGSIZE = (7.1, 3.22)
MAIN_WIDTH = 2.80
MAIN_HEIGHT = 2.20
BOTTOM = 0.52


def axes_rect(left, bottom, width, height):
    """Convert inches to figure coordinates without export-dependent cropping."""
    return [left / FIGSIZE[0], bottom / FIGSIZE[1],
            width / FIGSIZE[0], height / FIGSIZE[1]]


MAIN_RECT = axes_rect(0.55, BOTTOM, MAIN_WIDTH, MAIN_HEIGHT)
SECOND_RECT = axes_rect(4.15, BOTTOM, MAIN_WIDTH, MAIN_HEIGHT)
# The three contrast panels, including their gaps, span the same width and
# height as the main panel; both columns share the top and bottom boundaries.
CONTRAST_RECTS = [axes_rect(4.15, BOTTOM + (2 - j) * 0.825, MAIN_WIDTH, 0.55)
                  for j in range(3)]
