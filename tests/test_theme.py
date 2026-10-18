"""Keep website theme adjustments isolated from the LaTeX identity."""
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.theme import latex_color_defs, load_theme, write_web_css


class WebThemeTests(unittest.TestCase):
    def test_web_overrides_do_not_change_latex_colors(self):
        theme = load_theme()
        shared = copy.deepcopy(theme)
        shared["web"].pop("colors", None)
        self.assertEqual(latex_color_defs(theme), latex_color_defs(shared))

    def test_web_colors_override_shared_colors_without_mutating_theme(self):
        theme = load_theme()
        original = copy.deepcopy(theme)
        with TemporaryDirectory() as directory, patch("src.theme.ROOT", Path(directory)):
            css = write_web_css(theme).read_text()
        light = css.split(":root {")[1].split("}", 1)[0]
        dark = css.split(":root[data-theme='dark'] {")[1].split("}", 1)[0]
        self.assertIn(f"--blue: #{theme['web']['colors']['blue']};", light)
        self.assertIn(f"--blue: #{theme['web']['dark']['blue']};", dark)
        self.assertIn(f"--ink: #{theme['colors']['ink']};", light)
        self.assertEqual(theme, original)

    def test_existing_themes_without_web_overrides_still_build(self):
        theme = load_theme()
        theme["web"].pop("colors", None)
        with TemporaryDirectory() as directory, patch("src.theme.ROOT", Path(directory)):
            css = write_web_css(theme).read_text()
        self.assertIn(f"--blue: #{theme['colors']['blue']};", css)


if __name__ == "__main__":
    unittest.main()
