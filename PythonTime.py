import wx
import sqlconns
import decimal
import sys
import os
import gl
import personnel as ps

VERSION = "0.0.1"
APPSERVER = " - not connected yet"
APPNAME = "Python Time"

class MainScreen(wx.Frame):

    def __init__(self, parent, id):
        global VERSION
        global APPSERVER
        global APPNAME
        wx.Frame.__init__(self, parent, id, APPNAME + " - " + VERSION, size=(800, 600), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        wx.Frame.CenterOnScreen(self)

        if os.path.isfile('database.ini'):
            if sqlconns.readsql_connection() == 0:
                sql_messagebox = wx.MessageDialog(None, "Error reading 'database.ini'' file.", "User Alert!!!", wx.OK)
                sql_messagebox1 = sql_messagebox.ShowModal()
                sql_messagebox.Destroy()
                self.Destroy()
            elif sqlconns.readsql_connection() == 1:
                test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
                if test_comms == 0:
                    sql_messagebox = wx.MessageDialog(None, "Error connecting to SQL server..", "User Alert!!!", wx.OK)
                    sql_messagebox1 = sql_messagebox.ShowModal()
                    sql_messagebox.Destroy()
                    self.Destroy()
                else:
                    APPSERVER = gl.SERVER
                    self.SetTitle(APPNAME + " - " + VERSION + " - " +APPSERVER)
        else:
            test = wx.MessageDialog(None, "No 'database.ini' file found.", "User Alert!!!", wx.OK)
            test1 = test.ShowModal()
            test.Destroy()
            self.Destroy()


        panel = wx.Panel(self)

        icon1 = wx.Icon(gl.small_icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)

        status=self.CreateStatusBar()
        menubar = wx.MenuBar()
        personnel_menu = wx.Menu()
        attendance_menu = wx.Menu()
        id_personnel_personnel = personnel_menu.Append(wx.NewId(), "Personnel")
        id_personnel_exit = personnel_menu.Append(wx.NewId(), "Exit")
        id_attendance_clock_card = attendance_menu.Append(wx.NewId(), "Clock-card")
        id_attendance_absence_chart = attendance_menu.Append(wx.NewId(), "Absence Chart")


        menubar.Append(personnel_menu, "Personnel")
        menubar.Append(attendance_menu, "Adjustments")
        self.Bind(wx.EVT_MENU, self.personnel_screen, id_personnel_personnel)
        self.Bind(wx.EVT_MENU, self.closebutton, id_personnel_exit)
        self.Bind(wx.EVT_CLOSE, self.closewindow)
        self.SetMenuBar(menubar)


    def closebutton(self, event):
        print("close button")
        if gl.personnel_screen_open == 1:
            self.personnel.personnel_closewindow(event)

        self.Close(True)

    def closewindow(self, event):
        print("close window")
        if gl.personnel_screen_open == 1:
            self.personnel.personnel_closewindow(event)

        self.Destroy()


    def personnel_screen(self, event):
        if gl.personnel_screen_open == 0:
            gl.personnel_screen_open = 1
            self.personnel = ps.PersonnelScreen(parent=None, id=-1)
            self.personnel.Show()
        else:
            #we want to switch to the personnel screen now
            self.personnel.personnel_maximize()
            print("else")


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainScreen(parent=None, id=-1)
    frame.Show()
    app.MainLoop()