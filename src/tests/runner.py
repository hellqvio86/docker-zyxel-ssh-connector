"""Minimal test runner that supports module-level test functions without pytest."""

from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


def build_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    package = importlib.import_module("src.tests")

    for module_info in pkgutil.iter_modules(package.__path__):
        if not module_info.name.startswith("test_"):
            continue

        module = importlib.import_module(f"src.tests.{module_info.name}")
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))

        for _, func in inspect.getmembers(module, inspect.isfunction):
            if func.__module__ == module.__name__ and func.__name__.startswith("test_"):
                suite.addTest(unittest.FunctionTestCase(func))

    return suite


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(build_suite())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
