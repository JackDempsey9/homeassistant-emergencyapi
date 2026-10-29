"""max_warning_level over what DataQuoll publishes (API v1.105.0): a feature whose level DataQuoll cannot confirm
carries no warningLevel at all. Run: python3 -m unittest discover -s tests (no Home Assistant needed)."""
import importlib.util
import pathlib
import unittest

_PATH = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "emergencyapi" / "levels.py"
_SPEC = importlib.util.spec_from_file_location("levels", _PATH)
levels = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(levels)


def feature(fid, level=None):
    props = {} if level is None else {"warningLevel": level}
    return {"id": fid, "properties": props}


class MaxWarningLevel(unittest.TestCase):
    def test_present_levels_take_the_highest(self):
        self.assertEqual(levels.max_warning_level([feature("a", "advice"), feature("b", "watch_and_act")]), "watch_and_act")

    def test_all_none_is_none(self):
        self.assertEqual(levels.max_warning_level([feature("a", "none"), feature("b", "none")]), "none")

    def test_a_missing_level_is_unknown_never_none(self):
        # A QLD EMQ or TasALERT warning DataQuoll cannot confirm: the API leaves the level out.
        self.assertIsNone(levels.max_warning_level([feature("qld-emq-1")]))
        self.assertIsNone(levels.max_warning_level([feature("a", "none"), feature("qld-emq-1")]))
        self.assertIsNone(levels.max_warning_level([feature("a", "watch_and_act"), feature("qld-emq-1")]))

    def test_a_confirmed_emergency_warning_cannot_be_exceeded(self):
        self.assertEqual(levels.max_warning_level([feature("a", "emergency_warning"), feature("qld-emq-1")]), "emergency_warning")

    def test_a_twin_that_states_the_level_settles_it(self):
        # NSW RFS GeoJSON and its CAP twin are one incident: the GeoJSON row states the level.
        self.assertEqual(levels.max_warning_level([feature("nsw-rfs-681567", "none"), feature("nsw-rfs-cap-681567")]), "none")
        self.assertEqual(levels.max_warning_level([feature("nsw-rfs-681567", "advice"), feature("nsw-rfs-cap-681567")]), "advice")
        self.assertIsNone(levels.max_warning_level([feature("nsw-rfs-cap-681567")]))

    def test_no_incidents_is_unknown(self):
        self.assertIsNone(levels.max_warning_level([]))


if __name__ == "__main__":
    unittest.main()
