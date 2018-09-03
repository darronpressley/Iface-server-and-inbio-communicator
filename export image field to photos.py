import

def set_env():
        global VERSION
        global APPSERVER
        global APPNAME
        sql_tables = 0
        wx.Frame.__init__(self, None, -1, APPNAME + " - " + VERSION, size=(820, 480), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        wx.Frame.CenterOnScreen(self)

        if os.path.isfile('database.ini'):
            if sqlconns.readsql_connection_timeware_main_6() == 0:
                sql_messagebox = wx.MessageDialog(None, "Error reading 'database.ini'' file.", "User Alert!!!", wx.OK)
                sql_messagebox1 = sql_messagebox.ShowModal()
                sql_messagebox.Destroy()
                self.Destroy()
                return
            elif sqlconns.readsql_connection_timeware_main_6() == 1:
                test_comms = sqlconns.testsql(gl.SERVER, gl.SQL_LOGIN, gl.PASSWORD, gl.DATABASE)
                if test_comms == 0:
                    sql_messagebox = wx.MessageDialog(None, "Error connecting to SQL server..", "User Alert!!!", wx.OK)
                    sql_messagebox1 = sql_messagebox.ShowModal()
                    sql_messagebox.Destroy()
                    self.Destroy()
                    return
                else:
                    APPSERVER = gl.SERVER
                    self.SetTitle(APPNAME + " - " + VERSION + " - " +APPSERVER)
        else:
            grr = wx.MessageDialog(None, "No 'database.ini' file found.", "User Alert!!!", wx.OK)
            grr1 = grr.ShowModal()
            grr.Destroy()
            self.Destroy()
            return

