# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import sys, time, threading, queue, functools
from typing import Any
from types import MethodType
from abc import ABCMeta, abstractmethod

from . import utils


class VisBase(metaclass=ABCMeta):
    # these are expensive import so we attach to base class so derived class can use them
    from IPython import get_ipython, display
    import ipywidgets as widgets

    def __init__(self, widget, cell:widgets.Box, title:str, show_legend:bool, **vis_args):
        self.lock = threading.Lock()
        self._use_hbox = True
        #utils.set_default(vis_args, 'cell_width', '100%')

        self.widget = widget

        self.cell = cell or VisBase.widgets.HBox(layout=VisBase.widgets.Layout(\
            width=vis_args.get('cell_width', None))) if self._use_hbox else None
        if self._use_hbox:
            self.cell.children += (self.widget,) # type:ignore[OptionalMemberAcess]
        self._stream_vises = {}
        self.is_shown = cell is not None
        self.title = title
        self.last_ex = None
        self.layout_dirty = False
        self.q_last_processed = 0

    def show(self, blocking:bool=False):
        self.is_shown = True
        if VisBase.get_ipython():
            if self._use_hbox:
                VisBase.display.display(self.cell) # this method doesn't need returns
                #return self.cell
            else:
                return self._show_widget_notebook()
        else:
            return self._show_widget_native(blocking)

    def save(self, filepath:str)->None:
        self._save_widget(filepath)

    @abstractmethod
    def clear_plot(self, stream_vis, clear_history):
        """(for derived class) Clears the data in specified plot before new data is redrawn"""
        pass

    @abstractmethod
    def _show_widget_native(self, blocking:bool):
        pass
    @abstractmethod
    def _show_widget_notebook(self):
        pass
    def _save_widget(self, filepath:str)->None:
        raise NotImplementedError('Save functionality is not implemented')