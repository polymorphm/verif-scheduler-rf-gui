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

import tkinter
from tkinter import ttk, scrolledtext

ABOUT_TEXT = """\
Copyright 2012, 2013 Andrej A Antonov <polymorphm@gmail.com>.

Web page: https://github.com/verif-scheduler-2012-12-25 .

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
        self._root.title(string='О Программе "Планирование проверок"')
        
        self._text = scrolledtext.ScrolledText(master=self._root)
        self._text.insert(tkinter.END, ABOUT_TEXT)
        self._text.config(state=tkinter.DISABLED)
        
        self._close_button = ttk.Button(master=self._root, text='Закрыть',
                command=self._root.destroy)
        
        self._text.pack(fill=tkinter.BOTH, expand=True)
        
        self._close_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
