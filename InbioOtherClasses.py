import wx
import gl
import sqlconns
class advanced_options_screen(wx.Frame):

    def __init__(self,parent,id):
        populate_inbio_options()
        wx.Frame.__init__(self, None, id, 'Inbio Options', size=(400, 400), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        wx.Frame.CenterOnScreen(self)
        icon1 = wx.Icon(gl.small_icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)
        self.Bind(wx.EVT_CLOSE, self.advanced_options_screen_closewindow)
        panel = wx.Panel(self)

        title = wx.StaticText(panel, wx.ID_ANY, 'Inbio Options')

        logcommLabel = wx.StaticText(panel, -1, "Log Comm Errors:",wx.Point(100,100))
        self.logcommText = wx.CheckBox(panel, -1, "", (35, 40), (150, 20))
        if gl.LOG_COMMS_FAILURES=="1":
            self.logcommText.SetValue(True)
        else:
            self.logcommText.SetValue(False)

        spool_transactions_Label = wx.StaticText(panel, -1, "Spool Transactions:",wx.Point(100,100))
        self.spool_transactions_Text = wx.CheckBox(panel, -1, "", (35, 40), (150, 20))
        if gl.SPOOL_TRANSACTIONS=="1":
            self.spool_transactions_Text.SetValue(True)
        else:
            self.spool_transactions_Text.SetValue(False)

        commdelayLabel = wx.StaticText(panel, -1, "Comm Delay(ms):")
        self.commdelayText = wx.TextCtrl(panel, -1,str(gl.COMM_TIMEOUT),size=(60,-1))

        okBtn = wx.Button(panel, wx.ID_ANY, '&OK')
        okBtn.SetDefault()
        cancelBtn = wx.Button(panel, wx.ID_ANY, '&Cancel')
        self.Bind(wx.EVT_BUTTON, self.onOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.GridSizer(rows=3, cols=2, hgap=5, vgap=5)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(title, 0, wx.ALL, 5)
        inputOneSizer.Add((20,-1), proportion=1)  # this is a spacer
        inputOneSizer.Add(logcommLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        inputTwoSizer.Add((20,20), 1, wx.EXPAND) # this is a spacer
        inputTwoSizer.Add(spool_transactions_Label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        inputThreeSizer.Add((20,20), 1, wx.EXPAND) # this is a spacer
        inputThreeSizer.Add(commdelayLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        # Add the 3-item sizer to the gridsizer and
        # Right align the labels and icons
        gridSizer.Add(inputOneSizer, 0, wx.ALIGN_RIGHT)
        # Set the TextCtrl to expand on resize
        gridSizer.Add(self.logcommText, 0, wx.EXPAND)
        gridSizer.Add(inputTwoSizer, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(self.spool_transactions_Text, 0, wx.EXPAND)
        gridSizer.Add(inputThreeSizer, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(self.commdelayText, 0, wx.ALIGN_LEFT)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(gridSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        # SetSizeHints(minW, minH, maxW, maxH)
        panel.SetSizeHints(250,300,500,400)

        panel.SetSizer(topSizer)
        topSizer.Fit(self)


    def onOK(self, event):
        gl.advanced_options_open = 0
        data = self.commdelayText.GetValue()
        try:
            if (int(data) < 2000) | (int(data) > 20000):
                wx.MessageBox('Comm Delay value must be between 2000 to 20000.','User Alert')
                return
        except:
            wx.MessageBox('Comm Delay value must be numeric.','User Alert')
            return

        if data != gl.COMM_TIMEOUT:
            sqltext = """UPDATE d_inbio_misc SET value = """ + str(data) + """ WHERE property like 'COMM_TIMEOUT'
                    IF @@ROWCOUNT=0
                    INSERT INTO d_inbio_misc(property,value) VALUES ('COMM_TIMEOUT',""" + str(data) + """)"""
            ret = sqlconns.sql_command(sqltext)
        if self.logcommText.GetValue():
            data = 1
        else:
            data = 0
        if data != gl.LOG_COMMS_FAILURES:
            sqltext = """UPDATE d_inbio_misc SET value = """ + str(data) + """ WHERE property like 'LOG_COMMS_FAILURES'
                    IF @@ROWCOUNT=0
                    INSERT INTO d_inbio_misc(property,value) VALUES ('LOG_COMMS_FAILURES',""" + str(data) + """)"""
            ret = sqlconns.sql_command(sqltext)
        data = 0
        if self.spool_transactions_Text.GetValue():
            data = 1
        else:
            data = 0
        if data != gl.SPOOL_TRANSACTIONS:
            sqltext = """UPDATE d_inbio_misc SET value = """ + str(data) + """ WHERE property like 'SPOOL_TRANSACTIONS'
                    IF @@ROWCOUNT=0
                    INSERT INTO d_inbio_misc(property,value) VALUES ('SPOOL_TRANSACTIONS',""" + str(data) + """)"""
            ret = sqlconns.sql_command(sqltext)
        self.Destroy()

    def onCancel(self, event):
        gl.advanced_options_open = 0
        self.Destroy()

    def advanced_options_screen_closewindow(self, event):
        gl.advanced_options_open = 0
        self.Destroy()

    def advanced_options_screen_maximize(self):
        if self.IsIconized() == True:
            self.Iconize(False)
        self.Raise()

def populate_inbio_options():
    data = sqlconns.sql_select_single_field("Select value FROM d_inbio_misc WHERE property like 'COMM_TIMEOUT'")
    if data != -1:
        gl.COMM_TIMEOUT = data
    data = sqlconns.sql_select_single_field("Select value FROM d_inbio_misc WHERE property like 'SPOOL_TRANSACTIONS'")
    if data != -1:
        gl.SPOOL_TRANSACTIONS = data
    data = sqlconns.sql_select_single_field("Select value FROM d_inbio_misc WHERE property like 'LOG_COMMS_FAILURES'")
    if data != -1:
        gl.LOG_COMMS_FAILURES = data
    return

