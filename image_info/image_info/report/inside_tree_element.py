"""
Framework to handle the pluggable report elements
"""
import importlib.util
import sys
import os
from os import walk
from abc import abstractmethod

try:
    from attr import define
except ImportError:
    from attr import s as define

from image_info.report.report import ReportElement

already_imported = False


def import_plugins():
    """
    Loads all the modules under a specific folder and exec them
    """
    global already_imported
    if already_imported:
        return
    already_imported = True
    current_dir = os.path.dirname(__file__)
    image_info_dir = os.path.dirname(current_dir)
    path = os.path.join(image_info_dir, "report/inside_tree")
    if os.path.isdir(path):
        filenames = next(walk(path), (None, None, []))[2]
        for file in filenames:
            if ".py" in file:
                stem = os.path.splitext(file)[0]
                module_name = f"inside_tree.{stem}"
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    os.path.join(path, file)
                )
                lib = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = lib
                spec.loader.exec_module(lib)


@define(slots=False)
class InsideTreeElement(ReportElement):
    """
    InsideTreeElements are element that need a tree to explore in order to
    produce their bit of report.
    """

    @classmethod
    @abstractmethod
    def explore(cls, tree, is_ostree=False):
        """
        Generates and returns an instance of an InsideTreeElement child.
        """


def find_all():
    """
    Find all the classes inheriting InsideTreeElement, and return them
    """
    import_plugins()
    return InsideTreeElement.__subclasses__()
