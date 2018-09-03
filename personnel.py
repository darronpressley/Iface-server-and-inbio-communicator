import wx
import sqlconns
import decimal
import sys
import os
import gl


class PersonnelScreen(wx.Frame):

    def __init__(self,parent,id):
        wx.Frame.__init__(self, None, id, 'Personnel', size=(640, 480), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        wx.Frame.CenterOnScreen(self)


        icon1 = wx.Icon(gl.small_icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)

        self.Bind(wx.EVT_CLOSE, self.personnel_closewindow)


    def personnel_closewindow(self, event):
        gl.personnel_screen_open = 0
        print("close window_personnel")
        self.Destroy()


    def personnel_maximize(self):
        if self.IsIconized() == True:
            self.Iconize(False)
        self.Raise()





