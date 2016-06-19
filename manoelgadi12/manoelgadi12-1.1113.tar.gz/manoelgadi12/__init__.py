
# coding: utf-8





__author__ = 'ersh'
__email__ = 'ershov@student.ie.edu'
__version__ = '1.1113'
#There is a link to group github where you can find library manoelgadi12 and all the files
#and instructions
#https://github.com/ersh24/manoelgadi12

################
#L Automated data cleaning
####################
import pandas as pd
import numpy as np
import re
####################
#L Automated data cleaning
####################
def Faa1():
    import pandas as pd
    import numpy as np
    import re
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    np.seterr(invalid='ignore')
    print("Original Data Frame\n", data)
    
    #==============================================================================
    # GOAL: Clean files trying to get numerical columns:
    # - Usually NaN are 0 as there is no value.
    # - Whitespaces which can appear when copying data are noisy as they convert 
    #   numbers into strings that are not operable.
    # - Outliers usually are errors which can modify average values. Then it is
    #   better to sustitute them for more reasonable values.
    #==============================================================================
    
    # Replace all NaN with 0
    data.fillna(0, inplace=True)
    
    # If all the values in the column are float and whitespaces (one or several),
    # replaces the latter with 0.
    # Removes whitespaces before or after the numbers.
    for column in data.columns:
        
        if data[column].dtypes in ["object"]:
            change = True
    # The column is going to change if all the values (without whitespaces)
    # match numbers. Numbers need to have int side, though it could be easily
    # changed to accept numbers like .35 as 0.35
            for i in range (0,len(data)):
                if (re.match(r"[-+]?\d+(\.\d+)?$", str(data[column][i]).strip()) is None):
                    if (not pd.isnull(data[column][i]) and data[column][i].strip() != ''):
                        change = False
            if change:
    # If the value is a set of whitespaces, they are replaced by 0, otherwise
    # whitespaces are deleted and finally the column type is changed to numeric
                data[column]= data[column].replace(r"^\s+$", '0', regex=True)
                data[column]= data[column].replace(r"\s+", '', regex=True)
                data[column] = pd.to_numeric(data[column], errors='coerce')
    
    # Replace outliers for the border values
    # For each column several values which define it, are created
    # Values out of the upper and lower limits are replaced for the limit values
    datadict = {}
    for column in data.columns:
        if (data[column].dtypes in ["int64", "float64"]):
            max = np.max(data[column])        
            p75 = data[column].quantile(0.75)
            p50 = data[column].quantile(0.5)
            p25 = data[column].quantile(0.25)
            min = np.min(data[column])        
            mean = data[column].mean()
            iqr = p75 - p25
            lower = p25-1.5*iqr
            upper = p75 + 1.5*iqr
            valueslist = [lower, min, p25, p50, mean, p75, max, upper]
            tagslist = ["LOWER", "MIN", "P25", "P50", "Mean", "P75", "MAX", "UPPER"]
            datadict.update({column : pd.Series([data[column].dtypes]+valueslist, index=["Type"]+tagslist)})
    # If it is binary don't detect outliers
            if (set(data[column]) == {0,1}):
                continue
    # Loops the values in a column looking for extreme values
    # When it finds extreme values sustitutes them, offering several choices
            for i in range (0,len(data)):
                if (data[column][i] > upper):
                    data.set_value(i, column, upper)
                if (data[column][i] < lower):
                    data.set_value(i, column, lower)
            
    print ("\nInfo about the columns to transform:\n", pd.DataFrame(datadict),"\n")
    
    print("Transformed Data Frame\n", data)
    
    data.to_csv("transformed.csv", index=False)







####################
#L Human assisted data cleaning
####################


#     Human assisted data cleaning
   
def HAdatacleaning():
####################
#L Human assisted data cleaning
####################
    import pandas as pd
    import numpy as np
    import re
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    def open_file():
        filename = filedialog.askopenfilename(
        title = "Choose your file",
        filetypes = (("csv files", "*.csv"), ("all files", "*.*")),
        defaultextension = '.csv',
        initialdir = '.')
        return filename
    
    
    def save_file():
        filename = filedialog.asksaveasfilename(
        title = "Save file",
        filetypes = (("csv files", "*.csv"), ("all files", "*.*")),
        defaultextension = '.csv',
        initialdir = '.',
        initialfile = 'transformed.csv')
        if filename != "":
            data.to_csv(filename, index=False)
    
    
    def start():
        global data
    
#        fich = open_file()
#        id_entry.set (fich)
#        data = pd.read_csv (fich)
        print("Original Data Frame:\n", data)
    
    # Prepare interface to ask about NaN
        nan = ttk.Label(win_root, text = "Convert 'NaN'?:")
        nan.grid(row=1, column=0, sticky=tk.E)
        nanrad1 = tk.Radiobutton(win_root, text="No", variable = nanrad, value=0)
        nanrad2 = tk.Radiobutton(win_root, text="0", variable = nanrad, value=1)
        nanrad3 = tk.Radiobutton(win_root, text="Most Freq", variable = nanrad, value=2)
        nanrad1.grid(row=1, column = 1, sticky=tk.W)
        nanrad2.grid(row=1, column = 1)
        nanrad3.grid(row=1, column = 1, sticky=tk.E)
        nanrad1.deselect()
        nanrad2.select()
        nanrad3.deselect()
        button1.grid(row=1, column=2, sticky=tk.W)
        state.config(text = "\nHow to proceed with NaN?" )
    
    
    def cleannan():
        global data
        global c
    # NaN are not replaced
        if nanrad.get() == 0:
            state.config(text = "NaN not converted. Select columns to remove whitespaces." )
    # NaN are replaced by 0
        if nanrad.get() == 1:
            data.fillna(0, inplace=True)
            state.config(text = "'NaN' -> 0. Select columns to remove whitespaces." )
    # NaN are replaced by the most frequent vlaue: mode
        if nanrad.get() == 2:
            modes = data.mode()
            for column in data.columns:
                data[column].fillna(modes[column][0], inplace=True)
            state.config(text = "NaN to Most Frequent. Select columns to remove whitespaces." )
        button1.config(state="disabled")
#        button0.config(state="disabled")
        button2.focus()
    
    # Prepare intereface to remove whitespaces from columns if all the values can be numeric
        c=0
        first = True
        for column in data.columns:
            if data[column].dtypes in ["object"]:
                change = True
                for i in range (0,len(data)):
                    if (re.match(r"[-+]?\d+(\.\d+)?$", str(data[column][i]).strip()) is None):
                        if (not pd.isnull(data[column][i]) and data[column][i].strip() != ''):
                            change = False
                if change:
                    if first:
                        a = tk.Label(win_root, text="Do you want to remove whitespaces from numeric columns?")
                        a.grid(row=4, column=0, sticky=tk.W, columnspan=2)
                        first=False
                    a = tk.Label(win_root, text=column)
                    a.grid(row=5+c, column=0, sticky=tk.E)
                    enval = tk.StringVar()
                    en1 = tk.Radiobutton(win_root, text="Yes", variable = enval, value=column)
                    en2 = tk.Radiobutton(win_root, text="No", variable = enval, value="_NO_")
                    en1.grid(row=5+c, column = 1, sticky=tk.W)
                    en2.grid(row=5+c, column = 1)
                    en1.deselect()
                    en2.select()
                    entriesval.append(enval)
            c += 1
        button2.grid(row=4+c, column=2, sticky=tk.W)
    
    
    def cleanspaces():
        global data
        global c2
        
        button2.config(state="disabled")
        button3.focus()
        mess = "Whitespaces removed from: "
        for entry in entriesval:
            e = entry.get()
            if (e != "_NO_"):
    # If the value is a set of whitespaces, they are replaced by 0, otherwise
    # whitespaces are deleted and finally the column type is changed to numeric
                data[e].replace(r"^\s+$", '0', regex=True, inplace=True)
                data[e].replace(r"\s+", '', regex=True, inplace=True)
                data[e] = pd.to_numeric(data[e], errors='coerce')
                mess += str(entry.get() + ", ")
        mess = mess[:-2] + ". What about outliers?"
        state.config(text = mess )
    
    # Prepares interface to process outliers. Calculates possible values to sustitute outliers
        datadict = {}
        c2=0
        first = True
        for column in data.columns:
            if data[column].dtypes in ["int64", "float64"]:
                max = np.max(data[column])        
                p75 = data[column].quantile(0.75)
                p50 = data[column].quantile(0.5)
                p25 = data[column].quantile(0.25)
                min = np.min(data[column])        
                mean = data[column].mean()
                iqr = p75 - p25
                valueslist = [p25-1.5*iqr, min, p25, p50, mean, p75, max, p75 + 1.5*iqr]
                tagslist = ["LOWER", "MIN", "P25", "P50", "Mean", "P75", "MAX", "UPPER"]
                datadict.update({column : pd.Series([data[column].dtypes]+valueslist, index=["Type"]+tagslist)})
    # If it is binary don't detect outliers
                if (set(data[column]) == {0,1}):
                    continue
    # Loops the values in a column looking for extreme values
    # When it finds extreme values prepares the interface to sustitute them, offering several choices
                for i in range (0,len(data)):
                    if (data[column][i] > (p75 + 1.5*iqr)) or (data[column][i] < (p25 - 1.5*iqr)):
                        if first:
                            a = tk.Label(win_root, text="How do you want to process outliers?")
                            a.grid(row=5+c, column=0, columnspan=2, sticky=tk.W)
                            first=False
                        a = tk.Label(win_root, text=column + ": " + str(data[column][i]))
                        a.grid(row=6+c+c2, column=0, sticky=tk.E)
                        choice = tk.StringVar()
                        chosen = ttk.Combobox(win_root, width=12, textvariable=choice, value=column, state="readonly")
    # There is a choice "ITSELF" if this outlier is not desired to be changed
                        chosenlist = ["ITSELF: " + str(data[column][i])]
                        for j in range (0,len(tagslist)):
                            chosenlist.append(tagslist[j] + ": " + str(valueslist[j]))
                        chosen['values']= tuple(chosenlist)
                        chosen.grid(row=6+c+c2, column=1)
                        c2 += 1
                        chosen.current(0)
                        choices.append([column, i, choice])
        button3.grid(row=7+c+c2, column=2, sticky=tk.W)
    
    def processoutliers():
        global data
        
        mess = "\nOutliers replaced:\n"
    # Changes outliers for the selected values
        for choice in choices:
            col = choice[0]
            i = choice[1]
            ch = choice[2].get().split()[1]
            data.set_value(i, col, ch)
            mess += "- " + col + "[" + str(i) + "] -> " +str(ch) + "\n"
        mess = mess + "New changes can be proposed.\n"
        mess = mess + "Click 'Save Results' after.\n"
        mess = mess + "Thank you for using this program!!!"
        state.config(text = mess )
        print("Transformed Data Frame\n", data)
    #    print(data.dtypes)
        button4=tk.Button(win_root,text="Save Restults",command=lambda: save_file())
        button4.grid(row=8+c+c2, column=1, sticky=tk.W)
        button5=tk.Button(win_root,text="Exit",command=lambda: root.destroy())
        button5.grid(row=8+c+c2, column=1, sticky=tk.E)
        button4.focus()
    
    
    def onFrameConfigure(canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    
    # START MAIN
    np.seterr(invalid='ignore')
    entriesval = []
    choices = []
#    data = pd.DataFrame
    
    # Creates main window
    root = tk.Tk()
    root.title("Data Cleaning")
    root.geometry("600x800")
    root.resizable(width=True, height=True)
    canvas = tk.Canvas(root, borderwidth=0) #, background="#ffffff")
    win_root = tk.Frame(canvas) #, background="#ffffff")
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    vsb.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4,4), window=win_root, anchor="nw")
    win_root.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    
    label1 = ttk.Label(win_root, text="- Human Assisted Cleaner -\n",font=("Helvetica", 12), foreground="black")
    label1.grid(row=0,column=1)
#    
#    id_entry = tk.StringVar()
#    id_entered = ttk.Entry(win_root, width = 30, textvariable = id_entry)
#    id_entered.grid(row = 0, column = 1, sticky = tk.E)
    
#    button0 = tk.Button(win_root, text = "Browse computer")
#    button0.bind ("<Button-1>", start)
#    button0.grid(row=0, column=2, sticky=tk.W)
#    button0.focus()
    button1 = tk.Button(win_root,text = "Go", command=lambda: cleannan())
    button2 = tk.Button(win_root,text = "Go", command=lambda: cleanspaces())
    button3 = tk.Button(win_root,text = "Go", command=lambda: processoutliers())
    
    nanrad = tk.IntVar()
    
    state = ttk.Label(win_root, text="\nPlease, press \"Browse computer\" to select a file to clean.")
    state.grid(row=1000, column=0, columnspan=3, sticky=tk.W)
    
    start()
    root.mainloop()






########################################
#L H6 Human assisted feature selection
########################################






#     data = pd.read_csv("Example.csv")
def HAfeatureselection ():
    import pandas as pd
    import numpy as np
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from sklearn import linear_model
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    def open_file():
        filename = filedialog.askopenfilename(
        title = "Choose your file",
        filetypes = (("csv files", "*.csv"), ("all files", "*.*")),
        defaultextension = '.csv',
        initialdir = '.')
        return filename
    
    
    def save_file():
        filename = filedialog.asksaveasfilename(
        title = "Save file",
        filetypes = (("csv files", "*.csv"), ("all files", "*.*")),
        defaultextension = '.csv',
        initialdir = '.',
        initialfile = 'transformed.csv')
        if filename != "":
            data.to_csv(filename, index=False)
    
    
    def start():
    #    global data
        global c
    #    fich = open_file()
    #    id_entry.set (fich)
    #    data = pd.read_csv (fich)
    #    state.config(text = "" )
    
    
    #    a = tk.Label(win_root, text="Select the features you want to include:")
    #    a.grid(row=1, column=0, sticky=tk.W, columnspan=2)
        c=0
        
# Usually the target variable is the last column, then it is not offered as a choice
        for column in data.columns[:-1]:
#            a = tk.Label(win_root, text=column)
#            a.grid(row=2+c, column=0, sticky=tk.E)
            enval = tk.StringVar()
            en = tk.Checkbutton(win_root, text=column, variable = enval, textvariable = column)
            en.grid(row=2+c, column = 0, sticky=tk.W)
            en.deselect()
            entriesval.append(enval)
            c += 1
        button1.grid(row=2+c, column=0, sticky=tk.W)
        button1.focus()
    
    
    
    def checkselected():
        global data
        global c
        checked_fields = []
        count = 0
        cols = list(data.columns)
        for entry in entriesval:
            e = entry.get()
            if e=="1":
                checked_fields.append(cols[count])
            count += 1
        button5=tk.Button(win_root,text="Exit",command=lambda: root.destroy())
        button5.grid(row=2+c, column=1, sticky=tk.W)
    #    button4.focus()
        
        x = data[checked_fields]
        y = data['ob_target']
        
        Fin_model = linear_model.LinearRegression()
        Fin_model.fit(x, y)
        sw_fin = Fin_model.score(x,y)
        a = tk.Label(win_root, text="Using the variables you selected, the model score is "+str(sw_fin))
        a.grid(row=4+c, column=0, columnspan = 3, sticky=tk.W)
        state.config(text = "Select new variables to optimise your model, press Go to re-score" )
    
    
    def onFrameConfigure(canvas):
        import pandas as pd
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))
    
        # START MAIN
    np.seterr(invalid='ignore')
    entriesval = []
#    choices = []
    data = pd.DataFrame
    c = 0
    # Creates main window
    root = tk.Tk()
    root.title("Feature Selection")
    root.geometry("600x800")
    root.resizable(width=True, height=True)
    canvas = tk.Canvas(root, borderwidth=0) #, background="#ffffff")
    win_root = tk.Frame(canvas) #, background="#ffffff")
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    vsb.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4,4), window=win_root, anchor="nw")
    win_root.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    
    label1 = ttk.Label(win_root, text="Choose features to test:",font=("Helvetica", 12), foreground="black")
    label1.grid(row=0,column=0)
    
#    id_entry = tk.StringVar()
#    id_entered = ttk.Entry(win_root, width = 30, textvariable = id_entry)
#    id_entered.grid(row = 0, column = 1, sticky = tk.E)
    
    #button0 = tk.Button(win_root, text = "Browse computer", command=lambda: start())
    #button0.bind ("<Button-1>")
    #button0.grid(row=0, column=2, sticky=tk.W)
    #button0.focus()
    button1 = tk.Button(win_root,text = "Go", command=lambda: checkselected())
    
    #    state = ttk.Label(win_root, text="\nPlease, press \"Browse computer\" to select a file to clean.")
    state = ttk.Label(win_root, text="")
    state.grid(row=1000, column=0, columnspan=3, sticky=tk.W)
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv") 
    start()
    #def human_variable_selection(data):
    root.mainloop()
    
data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv") 



########################################
#A Genetic algorithm
########################################







def ga():
    import pandas as pd
    import numpy as np
    import re
    import deap
    from deap import creator, base, tools, algorithms 
    import random
    from sklearn import metrics, linear_model
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    #df = pd.read_csv("dev.csv") #DEV-SAMPLE
    #dfo = pd.read_csv("oot0.csv")#OUT-OF-TIME SAMPLE
    #df = pd.read_csv("/home/ab/Documents/MBD/financial_analytics/variable_creation/data/data.csv")
    #len(df.columns)
    
    in_model = []
    list_ib = set()  #input binary
    list_icn = set() #input categorical nominal
    list_ico = set() #input categorical ordinal
    list_if = set()  #input numerical continuos (input float)
    list_inputs = set()
    output_var = 'ob_target'
    
    for var_name in data.columns:
        if re.search('^ib_',var_name):
            list_inputs.add(var_name)      
            list_ib.add(var_name)
        elif re.search('^icn_',var_name):
            list_inputs.add(var_name)      
            list_icn.add(var_name)
        elif re.search('^ico_',var_name):
            list_inputs.add(var_name)      
            list_ico.add(var_name)
        elif re.search('^if_',var_name):
            list_inputs.add(var_name)      
            list_if.add(var_name)
        elif re.search('^ob_',var_name):
            output_var = var_name
    
    #####
    #SETING UP THE GENETIC ALGORITHM and CALCULATING STARTING POOL (STARTING CANDIDATE POPULATION)
    #####
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(list_inputs))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    def evalOneMax(individual):
        return sum(individual),
    
    toolbox.register("evaluate", evalOneMax)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    NPOPSIZE = (len(data.columns) -2) #RANDOM STARTING POOL SIZE
    population = toolbox.population(n=NPOPSIZE)
    
    #####
    #ASSESSING GINI ON THE STARTING POOL
    #####
    dic_gini={}
    for i in range(np.shape(population)[0]): 
    
        # TRASLATING DNA INTO LIST OF VARIABLES (1-81)
        var_model = []    
        for j in range(np.shape(population)[0]): 
            if (population[i])[j]==1:
                var_model.append(list(list_inputs)[j])
    
        # ASSESSING GINI INDEX FOR EACH INVIVIDUAL IN THE INITIAL POOL 
                
        X_train=data[var_model]
        Y_train=data[output_var]
    
        ######
        # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             
        '''        
        rf = RandomForestClassifier(n_estimators=100, random_state=50)                
        rf1 = rf.fit(X_train, Y_train)
        Y_predict = rf1.predict_proba(X_train)
        Y_predict  = Y_predict[:,1]
        '''
        Fin_model = linear_model.LinearRegression()
        Fin_model.fit(X_train, Y_train)
        Y_predict = Fin_model.predict(X_train)
        ######
        # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             
    
    
        ######
        # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
        #####                
        fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
        auc = metrics.auc(fpr, tpr)
        gini_power = abs(2*auc-1)
        ######
        # CHANGE_HERE - END: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
        #####                
        
        gini=str(gini_power)+";"+str(population[j]).replace('[','').replace(', ','').replace(']','')
        dic_gini[gini]=population[j]
    
    list_gini=sorted(dic_gini.keys(),reverse=True)
    
    
    
    #####
    #GENETIC ALGORITHM MAIN LOOP - START
    # - ITERATING MANY TIMES UNTIL NO IMPROVMENT HAPPENS IN ORDER TO FIND THE OPTIMAL SET OF CHARACTERISTICS (VARIABLES)
    #####
    sum_current_gini=0.0
    sum_current_gini_1=0.0
    sum_current_gini_2=0.0
    first=0    
    OK = 1
    a=0
    while OK:  #REPEAT UNTIL IT DO NOT IMPROVE, AT LEAST A LITLE, THE GINI IN 2 GENERATIONS
        a=a+1
        OK=0
    
        ####
        # GENERATING OFFSPRING - START
        ####
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1) #CROSS-X PROBABILITY = 50%, MUTATION PROBABILITY=10%
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population =toolbox.select(offspring, k=len(population))
        ####
        # GENERATING OFFSPRING - END
        ####
    
        sum_current_gini_2=sum_current_gini_1
        sum_current_gini_1=sum_current_gini
        sum_current_gini=0.0
    
        #####
        #ASSESSING GINI ON THE OFFSPRING - START
        #####
        for j in range(np.shape(population)[0]): 
            if population[j] not in dic_gini.values(): 
                var_model = [] 
                for i in range(np.shape(population)[0]): 
                    if (population[j])[i]==1:
                        var_model.append(list(list_inputs)[i])
                X_train=data[var_model]
                Y_train=data[output_var]
                
                ######
                # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####         
                Fin_model = linear_model.LinearRegression()
                Fin_model.fit(X_train, Y_train)
                Y_predict = Fin_model.predict(X_train)
                '''                
                rf = RandomForestClassifier(n_estimators=100, random_state=50)                
                rf1 = rf.fit(X_train, Y_train)
                Y_predict = rf1.predict_proba(X_train)
                Y_predict  = Y_predict[:,1]
                '''
                ######
                # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####            
                           
                
                ######
                # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
                #####                       
                fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
                auc = metrics.auc(fpr, tpr)
                gini_power = abs(2*auc-1)
                ######
                # CHANGE_HERE - END: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
                #####                       
               
                gini=str(gini_power)+";"+str(population[j]).replace('[','').replace(', ','').replace(']','')
                dic_gini[gini]=population[j]  
        #####
        #ASSESSING GINI ON THE OFFSPRING - END
        #####
    
        #####
        #SELECTING THE BEST FITTED AMONG ALL EVER CREATED POPULATION AND CURRENT OFFSPRING - START
        #####           
        list_gini=sorted(dic_gini.keys(),reverse=True)
        population=[]
        for i in list_gini[:NPOPSIZE]:
            population.append(dic_gini[i])
            gini=float(i.split(';')[0])
            sum_current_gini+=gini
        #####
        #SELECTING THE BEST FITTED AMONG ALL EVER CREATED POPULATION AND CURRENT OFFSPRING - END
        #####           
          
        #HAS IT IMPROVED AT LEAST A LITLE THE GINI IN THE LAST 2 GENERATIONS
        #print ('sum_current_gini=', sum_current_gini, 'sum_current_gini_1=', sum_current_gini_1, 'sum_current_gini_2=', sum_current_gini_2)
        if(sum_current_gini>sum_current_gini_1+0.0001 or sum_current_gini>sum_current_gini_2+0.0001):
            OK=1
    #####
    #GENETIC ALGORITHM MAIN LOOP - END
    #####
    
    
    gini_max=list_gini[0]        
    gini=float(gini_max.split(';')[0])
    features=gini_max.split(';')[1]
    
    ####
    # PRINTING OUT THE LIST OF FEATURES
    #####
    
    use_these = []
    f=0
    for i in range(len(features)):
        if features[i]=='1':
            f+=1
            use_these.append(list(list_inputs)[i])

    X = data[use_these]
    Y = data[output_var]
    Fin_model = linear_model.LinearRegression()
    Fin_model.fit(X, Y)
    Y_predict = Fin_model.predict(X)
    cv_score = Fin_model.score(X, Y)

    '''    
    rf = RandomForestClassifier(n_estimators=100, random_state=50)                
    rf1 = rf.fit(X, Y)
    Y_predict = rf1.predict_proba(X)
    Y_predict  = Y_predict[:,1]
    
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.2, random_state=10)    
    rfcv = Fin_model.fit(X_train, y_train)
    '''
    print("Genetic Algorithm Score", cv_score)
    print("Using", use_these) 
    return(cv_score)

# -*- coding: utf-8 -*-


def sw():
    from sklearn import linear_model,metrics
    import numpy as np
    import pandas as pd
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")

    
    
    def xattrSelect(x, idxset):
        """ Takes X matrix as list of list and returns subset containing columns in idxSet """
        xout = []
        for row in x:
            xout.append([row[i] for i in idxset])
        return xout
    
    
    #Read the data in: choose the first FA dataset OR the second FA dataset

    xLists = []
    labels = []
    names = pd.Series(data.columns) 
    firstline = True
    
    for line in data.values:
        row = list(line)
        # Populate labels list 
        labels.append(row[-1])
        # Remove headers
        row.pop()
        # Ensure everything is a float
        floatrow = [float(s) for s in row]
        xLists.append(floatrow)
    
    #Training and test data sets
    indices = range(len(xLists))
    
    xListtrain = [xLists[i] for i in indices if i % 3 != 0]
    xListtest = [xLists[i] for i in indices if i % 3 == 0]
    labeltest = [labels[i] for i in indices if i % 3 == 0]
    labeltrain = [labels[i] for i in indices if i % 3 != 0]
    
    #Stepwise Regression
    attributeList = []
    index = range(len(xLists[1])) 
    indexSet = set(index)
    indexSeq = []
    oosError = []
    
    for i in index:
        attSet = set(attributeList)
        # attributes not currently included
        attTryset = indexSet - attSet
        # form into list
        attTry = [o for o in attTryset]
        errorList = []
        attTemp = []
        # experiment with each feature 
        # select features with least oos error
        for j in attTry:
            attTemp = [] + attributeList
            attTemp.append(j)
    
            #Form training and testing sub matrixes lists of lists
            xTraintemp = xattrSelect(xListtrain, attTemp)
            xTesttemp = xattrSelect(xListtest, attTemp)
    
            #Convert into arrays because that is all the scikit learnregression can accept
            xTrain = np.array(xTraintemp)
            yTrain = np.array(labeltrain)
            xTest = np.array(xTesttemp)
            yTest = np.array(labeltest)
    
            # use scikitlearn linear regression
            Fin_model = linear_model.LinearRegression()
            Fin_model.fit(xTrain, yTrain)
            a = Fin_model.predict(xTrain)
            
            fpr, tpr, thresholds = metrics.roc_curve(yTrain, a)
            auc = metrics.auc(fpr, tpr)
            gini_power = abs(2*auc-1)
            errorList.append(gini_power)
            
    
            # Use trained model to generate prediction and calculate rmsError
            '''rmsError = np.linalg.norm((yTest - Fin_model.predict(xTest)), 2) / math.sqrt(len(yTest))
            errorList.append(rmsError)
            attTemp = []
            '''
        iBest = np.argmin(errorList)
        attributeList.append(attTry[iBest])
        oosError.append(errorList[iBest])
    
    #If you want the sample error 
    #print("Out of sample error versus attribute set size" )
    #print(oosError)
    
    #If you want the indices of the most useful attributes
    #print("\n" + "Best attribute indices")
    #print(attributeList)
    
    namesList = [names[i] for i in attributeList]
    
    x = data[namesList]
    y = data['ob_target']
    
    Fin_model = linear_model.LinearRegression()
    Fin_model.fit(x, y)
    sw_fin = Fin_model.score(x,y)
    print("Step Wise Score", sw_fin)
    print("Using", namesList)    
    return(sw_fin)


def compare_stepwise_genetic():
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")

    ga()
    sw()

####################
#V dummi creation
####################
def dummycreation ():
    import pandas as pd
    import numpy as np
    import re
    from deap import creator, base, tools, algorithms 
    import random
    from sklearn import metrics, linear_model
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    in_model = []
    list_ib = set()  #input binary
    list_icn = set() #input categorical nominal
    list_ico = set() #input categorical ordinal
    list_if = set()  #input numerical continuos (input float)
    list_inputs = set()
    output_var = 'ob_target'
    
    for var_name in data.columns:
        if re.search('^ib_',var_name):
            list_inputs.add(var_name)      
            list_ib.add(var_name)
        elif re.search('^icn_',var_name):
            list_inputs.add(var_name)      
            list_icn.add(var_name)
        elif re.search('^ico_',var_name):
            list_inputs.add(var_name)      
            list_ico.add(var_name)
        elif re.search('^if_',var_name):
            list_inputs.add(var_name)      
            list_if.add(var_name)
        elif re.search('^ob_',var_name):
            output_var = var_name

    data_num = data.select_dtypes(include=[np.float])
    data_int = data.select_dtypes(include=[np.int])
    data_string = list(data.select_dtypes(include=[np.object]))
    data_string = pd.get_dummies(data[data_string])
    datatemp= [data,data_string]
    compData = pd.concat(datatemp, axis=1)
    return compData
    
####################
#V bins creation
####################
def bincreation ():
    import pandas as pd
    import numpy as np
    import re
    from deap import creator, base, tools, algorithms 
    import random
    from sklearn import metrics, linear_model
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv")
    bins = [-1.,   0.,   1., 2.,3.]
    group_names = ['1', '2', '3', '4']
    for i in range(len(data.columns)-1,0,-1):
        if data.iloc[:,i].min()!=0 and data.iloc[:,i].max()!=1:
        
            data[i] = pd.cut(data.iloc[:,i], bins, labels=group_names)
    return data


