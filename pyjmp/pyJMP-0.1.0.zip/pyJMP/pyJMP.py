'''
#############################################

 PyJMP module
 Author: Kok Hua Tan (Guohua tan)
 Revised date: Mar 26 2014
 
##############################################

Usage:    
    API for SAS JMP

Updates:
     Jul 10 2014: Changes to tabulation to handle only grouping columns
     Jul 02 2014: Take care of legend pic (with temporary solution)
     May 24 2014: Add two functions: get_exist_req_para_list & get_para_not_exist_in_columns for columns checking
     Feb - Apr 2014: Convert most of the bivariate function to com object (instead of script based)
                   : Add in tabulation and saving
                   
     #################### Based on original pyJMP ##################
     Sept 27 2011: Add in resolve_xgroup_options function
     Sept 26 2011: Add get_list_of_col_name method in initialize
     Sept 18 2011: Complete the basic container template
     Sept 09 2011: Complete the variability template
     Sept 08 2011: Sort the self.grouping_list
     Sept 04 2011: Complete the bivariate and container template
     Sept 03 2011: Change the mako template
     Sept 02 2010: Add in separate grouping for legend
     July 27 2010: Add 2 functions: Get col name and check if col name exist
                 : Add in brief description of functions

Learning :
    Get tree structure by shift+ctrl plus right click
    Saving legend: legend = bivObj.GetGraphicItemByType("PictureBox", 2)
    To access the Display Tree, right-click on the uppermost disclosure icon and select Edit > Show Tree Structure.
    a.SaveGraphicOutputAs(r'c:\data\temp\try_'+ str(n)+'.jpg',2)#2 is jpeg
    Some of JMP function do not run as function  (without the ())
    To save most of the

    makepy directory
    C:\Python27\Lib\site-packages\win32com\gen_py\DCD36DE0-78F8-11CF-9E68-0020AF24E9FEx0x1x0.py

    JMP creating label
    https://community.jmp.com/thread/59537

    JMP select filter
    https://community.jmp.com/thread/59631
    

TODO:
    JMP commands for saving parts of graph.
    Make tabulation more flexible
    Handling mulitple sub group
    close the tabulation windows
    get col name to be initiated to save execution time.
    This will make the order change based on set funciton: get_exist_req_para_list

    Able to select particular point

    for the tabulation, if just require the config how??


    include a script to generate the marker type pg 273
    --> also have dict that list common shapes

    add in ability to change dec format in tabulation --> may have to prestore the values.

    global setting setup
    
'''

import os, re, time, sys
import win32com.client.dynamic

class JMPObj(object): 
    """
        Python JMP Interface. It provides methods for accessing the basic functionality of JMP Version 7/8/9
        from Python.
        >>> jmpFile = JMPObj()

    """ 

    def __init__(self, fileName=None): #may not want to set the filename here
        '''
            e.g. jmpFile = UseJMP("e:\\python23\myfiles\\testjmp1.JMP") 
        '''
        self.jmp_app = win32com.client.dynamic.Dispatch("JMP.Application")

        ##would require a activation 
        self.jmp_app.Activate()

        #general
        self.doc = object() 

        #general -- path
        self.folder_main_dir_prefix = r'c:\data\temp\cdajmpplots'
        self.jmp_plots_filename_list = [] #store all the plots filename generated --may need function to clear the lsit
        self.jmp_plots_filename_dict = dict()#still deciding which one is needed

        #tabulation paramters
        self.tabulate_column_list = list()
        self.tabulate_grp_list = list()
        self.tabulate_save_fname = ''

        #JMP col parameters
        self.col_name_list = []#initialize only, populated only after get col_name_list function is run

        #Grouping parameters for each individual template
        self.y_col_list = []
        self.x_col_list = [] #as to safeguard incase 
        self.grouping_key = ''

        #bivariate function
        self.fit_spline_scale = 0.1
        self.have_legend = 0 # will apply to all the plots inside

        #display paramters
        self.transparency_settting = 0.4 #from 0 to 1

        #debug and info
        self.verbose = 0    #allow more info during script running

    #################### JMP Functions ####################################

    def openfile(self,filename):
        '''
            Open file in JMP
        '''
        
        try:
           self.doc =  self.jmp_app.OpenDocument(filename)
           self.doc.Activate()
        except:
            print 'file not found'

    def show(self):
        self.jmp_app.Visible = True

    def save_data_as_jmp(self,save_filename):
        '''
            Save data table from Excel, txt file as JMP data file
        '''
        
        self.jmp_app.runcommand("dt=current data table()")
        temp_str = 'filename =' + '\"' + save_filename + '\"'
        self.jmp_app.runcommand(temp_str)
        self.jmp_app.runcommand("dt << save(filename)")   

    def clear_log(self):
        '''
            Clear the log in JMP
        '''
        self.jmp_app.runcommand("Clear Log()")

    def get_log_contents(self):
        '''
            Get log file contents
        '''
        return self.jmp_app.GetLogContents.encode()

    def issue_command(self,str):
        '''
            Issue JMP scripts command. Syntax should follow JMP scripts format
        '''
        self.jmp_app.runcommand(str)

    def get_error_mes(self):
        '''
            Print out error mes while running JMP script commands
        '''
        print self.jmp_app.GetRunCommandErrorString

    def extract_list_from_str(self,item):
        '''
            Return a list from string form of a list. List structure obtained from Log contents is a string.
        '''
        #the output will be '"xxx"', need to remove the internal str
        mobj = re.search('\{(.*)\}$',item)
        req_list= list()
        if mobj:
            wl = mobj.group(1)
            temp =  wl.split(',')
            for n in temp:
                mobj1 = re.search('\"(.*)\"$',n)
                req_list.append(str(mobj1.group(1)))
            return req_list
        else:
            return []#return empty list


    def get_col_data(self,col_name,remove_duplicate =1):
        '''
            Get the particular column data. Useful in determining the different groups. 
        '''
        
        self.clear_log()
        temp_str = "myList = :%s << get values;"%col_name
        self.issue_command(temp_str)
        self.issue_command("print(mylist)")
        a = self.get_log_contents()
        if not remove_duplicate:
            return self.extract_list_from_str(str(a))
        else:
            temp = self.extract_list_from_str(str(a))
            temp = set(temp)
            templist = list()
            while True:
                try:
                    templist.append(temp.pop())
                except:
                    break
            return templist

    def get_list_of_col_name(self):
        '''
            Get all column names in current table 
        '''
        self.clear_log()
        self.issue_command('print(Current Data Table()<<Get Column Names(String))')
        names =  self.get_log_contents()        
        names = self.extract_list_from_str(names)
        if self.verbose: print 'List of Col names' ,[n.replace('\\!','') for n in names]
        self.col_name_list = names
        return names

    def get_list_of_numeric_col(self):
        all_columns = self.get_list_of_col_name()
        required_col_list = [] 
        for n in all_columns:
            self.clear_log()
            temp_cmd_str = 'print(column("%s") << Get Data Type)'%n
            #print temp_cmd_str
            self.issue_command(temp_cmd_str)
            mobj1 = re.search('\"(.*)\"$',self.get_log_contents())
            type = str(mobj1.group(1))
            #print type
            if type == 'Numeric':
                required_col_list.append(n)
        return required_col_list

    def check_col_name_exist(self,checklist):
        '''
            Pass in a checklist and check whether the items in checklist appears in particular Column
            #enable word slightly different yet still can accept

        '''
        col_names = self.get_list_of_col_name()
        for n in checklist:
            if col_names.__contains__(str(n)):
                continue
            print 'item: not exist  ', n
            return 0 #return false
        return 1 #return true


    def return_no_data_column(self, checklist):
        """ Highlight columns fr list with no data
            Args:
                checklist (list): list of column names
            Returns:
                (list): list of columns with no data

        """
        no_data_columns = []
        for n in checklist:
            self.clear_log()
            cmd =  'print(Col Number( :%s ));'%n
            self.issue_command(cmd)
            value =  int(self.get_log_contents())
            if value == 0:
                no_data_columns.append(n)

        return no_data_columns
            
    def get_exist_req_para_list(self,checklist):
        """ Function that return those required parameters that exists in JMP columns.

            Args:
                checklist (list): inputted list of columns name to check.
                
            Returns:
                (list) : modified columns names that exists.    

        """
        return list(set(self.get_list_of_col_name()) & set(checklist))

    def get_exist_with_value_col_list(self, checklist):
        """Screen out those columns that exists and also have values in row.
            Args:
                checklist (list): list of required columns.
            Returns:
                (list): list of columns that exists and has values.
        """
        exist_columns = self.get_exist_req_para_list(checklist)
        return list(set(exist_columns) - set(self.return_no_data_column(exist_columns)))


    def get_para_not_exist_in_columns(self,checklist):
        """ Function that return those required parameters that does not exists in particular JMP columns.

            Args:
                checklist (list): inputted list of columns name to check.
                
            Returns:
                (list) : Columns names that do not exists.    

        """
        return list( set(checklist) - set(self.get_list_of_col_name()) )

    def grouping_data(self):
        '''Simulate a legend for '''
        self.issue_command("dt=current data table()")
        command_str = " dt<<Color By Column(:Name( \"%s\" ));"%self.grouping_key
        self.issue_command(command_str)

    def create_folder(self):
        '''Create a folder to put the log data segregate by date'''
        self.ls_raw_dirpath = os.path.join(self.folder_main_dir_prefix, time.strftime("_%d_%b%y", time.localtime()))
        if not os.path.exists(self.ls_raw_dirpath):
            os.makedirs(self.ls_raw_dirpath)

    def create_bivariate_plot(self):
        '''
            For every column name save the graph with prefix string of the column name (do need the x axis label??)
            NB: there will be the first plot with the legend

        '''
        
        first_plot_created = 0
        ## Add in a dummy first ycol list for legend copy
        self.y_col_list = [self.y_col_list[0]] + self.y_col_list #temp solution
        for nx in self.x_col_list:
            for ny in self.y_col_list:
                a = self.doc.CreateBivariate
                a.LaunchAddX(nx)
                a.LaunchAddY(ny)
                a.Launch
                a.GroupBy(self.grouping_key)
                a.FitSpline(self.fit_spline_scale)

                if self.have_legend or not first_plot_created:
                    self.insert_legend_to_plot()
                    
                framebox_handler = a.GetGraphicItemByType("Frame Box", 1)
                a.FrameBoxTransparency(framebox_handler,self.transparency_settting)#set the transparency
                
                hand = a.GetGraphicItemByType("PictureBox", 1)#handle value keep increasing.
                
                if not first_plot_created:
                    legend_box = a.GetGraphicItemByType("PictureBox", 2)
                    
                    ## legend file graph creation in this format groupingkey_legend
                    ## legend filename remain constant, independent of self.grouping_key
                    legend_savefilename = 'group' + '_legend.png'
                    legend_savefilename = os.path.join(self.ls_raw_dirpath,legend_savefilename)
                    a.SaveGraphicItem(legend_box,legend_savefilename,1)
                    first_plot_created = 1
                    
                else:
                    tempsavefilename = ny + 'vs' + nx + '_bivar.png'
                    tempsavefilename = os.path.join(self.ls_raw_dirpath,tempsavefilename)
                    self.jmp_plots_filename_dict[ny] = tempsavefilename
                    self.jmp_plots_filename_list.append(tempsavefilename)

                    a.SaveGraphicItem(hand,tempsavefilename,1)#2 -- jpg, 1-- Png
                    a.CloseWindow

    def create_simple_scatter(self):
        """ Simplified form of bivariate form without legend, grouping and trend line.
            Required the following parameters to be set.
            self.x_col_list, self.y_col_list, self.transparency_settting, self.ls_raw_dirpath
            possible output: self.jmp_plots_filename_list

        """
        
        for nx in self.x_col_list:
            for ny in self.y_col_list:
                a = self.doc.CreateBivariate
                a.LaunchAddX(nx)
                a.LaunchAddY(ny)
                a.Launch
                    
                framebox_handler = a.GetGraphicItemByType("Frame Box", 1)
                a.FrameBoxTransparency(framebox_handler,self.transparency_settting)#set the transparency
                
                hand = a.GetGraphicItemByType("PictureBox", 1)#handle value keep increasing.
                
                tempsavefilename = ny + 'vs' + nx + '_bivar.png'
                tempsavefilename = os.path.join(self.ls_raw_dirpath,tempsavefilename)
                self.jmp_plots_filename_dict[ny] = tempsavefilename
                self.jmp_plots_filename_list.append(tempsavefilename)

                a.SaveGraphicItem(hand,tempsavefilename,1)#2 -- jpg, 1-- Png
                a.CloseWindow


    def create_variability_plot(self, clean = 0):
        """ Create varaiability plot.
            Extra options
            Kwargs:
                clean: default 0. If 1, will give minialistic dataset
        
        """
        
        for ny in self.y_col_list:
            a = self.doc.CreateVariabilityChart
            a.LaunchAddY(ny)
            # add the x grouping indvidually.
            for nx in self.x_col_list:
                a.LaunchAddX(nx)

            a.Launch
            a.ShowStdDevChart(0)
            a.ShowVariabilityChart(1)
            a.ShowPoints(1)

            if clean:
                a.ShowPoints(0)
                a.ConnectCellMeans(1)
                a.ShowRangeBars(0)                
            
            tempsavefilename = ny + '_var.png'
            tempsavefilename = os.path.join(self.ls_raw_dirpath,tempsavefilename)
            #may have a problem with naming of file --> it might conincide with the biv plot --> need understand the obj scan flow            
            self.jmp_plots_filename_list.append(tempsavefilename)

            a.SaveGraphicOutputAs(tempsavefilename,1)#2 -- jpg, 1-- Png
            a.CloseWindow


    def insert_legend_to_plot(self):
        '''
            Use for inserting in Legend to plots

        '''
        ## set legend
        self.issue_command('a = Window(1);')
        #may not work properly if the window is worong....
        #self.issue_command('rbiv = Window(2); framebox = rbiv[Frame Box( 1 )]; framebox <<Row Legend( "%s");framebox<<Transparency(0.1);'%self.grouping_key) 
        self.issue_command('Wait(0.1); Report(Bivariate[1])[FrameBox(1)] << Row Legend("%s");'%self.grouping_key)
        #self.issue_command('rbiv = Window(2); framebox = rbiv[Frame Box( 1 )]; framebox <<Row Legend( "%s");'%self.grouping_key) 

    def create_tabulation(self):
        '''
            Create summary tabulation
            WIll still relies on the JMP scripting
            simple table with few commands
            how to save tabulation

            NB: this only allow for mean 
            Will add in decimal

            TODO:
                Setting dec pl  as args
                do the column check here.
            
        '''
        #create column first
        tabulate_col_str = ''
        for col_name in self.tabulate_column_list:
             tabulate_col_str = tabulate_col_str + 'Column Table( Analysis Columns( :Name("%s") ) ),'%col_name
            
        #extra treatment for grouping data
        tabulate_config_name_grp_str = ''
        for group_name in self.tabulate_grp_list:
            tabulate_config_name_grp_str =  tabulate_config_name_grp_str  + ':Name("%s"),'%group_name
        tabulate_config_name_grp_str = tabulate_config_name_grp_str[:-1]
        
        if not self.tabulate_column_list == []:
            full_tabulate_config_name_grp_str = 'Row Table( Grouping Columns( %s ), Statistics( Mean ) )'%tabulate_config_name_grp_str
            combined_cmd_addon_str = tabulate_col_str + '\n' + full_tabulate_config_name_grp_str
        else:
            full_tabulate_config_name_grp_str = 'Row Table( Grouping Columns( %s ))'%tabulate_config_name_grp_str
            combined_cmd_addon_str = full_tabulate_config_name_grp_str

        full_tabulate_cmd = '''
                    dt = Tabulate(
                    Show Control Panel( 0 ),
                    Set Format( Uniform Format( 6, 2 ) ),
                    Add Table(
                        %s
                        )
                    );

                Report(dt)[Box(1)]<<save picture("%s",png);

                '''%(combined_cmd_addon_str,self.tabulate_save_fname)
        #print full_tabulate_cmd
        self.issue_command(full_tabulate_cmd)

    def run_series_of_tabulation(self, tabulation_list):
        '''
            Function to create multiple list of tabulation and save to individual files
            get in input containing suffix, list of columns, list of group. pic filename from suffix and type
            list of [str, list, list] --> None
        '''
        for single_tab in tabulation_list:
            self.tabulate_column_list = single_tab[1] 
            self.tabulate_grp_list = single_tab[2]
            filename = single_tab[0] + '_' + 'tabulation.png'
            self.tabulate_save_fname = os.path.join(self.ls_raw_dirpath,filename)
            self.create_tabulation()

    def create_bar_chart(self):
        """Method to create bar chart"""


    ## cells formatting for below functions

    def set_col_as_label(self, col_name):
        """ set column to be used as label.
           Args:
               col_name (str): column name
        """
        cmd_str = 'column("%s") << label(1);'%col_name
        self.issue_command(cmd_str)

    def enable_label_in_plots(self):
        """ Enable label of target cells to be display in plots.
            Note: cells have to be selected first for this to be active.
            Cells can then be subsequently clear of selection.
        """
        self.issue_command('dt=current data table(); dt << Label(1); // Turn on row labels.')

    def invert_selection(self):
        """ Invert a selection of target cells.
            Note target cells must first be chosen.
        """
        self.issue_command('dt=current data table();  dt << invert row selection; // Invert selection')
        
    def clear_selection(self):
        """ Clear selection of target cells. """
        self.issue_command('dt=current data table(); dt << Clear Select;')

    def change_cell_marker(self, color):
        """Changing cell marker color
            Args:
                color: selected color.
        """
        cmd_str ='dt=current data table(); dt << Colors(%s)'%str(color)
        self.issue_command(cmd_str)

    def select_rows_single_criteria(self, col_name, value):
        """
            eg>  << Select Where( :SOURCE == "Facebook");
        """
        cmd_str = 'dt=current data table(); dt  << Select Where( :%s == %s);'%(col_name,value )
        self.issue_command(cmd_str)

    def mark_target_cells(self, criteria, marker_size, marker_color):
        """Highlight marker for target cell which meet certain criteria.

            Args:
                criteria (str): formula that acts as filter.
                marker_size (int): int reference for particular color
                marker_color (int): int reference for particular color

            TODO: a dict with the size and marker color
        
            Make use of the jmp script command
        """
        cmd_str = '''
                    dt= Current Data Table();
                    dt<<Select Where(%s) 
                    <<colors(%d)<<markers(%d);

                  '''%(criteria, marker_size,marker_color)

        self.issue_command(cmd_str)

    def clear_row_state(self):
        """Method to clear current row state (remove markers etc)

        """
        cmd_str = '''
                    dt= Current Data Table();
                    dt<<Clear Row States();
                  '''
        self.issue_command(cmd_str)

    def jmp_color_dict(self, color):
        """Return the dict color to value matching.
            Args:
                color (str): color description.
            Returns:
                (int): value matching the color in JMP.

        """
        marker_dict = {'black':0, 'grey':1,'white':2,'red':3,'green':4,'blue':5,
                    'orange':6,'bluegreen':7,'purple':8,'yellow':9,'cyan':10,'magenta':11}

        return marker_dict[color]

    def jmp_marker_shape_dict(self, shape):
        """Return the dict marker shape to value matching.
            Args:
                shape (str): shape description (only set for the more common shape).
            Returns:
                (int): value matching the shape in JMP.

        """
        shape_dict = {'plus':1,'cross':2,'open_Square':3,'open_diamond':4,'open_triangle':5,'y':6,'z':7,
                    'open_circle':8,'open_rect':9,'asterick':11,'circle':12,'rect':13,'square':15,'diamond':16}

        return shape_dict[shape]



#####################

if (__name__ == "__main__"):
    import sys
    choice = 90
        
    if choice ==1:


        '''
                Legend only work if all the jmp windows are closed. (or cycle through all the window for to set.add
                the saving of file only for all whole plots. and the qty is bad

        '''


        jmpFile = JMPObj()
        filename = r'\\SGP-L071166D033\Chengai main folder\Chengai_combined_data_set\Iteration eval 50 FW41\Iteration eval 50 FW41 1 to 1.csv'
        jmpFile.openfile(filename)
        jmpFile.show()
        jmpFile.x_col_list = ['WPE_UIN']
        #full data retrieval
        jmpFile.y_col_list = jmpFile.get_list_of_numeric_col() 
        jmpFile.y_col_list = [
                        'CTQ_AMP',
                        'CTQ_OVW',
                        'CTQ_BER',
                        'CTQ_CP_CLRNC',
                        'ACTUAL_SMR_BPIC_AVG',
                        'ACTUAL_SMR_TPIC_AVG',
                        'ACTUAL_SMR_ADC_AVG',
                        'DRV_CAPACITY',
                        'ACTUAL_CMR_BPIC_AVG',
                        'ACTUAL_CMR_TPIC_AVG',
                        'ACTUAL_CMR_ADC_AVG',
                        'RHEAT_APPLIED_AVG',
                        'PREHEAT_APPLIED_AVG',
                        'WHEAT_APPLIED_AVG',
                        'WRT_CUR_AVG',
                        'OSH_AVG',
                        'OSHD_AVG'
                        ]
        jmpFile.grouping_key = 'DRIVE_SBR_NUM'
        jmpFile.create_folder()
        jmpFile.grouping_data()

        ## experiment on the filter type
        jmpFile.mark_target_cells('ACTUAL_SMR_BPIC_AVG>2300', 8, 8)

        jmpFile.create_bivariate_plot()
        #may need to close document in the end

        #need to increase width and increase tranpiracy
        
                  
    ##    print jmpFile.get_list_of_col_name()
    ##    sys.exit()


    if choice ==2:
        #create a pyjmp 2 without use of mako
        '''Unable to get the legend to work.....'''
        print 'get fundamentatl'
        print
        #jmp_app = win32com.client.dynamic.Dispatch("JMP.Application")
        jmp_app = win32com.client.Dispatch("JMP.Application")
        jmp_app.Activate()
        filename = r'C:\Program Files\SAS\JMP\9\Support Files English\Sample Data\Big Class.jmp'
        doc =  jmp_app.OpenDocument(filename)#return object of type IJMPDoc
        #ignore the parentistic --> may cause errror downstream
        #do not seem to have option to add legend for the bivariate
        jmp_app.runcommand("dt=current data table()")
        jmp_app.runcommand(" dt<<Color By Column(:sex);")
        #for n in ['Height','age']:

        for n in ['Height','Age']:
            a = doc.CreateBivariate
            print a.LaunchAddX(n)
            print a.LaunchAddY("Weight")
            #some of the function do not have the parenesis
            a.Launch
            a.GroupBy('sex')
            a.FitSpline(0.1)
            hand = a.GetGraphicItemByType("PictureBox", 1)#handle value keep increasing.#1- is the main box, 2 - is the fit legend
            framebox_handler = a.GetGraphicItemByType("Frame Box", 1)
            a.FrameBoxTransparency(framebox_handler,0.1)
            jmp_app.runcommand('a = Window(1);')
            #may not work properly if the window is worong....
            jmp_app.runcommand(' rbiv = Window(2); framebox = rbiv[Frame Box( 1 )]; framebox <<Row Legend( "sex");') #need to switch the window to his            


            a.SaveGraphicItem(hand,r'c:\data\temp\try_'+ str(n)+'.jpg',2)#will not copy the legend
            a.SaveGraphicOutputAs(r'c:\data\temp\jj'+ str(n)+'.jpg',2) #this will save all the graphic

            a.CloseWindow

            #jmp_app.runcommand(' rbiv = Current Window(); framebox = rbiv[Frame Box( 1 )]; framebox <<Row Legend( "sex");')
            #a.SaveGraphicOutputAs(r'c:\data\temp\try_'+ str(n)+'.jpg',2)#2 is jpeg
            #a.CloseWindow
        #a.CopyToClipboard --> can copy to clipboad
        #Use mainly the run coomand option
        #self.jmp_app.runcommand("dt=current data table()")
        #http://www.gossamer-threads.com/lists/python/python/23590


    if choice ==3:
        print 'use the string substitution method'

    if choice ==4:
        print 'Converting csv to jmp first'
        #check where is the makepy directory

    if choice ==5:
        
        jmpFile = JMPObj()
        filename = r'\\SGP-L071166D033\Chengai main folder\Chengai_combined_data_set\TDK_tss10.6b_set_FW37\TDK_tss10.6b_set_FW37_with_ref.csv'
        jmpFile.openfile(filename)
        jmpFile.show()
        jmpFile.verbose = 0

        # a dict of  different tabulation??? put here or put at the consolidation??
        jmpFile.tabulate_column_list = ['ACTUAL_SMR_BPIC_AVG','ACTUAL_SMR_TPIC_AVG','ACTUAL_SMR_ADC_AVG']
        jmpFile.tabulate_grp_list = ['CONFIG_GEN','CONFIG1']
        jmpFile.tabulate_save_fname = 'c:\\data\\temp\\myGraph.png'
        jmpFile.create_tabulation()

    if choice == 6:
        '''Tabulation plots'''
        jmpFile = JMPObj()
        filename = r'\\SGP-L071166D033\Chengai main folder\Chengai_combined_data_set\TDK_tss10.6b_set_FW37\TDK_tss10.6b_set_FW37_with_ref.csv'
        jmpFile.openfile(filename)
        jmpFile.show()
        jmpFile.create_folder()
        tabulation_list = [
                            ['CONFIG',[],['CONFIG_GEN','CONFIG1', 'CONFIG2', 'CONFIG_HEAD']],
                            ['SMR',['ACTUAL_SMR_BPIC_AVG','ACTUAL_SMR_TPIC_AVG','ACTUAL_SMR_ADC_AVG'],['CONFIG_GEN','CONFIG1']],
                            ['CMR',['ACTUAL_CMR_BPIC_AVG','ACTUAL_CMR_TPIC_AVG','ACTUAL_CMR_ADC_AVG'],['CONFIG_GEN','CONFIG1']]

                            ]
        jmpFile.run_series_of_tabulation(tabulation_list)


    if choice == 8:
        jmpFile = JMPObj()
        filename = r'\\SGP-L071166D033\Chengai main folder\Chengai_combined_data_set\Gen3B RHO FW52\Gen3B RHO FW52_1_CAL2PASS.csv'
        jmpFile.openfile(filename)
        jmpFile.show()
        jmpFile.mark_target_cells("ACTUAL_SMR_BPIC_AVG>=2100",8,8)
##        checklist = ['PRE2_DRIVE_GROUP','MULTI_EXIST','FIN2_STATUS','PE_EFL','aaaa']
##        #print jmpFile.return_no_data_column(checklist)
##        print jmpFile.get_exist_with_value_col_list(checklist)


    if choice == 7:
        """table function"""
        #jmp_app = win32com.client.dynamic.Dispatch("JMP.Application")
        jmp_app = win32com.client.Dispatch("JMP.Application")
        jmp_app.Activate()
        filename = r'C:\Program Files\SAS\JMP\9\Support Files English\Sample Data\Big Class.jmp'
        doc =  jmp_app.OpenDocument(filename)#return object of type IJMPDoc
        b = doc.GetDataTable

        

        # for marking cell which meet certain criteria..... by jmp scriptin
        cmd  = '''dt << Current Data Table();
        dt<<Select Where(age==13) // select the youngest subjects
        <<colors(8)<<markers(8); // and use purple open circles for them'''
        #Current Data Table() <<Select Where(age==13)<<colors(8)<<markers(8);

        jmp_app.runcommand(cmd)

        #current data table()<<get script; #avaliable in log

    if choice ==90:
        """ For creating labels"""
        jmpFile = JMPObj()
        filename = r'C:\Users\356039\Desktop\Chengai main folder\Chengai_combined_data_set\CRT2 Reli ATI Failures\TDK_2SBR_withFailheads.csv'
        jmpFile.openfile(filename)
        jmpFile.show()
        jmpFile.set_col_as_label('SERIALNUM_SUBSTR')
        jmpFile.select_rows_single_criteria('Fail Head',1)
        jmpFile.enable_label_in_plots()
        jmpFile.invert_selection()
        jmpFile.change_cell_marker(jmpFile.jmp_color_dict('grey'))

        jmpFile.select_rows_single_criteria('Fail Head',1) #set selection again to bold it

        ##maybe need to set the row legend first.


    if choice == 9:
        """table function"""
        #jmp_app = win32com.client.dynamic.Dispatch("JMP.Application")
        jmp_app = win32com.client.Dispatch("JMP.Application")
        jmp_app.Activate()
        filename = r'C:\Users\356039\Desktop\Chengai main folder\Chengai_combined_data_set\CRT2 Reli ATI Failures\HWYRHOCRT2SBR.csv'
        doc =  jmp_app.OpenDocument(filename)#return object of type IJMPDoc
        jmp_app.Visible = True
        
        ##run as script based
        jmp_app.runcommand('column("DRIVE_SERIAL_NUM") << label(1);')

        ## doing filter

        ## select one parameters such as fail = 1 for selection

        ## enable mutlipel selection

        ## str away do as jmp script??

        ##set label to graphs
        #jmp_app.runcommand('dt=current data table(); dt << Select Randomly(5) << Label(1) << Clear Select; // Turn on row labels.') # turn on label before plotting

        #also need to invert selection and change marker color
        
        
        #add label
        #column("name") << label(1);
        #http://www.jmp.com/support/help/Columns.shtml

        #how to select rows

        #graph also need to use enable label options
        #bigClass << Select Randomly(5) << Label(1) << Clear Select; // Turn on row labels.
        #turn on row label from table
        #https://community.jmp.com/thread/59537




##        b = doc.GetDataTable

##        """variability plots paramters"""
##        a = doc.CreateVariabilityChart
##        a.LaunchAddY("height")
##        a.LaunchAddX("sex")
##        a.LaunchAddX("age")#right now have to add one by one
##        a.Launch
##        a.ShowStdDevChart(0)
##        a.ShowVariabilityChart(1)
##        a.SaveGraphicOutputAs(r'c:\data\temp\try_'+ str(n)+'.jpg',2)#2 is jpeg
##        a.CloseWindow
##        #cannot settle the variability report --> see can use the below command to issue the variability plot
##        self.issue_command('Wait(0.1); Report(Bivariate[1])[FrameBox(1)] <<  Row Legend("%s");'%self.grouping_key)








