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

import itertools
import tkinter
import threading
from tkinter import ttk, scrolledtext
from . import tk_mt
from . import about_window
from .lib_verif_scheduler import date_parser
from .lib_verif_scheduler import excl_file
from .lib_verif_scheduler import verif_scheduler

DATA_STATE=object()
CALC_STATE=object()
RESULT_STATE=object()

DEFAULT_MAIN_WINDOW_WIDTH = 700
DEFAULT_MAIN_WINDOW_HEIGHT = 500

class UserError(Exception):
    pass

class Data:
    pass

class CalcParams:
    pass

def get_date_list(text):
    for line in filter(None, map(lambda s: s.strip(), text.split('\n'))):
        if ':' not in line:
            yield date_parser.parse_date(line)
            continue
        
        begin_date, end_date = \
                map(date_parser.parse_date,
                        map(lambda s: s.strip(),
                                line.split(':', 1)))
        
        for date in verif_scheduler.make_date_iter(begin_date, end_date):
            # TODO: in Python-3.3+ we may use ``yield from``
            yield date

class WeekDaysWidget:
    def __init__(self, master):
        self.frame = ttk.Frame(master=master)
        
        self.mo_var = tkinter.BooleanVar()
        self.tu_var = tkinter.BooleanVar()
        self.we_var = tkinter.BooleanVar()
        self.th_var = tkinter.BooleanVar()
        self.fr_var = tkinter.BooleanVar()
        self.sa_var = tkinter.BooleanVar()
        self.su_var = tkinter.BooleanVar()
        
        self.mo = ttk.Checkbutton(master=self.frame, variable=self.mo_var, text='Пн')
        self.tu = ttk.Checkbutton(master=self.frame, variable=self.tu_var, text='Вт')
        self.we = ttk.Checkbutton(master=self.frame, variable=self.we_var, text='Ср')
        self.th = ttk.Checkbutton(master=self.frame, variable=self.th_var, text='Чт')
        self.fr = ttk.Checkbutton(master=self.frame, variable=self.fr_var, text='Пт')
        self.sa = ttk.Checkbutton(master=self.frame, variable=self.sa_var, text='Сб')
        self.su = ttk.Checkbutton(master=self.frame, variable=self.su_var, text='Вс')
        
        self.mo.pack(side=tkinter.LEFT, padx=5)
        self.tu.pack(side=tkinter.LEFT, padx=5)
        self.we.pack(side=tkinter.LEFT, padx=5)
        self.th.pack(side=tkinter.LEFT, padx=5)
        self.fr.pack(side=tkinter.LEFT, padx=5)
        self.sa.pack(side=tkinter.LEFT, padx=5)
        self.su.pack(side=tkinter.LEFT, padx=5)
    
    def get(self):
        week_days = []
        
        if self.mo_var.get():
            week_days.append(0)
        if self.tu_var.get():
            week_days.append(1)
        if self.we_var.get():
            week_days.append(2)
        if self.th_var.get():
            week_days.append(3)
        if self.fr_var.get():
            week_days.append(4)
        if self.sa_var.get():
            week_days.append(5)
        if self.su_var.get():
            week_days.append(6)
        
        return tuple(week_days)
    
    def set(self, week_days):
        self.mo_var.set(False)
        self.tu_var.set(False)
        self.we_var.set(False)
        self.th_var.set(False)
        self.fr_var.set(False)
        self.sa_var.set(False)
        self.su_var.set(False)
        
        for week_day in week_days:
            if week_day == 0:
                self.mo_var.set(True)
            if week_day == 1:
                self.tu_var.set(True)
            if week_day == 2:
                self.we_var.set(True)
            if week_day == 3:
                self.th_var.set(True)
            if week_day == 4:
                self.fr_var.set(True)
            if week_day == 5:
                self.sa_var.set(True)
            if week_day == 6:
                self.su_var.set(True)

def week_days_to_str(week_days):
    week_days_str = []
    
    for week_day in week_days:
        if week_day == 0:
            week_days_str.append('Пн')
        if week_day == 1:
            week_days_str.append('Вт')
        if week_day == 2:
            week_days_str.append('Ср')
        if week_day == 3:
            week_days_str.append('Чт')
        if week_day == 4:
            week_days_str.append('Пн')
        if week_day == 5:
            week_days_str.append('Сб')
        if week_day == 6:
            week_days_str.append('Вс')
    
    return ', '.join(week_days_str)

class MainWindow:
    def __init__(self):
        self._root = tkinter.Tk()
        self._tk_mt = tk_mt.TkMt(self._root)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root_frame = ttk.Frame(master=self._root)
        
        self._root.title(string='Планирование проверок')
        self._root.geometry('{}x{}'.format(
                DEFAULT_MAIN_WINDOW_WIDTH, DEFAULT_MAIN_WINDOW_HEIGHT))
        
        self._menubar = tkinter.Menu(master=self._root)
        self._program_menu = tkinter.Menu(master=self._menubar)
        self._clipboard_menu = tkinter.Menu(master=self._menubar)
        self._help_menu = tkinter.Menu(master=self._menubar)
        
        self._program_menu.add_command(label="Выполнить расчёт", command=self._do_calc)
        self._program_menu.add_command(label="Изменить данные", command=self._recalc)
        self._program_menu.add_command(label="Очистить", command=self._clear)
        self._program_menu.add_separator()
        self._program_menu.add_command(label="Закрыть", command=self.close)
        
        self._clipboard_menu.add_command(
                label="Копировать исключения в буфер обмена", command=self._excl_copy)
        self._clipboard_menu.add_command(
                label="Вставить исключения из буфера обмена", command=self._excl_paste)
        self._clipboard_menu.add_command(
                label="Копировать результат в буфер обмена", command=self._result_copy)
        
        self._help_menu.add_command(label="О программе...", command=self._show_about)
        
        self._menubar.add_cascade(label="Программа", menu=self._program_menu)
        self._menubar.add_cascade(label="Буфер обмена", menu=self._clipboard_menu)
        self._menubar.add_cascade(label="Справка", menu=self._help_menu)
        self._root.config(menu=self._menubar)
        
        self._notebook = ttk.Notebook(master=self._root_frame)
        self._data_tab = ttk.Frame(master=self._notebook)
        self._excl_tab = ttk.Frame(master=self._notebook)
        self._result_tab = ttk.Frame(master=self._notebook)
        
        self._data_tab.propagate(False)
        self._excl_tab.propagate(False)
        self._result_tab.propagate(False)
        self._notebook.add(self._data_tab, text='Данные')
        self._notebook.add(self._excl_tab, text='Исключения')
        self._notebook.add(self._result_tab, text='Результат')
        
        self._status_var = tkinter.StringVar()
        self._statusbar = ttk.Label(master=self._root_frame,
                textvariable=self._status_var)
        
        self._notebook.pack(fill=tkinter.BOTH, expand=True)
        self._statusbar.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self._root_frame.pack(fill=tkinter.BOTH, expand=True)
        
        self._data_text = None
        self._excl_text = None
        self._result_text = None
        self._state = None
        
        self._clear()
    
    def close(self):
        self._tk_mt.push_destroy()
    
    def _excl_copy(self):
        if self._excl_text is None:
            self._root.bell()
            return
        
        content = self._excl_text.get(1.0, tkinter.END).rstrip()
        self._root.clipboard_clear()
        self._root.clipboard_append(content)
    
    def _excl_paste(self):
        if self._state != DATA_STATE or self._excl_text is None:
            self._root.bell()
            return
        
        content = self._root.clipboard_get()
        self._excl_text.delete(1.0, tkinter.END)
        self._excl_text.insert(tkinter.END, content)
        
        self._notebook.select(tab_id=1)
        self._excl_text.focus()
    
    def _result_copy(self):
        if self._state != RESULT_STATE or self._result_str is None:
            self._root.bell()
            return
        
        content = self._result_str
        self._root.clipboard_clear()
        self._root.clipboard_append(content)
    
    def _destroy_widgets(self):
        if self._data_text is not None:
            self._data_text.frame.destroy()
            self._data_text = None
            
        if self._data_tab_frame is not None:
            self._data_tab_frame.destroy()
            self._data_tab_frame = None
        
        if self._excl_text is not None:
            self._excl_text.frame.destroy()
            self._excl_text = None
        
        if self._do_calc_button is not None:
            self._do_calc_button.destroy()
            self._do_calc_button = None
        
        if self._result_text is not None:
            self._result_text.frame.destroy()
            self._result_text = None
    
    def _create_data_widgets(self):
        self._data_tab_frame = ttk.Frame(master=self._data_tab)
        self._begin_date_label = ttk.Label(master=self._data_tab_frame,
                text='Дата начала периода:')
        self._begin_date_entry = ttk.Entry(master=self._data_tab_frame)
        self._end_date_label = ttk.Label(master=self._data_tab_frame,
                text='Дата окончания периода (не включая этот день):')
        self._end_date_entry = ttk.Entry(master=self._data_tab_frame)
        self._verif_count_label = ttk.Label(master=self._data_tab_frame,
                text='Количество проверок (Количество приборов):')
        self._verif_count_entry = ttk.Entry(master=self._data_tab_frame)
        self._week_days_label = ttk.Label(master=self._data_tab_frame,
                text='Дни недели проверок:')
        self._week_days_widget = WeekDaysWidget(self._data_tab_frame)
        
        self._begin_date_label.pack(padx=10, pady=10)
        self._begin_date_entry.pack(padx=10, pady=10)
        self._end_date_label.pack(padx=10, pady=10)
        self._end_date_entry.pack(padx=10, pady=10)
        self._verif_count_label.pack(padx=10, pady=10)
        self._verif_count_entry.pack(padx=10, pady=10)
        self._week_days_label.pack(padx=10, pady=10)
        self._week_days_widget.frame.pack(padx=10, pady=10)
        
        self._excl_text = scrolledtext.ScrolledText(master=self._excl_tab)
        
        self._do_calc_button = ttk.Button(master=self._result_tab,
                text='Выполнить расчёт', command=self._do_calc)
        
        if self._data is not None:
            self._set_data()
        
        self._data_tab_frame.pack()
        self._excl_text.pack(fill=tkinter.BOTH, expand=True)
        self._do_calc_button.pack(padx=10, pady=10)
    
    def _create_calc_widgets(self):
        self._data_text = scrolledtext.ScrolledText(master=self._data_tab)
        self._excl_text = scrolledtext.ScrolledText(master=self._excl_tab)
        self._result_text = scrolledtext.ScrolledText(master=self._result_tab)
        
        self._data_text.config(state=tkinter.DISABLED)
        self._excl_text.config(state=tkinter.DISABLED)
        self._result_text.config(state=tkinter.DISABLED)
        
        self._set_calc_data()
        
        self._data_text.pack(fill=tkinter.BOTH, expand=True)
        self._excl_text.pack(fill=tkinter.BOTH, expand=True)
        self._result_text.pack(fill=tkinter.BOTH, expand=True)
        
    def destroy(self):
        self._root.destroy()
    
    def _get_data(self):
        data = Data()
        
        data.begin_date = self._begin_date_entry.get()
        data.end_date = self._end_date_entry.get()
        data.verif_count = self._verif_count_entry.get()
        data.week_days = self._week_days_widget.get()
        data.excl = self._excl_text.get(1.0, tkinter.END).rstrip()
        
        self._data = data
    
    def _set_data(self):
        self._begin_date_entry.delete(0, tkinter.END)
        self._begin_date_entry.insert(0, self._data.begin_date)
        
        self._end_date_entry.delete(0, tkinter.END)
        self._end_date_entry.insert(0, self._data.end_date)
        
        self._verif_count_entry.delete(0, tkinter.END)
        self._verif_count_entry.insert(0, self._data.verif_count)
        
        self._week_days_widget.set(self._data.week_days)
        
        self._excl_text.delete(1.0, tkinter.END)
        self._excl_text.insert(tkinter.END, self._data.excl)
    
    def _set_calc_data(self):
        data_str = 'Дата начала периода: {}\n\n' \
                'Дата окончания периода (не включая этот день): {}\n\n' \
                'Количество проверок (Количество приборов): {}\n\n' \
                'Дни недели проверок: {}\n\n' \
                'Исключения: {}\n\n'.format(
                        self._data.begin_date,
                        self._data.end_date,
                        self._data.verif_count,
                        week_days_to_str(self._data.week_days),
                        '<присутствуют>' if self._data.excl.strip() else '<отсутствуют>',
                        )
        
        self._data_text.config(state=tkinter.NORMAL)
        self._data_text.delete(1.0, tkinter.END)
        self._data_text.insert(tkinter.END, data_str)
        self._data_text.config(state=tkinter.DISABLED)
        
        self._excl_text.config(state=tkinter.NORMAL)
        self._excl_text.delete(1.0, tkinter.END)
        self._excl_text.insert(tkinter.END, self._data.excl)
        self._excl_text.config(state=tkinter.DISABLED)
        
        self._result_text.config(state=tkinter.NORMAL)
        self._result_text.delete(1.0, tkinter.END)
        self._result_text.insert(tkinter.END, 'Результат ещё не готов... Пожалуйста подождите!')
        self._result_text.config(state=tkinter.DISABLED)
    
    def _get_calc_params(self):
        calc_params = CalcParams()
        
        if not self._data.begin_date:
            raise UserError('необходимо ввести дату начала периода')
        if not self._data.end_date:
            raise UserError('необходимо ввести дату конца периода')
        if not self._data.verif_count:
            raise UserError('необходимо ввести количество проверок')
        if not self._data.week_days:
            raise UserError('необходимо указать хотя бы какой-нибудь день недели')
        
        calc_params.begin_date = date_parser.parse_date(self._data.begin_date)
        calc_params.end_date = date_parser.parse_date(self._data.end_date)
        calc_params.verif_count = int(self._data.verif_count)
        calc_params.week_days = self._data.week_days
        calc_params.excl_list = tuple(get_date_list(self._data.excl))
        
        if calc_params.verif_count <= 0:
            raise UserError('количество проверок должно быть больше нуля')
        
        return calc_params
    
    def result_handle(self, calc_id, result, error):
        if self._state != CALC_STATE or self._calc_id != calc_id:
            return
        
        if error is None:
            self._result_str = result
            
            self._result_text.config(state=tkinter.NORMAL)
            self._result_text.delete(1.0, tkinter.END)
            self._result_text.insert(tkinter.END, self._result_str)
            self._result_text.config(state=tkinter.DISABLED)
            self._status_var.set('Расчёт успешно выполнен')
        else:
            self._result_str = None
            
            self._result_text.config(state=tkinter.NORMAL)
            self._result_text.delete(1.0, tkinter.END)
            self._result_text.insert(tkinter.END, 'Ошибка во время расчёта')
            self._result_text.config(state=tkinter.DISABLED)
            self._status_var.set(
                    'Ошибка: {}: {}'.format(error[0], error[1]))
        
        self._state = RESULT_STATE
    
    def _do_calc(self):
        if self._state is not DATA_STATE:
            self._root.bell()
            return
        
        self._get_data()
        try:
            calc_params = self._get_calc_params()
        except Exception as e:
            if type(e) == UserError:
                t = ''
            else:
                t = '{}: '.format(type(e))
            self._status_var.set(
                    'Ошибка: {}{}'.format(t, e))
            self._root.bell()
            return
        
        self._destroy_widgets()
        self._create_calc_widgets()
        
        self._status_var.set('Происходит расчёт...')
        self._calc_id = object()
        self._state = CALC_STATE
        self._notebook.select(tab_id=2)
        self._result_text.focus()
        
        def thread_target(calc_id):
            sch_dates = verif_scheduler.verif_schedule(
                    verif_scheduler.get_dates(
                            calc_params.begin_date,
                            calc_params.end_date,
                            calc_params.week_days,
                            excl_list=calc_params.excl_list,
                            ),
                    calc_params.verif_count,
                    )
            
            result = '\n'.join(sch_date.strftime('%d.%m.%Y') for sch_date in sch_dates)
            
            return result
        
        self._tk_mt.start_daemon(
                lambda _calc_id=self._calc_id: thread_target(_calc_id),
                callback=lambda result, error, _calc_id=self._calc_id:
                        self.result_handle(_calc_id, result, error),
                )
    
    def _recalc(self):
        if self._state is DATA_STATE:
            self._get_data()
        
        if self._state is not None:
            self._destroy_widgets()
        
        self._create_data_widgets()
        
        self._status_var.set('')
        self._state = DATA_STATE
        self._notebook.select(tab_id=0)
        self._begin_date_entry.focus()
    
    def _clear(self):
        if self._state is not None:
            self._destroy_widgets()
        
        self._data = None
        self._create_data_widgets()
        
        self._status_var.set('')
        self._state = DATA_STATE
        self._notebook.select(tab_id=0)
        self._begin_date_entry.focus()
    
    def _show_about(self):
        about_window.AboutWindow()
