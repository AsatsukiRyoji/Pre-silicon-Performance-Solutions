#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Methodology GUI
@author: Li Lizhao
"""
import sys, pdb, argparse
if (sys.version_info < (3, 0)):
    print("[ERROR] This script can only work with 'python3'")
    ##Python 2.x
    import Tkinter as tk
    import ttk
else:
    ##Python 3.x
    import tkinter as tk
    from tkinter import ttk
from tkinter import Scrollbar
from tkinter import *
import tkinter.messagebox
import pandas as pd
from pandas import DataFrame as DF
import numpy as np

def gui_option_parser(type=None):
    
    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--fil', default= None, dest= 'fil', help = "file to read, .csv now")
    parser.add_argument('-c', '--clm', default= '', dest= 'clm', help = "columns to show in first frame. format is '<str>,<str>,...' ")
    options = parser.parse_args()

    return options

class PMGui:
    def __init__(self):
        self.top=tk.Tk()
        self.top.geometry('650x390')
        self.stl=ttk.Style()
        self.schm={'bwidth':2, 'bg_clr_l':'aliceblue','bg_clr_s':'ivory'}
        self.stl.configure('MY.TFrame',background=self.schm['bg_clr_l'],borderwidth=self.schm['bwidth'], relief='raised')
        self.stl.configure('MY.Treeview',background=self.schm['bg_clr_l'],fieldbackground=self.schm['bg_clr_l'], padding = (2, 2, 16, 16) )
        self.stl.configure('MY.TPanedwindow',background=self.schm['bg_clr_l'])
        self.stl.configure('MY.TLabel',background=self.schm['bg_clr_s'],borderwidth=self.schm['bwidth'])
        self.stl.configure("MY.TButton",background=self.schm['bg_clr_s'], relief='raised',borderwidth=self.schm['bwidth'])
        self.stl.configure('MY.TEntry',fieldbackground=self.schm['bg_clr_s'],borderwidth=self.schm['bwidth'])
        self.stl.configure('MY.Horizontal.TScrollbar',background=self.schm['bg_clr_s'],relief='raised')
        self.stl.configure('MY.Vertical.TScrollbar',background=self.schm['bg_clr_s'], relief='raised')
        self.frame_pos='top'
    
    def __frame(self,master):
        '''Frame
        '''
        frm=ttk.Frame(master, style='MY.TFrame')
        frm.pack(expand=True,fill='both',side=self.frame_pos)#,anchor='n')
        return frm

    def __pane(self,master,orient):
        '''PanedWindow
        '''
        pan=ttk.PanedWindow(master,orient=orient,style='MY.TPanedwindow')
        if master is self.top:  #Must be the exactly same object 
            pan.pack(expand=True,fill='both')#, padx=4,pady=4)
        return pan

    def __treeview(self,master, columns):
        return ttk.Treeview(master,style='MY.Treeview', columns=columns, show='headings')

    def __entry(self,master,scalable=False,**kw):
        ent=ttk.Entry(master,style='MY.TEntry',width=8)
        if scalable == False:
            kw['expand'],kw['fill']=False,'none'
            ent.pack(kw)#,padx=self.bw)
        return ent

    def __button(self,master,text,command=None,**kw):
        kw['expand'],kw['fill']=False,'none'
        btn=ttk.Button(master,text=text,style="MY.TButton",command=command)
        btn.pack(kw)
        return btn
    
    def __scrollbar(self,master, tvw, **kw):
        y_scrollbar = ttk.Scrollbar(master, orient = 'vertical', command = tvw.yview)
        x_scrollbar = ttk.Scrollbar(master, orient = 'horizontal', command = tvw.xview)
        y_scrollbar.pack(side = 'right', fill = 'y',)
        x_scrollbar.pack(side = 'bottom', fill = 'x')
        tvw.config(yscrollcommand = y_scrollbar.set, xscrollcommand = x_scrollbar.set)
        return y_scrollbar, x_scrollbar

   # def double_click(self, event):
   #     print('Double clicked at x = %s, y = %s'%(event.x, event.y))
   #     return x, y
   #     
    def search_df(self,df,name):
        try:    #[FIXME]Use eval() to check if the name is string or int is simple but dangerous
            name=eval(name)
        except:
            pass
        name=[name] #df.eq needs list type on this pandas version
        try:
            ##[XXX]A tricky but simple way to fetch the row and column of specific item
            ##where() turns False to NA, and stack removes them and turn 
            ##things to a multi-index Series
            #pdb.set_trace()
            _=df.where(df.eq(name)).stack()
            fnd = [i[0] for i in _.index.tolist()]
            #tk.messagebox.showinfo('Result',df.loc[r,:].to_dict())
            _gui = PMGui()
            _gui.run([df.loc[fnd,:]])
        except:
            tk.messagebox.showerror('Error', ("%s doesn't exist" %name))

    def show(self, fil, clm=''):
        df = pd.read_csv(fil)
        df = df.drop(['Unnamed: 0'], axis=1)
        col = clm.split(',') if clm != '' else []
        self.run([df], col)

    def run(self, df_l, cols=[]):
        '''
        :cols: 2D list as [[DF.columns(<columns of DF N>], ]
        '''
        #TODO: Use tests to filter
        pan=self.__pane(self.top,'vertical')
        dn_pan = self.__pane(pan, 'vertical')

        for i, df in enumerate(df_l):
            ds = []
            nm = df.iloc[:,0] if i==0 else nm
            remain_cols = list(df.columns)
            if cols==[]:
                cols.append(remain_cols)
            for cs in cols:
                _df = df.loc[:,cs]
                if i != 0:
                    _df.insert(0, nm.name, nm) #Or pd.concat([nm,_df], axis=1)
                ds.append(_df)
                remain_cols = [i for i in remain_cols if i not in list(cs)]
            if len(remain_cols):
                _df = df.loc[:,remain_cols]
                _df.insert(0, nm.name, nm)
                ds.append(_df)
            
            for d in ds:
                cols=d.columns.tolist()
                idxs=d.index.tolist()
                _tvw=self.__treeview(dn_pan,cols)
                self.__scrollbar(_tvw, _tvw)

                for c in cols:
                    _tvw.column(c, anchor="w", minwidth=0, width=80)
                    _tvw.heading(c, text=c, anchor="center")
                for i in idxs:
                    _tvw.insert('','end',values=d.loc[i,:].tolist())
                dn_pan.add(_tvw)

        frm=self.__frame(self.top)
        ent=self.__entry(frm,side='right')
        ##[XXX]Must use lambda at here(cannot be wrapped in function)
        ##to make it's invoked on clicking button
        btn=self.__button(frm,text="search", 
                          command=lambda:self.search_df(df_l[0],ent.get()),
                          side='right',before=ent)

        #btn.bind('<Double-Button-1>', double_click)
        pan.add(frm)
        pan.add(dn_pan)

        self.top.mainloop()

if __name__ == "__main__":
    opt = gui_option_parser()
    pmgui=PMGui()
    pmgui.show(opt.fil, opt.clm)

    #da = DF(np.arange(12).reshape((3, 4)),
    #        index=['a', 'b', 'c'],
    #        columns=['x','y','z','w'])
    #da.insert(0,'name',value=da.index.tolist())
    #pmgui.run([da])

