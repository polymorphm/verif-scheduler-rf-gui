# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2013 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import subprocess
import tkinter
from tkinter import ttk, scrolledtext
from . import tk_mt

WEB_PAGE = 'https://github.com/verif-scheduler-2012-12-25'

ABOUT_TEXT = """\
Copyright 2012, 2013 Andrej A Antonov <polymorphm@gmail.com>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

class AboutWindow:
    def __init__(self):
        self._root = tkinter.Tk()
        self._tk_mt = tk_mt.TkMt(self._root)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        
        self._root.title(string='О Программе "Планирование проверок"')
        
        self._text = scrolledtext.ScrolledText(master=self._root)
        self._text.insert(tkinter.END, ABOUT_TEXT)
        self._text.config(state=tkinter.DISABLED)
        
        self._web_button = ttk.Button(master=self._root,
                text='Открыть web-страницу',
                command=self._open_web_page)
        self._close_button = ttk.Button(master=self._root,
                text='Закрыть окно',
                command=self.close)
        
        self._text.pack(fill=tkinter.BOTH, expand=True)
        self._web_button.pack()
        self._close_button.pack()
    
    def close(self):
        self._tk_mt.push_destroy()
    
    def _open_web_page(self):
        def thread_target():
            subprocess.call(('xdg-open', WEB_PAGE))
        
        self._tk_mt.start_daemon(thread_target)
