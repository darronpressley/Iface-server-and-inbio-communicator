import sys
import wx
import functions as f
import wx.grid as gridlib
import sqlconns
import os
import gl
from ctypes import *
import datetime
import threading
import InbioOtherClasses as iob

VERSION = "0.0.1"
APPSERVER = " - not connected yet"
APPNAME = "InBio Updater"

ID_SIMPLE = wx.NewId()
ID_WARNING_LABEL = wx.NewId()
ID_WARNING_LABEL1 = wx.NewId()

INBIO_GRID_ROWS = 0

#multithreating returns to make life easy
INBIO_REBOOT_OK = 0
INBIO_BLANK_OK = 0

#for later IF OBJECT_ID (N'd_inbio_events', N'U') IS NOT NULL
#SELECT 1 AS res ELSE SELECT 0 AS res;

class MainScreen(wx.Frame):

    def __init__(self):
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

        top_panel = wx.Panel(self)
        self.bottom_panel = wx.Panel(self, -1)


        button_refresh = wx.Button(top_panel,-1,label = 'Refresh',pos=(40,40))
        button_refresh.Bind(wx.EVT_BUTTON,self.onbutton_refresh)
        self.button_start_service = wx.Button(top_panel,-1,label = 'Start Service',pos=(100,40))
        self.button_start_service.Bind(wx.EVT_BUTTON,self.onbutton_start_service)
        self.button_stop_service = wx.Button(top_panel,-1,label = 'Pause Service',pos=(140,40))
        self.button_stop_service.Bind(wx.EVT_BUTTON,self.onbutton_stop_service)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.AddSpacer(10)
        top_sizer.Add(button_refresh, flag=wx.EXPAND)
        top_sizer.Add(self.button_start_service, flag=wx.EXPAND)
        top_sizer.Add(self.button_stop_service, flag=wx.EXPAND)

        top_panel.SetSizer(top_sizer)

        self.inbio_controller_grid=gridlib.Grid(self.bottom_panel,-1,size=(800,300))

        bottom_sizer = wx.BoxSizer(wx.VERTICAL)

        bottom_sizer.Add(self.inbio_controller_grid,1,flag=wx.EXPAND)#,pos=(200,200)

        upDownSizer = wx.BoxSizer(wx.VERTICAL)
        upDownSizer.AddSpacer(3)
        upDownSizer.Add(top_panel, 0, flag=wx.EXPAND)
        upDownSizer.AddSpacer(3)
        upDownSizer.Add(self.bottom_panel, 1, flag=wx.EXPAND)

        sql_tables = test_inbio_sql_tables()

        if sql_tables==0:
            warning_panel = wx.Panel(self)
            self.warning_label = wx.StaticText(warning_panel,ID_WARNING_LABEL,label="Warning Information:")
            self.warning_label1 = wx.StaticText(warning_panel,ID_WARNING_LABEL1,label="d_inbio tables may need to be created, use Advanced menu option.")
#all these probably need to be self. if you want to get at them from abnother func
            warning_sizer = wx.BoxSizer(wx.VERTICAL)
            warning_sizer.Add(self.warning_label,0)
            warning_sizer.AddSpacer(2)
            warning_sizer.Add(self.warning_label1,0)
            warning_panel.SetSizer(warning_sizer)
            upDownSizer.AddSpacer(3)
            upDownSizer.Add(warning_panel, 2, flag=wx.EXPAND)

        self.SetSizer(upDownSizer)

        if sql_tables == 0:
            self.button_start_service.Enable(False)
            self.button_stop_service.Enable(False)
        else:
            if self.test_service_started() == True:
                self.button_start_service.Enable(False)
            else:
                self.button_stop_service.Enable(False)

        self.inbio_controller_grid.CreateGrid(0, 8)
        #self.inbio_controller_grid = inbio_controller_grid
        self.inbio_controller_grid.SetRowLabelSize(0)
        self.inbio_controller_grid.EnableEditing(False)
        self.inbio_controller_grid.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.showPopupMenu)
        self.inbio_controller_grid.SetColLabelAlignment(wx.HORIZONTAL,wx.ALIGN_LEFT)
        self.populate_terminal_grid(self.inbio_controller_grid)
        #self.inbio_controller_grid.AutoSize()
        self.inbio_controller_grid.ForceRefresh()

        icon1 = wx.Icon(gl.small_icon_path, wx.BITMAP_TYPE_ICO)

        self.SetIcon(icon1)
#statusbar
        status=self.CreateStatusBar()
#menus
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        advanced_menu = wx.Menu()
        id_file_exit = file_menu.Append(wx.NewId(), "Exit")
        menubar.Append(file_menu, "&File")
        advanced_menu.Append(ID_SIMPLE, "Create Tables")
        menubar.Append(advanced_menu,"&Advanced")
        id_advanced_options = advanced_menu.Append(wx.NewId(),"Options")

#file menu bind
        self.Bind(wx.EVT_MENU, self.closebutton, id_file_exit)
#advanced menu bind
        self.Bind(wx.EVT_MENU, self.create_inbio_sql_tables,id=ID_SIMPLE)
        self.Bind(wx.EVT_MENU, self.advanced_options_screen,id_advanced_options)

#X button to close I think
        self.Bind(wx.EVT_CLOSE, self.closewindow)
#setup bar
        self.SetMenuBar(menubar)
#enable or disable sql creation menus after everything else
        if sql_tables == 0:
            menubar.Enable(ID_SIMPLE, True)
        else:
            menubar.Enable(ID_SIMPLE,False)


    def advanced_options_screen(self, event):
        if gl.advanced_options_open == 0:
            gl.advanced_options_open = 1
            self.adv_options = iob.advanced_options_screen(parent=None, id=-1)
            self.adv_options.Show()
        else:
            self.adv_options.advanced_options_screen_maximize()



    def test_service_started(self):
        list = sqlconns.sql_select_into_list("SELECT TOP 1 value FROM d_inbio_misc WHERE property like 'paused'")
        if list == -1: return False
        if len((list)) == 0 : return True
        if list[0][0] == "0": return True
        return False


    def onbutton_start_service(self,event):
        sqlconns.sql_command("UPDATE d_inbio_misc SET value = 0 WHERE property like 'paused'")
        progressMax = 7
        dialog = wx.ProgressDialog("Progress Information", ("Starting Inbio Comunications Service."), progressMax)
        keepGoing = True
        count = 0
        while keepGoing and count < progressMax:
            count = count + 1
            wx.Sleep(1)
            keepGoing = dialog.Update(count)
        dialog.Destroy()
        self.button_start_service.Enable(False)
        self.button_stop_service.Enable(True)


    def onbutton_stop_service(self,event):
        sqltext = """UPDATE d_inbio_misc SET value = 1 WHERE property like 'paused'
                    IF @@ROWCOUNT=0
                    INSERT INTO d_inbio_misc(property,value) VALUES ('paused',1)"""
        ret = sqlconns.sql_command(sqltext)
        progressMax = 30
        dialog = wx.ProgressDialog("Progress Information", ("Pausing Inbio Comunications Service."), progressMax)
        keepGoing = True
        count = 0
        while keepGoing and count < progressMax:
            count = count + 1
            wx.Sleep(1)
            keepGoing = dialog.Update(count)
        dialog.Destroy()
        self.button_start_service.Enable(True)
        self.button_stop_service.Enable(False)


    def showPopupMenu(self,event):
        x, y = self.inbio_controller_grid.CalcUnscrolledPosition(event.GetX(), event.GetY())
        row, col = self.inbio_controller_grid.XYToCell(x, y)
        if row < 0:return
        terminal_code = self.inbio_controller_grid.GetCellValue(row,1)
        self.terminal_number = self.inbio_controller_grid.GetCellValue(row,2)
        self.terminal_ip = self.inbio_controller_grid.GetCellValue(row,3)
        if int(terminal_code) % 100 == 1:
            if "no connection" in self.inbio_controller_grid.GetCellValue(row,7).lower():
                return
        else:
            return

        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()

        menu = wx.Menu()

        item = wx.MenuItem(menu, self.popupID1,"Send All Settings")
        menu.Append(item)
        menu.Append(self.popupID2, "Blank Terminal")
        menu.Append(self.popupID3, "Reboot Terminal")

        self.reboot_command = "Reboot=1"

        self.Bind(wx.EVT_MENU, self.update_inbio,id=self.popupID1)

        self.Bind(wx.EVT_MENU, self.blank_inbio,id=self.popupID2)

        self.Bind(wx.EVT_MENU, self.reboot_inbio,id=self.popupID3)


        self.PopupMenu(menu)
        menu.Destroy()


    def update_inbio(self,event):
        ret = wx.MessageDialog(None,'Do you wish to update all terminal tables in Inbio ' + self.terminal_ip + '?', 'User Option', wx.YES_NO)
        ret1 = ret.ShowModal()
        if ret1 == wx.ID_NO:
            ret.Destroy()
            return -1
    #keep track of how many items to send for the progress bar later
        progressMax = 0
        sql_text = "Select * From taccess_pattern"
        access_patterns = sqlconns.sql_select_into_list(sql_text)
        access_list = build_access_string(access_patterns)
        personnel_list, personnel_auth_list,finger_template_list = build_personnel_list(self.terminal_ip)
        progressMax +=len(personnel_list) + len(access_list) + len(personnel_auth_list) +len(finger_template_list)
        if len(personnel_list) == 0:
            wx.MessageBox('No data to send, please check personnel.','User Alert')
            return
        progressMax+=1
        constr = create_string_buffer(str.encode('protocol=TCP,ipaddress='+ self.terminal_ip + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) +',passwd='))
        commpro = windll.LoadLibrary("plcommpro.dll")
        hcommpro = commpro.Connect(constr)
        if hcommpro == 0:
            wx.MessageBox('No communications, please check connections.','User Alert')
            return
    #relay times
        term_list = get_doors_from_ip(self.terminal_ip)
        for index in range(len(term_list)):
            tx = 'select top 1 relay_trip_seconds from tterminal where terminal_id = ' +  str(term_list[index][0])
            relay_time= sqlconns.sql_select_single_field(tx)
            if relay_time == - 1:
                wx.MessageBox('Error during communications (relay list)...' + '(' + str(relay_time) + ')','User Alert')
                commpro.Disconnect(hcommpro)
                return
            if term_list[index][1]%100 == 1:
                door_relay = 'Door1Drivertime=' + str(relay_time)
                p_items = create_string_buffer(str.encode(door_relay))
                ret = commpro.SetDeviceParam(hcommpro, p_items)
                if ret < 0:
                    wx.MessageBox('Error during communications (door relay)...' + '(' + str(ret) + ')','User Alert')
                    commpro.Disconnect(hcommpro)
                    return
            if term_list[index][1]%100 == 2:
                door_relay = 'Door2Drivertime=' + str(relay_time)
                p_items = create_string_buffer(str.encode(door_relay))
                ret = commpro.SetDeviceParam(hcommpro, p_items)
                if ret < 0:
                    wx.MessageBox('Error during communications (door relay)...' + '(' + str(ret) + ')','User Alert')
                    commpro.Disconnect(hcommpro)
                    return
            if term_list[index][1]%100 == 3:
                door_relay = 'Door3Drivertime=' + str(relay_time)
                p_items = create_string_buffer(str.encode(door_relay))
                ret = commpro.SetDeviceParam(hcommpro, p_items)
                if ret < 0:
                    wx.MessageBox('Error during communications (door relay)...' + '(' + str(ret) + ')','User Alert')
                    commpro.Disconnect(hcommpro)
                    return
            if term_list[index][1]%100 == 4:
                door_relay = 'Door4Drivertime=' + str(relay_time)
                p_items = create_string_buffer(str.encode(door_relay))
                ret = commpro.SetDeviceParam(hcommpro, p_items)
                if ret < 0:
                    wx.MessageBox('Error during communications (door relay)...' + '(' + str(ret) + ')','User Alert')
                    commpro.Disconnect(hcommpro)
                    return
        p_data = create_string_buffer(str.encode(""))
        p_table = create_string_buffer(str.encode("userauthorize"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        p_table = create_string_buffer(str.encode("user"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        p_table = create_string_buffer(str.encode("timezone"))
        dialog = wx.ProgressDialog("Progress Information", ("Sending Settings to Inbio  = " + self.terminal_ip+"."), progressMax)
        counter = 0
        for index in range(len(access_list)):
            ret = commpro.SetDeviceData(hcommpro,p_table,create_string_buffer(str.encode(access_list[index])),"")
            if ret < 0:
                wx.MessageBox('Error during communications...' + '(' + str(ret) + ')','User Alert')
                commpro.Disconnect(hcommpro)
                return
            counter +=1
            dialog.Update(counter)
        p_table = create_string_buffer(str.encode("user"))
        for index in range(len(personnel_list)):
            ret = commpro.SetDeviceData(hcommpro,p_table,create_string_buffer(str.encode(personnel_list[index])),"")
            if ret < 0:
                dialog.Destroy()
                wx.MessageBox('Error during communications...' + '(' + str(ret) + ')','User Alert')
                commpro.Disconnect(hcommpro)
                return
            counter +=1
            dialog.Update(counter)
        p_table = create_string_buffer(str.encode("userauthorize"))
        for index in range(len(personnel_auth_list)):
            ret = commpro.SetDeviceData(hcommpro,p_table,create_string_buffer(str.encode(personnel_auth_list[index])),"")
            if ret < 0:
                dialog.Destroy()
                wx.MessageBox('Error during communications...' + '(' + str(ret) + ')','User Alert')
                commpro.Disconnect(hcommpro)
                return
            counter +=1
            dialog.Update(counter)
        #finger part
        p_table = create_string_buffer(str.encode("templatev10"))
        for index in range(len(finger_template_list)):
            ret = commpro.SetDeviceData(hcommpro,p_table,create_string_buffer(str.encode(finger_template_list[index])),"")
            if ret < 0:
                dialog.Destroy()
                wx.MessageBox('Error during communications...' + '(' + str(ret) + ')','User Alert')
                commpro.Disconnect(hcommpro)
                return
            counter +=1
            dialog.Update(counter)
        #time, do other params here if you need, make sure set as two way up above if need be
        ret = commpro.SetDeviceParam(hcommpro,create_string_buffer(str.encode("DateTime="+str(convert_now_to_int()))))
        if ret < 0:
            dialog.Destroy()
            wx.MessageBox('Error during communications...' + '(' + str(ret) + ')','User Alert')
            commpro.Disconnect(hcommpro)
            return
        counter +=1
        dialog.Update(counter)
        wx.MessageBox('Send all Settings to Inbio ' + self.terminal_ip + ' was successful.','User Alert')
        return


    def blank_inbio(self,event):
        ret = wx.MessageDialog(None,'Do you wish to delete all terminal tables (including transaction) in Inbio ' + self.terminal_ip + '?', 'User Option', wx.YES_NO)
        ret1 = ret.ShowModal()
        if ret1 == wx.ID_NO:
            ret.Destroy()
            return -1
        constr = create_string_buffer(str.encode('protocol=TCP,ipaddress='+ self.terminal_ip + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) +',passwd='))
        commpro = windll.LoadLibrary("plcommpro.dll")
        hcommpro = commpro.Connect(constr)
        if hcommpro == 0:
            wx.MessageBox('No communications, please check connections.','User Alert')
            return
        p_table = create_string_buffer(str.encode("user"))
        p_data = create_string_buffer(str.encode(""))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        if ret != 0:
            wx.MessageBox('There was an error during Blank Terminal.','User Alert')
            commpro.Disconnect(hcommpro)
            return
        p_table = create_string_buffer(str.encode("holiday"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        if ret != 0:
            wx.MessageBox('There was an error during Blank Terminal.','User Alert')
            commpro.Disconnect(hcommpro)
            return
        p_table = create_string_buffer(str.encode("timezone"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        if ret != 0:
            wx.MessageBox('There was an error during Blank Terminal.','User Alert')
            commpro.Disconnect(hcommpro)
            return
        p_table = create_string_buffer(str.encode("transaction"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        if ret != 0:
            wx.MessageBox('There was an error during Blank Terminal.','User Alert')
            commpro.Disconnect(hcommpro)
            return
        p_table = create_string_buffer(str.encode("templatev10"))
        ret = commpro.DeleteDeviceData(hcommpro,p_table,p_data,"")
        if ret != 0:
            wx.MessageBox('There was an error during Blank Terminal.','User Alert')
            commpro.Disconnect(hcommpro)
            return
        wx.MessageBox('Terminal tables have been deleted','User Alert')
        commpro.Disconnect(hcommpro)


    def reboot_inbio(self, event):
        t = threading.Thread(target = send_params_inbio,args = (self.reboot_command,self.terminal_ip))
        t.start()
        progressMax = 35
        dialog = wx.ProgressDialog("Progress Information", ("Rebooting Inbio IP = " + self.terminal_ip+"."), progressMax)
        keepGoing = True
        count = 0
        while keepGoing and count < progressMax:
            count = count + 1
            wx.Sleep(1)
            keepGoing = dialog.Update(count)
        dialog.Destroy()
        #failure
        if INBIO_REBOOT_OK == 1:
            wx.MessageBox(("Error Rebooting Inbio IP = " + self.terminal_ip + "..check comms."),'User Alert')



    def create_inbio_sql_tables(self, event):
        ret = wx.MessageDialog(None,'Do you wish to create Inbio Sql Tables?  (Ensure  not already created)', 'User Option', wx.YES_NO)
        ret1 = ret.ShowModal()
        if ret1 == wx.ID_NO:
            ret.Destroy()
            return -1
        if ret1 == wx.ID_YES:
            sql = """CREATE TABLE [dbo].[d_inbio_misc](
	                    [index] [int] IDENTITY(1,1) NOT NULL,
	                    [property] [nvarchar](max) NULL,
	                    [value] [nvarchar](max) NULL
                        ) ON [PRIMARY]"""
            sqlret = sqlconns.sql_command(sql)
            if sqlret == -1:
                wx.MessageBox('There was an issue creating Inbio Tables, please investigate.','User Alert')
                return -1
            else:
                sql = '''CREATE TABLE [dbo].[d_inbio_events](
	                        [index] [int] IDENTITY(1,1) NOT NULL,
	                        [key] [nvarchar](max) NULL,
	                     [unhandled_terminals] [nvarchar](max) NULL,
	                        [last_attempt] [datetime] NULL,
	                        [completion_date] [datetime] NULL,
	                        [completed] [int] NULL
                            ) ON [PRIMARY]'''
                sqlret = sqlconns.sql_command(sql)
                if sqlret == -1:
                    wx.MessageBox('There was an issue creating Inbio Tables, please investigate.','User Alert')
                    return -1

        sql = '''CREATE TRIGGER tevent_to_inbio_event
                    ON  tevent_update
                    for  insert,update
                    AS
                    if (SELECT COUNT (*) FROM inserted WHERE [event_update_command_ref_id] =1) > 0
	                INSERT INTO d_inbio_events([key],[completed])
	                values ((SELECT [find_key] from inserted),0)'''
        sqlret = sqlconns.sql_command(sql)

        wx.MessageBox('Inbio Tables Created successfully','User Information')

#disable create menu option
        menubar = self.GetMenuBar()
        menubar.Enable(ID_SIMPLE, False)
#remove warning information from warning panel
        self.warning_label.SetLabel("")
        self.warning_label1.SetLabel("")
        self.button_stop_service.Enable(True)

        return 0


    def closebutton(self, event):
        self.Close(True)


    def closewindow(self, event):
        self.Destroy()

    def onbutton_refresh(self,event):
        self.Close()
        app = wx.App(False)
        frame = MainScreen()
        frame.Show()
        app.MainLoop()

    def populate_terminal_grid(self,inbio_controller_grid):
        global INBIO_GRID_ROWS
        INBIO_GRID_ROWS = 0
        colLabels = ["Id", "Number", "Description", "IP Address", "Gateway","Net Mask","Receive Time","Information"]
        colSize = [20,50,150,100,100,100,110,150]
        sql_text = "SELECT terminal_id,number,description,ip_address FROM tterminal WHERE number >= 1000 AND configuration = " + gl.access_terminal_configuration + \
                   " ORDER BY number"
        terminal_list = sqlconns.sql_select_into_list(sql_text)
        if terminal_list ==-1:return -1
        inbio_controller_grid.AppendRows(len(terminal_list), updateLabels = 1)
        for index in range(len(terminal_list)):
            INBIO_GRID_ROWS += 1
            for col in range(4):
                inbio_controller_grid.SetCellValue(index,col,str(terminal_list[index][col]))
        #sort out columns
        for index in range(8):
            inbio_controller_grid.SetColLabelValue(index,colLabels[index])
            inbio_controller_grid.SetColSize(index,colSize[index])
        self.refresh_terminal_grid(inbio_controller_grid)
        #self.inbio_controller_grid.ForceRefresh()

    def refresh_terminal_grid(self,inbio_controller_grid):
        global INBIO_GRID_ROWS
        if INBIO_GRID_ROWS == 0:
            return
        for x in range(INBIO_GRID_ROWS):
            terminal_num = int(inbio_controller_grid.GetCellValue(x, 1))
            if terminal_num % 100 == 1:
                attr = wx.grid.GridCellAttr()
                attr.SetBackgroundColour("#CCFFCC")
                inbio_controller_grid.SetRowAttr(x, attr)
                info = ["0","0","0","0"]
                #info is gateway, serial number, datetime, netmask
                info = test_inbio_terminal(inbio_controller_grid.GetCellValue(x, 3))
                if info[0] == "0":
                    inbio_controller_grid.SetCellBackgroundColour(x,7,"RED")
                    inbio_controller_grid.SetCellValue(x,7,"Door 1 No Connection (m)")
                    info = ["","No Connection","",""]
                else:
                    inbio_controller_grid.SetCellValue(x,4,info[0])
                    inbio_controller_grid.SetCellValue(x,5,info[3])
                    inbio_controller_grid.SetCellValue(x,6,info[2])
                    self.inbio_controller_grid.SetCellBackgroundColour(x,7,"#006600")
                    inbio_controller_grid.SetCellValue(x,7,("Door 1 " + info[1]+ " (m)"))
            elif terminal_num % 100 == 2:
                    attr = wx.grid.GridCellAttr()
                    attr.SetBackgroundColour("#FFFFCC")
                    inbio_controller_grid.SetRowAttr(x, attr)
                    inbio_controller_grid.SetCellValue(x,4,info[0])
                    inbio_controller_grid.SetCellValue(x,5,info[3])
                    inbio_controller_grid.SetCellValue(x,6,info[2])
                    inbio_controller_grid.SetCellValue(x,7,("Door 2 " + info[1]))
            elif terminal_num % 100 == 3:
                    attr = wx.grid.GridCellAttr()
                    attr.SetBackgroundColour("#FFFFCC")
                    inbio_controller_grid.SetRowAttr(x, attr)
                    inbio_controller_grid.SetCellValue(x,4,info[0])
                    inbio_controller_grid.SetCellValue(x,5,info[3])
                    inbio_controller_grid.SetCellValue(x,6,info[2])
                    inbio_controller_grid.SetCellValue(x,7,("Door 3 " + info[1]))
            elif terminal_num % 100 == 4:
                    attr = wx.grid.GridCellAttr()
                    attr.SetBackgroundColour("#FFFFCC")
                    inbio_controller_grid.SetRowAttr(x, attr)
                    inbio_controller_grid.SetCellValue(x,4,info[0])
                    inbio_controller_grid.SetCellValue(x,5,info[3])
                    inbio_controller_grid.SetCellValue(x,6,info[2])
                    inbio_controller_grid.SetCellValue(x,7,("Door 4 " + info[1]))


def build_personnel_list(terminal_ip):
#user table list
#authorised table list
    personnel_auth_list =[]
    personnel_list=[]
    finger_template_list=[]
    term_list = get_doors_from_ip(terminal_ip)

    if len(term_list) == 0: return -1,-1
    for index in range(len(term_list)):
        sql_text = """SELECT temployee.employee_id, temployee.badge, temployee.date_started_with_company, temployee.badge_activation, temployee.badge_expiry, tterminal_policy.data
                FROM temployee INNER JOIN
                temployee_status ON temployee.employee_status_id = temployee_status.employee_status_id INNER JOIN
                tterminal_policy ON temployee.terminal_policy_id = tterminal_policy.terminal_policy_id
                WHERE exclude_from_calculation = 0 AND (
                data like '%TerminalAssignment\AccessControl\optAllYes,True%'"""
        sql_text += """ OR data like """ + "'%TerminalAssignment\\AccessControl\\Terminal\\" + str(term_list[index][0]) + ",True%'"
        sql_text +=")"
        employee_list = sqlconns.sql_select_into_list(sql_text)
    #personnel_list=[[0 for cols in range(5)] for rows in range(len(employee_list))]
#now need to convert_personnel_list for sending to clock
        for index in range(len(employee_list)):
            x_string = "Pin=" + str(employee_list[index][0])
            x_string +="""\tCardNo="""
            if employee_list[index][1] != None: x_string += str(int(employee_list[index][1]))
            x_string += "\tStartTime=" + get_start_time(employee_list[index][2],employee_list[index][3]) + "\tEndTime=" + get_end_time(employee_list[index][4])
            personnel_list.append(x_string)
#now do authorised
#big question on whether you can have different timezone for each door
#if not this will need recoded for now assuming you can do that
        for index in range(len(employee_list)):
    #code finger stuff here
            emp_finger=[]
            emp_finger = get_finger_template(employee_list[index][0])
            if len(emp_finger) > 0: finger_template_list.extend(emp_finger)
            data = employee_list[index][5]
            datalist = data.split("""\r""")
    #got term list for employee for this inbio, now build authorised list
            for z in range(len(term_list)):
            #check you allowed for this clock
                for y in range(len(datalist)):
                    term_policy_string = """AccessControl\\Terminal\\"""
                    term_policy_string += str(term_list[z][0]) + """,True"""
                    if term_policy_string in datalist[y]:
                        door_id = get_door_id(term_list[z][1])
                        auth_timezone_id = datalist[y+1]
                        auth_timezone_id = auth_timezone_id[-1]
                        if int(auth_timezone_id) > 0: personnel_auth_list.append("Pin=" + str(employee_list[index][0]) + "\tAuthorizeTimezoneId=" + auth_timezone_id + "\tAuthorizeDoorId=" + str(door_id))
                        print(personnel_list)
                        print(personnel_auth_list)
    return personnel_list,personnel_auth_list,finger_template_list

def get_finger_template(emp_id):
    finger_list=[]
    employee_fingers = sqlconns.sql_select_into_list("SELECT size,fid,tmp from d_iface_finger WHERE employee_id = " + str(emp_id))
    if employee_fingers ==-1:
        return finger_list
    p_fingers = create_string_buffer(str.encode("templatev10"))
    for z in range(len(employee_fingers)):
        tx = 'Size=0\tUID=#\tPin='+str(emp_id)+'\tFingerID='+str(employee_fingers[z][1])+\
                '\tValid=1\tTemplate='+str(employee_fingers[z][2])+'\tResverd=\tEndTag='
        finger_list.append(tx)
    return finger_list

def get_start_time(dte_started,dte_activated):
    return "20000101"
    base_date = datetime.datetime(2015,1,1)
    if dte_activated == None:
        dte_activated = base_date
    if dte_started == None:
        dte_started = base_date
    if dte_activated < base_date: dte_activated = base_date
    if dte_started < base_date: dte_started = base_date
    if dte_activated >= dte_started:
        return f.convert_sql_date(dte_activated,'yyyymmdd')
    else:
        return f.convert_sql_date(dte_started,'yyyymmdd')

def get_end_time(dte):
    return "23000101"
    if dte == None: return "23000101"
    return f.convert_sql_date(dte,"yyyymmdd")


def get_door_id(term_id):
    print(term_id)
    if term_id % 100 == 1: return 1
    if term_id % 100 == 2: return 2
    if term_id % 100 == 3: return 4
    if term_id % 100 == 4: return 8
    return 0


def build_terminal_policy_list(data):
    data_list = data.split('\\r')
    for index in range(len(data_list)):
        return data_list

def get_doors_from_ip(terminal_ip):
    door_list=[]
    sql_text = "SELECT terminal_id,number from tterminal where number >= 1000 AND ip_address like '%" + terminal_ip + "%'"  + " AND configuration =" + gl.access_terminal_configuration + " order by number"
    door_list_list = sqlconns.sql_select_into_list(sql_text)
    if door_list_list == -1: return -1
    #turn list of lists into a list as there is only one field
    return door_list_list


def build_access_string(access_patterns):
        timezone_list = []
        for index in range(len(access_patterns)):
            a = [0,0,0,0,0,0,0]
            timezone_id = access_patterns[index][0]
            timezone_string = "TimezoneId=" + str(timezone_id)
            for x in range(10):
                if access_patterns[index][x+4] is not None:
                    time_from = f.convert_sql_date(access_patterns[index][x+4],"hh:mm")
                    time_to = f.convert_sql_date(access_patterns[index][x+14],"hh:mm")
                    type = access_patterns[index][x+24]
                    value = str(timezone_dec(time_from,time_to))
                    if type.lower() == "all days":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "=" + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                        if a[5] < 3:
                            y = int(a[5])+1
                            timezone_string += "\t" + "FriTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[5] +=1
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    if type.lower() == "sunday":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                    if type.lower() == "monday":
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                    if type.lower() == "tuesday":
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                    if type.lower() == "wednesday":
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                    if type.lower() == "thursday":
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                    if type.lower() == "friday":
                        if a[5] < 3:
                            y = int(a[5])+1
                            timezone_string += "\t" + "FriTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[5] +=1
                    if type.lower() == "saturday":
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    if type.lower() == "mon-thu":
                        if a[1] < 3:
                            y = int(a[1])+1
                            timezone_string += "\t" + "MonTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[1] +=1
                        if a[2] < 3:
                            y = int(a[2])+1
                            timezone_string += "\t" + "TueTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[2] +=1
                        if a[3] < 3:
                            y = int(a[3])+1
                            timezone_string += "\t" + "WedTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[3] +=1
                        if a[4] < 3:
                            y = int(a[4])+1
                            timezone_string += "\t" + "ThuTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[4] +=1
                    if type.lower() == "sat-sun":
                        if a[0] < 3:
                            y = int(a[0])+1
                            timezone_string += "\t" + "SunTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[0] +=1
                        if a[6] < 3:
                            y = int(a[6])+1
                            timezone_string += "\t" + "SatTime%d"%(y) + "="  + str(timezone_dec(time_from,time_to))
                            a[6] +=1
                    timezone_list[len(timezone_list):] = [timezone_string]

        return timezone_list


def send_params_inbio(command, ip_address):
     global INBIO_REBOOT_OK
     param =  'protocol=TCP,ipaddress='+ ip_address + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) +',passwd='
     params = str.encode(param)
     commpro = windll.LoadLibrary("plcommpro.dll")
     constr = create_string_buffer(params)
     hcommpro = commpro.Connect(constr)
     if hcommpro == 0:
        return -1
     items = str.encode(command)
     p_items = create_string_buffer(items)
     ret = commpro.SetDeviceParam(hcommpro,p_items)
     commpro.Disconnect(hcommpro)
     if command=="Reboot=1" and ret==-2:
         return 0
         INBIO_REBOOT_OK = 1
     if ret == 0:
        INBIO_REBOOT_OK = 1


def test_inbio_terminal(ip_address):
    output = ["0","0","0","0"]
    param =  'protocol=TCP,ipaddress='+ ip_address + ',port=4370,timeout=' + str(gl.COMM_TIMEOUT) +',passwd='
    params = str.encode(param)
    commpro = windll.LoadLibrary("plcommpro.dll")
    constr = create_string_buffer(params)
    hcommpro = commpro.Connect(constr)
    buffer= create_string_buffer(2048)
    items = b"GATEIPAddress,~SerialNumber,DateTime,NetMask"
    p_items = create_string_buffer(items)
    ret = commpro.GetDeviceParam(hcommpro,buffer,256,p_items)
    if ret ==0:
        string = (buffer.raw)
        strong = str(string)
        strong = strong.replace("b'","")
        strong = strong[:-1]
        strong = strong.replace("\\x00","")
        #put the data into a list
        output = strong.split(',')
        timeanddate = output[2]
        date_output = timeanddate.split('=')
        output[2] = str(convert_int_to_time_date(date_output[1]))
        output[3] = output[3].replace("NetMask=","")
        output[0] = output[0].replace("GATEIPAddress=","")
        output[1] = output[1].replace("~SerialNumber=","")
    commpro.Disconnect(hcommpro)
    return output


def timezone_dec(time1,time2):
    lister = time1.split(':') + time2.split(':')
    return append_hex(((int(lister[0])*100+int(lister[1]))), ((int(lister[2])*100+int(lister[3]))))


def append_hex(a, b):
#for timezone, convert from and to time to decimal
    hexa = ("{0:#0{1}x}".format(int(a),6))
    hexb = ("{0:#0{1}x}".format(int(b),6))
    hexb = hexb.replace("0x","")
    hexa = hexa+hexb
    return int(hexa,0)


def convert_int_to_time_date(y):
    x = int(y)
    second = int(x % 60)
    minute = int((x / 60) % 60)
    hour = int((x / 3600) % 24)
    day = int((x / 86400) % 31 +1)
    month = int((x / 2678400) % 12 + 1)
    year = int((x / 32140800) + 2000)
    #d = datetime.datetime(year,month,day,hour,minute,second)
    d = datetime.datetime(year,month,day,hour,minute,second)
    dte = d.strftime('%d\%m\%y-%H:%M:%S')
    return dte


def convert_now_to_int():
    x = convert_date_to_int(datetime.datetime.now())
    return x


def convert_date_to_int(dte):
    second = int(dte.strftime("%S"))
    minute = int(dte.strftime("%M"))
    hour = int(dte.strftime("%H"))
    day = int(dte.strftime("%d"))
    month = int(dte.strftime("%m"))
    year = int(dte.strftime("%y"))
    x = ((year * 12 * 31) + ((month - 1) * 31) + (day-1))*(24*60*60) + (hour * 60 * 60) + (minute * 60) + second
    return x


def test_inbio_sql_tables():
    sql = """IF OBJECT_ID (N'd_inbio_events', N'U') IS NOT NULL SELECT 1 AS res ELSE SELECT 0 AS res"""
    ret = sqlconns.sql_select_single_field(sql)
    if ret == '0':
        return 0
    elif ret == -1:
        return 0
    else:
        sql = """IF OBJECT_ID (N'd_inbio_misc', N'U') IS NOT NULL SELECT 1 AS res ELSE SELECT 0 AS res"""
        ret = sqlconns.sql_select_single_field(sql)
        if ret  == '0':
            return 0
        elif ret == -1:
            return 0
        else:
            return 1


def main():
    app = wx.App(False)
    frame = MainScreen()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    sys.exit(main())
