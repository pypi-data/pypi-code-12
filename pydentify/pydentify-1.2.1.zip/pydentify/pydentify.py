#try:
from lxml import etree 
#except ImportError:
#    'The lxml module is required. Use \'pip install lxml\' at command line with admin rights if you have pip. If you do not have pip, install pip'

#try:
#    import argparse
#except ImportError:
#        'The argparse module is required. Use \'pip install argparse\' at command line with admin rights if you have pip. If you do not have pip, install pip'

#import argparse
import os
import shutil
import re
import glob
import pandas
import scipy,scipy.stats
from scipy.interpolate import interp1d
import numpy
import matplotlib.pyplot as plt
import subprocess
import math
from textwrap import wrap
import insert_copasi_parameters
import matplotlib
'''

Author: Ciaran Welsh. Email: c.welsh2@newcastle.ac.uk.

    
Before using this script to perform Identifiability analysis 
in Copasi, as described by Jorg Schabber, you must first define an
appropriate CopasiML using the GUI. 

Ensure you have done the following:
	1) Ensure the parent .cps file is located in the SAME directory as the data files used for parameterization and that no other text files are present in this directory. Its best to have a dedicated folder for your identifiability analysis.
	2) Perform parameter estimation to locate the global minimum and update model. Alternatively you can use the repeat feature in COPASI's scan task to perform multiple parameter estimations and have the results written to a report. The latter procedure is best accomplished using a computer cluster. 
	3) Create a new report from COPASI's 'output specifications' window that contains any, but only one estimated parameter and the RSS value. The latter can be found by checking the 'expert mode' button and then going to: 'ModelList>Root>TaskList>ParameterEstimation>ParameterEstimation>BestValue'.
	4) Ensure you are using Hook and Jeeves for all secondary parameter estimations. 
	5) Create a scan in the parameter scan subtask with any estimated parameter:
	6) Change the scan subtask to parameter estimation
	7) Check the 'Log' checkbox to scan on a log scale
	8) Check the executable box  in the top right hand corner of the scan window
	9) Define a report using the 'ProfileLikelihood' report that was previously defined. Name it anything and uncheck the 'append' and 'confirm overwrite' buttons. 
	10) Delete any other reports that you have defined in other subtasks
	11) Delete any parameter sets or events that you have defined
	12) Ensure the time, volume and quantity units are properly defined as they are used in some calculations with Avogadro's constant.

Then use: 

    PL=ProfileLikelihood(<copasi_file>)
    PL.run(mode='slow')
    
    <copasi_file> : absolute path to your configured copasi file
or:
    MLP=MultiProfileLikelihoods(<copasi_file>,[index],results_dir=<results_directory>)
    
    [index] : python list for index of parameter estimation runs you want to calcualte profile likelihoods for
    results_dir: absolute path to a directory containing parameter estimation output from copasi
    results_file:   absolute path to file containing patameter estimation data
Which depends on the module 'InsertCopasiParameters' provided with pydentify.py. 
More infromation about the model is found in the documentation. 

#Note that for some reason this program will not run from a Dropbox (or similar) directory
    
#Also, if you have to stop running the script half way through and attempt to restart, 
you'll be better off starting again from a new directory or deleting the IA file 
before restarting the program


To visualize results:

If using pydentify.ProfileLikelihood():
    
    P=pydentify.Plot(copasi_file,RSS_i)
        copasi_file: an appropiately configured copasi file
        RSS_i:      the RSS value for the original parameter estimation 
    P.plot_all(savefig=True)
    
If using pydentify.MultiProfileLikelihood():

    MP=pydentify.MultiPlot(copasi_file,results_dir=<results_directory>)
    
    OR
    
    MP=pydentify.MultiPlot(copasi_file, results_file=<results_file>)
    
    where:
        copasi_file:  an appropiately configured copasi file
        results_dir:  full path to a results directory (containing multi files of parmaeter estimation data in txt format, such as the output from copasi parameter estimation)
        results_file: full path to a results file containing parameter estimation data (xlsx/xls/csv/txt)
        
    Then 
    MP.plot_index(0,savefig=True) #to plot index 0 of your multi profile likelihood
    or 
    MP.plot_all_indexes(savefig=True,multiplot=False) ' #to plot all indexes 
    MP.plot_all_indexes(savefig=True,multiplot=True)   #to plot all profiles on the same graph for comparison. Resutls are viewed in the largest index folder as this is an iterative process


'''
    
class InputError(Exception):
    pass
          
class Initialize(object):
    '''
    This class's purpose is to initiate the program. It sets up inheritance for other
    classes and accepts user defined parameters for passing on to appropiate classes
    
    copasi_file:    an appropiatly configured copasi file. 
    
    User has no interaction with this class
    '''
    def __init__(self,copasi_file):
        self.copasi_file=copasi_file #The copasi file to perform IA on
        '''
        The below attributes accept a copasi file as input. 
        This is more useful than automatically deriving which file
        to use so it can be reused later in Setup()
        '''
        self.copasiML=self._parse_copasiML(self.copasi_file)
        self.model_name=self._get_model_name(self.copasi_file)
        self.quantity_unit=self._get_quantity_units(self.copasi_file)
        self.vol_unit=self._get_volume_unit(self.copasi_file)
        self.time_unit=self._get_time_unit(self.copasi_file)
        
        '''
        Some directory based attributes
        '''
        self.IA_dir=self._create_directory()  #results directory/IA dir
        
        self.data_files=self._copy_data_files() #data files
        self.child_copasi_files=self._get_copasi_child_files() #copasi files in the IA dir
        '''
        Note: you need to copy the copasi files into the newly created directory in a 
        separate line of code to prevent creation of an infinite loop 
        '''
        self.debug()
        
    def debug(self):
        assert os.path.isfile(self.copasi_file),'{} does not exist'.format(self.copasi_file)
        assert self.copasi_file[-4:]=='.cps','Ensure {} is a valid copasi file'.format(self.copasi_file)
        assert self.data_files!=None,'Have you put the data files in the same directory as your .cps file?'
        
    def _get_copasi_child_files(self):
        '''
        returns a list of filenames pointing to the 'child' copasi files (in self.IA_dir)
        '''
        os.chdir(self.IA_dir)
        cps=[]
        for i in glob.glob('*.cps'):
            cps.append(os.path.join(self.IA_dir,i))
        return cps
        
    def _parse_copasiML(self,copasi_file):
        with open(copasi_file) as f:
            copasiML_str=f.read()
        return etree.fromstring(copasiML_str)
        
    def _get_quantity_units(self,copasi_file):
        '''
        Get model quantity units (nM for example)
        '''
        query="//*[@avogadroConstant]"
        for i in self.copasiML.xpath(query):
            quantity_unit= i.attrib['quantityUnit']
        return quantity_unit
        
    def _get_volume_unit(self,copasi_file):
        '''
        get model volume units. ml for example
        '''
        query="//*[@avogadroConstant]"
        for i in self.copasiML.xpath(query):
            vol_unit= i.attrib['volumeUnit']
        return vol_unit
        
    def _get_time_unit(self,copasi_file):
        query="//*[@avogadroConstant]"
        for i in self.copasiML.xpath(query):
            time_unit= i.attrib['timeUnit']
        return time_unit
        
    def _get_model_name(self,copasi_file):
        query="//*[@avogadroConstant]"
        for i in self.copasiML.xpath(query):
            name= i.attrib['name']
        return name

    def convert_particles_to_molar(self,particles,mol_unit,vol_unit):
        '''
        Converts particle numbers to Molarity. 
        particles=number of particles you want to convert
        mol_unit=one of, 'fmol, pmol, nmol, umol, mmol or mol'
        vol_unit= one of 'l,ml,um,nl,pl,fl'
        '''
        type(particles)
        mol_dct={
            'fmol':1e-15,
            'pmol':1e-12,
            'nmol':1e-9,
            'umol':1e-6,
            'mmol':1e-3,
            'mol':float(1),
            'dimensionless':1,
            '#':1}
        vol_dct={
            'l':float(1),
            'ml':1e-3,
            'ul':1e-6,
            'nl':1e-9,
            'pl':1e-12,
            'fl':1e-15,
            'dimensionless':1}
        mol_unit_value=mol_dct[mol_unit]
        vol_unit_value=vol_dct[vol_unit]
        avagadro=6.02214179e+023
        molarity=float(particles)/(mol_unit_value/vol_unit_value*avagadro)
        if mol_unit=='dimensionless':
            molarity=particles
        if mol_unit=='#':
            molarity=particles
        return molarity    
    
    def write_copasi_file(self,copasi_filename,copasiML):
        '''
        Often you need to delete a copasi file and rewrite it
        directly from the string. This function does this.
        
        copasi_filename = a valid .cps file
        copasiML = an xml string. Convert to xml string
        before using this function using etree.fromstring(xml_string)
        '''
        os.remove(copasi_filename)
        with open(copasi_filename,'w') as f:
            f.write(etree.tostring(copasiML))
            
    def _create_directory(self):
        '''
        Creates a new directory for IA results if it does not already exist. 
        
        Returns the path to the results directory
        '''

        copasi_file_dir = os.path.dirname(self.copasi_file)
        os.chdir(copasi_file_dir)
        IA_dir_name=os.path.split(self.copasi_file)[-1][:-4]+'_PL'
        if not os.path.isdir(IA_dir_name):
            os.mkdir(os.path.join(copasi_file_dir,IA_dir_name))
            
#        self.copy_copasi_file()
        return os.path.join(copasi_file_dir,IA_dir_name)

    def copy_copasi_file(self):
        '''
        use create_directory to create a IA_results folder: one for each estimated parameter
        returns filenames 
        '''
        #first retreive the estimated parameters
        GEP=GetEstimatedParameters(self.copasi_file)
        global_parameters=GEP.globals
        local_parameters=GEP.locals
        ICs=GEP.ICs
        #collate estimated parameter names as filenames and copy
        filenames= global_parameters.keys()+local_parameters.keys()+ICs.keys()
        os.chdir(self.IA_dir)
        for i in filenames:
            shutil.copy(self.copasi_file,i+'.cps')
        os.chdir('..')
        return filenames

    def _copy_data_files(self):
        os.chdir(os.path.dirname(self.copasi_file))
        data_files=[]
        for i in glob.glob('*.txt'):
            path,fle= os.path.split(self.IA_dir)
            shutil.copy( os.path.join(os.getcwd(),i),self.IA_dir)
            data_files.append(os.path.join(self.IA_dir,i))
        return data_files            
#==============================================================================
            
class GetEstimatedParameters(Initialize):
    '''
    Class for getting estimated parameters from the copasi parameter estimation task
    
    Use:
    GetEstimatedParameters(<copasi_file>).globals
    GetEstimatedParameters(<copasi_file>).locals
    GetEstimatedParameters(<copasi_file>).ICs
        
    For retrieving global, local or initial concentrations respectively from the 
    copasi parameter estimation subtask. 
    
    Again, user doesn't really need to touch this class
    '''
    def __init__(self,copasi_file):
        super(GetEstimatedParameters,self).__init__(copasi_file)
        self.globals=self.get_estimated_globals()
        self.locals=self.get_estimated_locals()
        self.ICs=self.get_estimated_ICs()
        self.compartments=self.get_ICs_compartments()
        self.all_params=dict(self.globals.items()+self.locals.items()+self.ICs.items())
        
    def get_estimated_globals(self):
        '''
        Gets the subset of global variables defined in the estimtion task
        returns python dict name:value pairs        
        '''
        query="//*[@name='FitItem']"
        names=[]        
        global_dct={}
        pattern=re.compile('Values\[(.*)\],Reference=InitialValue')
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                if j.attrib['name']=='ObjectCN':
                    if re.search(pattern,j.attrib['value']):
                        names.append(re.findall(pattern, j.attrib['value']))
                        for k in j.getparent():
                            if k.attrib['name']=='StartValue':
                                name =re.findall(pattern, j.attrib['value'])[0]
                                global_dct[name]=k.attrib['value']
        return global_dct


    def get_estimated_locals(self):
        '''
        Gets the subset of local variables defined in the estimtion task. 
        returns python dict name:value pairs
        '''
        local_estimated_parameters={}
        query="//*[@name='FitItem']"
        pattern=re.compile('CN=Root,Model=.*,\
Vector=Reactions\[(.*)\],\
ParameterGroup=Parameters,\
Parameter=(.*),Reference=Value')
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                if j.attrib['name']=='ObjectCN':
                    result= re.findall(pattern,j.attrib['value'])
                if j.attrib['name']=='StartValue':
                    value = j.attrib['value']
                    if result!=[]:
                        local_estimated_parameters['('+result[0][0]+').'+result[0][1]]=value
        return local_estimated_parameters

        
    def get_ICs_particle_numbers_nested_dct(self):
        '''
        CopasiML's store ICs only as particle numbers. 
        This function retrives the IC:value (As particle numbers) pairs as dict 
        '''
        query="//*[@cn='String=Initial Species Values']" #and "//*[@type='cn']"
        IC_dct={}
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                pattern=re.compile('CN=Root,Model=.*,Vector=Compartments\[(.*)\],Vector=Metabolites\[(.*)\]')
                species=re.findall(pattern,j.attrib['cn'])[0]
                IC_dct[species[1]]={}
                for key in IC_dct.keys():
                    IC_dct[species[1]][j.attrib['value']]=species[0]
        return IC_dct

    def get_ICs_compartments(self):
        '''
        dct of species:compartment name
        '''
        query="//*[@cn='String=Initial Species Values']" #and "//*[@type='cn']"
        compartment_dct={}
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                pattern=re.compile('CN=Root,Model=.*,Vector=Compartments\[(.*)\],Vector=Metabolites\[(.*)\]')
                search_results=re.findall(pattern,j.attrib['cn'])[0]
                compartment_dct[search_results[1]]=search_results[0]
        return compartment_dct
        
    def get_ICs_particle_numbers(self):
        '''
        CopasiML's store ICs only as particle numbers. 
        This function retrives the IC:value (As particle numbers) pairs as dict 
        '''
        query="//*[@cn='String=Initial Species Values']" #and "//*[@type='cn']"
        IC_dct={}
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                pattern=re.compile('CN=Root,Model=.*,Vector=Compartments\[.*\],Vector=Metabolites\[(.*)\]')
                species=re.findall(pattern,j.attrib['cn'])[0]
                IC_dct[species[1]]=float(j.attrib['value'])
        return IC_dct            
            
    def get_ICs_concentrations(self):
        '''
        Get IC's as concentrations, rather than particle numbers
        
        Returns  dict -> {Specie:conc:}
        '''
        IC_dct=self.get_ICs_particle_numbers() #get particle numbers
        conc_dct={}                    
        for key in IC_dct.keys():
            conc=self.convert_particles_to_molar(IC_dct[key],self.quantity_unit,self.vol_unit)
            conc_dct[key]=conc
        return conc_dct
            
    def get_ICs_concentrations_nested_dct(self):
        '''
        Get IC's as concentrations, rather than particle numbers
        
        Returns nested dict -> {Specie:{conc:compartment}}
        '''
        IC_dct=self.get_ICs_particle_numbers() #get particle numbers 
        conc_dct={}                    
        for key in IC_dct.keys():
            particles=IC_dct[key].keys()[0]
            compartment=IC_dct[key][particles]
            conc=self.convert_particles_to_molar(particles,self.quantity_unit,self.vol_unit)
            conc_dct[key]={}
            for i in conc_dct.keys():
                conc_dct[key][conc]=compartment
        return conc_dct

            
    def get_estimated_ICs_deprecated(self):
        '''
        Take a copasi file and return dictionary with keys being 
        species whos initial concnetations that are estimated and 
        values are the compartment to which that species belongs
        returns dct of the form:
            {specie:concentration}
        
        '''
        #look up 'FitItems' in CopasiML
        query="//*[@name='FitItem']" 
        #get initial concnetrations for all metabolites 
        IC_dct=self.get_ICs_concentrations()
        #define empty dict    
        estimated_ICs_dct={}
        #search for pattern in the xml    
        pattern=re.compile('CN=Root,Model=.*,\
    Vector=(.*),Reference=InitialValue')
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.attrib:
                    #exclude speies from kinetic ro global parameters
                    pattern=re.compile('Reference=InitialConcentration')
                    try:
                        if j.attrib['name']=='ObjectCN': #
                            if re.findall(pattern,j.attrib['value']):
                                pattern=re.compile('CN=Root,Model=.*,Vector=Compartments\[(.*)\],Vector=Metabolites\[(.*)\],Reference=InitialConcentration')#extract compartment and metabolite name of all metabolites currently present in the paramtere estimation task
                                ICs=re.findall(pattern,j.attrib['value'])[0]
                        estimated_ICs_dct[ICs[1]]=IC_dct[ICs[1]] #produce dict
                    except:
                        continue
        return estimated_ICs_dct


    def get_estimated_ICs(self):
        '''
        Gets the subset of global variables defined in the estimtion task
        returns python dict name:value pairs        
        '''
        query="//*[@name='FitItem']"
        names=[]        
        IC_dct={}
        pattern=re.compile('Vector=Metabolites\[(.*)\],Reference=InitialConcentration')
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                if j.attrib['name']=='ObjectCN':
                    if re.search(pattern,j.attrib['value']):
                        name= re.findall(pattern,j.attrib['value'])[0]
                        for k in j.getparent():
                            if k.attrib['name']=='StartValue':
                                IC_dct[name]=k.attrib['value']
        return IC_dct

#==============================================================================        


   
class Setup(object):
    '''
    Perform the setting up required for IA in copasi. 
    
    Takes a Copasi file as input. 
    
    Main method is setup_all(). User doesn't need to touch the rest. 
    '''
    def __init__(self,copasi_file,lb=int(4),ub=int(4),intervals=10,verbose=False):
        self.copasi_file=copasi_file
        self.lb=lb
        self.ub=ub
        self.intervals=intervals
        self.verbose=verbose
        assert isinstance(self.verbose,bool),'verbose must be true of false'
        self.I=Initialize(copasi_file)
        os.chdir(self.I.IA_dir)
        self.I.copy_copasi_file()
        self.child_copasi_files=self._get_child_copasi_files()
        self.GEP=GetEstimatedParameters(self.copasi_file)
#        self.setup_all() #had problems initializing this function. Just run it separately
        
    def _get_child_copasi_files(self):
        os.chdir(self.I.IA_dir)
        files=[]
        for i in glob.glob('*.cps'):
            files.append(os.path.join(self.I.IA_dir,i))
        return files


    def parse_copasiML(self,copasi_file):
        with open(copasi_file) as f:
            copasiML_str=f.read()
        return etree.fromstring(copasiML_str)
        
    def setup_PE(self,child_copasi_file):
        '''
        Takes a copasi file and parameter name as input. 
        Returns the copasi file with the parameter of interest
        removed from the parameter estiamtion task     
        
        Intended to be used by a later function on all files
        '''
        assert os.path.isfile(child_copasi_file), 'Make sure your child copasi file actually exists'
        p,parameter= os.path.split(child_copasi_file) #get path and file (latter is the parameter of interest)
        
        parameter= parameter[:-4] #remove '.cps'
        #some flow control
        local=False
        Global=False
        IC=False
        if parameter in self.GEP.locals:
            local=True
        elif parameter in self.GEP.globals:
            Global=True
        elif parameter in self.GEP.ICs:
            IC=True
            
            
        #parse child file
        child_copasiML= self.I._parse_copasiML(child_copasi_file)
        
        #Remove from estimation task if local paramteer
        if local:
            reaction_name= parameter.split('.')[0]
            parameter_name= parameter.split('.')[1]
            reaction_name=reaction_name[1:-1]
            query="//*[@name='FitItem']"                        
            for i in child_copasiML.xpath(query):
                for j in i.getchildren():
                    #try block??????
                    if j.attrib['name']=='ObjectCN':
                        pattern=re.compile('CN=Root,Model=.*,Vector=Reactions\['+reaction_name+'\],ParameterGroup=Parameters,Parameter='+parameter_name+',Reference=Value')
                        if re.findall(pattern,j.attrib['value']):
                            parent=j.getparent()
                            parent.getparent().remove(parent)
                            #except and continue
            self.I.write_copasi_file(child_copasi_file,child_copasiML)
            
        #remove from estimation task if global or IC
        if Global or IC:
            query="//*[@name='FitItem']"                        
            for i in child_copasiML.xpath(query):
                for j in i.getchildren():
                    if j.attrib['name']=='ObjectCN':
                        if parameter in j.attrib['value']:
                            if IC:
                                pattern=re.compile('Vector=Metabolites\[{}\]'.format(parameter))
                            if Global:
                                pattern=re.compile('Vector=Values\[{}\]'.format(parameter))
                            if re.findall(pattern,j.attrib['value']):
                                parent=j.getparent()
                                parent.getparent().remove(parent)
            self.I.write_copasi_file(child_copasi_file,child_copasiML)


    def setup_report(self,child_copasi_file):
        '''
        Takes a copasi file which must already have a 
        'ProfileLikelihood' report defined and changes the
        definition to include the parameter in the filename    
        '''
        assert os.path.isfile(child_copasi_file), 'Make sure your child copasi file actually exists'
        p,parameter= os.path.split(child_copasi_file) #get path and file (latter is the parameter of interest)
        
        parameter= parameter[:-4] #remove '.cps'
        #some flow control
        local=False
        Global=False
        IC=False
        if parameter in self.GEP.locals:
            local=True
        elif parameter in self.GEP.globals:
            Global=True
        elif parameter in self.GEP.ICs:
            IC=True

        #read copasiML and get model name
        child_copasiML=self.parse_copasiML(child_copasi_file)
        
        #if parameter is a local parameter 'replacement' takes on this value
        if local:
            reaction_name= parameter.split('.')[0]
            #print reaction_name
            parameter_name= parameter.split('.')[1]
            #print parameter_name
            reaction_name=reaction_name[1:-1] #remove brackets
            #print reaction_name
            replacement='CN=Root,Model={},Vector=Reactions[{}],ParameterGroup=Parameters,Parameter={},Reference=Value'.format(self.I.model_name,reaction_name,parameter_name)

        #if parameter is a global parameter 'replacement' takes on this value
        if Global:
            replacement='CN=Root,Model={},Vector=Values[{}],Reference=Value'.format(self.I.model_name,parameter)
            
        #if parameter is a species parameter 'replacement' takes on this value
        if IC:
            compartment= self.GEP.compartments[parameter]
            replacement='CN=Root,Model={},Vector=Compartments[{}],Vector=Metabolites[{}],Reference=InitialConcentration'.format(self.I.model_name,compartment,parameter)
            
        #replace the appropiate field with 'replacement'
        query="//*[@name='ProfileLikelihood']"   
        for i in child_copasiML.xpath(query):
            assert isinstance(i.attrib,etree._Attrib),'Make sure your report definition is called ProfileLikelihood'
            for j in i.getchildren():
                for k in j.getchildren():
                    if self.I.model_name in k.attrib['cn']: #need an assert statement here somewhere to ensure name == ProfileLikelihood'
                        k.attrib['cn']=replacement
            self.I.write_copasi_file(child_copasi_file,child_copasiML)
            
            
    def setup_scan(self,child_copasi_file):
        '''
        Doesn't use 'self' arguments for IA since two instances
        of the IA class need defining. One for the parent and 
        one for the child. This is the the other version 
        is depricated 
        '''
        assert os.path.isfile(child_copasi_file), 'Make sure your child copasi file actually exists'
        p,parameter= os.path.split(child_copasi_file) #get path and file (latter is the parameter of interest)
        
        parameter= parameter[:-4] #remove '.cps'
        #some flow control
        local=False
        Global=False
        IC=False
        if parameter in self.GEP.locals:
            local=True
        elif parameter in self.GEP.globals:
            Global=True
        elif parameter in self.GEP.ICs:
            IC=True
    
        #read copasiML 
        child_copasiML=self.I._parse_copasiML(child_copasi_file)
        
        if IC:
            compartment=self.GEP.compartments[parameter]
            
            start_value= self.GEP.ICs[parameter]
            assert start_value!=0,'''Starting value for this IC parameter is 0. 
            This means that it probably wasn\'t estimated during the original optimization. 
            If you really do want to perform profile likelihood calculations for this parameter, 
            my advice is to manually open the .cps file for the {} parameter and manually choose the 
            intervals that you want to calculate likelihood between'''

            mini=float(start_value)/float(self.lb)
            maxi=float(start_value)*float(self.ub)
            report_name=parameter+'.txt'
            replacement='CN=Root,Model={},Vector=Compartments[{}],Vector=Metabolites[{}],Reference=InitialConcentration'.format(self.I.model_name,compartment,parameter)
            if self.verbose==True:
                print 'Maximum Scan Value: \t{}'.format(maxi)
                print 'Minimum Scan Value: \t{}'.format(mini)
                print 'Compartment = \t{}'.format(compartment)
                print 'Model Value: \t{}'.format(start_value)
                print 'Output File=:\t{}\n\n'.format(report_name)
      
        if local:
            reaction_name= parameter.split('.')[0]
            parameter_name= parameter.split('.')[1]
            reaction_name=reaction_name[1:-1]
            replacement='CN=Root,Model={},Vector=Reactions[{}],ParameterGroup=Parameters,Parameter={},Reference=Value'.format(self.I.model_name,reaction_name,parameter_name)
            
        if Global:
            replacement='CN=Root,Model={},Vector=Values[{}],Reference=InitialValue'.format(self.I.model_name,parameter)
            
        if local==True or Global==True:
            start_value= self.GEP.all_params[parameter]
            mini=float(start_value)/float(self.lb)
            maxi=float(start_value)*float(self.ub)
            report_name=parameter+'.txt'
            if self.verbose==True:
                print 'Model Value: \t{}'.format(start_value)
                print 'Maximum Scan Value: \t{}'.format(maxi)
                print 'Minimum Scan Value: \t{}'.format(mini)
                print 'Output File=:\t{}\n\n'.format(report_name)
            
        #change report name
        query="//*[@name='Scan']" and "//*[@type='scan']"
        for i in child_copasiML.xpath(query):
            for j in i.getchildren():
                j.attrib['target']=report_name

        #change parameter name, min and maxi
        query="//*[@name='ScanItem']"
        for i in child_copasiML.xpath(query):
            for j in i.getchildren():
                if j.attrib['name']=='Object':
                    j.attrib['value']=replacement
                if j.attrib['name']=='Maximum':
                    j.attrib['value']=str(maxi)
                if j.attrib['name']=='Minimum':
                    j.attrib['value']=str(mini)
                if j.attrib['name']=='Number of steps':
                    if self.intervals%2==0:
                        self.intervals=self.intervals+1
                    j.attrib['value']=str(self.intervals)
        #save file
        self.I.write_copasi_file(child_copasi_file,child_copasiML)
        
    def setup_all(self):
        files= [t.replace('\\','\\') for t in self.child_copasi_files]
        for i in files:
            try:
                self.setup_PE(i)
            except:
                print 'setup_PE failed for {}'.format(i)
            try:
                self.setup_report(i)
            except:
                print 'setup_report failed for {}'.format(i)
            try:
                self.setup_scan(i)
            except:
                print 'setup_scan failed for {}'.format(i)


#======================================================================

        
class Run():
    '''
    Functions to run .CPS via CopasiSE
        
    '''
    def __init__(self,IA_dir):
        self.IA_dir=IA_dir
        os.chdir(self.IA_dir)
    
    def run1(self,copasi_filename):
        assert os.path.isfile(copasi_filename),'{} must be a real filename'.format(copasi_filename)
        os.system('CopasiSE {}'.format(copasi_filename))
    
    def copasiSE_batch_run(self):
        '''
        Run each file sequentially. This is slow but doesn't eat all your computer power. 
        '''
        os.chdir(self.IA_dir)
        count=0
        for i in glob.glob('*.cps'):
            os.system('CopasiSE "{}"'.format(i))
            count = count+1
            print '\n\n\n {}:\tProfile liklihood for {}  has been calculated'.format(count,i)
            
    def copasiSE_batch_run_subprocess(self):
        '''
        Use the subprocess module to loop through the list of cps files and send them 
        for execution. This function doesn't seem to wait for one process to finish before
        starting the next so it WILL sap all of your computer power. However
        it will be done faster.
        '''
        os.chdir(self.IA_dir)
        for i in glob.glob('*.cps'):
            command='CopasiSE "{}"'.format(i)
            subprocess.Popen( command)


class SubmitCopasiJob(object):
    '''
    Class to submit an appropiately formatted .cps file to sun grid engine job sheduler
    
    
    An appropiately configured copasi file conforms to the following:
    1) You must set up a scan task with a repeat item. Even if you are just submiting one parameter estimation it must be submitted via the parameter scan task
    2) To get the resutls you need to define a report. The default parameter estimation report will work but it gives a little too much information. I instead tend to define a new report in the output specifications containing all parameters I am estimating plus the best value (from the expert mode)
    3) now use the report you've just defined in the parameter scan window. Set 'append' and 'confirm overwrite' to off
    4) ensure parameter estimation is set as subtask and the 'executable' box is checked in the top right hand corner of the parameter scan task
    5) go to the parameter estimation task and configure your estimation however you like
    6) Save and close
    
    
    '''
    def __init__(self,copasi_file):
        self.copasi_file=copasi_file
        self.report_name=os.path.split(self.copasi_file)[1][:-4]+'.txt'
        self.copasiML_str=self._read_copasiML_as_string()
        self.SubmitCopasiJob_SGE()

    def _read_copasiML_as_string(self):
        '''
        Read a copasiML file as string 
        '''
        assert os.path.exists(self.copasi_file), "{} does not exist!".format(self.copasi_file)
        with open(self.copasi_file) as f:
            fle = f.read()
        return fle
    
    def change_scan_report_name(self):
        '''
        Takes copasi_file as input and changes the predifined report name 
        to be the same as the copasi filename. Best to make sure you only have one
        report defined at any one time
        '''
        copasiML=etree.fromstring(self.copasiML_str)  
        query = "//*[@name='Scan']" and "//*[@type='scan']"
        for i in copasiML.xpath(query): 
            for j in i.getchildren():
                for k in j.attrib.keys():
                    if k=='target':
                        j.attrib['target']=self.report_name
        os.remove(self.copasi_file) #remove original and replace with new copasiML
        with open(self.copasi_file,'w') as f:
            f.write(etree.tostring(copasiML))
                  
    def SubmitCopasiJob_SGE(self):
        '''
        Will run a job on the fms cluster by submitting to sun grid engine
        '''
        self.change_scan_report_name()
        with open('run_script.sh','w') as f:
            f.write('#!/bin/bash\n#$ -V -cwd\nmodule addapps/COPASI/4.16.104-Linux-64bit\nCopasiSE "{}"'.format(self.copasi_file))
        os.system('qsub {}'.format('run_script.sh'))
        os.remove('run_script.sh')


#===========================================================        
class SubmitCopasiIADir(SubmitCopasiJob):
    '''
    Submit all .cps files in the IA_dir to SGE using SubmitCopasiJob
    '''
    def __init__(self,copasi_file,custom_IA_dir=None):
        self.copasi_file=copasi_file
        self.I=Initialize(self.copasi_file)
        self.custom_IA_dir=custom_IA_dir
        self.report_name=self.report_name=os.path.split(self.copasi_file)[1][:-4]+'.txt'
        self.submit_IA_dir_to_SGE()
        
    def submit_IA_dir_to_SGE(self):
        '''
        Submit the contents of IA_dir to sun grid engine. IA_dir is the directory
        where your profile likelihood caluclations are stored. 
        '''
        os.chdir(self.I.IA_dir)
        if self.custom_IA_dir!=None:
            assert os.path.isdir(self.custom_IA_dir),'custom_IA_dir must be the full directory to a set up profile likelihood analysis'
            os.chdir(self.custom_IA_dir)
        for i in glob.glob('*.cps'):
            SubmitCopasiJob(i)    
            

            
class ProfileLikelihood():
    '''
    Run a profile likelihood calculation 
    Arguments:
    copasi_file:    An appropiately configured copasi file (see top of this script)
    lb:             lower bound for profile likelihood. Calculated in terms of current parameter value
                        i.e. parameter_value/lb. 
                        default=2. 
    ub:             upper bound for profile likelihood calcualtion. Calculated in terms of current parameter value
                        i.e. parameter_value*ub
                        default=2
    intervals:      Number of intervals between lb and ub. Default=10
        
    Main method is run. 
    '''
    def __init__(self,copasi_file,lb=4,ub=4,intervals=10,verbose=False):
        self.copasi_file=copasi_file
        self.lb=lb
        self.ub=ub
        self.interavls=intervals
        self.verbose=verbose
        self.s=Setup(self.copasi_file,lb=self.lb,ub=self.ub,intervals=self.interavls,verbose=self.verbose)
        self.s.setup_all()


    def run(self,mode='slow'):
        '''
        Run profile likleihood calculation. 
        mode: 
            slow:   Use one process to sequentially process all profile likleihood calcualtions
            fast:   Use multiple processes to process all profile likelihooods in parallel. 
                    Warning: This mode will sap your computer power
            SGE:    Submit to job scheduler SunGrid Engine if you have it. 
        '''
        assert mode in ['slow','fast','SGE'],'mode must be either \'slow\' or \'fast\ or \'SGE\''
        
        
        r=Run(self.s.I.IA_dir)
        if mode == 'slow':
            #uses one process
            r.copasiSE_batch_run()
        elif mode == 'fast':
            #uses seperate process for each parameter
            r.copasiSE_batch_run_subprocess()
        elif mode =='SGE':
            SubmitCopasiIADir(self.copasi_file)
            
     



#========================================================


class Plot():
    '''
    This class facilitates the visualization of the profile likelihood
    calculations. 
    The main functions:
    plot1() to plot one graph
    plot_all() to plot all graphs
    plot_all(multiplot=True) to plot multiple profile likleihood 
    '''
    def __init__(self,copasi_file,RSS_value):
#        self.alpha=alpha
        self.copasi_file=copasi_file
        self.RSS_value=RSS_value
        if isinstance(RSS_value,int):
            self.RSS_value=float(self.RSS_value)
        else:
            assert isinstance(self.RSS_value,float),'RSS_value should be either an integer or a float'
        self.GEP=GetEstimatedParameters(self.copasi_file)
        self.I=Initialize(self.copasi_file)
        os.chdir(self.I.IA_dir)
        self.IA_result_files=self._get_IA_result_filepaths()
        self.IA_results=self._parse_IA_results()
        self.dof=self.degrees_of_freedom()
        self.alphas=self.get_alphas()
        self.n=self.n()
        
    def _get_IA_result_filepaths(self):
        '''
        Gets files paths to all results files whilst excluding any 
        data files and 'double slashing' all single slashes. 
        returns list assessible by self.IA_results_files
        '''
        os.chdir(self.I.IA_dir)
        files=[]
        for i in glob.glob('*.txt'):   
            files.append(i)
        for i in range(len(files)):
            files[i]=os.path.abspath(files[i])
        files= [i for i in files if i not in self.I.data_files]
        assert len(files)!=0,'There are no profile likelihood results in {}. Have you used the PL.run() command yet?'.format(self.I.IA_dir)
        return files 
        
    def _parse_IA_results(self,filter_copasi_parameter_names=True):
        '''
        Read all the results into a list of pandas dataframes. Also renames the
        default copasi name for the RSS (TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value), to RSS
        '''
        df_list=[]
        for i in range(len(self.IA_result_files)):
            try:
                data=pandas.read_csv(self.IA_result_files[i],sep='\t')
            except:
                print '{} file cannot be read. File might be empty.'.format(self.IA_result_files[i])
                continue
            assert data.shape[0]!=0,'{} parameter has no data. Rerun profile likelihood calcualtion'.format(self.IA_result_files[i])
            data=data.rename(columns={'TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value':'RSS'})
            data=data.rename(columns={'Parameter Estimation'.lower():'RSS'})

            if filter_copasi_parameter_names==True:
            #filter data names for global and IC nomenclature
                global_parameter_names= re.findall('\[(.*)\]',data.keys()[0])
                if global_parameter_names!=[]:
                    data=data.rename(columns={ data.keys()[0]:global_parameter_names[0]})
            df_list.append(data)
        return df_list
      



    def degrees_of_freedom(self):
        '''
        The number of parameters being estimated minus 1
        '''
        return len(self.GEP.all_params.keys())-1
        
    def list_parameters(self):
        return sorted(self.GEP.all_params.keys())
        
        
    def chi2_lookup_table(self,alpha,dof):
        '''
        Looks at the cdf of a chi2 distribution at incriments of 
        0.1 between 0 and 100. 
        
        Returns the x axis value at which the alpha interval has been crossed, 
        i.e. gets the cut off point for chi2 dist with self.dof and alpha . 
        '''
        nums= numpy.arange(0,100,0.1)
        table=zip(nums,scipy.stats.chi2.cdf(nums,dof) )
        for i in table:
            if i[1]<=alpha:
                chi2_df_alpha=i[0]
        return chi2_df_alpha     

    def get_alphas(self):
        '''
        
        '''
        dct={}
        alphas=numpy.arange(0,1,0.01)
        for i in alphas:
            dct[round(i,3)]=self.chi2_lookup_table(i,self.dof)
        return dct
                

                
    def n(self):
        '''
        returns number of data points in your data files
        '''
        data= [pandas.read_csv(i,sep='\t') for i in self.I.data_files]
        var_length=[] #lengths of each column in your data set
        for i in data:
            for j in i.keys():
                if re.findall('time',j.lower())==[] and re.findall('unnamed',j.lower())==[]:
                    var_length.append( len(i[j]))
        return sum(var_length)


    def best_value_at_minimum_deprecated(self,parameter):
        '''
        This function was deprecated because it doesn't function as intended. 
        My attempts at automatically retreiving the RSS value from the model
        have failed. I now require that the user specified this value when initializing the
        Plot class. 
        
        ---old---
        Get the model value and RSS at the global minium. This should be identical for each 
        specie since there is only one best value
        
        returns the original model parameter value and the RSS for specie
        '''
        assert isinstance(parameter,str),'specie must be a string'
        assert parameter in self.GEP.all_params.keys(),'specie must be an estimated parameter in your model'
        if isinstance(self.GEP.all_params[parameter],dict):
            species_value=round(float(self.GEP.all_params[parameter].keys()[0]),5)
        else:
            species_value=round(float(self.GEP.all_params[parameter]),5)
        #use model value to find RSS
        for i in self.IA_results:
            if i.keys()[0]==parameter:
#                print i
                abs_diff= abs(i[parameter]-species_value)
#                print abs_diff
                closest_to_0_index= abs_diff.idxmin()
#                print closest_to_0_index
                return i.iloc[closest_to_0_index]
                
    def calc_chi2_CI(self,alpha=0.95):
        '''
        get chi2 CI at alpha
        alpha=decimal between 0 and 1 with 2 decimal places 
        '''
        assert isinstance(alpha,float),'alpha must be float'
        assert alpha in self.alphas.keys(),'alpha must be one of: {}'.format(sorted(self.alphas.keys()))
        return self.RSS_value*math.exp(self.alphas[alpha]/self.n)
        


    def plot1_deprecated(self,parameter,extra_title=None,multiplot=False,savefig=False,title_wrap_size=30,fontsize=15,ylimit=None,xlimit=None,alpha=0.95):
        '''
        Plot one parameter. 
        
        extra_title: default==None, if savefig==True, you have the option to name the file with extra_title
        savefig: default==False, if True, will save to current directory (which should be IA_dir [results dir])
        title_wrap_size: default == 30, number of characters for title of graph before word wrap
        fontsize: default ==15. Text fontsize
        ylimit: default==None, restrict amount of data shown on y axis. Useful for honing in on small confidence intervals
        xlimit: default==None, restrict amount of data shown on x axis. Useful for honing in on small confidence intervals
        alpha: default == 0.95, i.e. the 95th percentile of the chi squared distribution, must be a float between 0 and 1
        
        '''

        assert isinstance(alpha,float),'alpha must be a float between 0 and 1'
        assert isinstance(parameter,str),'parameter must be a string'
        assert parameter in [i.keys()[0] for i in self.IA_results],'{} is not a parameter'.format(parameter)
        if multiplot==True:
            plt.figure(parameter)
        else:
            plt.figure()
        ax = plt.subplot(111)
        data= [i for i in self.IA_results if i.keys()[0]==parameter][0]
        parameter_val,RSS_val=(data[data.keys()[0]],data[data.keys()[1]])
        
        #plot parameter vs RSS once as green circles the other as lines
        plt.plot(parameter_val,RSS_val,'bo')
        handle= plt.plot(parameter_val,RSS_val,'--')
        plt.setp(handle,'color','black',linewidth=2)
        
        #plot the confidence interval (chi squared)
        CI= self.calc_chi2_CI(alpha)
        plt.plot(parameter_val,[CI]*len(parameter_val),'g--',label=str(i))
        
        #plot best value vs RSS as red dots. 
        GEP=GetEstimatedParameters(self.copasi_file)
        #pretty stuff
        plt.title(parameter,fontsize=fontsize)
        plt.ylabel('RSS',fontsize=fontsize)
        plt.xlabel('Parameter Value',fontsize=fontsize) 
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        
        #options for changing the plot axis
        if ylimit!=None:
            assert isinstance(ylimit,list),'ylim is a list of coordinates for y axis,i.e. [0,10]'
            assert len(ylimit)==2,'length of the ylim list must be 2'
            ax.set_ylim(ylimit)
        if xlimit!=None:
            assert isinstance(xlimit,list),'ylim is a list of coordinates for y axis,i.e. [0,10]'
            assert len(xlimit)==2,'length of the ylim list must be 2'
            ax.set_xlim(xlimit)
            
        #save figure options
        if savefig==True:
            if extra_title !=None:
                assert isinstance(extra_title,str),'extra title should be a string'
                plt.savefig(parameter+'_'+extra_title+'.jpeg',bbox_inches='tight',format='jpeg',dpi=500)
            else:
                plt.savefig(parameter+'.jpeg',format='jpeg',bbox_inches='tight',dpi=300)         
        

    def plot_all2(self,size=1,extra_title=None,show=False,savefig=False,title_wrap_size=30,fontsize=8,alpha=0.95):
        '''
        Plot all graphs in grid of size^2. 
        
        size: default==2, means 2^2=4 graphs per figure. 
        rest of the options arethe same as plot1
        
        less stable than plot_all
        '''
        size_squared=size**2
        full_subplots= len(self.IA_results)/size_squared
        for i in range(full_subplots):
            fig=plt.figure(i)
            for j in range(size_squared):
                ax=plt.subplot(size,size,j)
                parameter_name,parameter_val= (self.IA_results[i*size_squared+j].keys()[0],self.IA_results[i*size_squared+j][self.IA_results[i*size_squared+j].keys()[0]])
                RSS_val=self.IA_results[i*size_squared+j][self.IA_results[i*size_squared+j].keys()[1]]


        
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                ax.xaxis.set_ticks_position('bottom')
                ax.yaxis.set_ticks_position('left')
                ax.spines['left'].set_smart_bounds(True)
                ax.spines['bottom'].set_smart_bounds(True)
#                
                plt.plot(parameter_val,RSS_val,'black')
#                plt.setp(RSS_line,color='black')
                plt.plot(parameter_val,RSS_val,'ro')
                
                CI= self.calc_chi2_CI(alpha)
                plt.plot(parameter_val,[CI]*len(parameter_val),'g--',label=str(i))
                #Pretty stuff                
                plt.title('\n'.join(  wrap(str(parameter_name)+',n='+str(len(self.IA_results[size_squared*i+j])),title_wrap_size)),y=0.85,fontsize=fontsize)
                fig.text(0.5,0.02,'RSS',ha='center')
                fig.text(0.04,0.55,'Parameter Value',ha='center',rotation='vertical')
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=35)
                
            if savefig==True:
                if extra_title !=None:
                    assert isinstance(extra_title,str),'extra title should be a string'
                    plt.savefig(str(i)+'_'+extra_title+'.jpeg',bbox_inches='tight',format='jpeg',dpi=500)
                else:
                    plt.savefig(str(i)+'.jpeg',format='jpeg',bbox_inches='tight',dpi=300) 
            if show==True:
                plt.show()

    def plot1(self,parameter,extra_title=None,show=False,multiplot=False,axis_size=22,interpolation_kind='slinear',interp_res=1000,savefig=False,dpi=100,title_wrap_size=30,fontsize=20,ylimit=None,xlimit=None,alpha=0.95):
        '''
        Plot one parameter. 
        
        extra_title: default==None, if savefig==True, you have the option to name the file with extra_title
        savefig: default==False, if True, will save to current directory (which should be IA_dir [results dir])
        title_wrap_size: default == 30, number of characters for title of graph before word wrap
        fontsize: default ==15. Text fontsize
        ylimit: default==None, restrict amount of data shown on y axis. Useful for honing in on small confidence intervals
        xlimit: default==None, restrict amount of data shown on x axis. Useful for honing in on small confidence intervals
        alpha: default == 0.95, i.e. the 95th percentile of the chi squared distribution, must be a float between 0 and 1
        
        '''

        assert isinstance(alpha,float),'alpha must be a float between 0 and 1'
        assert isinstance(parameter,str),'parameter must be a string'
        assert parameter in [i.keys()[0] for i in self.IA_results],'{} is not a parameter'.format(parameter)
        assert interpolation_kind in ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'],"interpolation kind must be one of ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic']"
        matplotlib.rcParams.update({'font.size': 22})
        if multiplot==True:
            plt.figure(parameter)
        else:
            plt.figure()
        ax = plt.subplot(111)
        data= [i for i in self.IA_results if i.keys()[0]==parameter][0]
        parameter_val,RSS_val=(data[data.keys()[0]],data[data.keys()[1]])
        
        #plot parameter vs RSS once as green circles the other as lines
        plt.plot(parameter_val,RSS_val,'bo')
        #now get your interpolation on...
        f=interp1d(parameter_val,RSS_val,kind=interpolation_kind)
        interp_parameter_value=numpy.linspace(min(parameter_val),max(parameter_val), num=interp_res*len(parameter_val), endpoint=True)
        interp_RSS_value=f(interp_parameter_value)        
        handle=plt.plot(interp_parameter_value,interp_RSS_value,'black')
        plt.setp(handle,'color','black',linewidth=2)
#        
#        #plot the confidence interval 
        CI= self.calc_chi2_CI(alpha)
        plt.plot(parameter_val,[CI]*len(parameter_val),'g--',label=str(i))

#        #plot best value vs RSS as red dots. 
        GEP=GetEstimatedParameters(self.copasi_file)
#        #initial concentrations are nested dictionaries
        best_parameter_value=float(GEP.all_params[parameter])
            
#        best parameter value contains the model value for pparameter
        #we now need to look this value up on the interpolation and read off the corresponding RSS value
        #first find the parameter value in the interolation that is closest to the best param val
        pandas.set_option('precision',15)
        interp_df= pandas.DataFrame([interp_parameter_value,interp_RSS_value],index=[parameter,'RSS']).transpose()
        best_parameter_value=numpy.round(best_parameter_value,15)
        abs_diff_df= abs(interp_df-best_parameter_value)
        minimum_index= abs_diff_df.idxmin()[parameter]
        best_parameter_value= interp_df.iloc[minimum_index][parameter]
        best_RSS_value=interp_df.iloc[minimum_index]['RSS']
        plt.plot(best_parameter_value,best_RSS_value,'ro')
        
        
            
       #pretty stuff
        plt.title('\n'.join(wrap('{}'.format(parameter),title_wrap_size)),fontsize=fontsize)
        plt.ylabel('RSS',fontsize=fontsize)
        plt.xlabel('Parameter Value',fontsize=fontsize) 
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        
        #options for changing the plot axis
        if ylimit!=None:
            assert isinstance(ylimit,list),'ylim is a list of coordinates for y axis,i.e. [0,10]'
            assert len(ylimit)==2,'length of the ylim list must be 2'
            ax.set_ylim(ylimit)
        if xlimit!=None:
            assert isinstance(xlimit,list),'ylim is a list of coordinates for y axis,i.e. [0,10]'
            assert len(xlimit)==2,'length of the ylim list must be 2'
            ax.set_xlim(xlimit)
            
        #save figure options
        if savefig==True:
            if extra_title !=None:
                assert isinstance(extra_title,str),'extra title should be a string'
                plt.savefig(parameter+'_'+extra_title+'.jpeg',bbox_inches='tight',format='jpeg',dpi=dpi)
            else:
                plt.savefig(parameter+'.jpeg',format='jpeg',bbox_inches='tight',dpi=dpi)     
        if show==True:
            plt.show()

#        return (lower_CI,upper_CI) #not working 


    def get_CI(self,parameter,interpolation_kind='slinear',alpha=0.95,interp_res=10000 ):
        assert parameter in [i.keys()[0] for i in self.IA_results],'{} is not a parameter'.format(parameter)
        assert interpolation_kind in ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'],"interpolation kind must be one of ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic']"
        data= [i for i in self.IA_results if i.keys()[0]==parameter][0]
        parameter_val,RSS_val=(data[data.keys()[0]],data[data.keys()[1]])
        CI= self.calc_chi2_CI(alpha)
        #now get your interpolation on...
        f=interp1d(parameter_val,RSS_val,kind=interpolation_kind)
        interp_parameter_value=numpy.linspace(min(parameter_val),max(parameter_val), num=interp_res*len(parameter_val), endpoint=True)
        interp_RSS_value=f(interp_parameter_value)        
#            
##        best parameter value contains the model value for pparameter
#        #we now need to look this value up on the interpolation and read off the corresponding RSS value
#        #first find the parameter value in the interolation that is closest to the best param val
        pandas.set_option('precision',15)
        interp_df= pandas.DataFrame([interp_parameter_value,interp_RSS_value],index=[parameter,'RSS']).transpose()
        below0=interp_df[interp_df['RSS']-CI<0]
        plt.figure()
        plt.plot(below0[parameter],below0['RSS'],below0[parameter],[CI]*len(below0[parameter]))
  





    def plot_all(self,extra_title=None,show=False,multiplot=False,axis_size=22,savefig=False,dpi=150,interpolation_kind='slinear',title_wrap_size=30,fontsize=15,ylimit=None,xlimit=None,alpha=0.95):
        '''
        Use plot1 function to plot all the profile likelihoods
        
        options same as in plot1
        '''
        lb_lst=[]
        ub_lst=[]
        df_list=[]
        for i in range(len(self.IA_results)):
            parameter= self.IA_results[i].keys()[0]
            self.plot1(parameter,extra_title=extra_title,axis_size=axis_size,show=show,savefig=savefig,dpi=dpi, multiplot=multiplot,  interpolation_kind=interpolation_kind,  title_wrap_size=title_wrap_size,     fontsize=fontsize,   ylimit=ylimit,   xlimit=xlimit,alpha=0.95)

class SubmitCopasiMultiJob():
    '''
    submit cps multi profile likelihood analysis to SGE. 
    Will submit all PLs in MPL if they are there. Therefore if you have 8 parameters and are
    submitting 3 times, you expect 24 submissions in total. However if you do another MPL analysis
    but this time only 2 MPLs are being submitted, then you still submit 24, because you have also submitted the third again!
    '''
    def __init__(self,copasi_file):
        self.copasi_file=copasi_file
        self.cps_dir=self.get_cps_dir()
        self.MPL_dir=self.get_MPL_dir()
        self.index_dirs=self.get_index_dirs()
        self.PL_dirs=self.get_PL_dirs()
        self.sub_cps_files=self.get_sub_cps_files()
        self.number_of_submitted_files=self.submit_cps_to_SGE()

    def get_cps_dir(self):
        '''
        get Parent CPS file directory
        '''
        return os.path.dirname( self.copasi_file)

    def get_cps_filename(self):
        '''
        gets the name of the parent CPS file without the cps
        '''
        assert os.path.isfile(self.copasi_file),'{} is not a file'.format(self.copasi_file)
        return os.path.split(self.copasi_file)[1][:-4]
        
        
    def get_MPL_dir(self):
        '''
        gets path to overall multiprofile likelihood analysis
        '''
        MPL_dir=self.get_cps_filename()+'_MPL'
        MPL_dir= os.path.join(self.cps_dir,MPL_dir)
        assert os.path.isdir(MPL_dir),'{} is not a directory'.format(MPL_dir)
        return MPL_dir

    def get_index(self):
        '''
        Get index from file paths
        
        '''
        PL_dirs=[os.path.join(self.MLP_dir,i) for i in os.listdir(self.MLP_dir)]
        return [os.path.split(i)[1] for i in PL_dirs]
        
    def get_index_dirs(self):
        '''
        gets path to indexed directories, indexed by rank best fit from PE results
        '''
        return [ os.path.join(self.MPL_dir,i) for i in os.listdir(self.get_MPL_dir())]

    def get_PL_dirs(self):
        '''
        get the PL directory for each index
        '''
        PL_name=self.get_cps_filename()+'_PL'
        PL_dirs= [os.path.join(i,PL_name) for i in self.get_index_dirs()]
        for i in PL_dirs:
            assert os.path.isdir(i),'{} is not a real directory'.format(i)
        return PL_dirs
        
    def get_sub_cps_files(self):
        '''
        get list of all CPS files for subsequent submission to SGE
        
        '''
        cps_dirs=[]
        for i in self.PL_dirs:
            for j in os.listdir(i):
                if j.endswith('.cps'):
                    cps_dirs.append( os.path.join(i,j))
        for i in cps_dirs:
            assert os.path.isfile(i),'{} is not a real file'.format(i)
        return list(set(cps_dirs))
        
    def submit_cps_to_SGE(self):
        '''
        Use SubmitCoapsiJob to submit all cps files to cluster
        '''
        [SubmitCopasiJob(i) for i in  self.sub_cps_files]
        print '{} cps files have been submitted'.format(len(self.sub_cps_files))
        return len(self.sub_cps_files)



class ParseData():
    def __init__(self,results):
        self.results=results
        assert os.path.exists(results),'The {} file or folder does not exist!'
        if os.path.isdir(results):
            self.data=self._parse_datadir()
        elif os.path.isfile(results):
            self.data=self._parse_datafile()

    def _parse_datafile(self):
        '''
        Parse a single datafile (xlsx or csv) into a pandas dataframe
        if self.results_file is specified and self.results_dir is not
        
        '''
        if self.results!=None:
            assert os.path.isfile(self.results)
            ext= os.path.splitext(self.results)[1]
            assert ext in ['.xlsx','.xls','.csv','.txt'],'results dir must be a xlsx/xls/csv or tab seperated text file (the latter for the output from copasi)'
        if ext=='.xlsx':
            data=pandas.read_excel(self.results)
        elif ext=='.csv':
            data=pandas.read_csv(self.results)
        elif ext=='.txt':
            data=pandas.read_csv(self.results,sep='\t')
        data=data.rename(columns={'TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value':'RSS'})
        return data
        
    def _parse_datadir(self):
        '''
        Parse PE results from a list of text files in a directory called results_dir
        Do not specify results_file at the same time as results_dir
        '''
        df_list=[]
        count=0
        if self.results!=None:
            os.chdir(self.results)
            for i in glob.glob('*.txt'):
                count+=1
                data=pandas.read_csv(os.path.join(self.results,i),sep='\t')
                data=data.rename(columns={'TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value':'RSS'})
                df_list.append(data)
        df=pandas.concat(df_list) #flatten list
        df=df.reset_index()
        del df['index']
        return df
        


    def _get_parameter_sets(self):
        '''
        Get parameter sets from index to input into copasi to calcualte PLs for
        '''
        return self.data.iloc[self.index]
        
    def write_parameter_sets_xlsx(self):
        name=os.path.join(os.path.dirname(self.copasi_file),'Parameter_sets.xlsx')
        self.parameter_sets.to_excel(name)
        print 'parameter sets written to {}'.format(name)
        return name
    
    def write_PE_xlsx(self):
        '''
        Write parameter estimation results to xlsx file
        '''
        name=os.path.join(os.path.dirname(self.results),'PE_Results.xlsx')
        self.data.to_excel(name)
        print 'parameter sets written to {}'.format(name)
        return name


        
#==================================================================
class MultiProfileLikelihood():
    def __init__(self,copasi_file,index,results_dir=None,results_file=None,lb=4,ub=4,intervals=10,verbose=False):
        self.lb=lb
        self.ub=ub
        self.intervals=intervals
        self.verbose=verbose
        self.copasi_file=copasi_file
        os.chdir(os.path.dirname(self.copasi_file))
        self.copasiML_str=self._read_copasiML_as_string()
        self.copasiML=etree.fromstring(self.copasiML_str)
        self.results_file=results_file
        self.results_dir=results_dir
        #make sure both results file and results dir are not None
        if self.results_file==None:
            assert self.results_dir !=None,'''Must give either a results file
            (xlsx/xls/csv) or a results directory (containing output from many 
            individual copasi parameter estimation runs),not both'''
        if self.results_dir==None:
            assert self.results_file!=None,'''Must give either a results file
            (xlsx/xls/csv) or a results directory (containing output from many 
            individual copasi parameter estimation runs), not both'''  
        #make sure that results file and results dir are not both given at the same time
        if self.results_file!=None:
            assert os.path.isfile(self.results_file),'{} must be a real file'.format(self.results_dir)
            assert self.results_dir ==None,'''Must give either a results file
            (xlsx/xls/csv) or a results directory (containing output from many 
            individual copasi parameter estimation runs),not both'''
        if self.results_dir!=None:
            assert os.path.isdir(self.results_dir),'{} must be a real directory'.format(self.results_dir)
            assert self.results_file==None,'''Must give either a results file
            (xlsx/xls/csv) or a results directory (containing output from many 
            individual copasi parameter estimation runs), not both'''  
        self.index=index
        assert isinstance(self.index,list)==True,'Index must be a python list'
        self.subdirs=self._make_dirs()
        self.datadirs=self._copy_data()
        self.cps_dirs=self._copy_cps()
        #parse data
        self.data=self._parse_data()
        self.parameter_sets=self._get_parameter_sets()
        self.insert_copasi_parameters()
        self.multi_IA_dirs=self.setup_profile_likelihoods()


    
    
    def _read_copasiML_as_string(self):
        with open(self.copasi_file) as f:
            return f.read()
        
    def write_copasi_file(self,copasiML):
        '''
        Often you need to delete a copasi file and rewrite it
        directly from the string. This function does this.
        
        copasi_filename = a valid .cps file
        copasiML = an xml string. Convert to xml string
        before using this function using etree.fromstring(xml_string)
        '''
        os.remove(self.copasi_file)
        with open(self.copasi_file,'w') as f:
            f.write(etree.tostring(copasiML))
            
            
    def _make_dirs(self):
        parent_name=os.path.join( os.path.dirname(self.copasi_file) , os.path.split(self.copasi_file)[1][:-4]+'_MPL')
        sub_dirs=[]        
        for i in range(len(self.index)):
            sub_dirname=os.path.join(parent_name,str(self.index[i]))
            sub_dirs.append(sub_dirname)
            if os.path.isdir(sub_dirname)==False:
                os.makedirs(sub_dirname)
        return sub_dirs
    
    def _copy_cps(self):
        '''
        copy copasi file into each direcotry        
        '''
        cps_list=[]
        cps_filename=os.path.split(self.copasi_file)[1]
        for i in self.subdirs:
            cps_list.append(os.path.join(i,cps_filename))
            shutil.copy(self.copasi_file,i)
        return cps_list
        
    def _copy_data(self):
        '''
        copy data files into each direcotry
        '''
        data_list=[]
        for i in glob.glob('*.txt'):
            for j in self.subdirs:
                data_list.append( os.path.join(j,i) )
                shutil.copy(i,j)
        return data_list


    def _parse_datafile(self):
        '''
        Parse a single datafile (xlsx or csv) into a pandas dataframe
        if self.results_file is specified and self.results_dir is not
        
        '''
        if self.results_file!=None:
            assert os.path.isfile(self.results_file)
            ext= os.path.splitext(self.results_file)[1]
            assert ext in ['.xlsx','.xls','.csv','.txt'],'results dir must be a xlsx/xls/csv or tab seperated text file (the latter for the output from copasi)'
        if ext=='.xlsx':
            data=pandas.read_excel(self.results_file)
        elif ext=='.csv':
            data=pandas.read_csv(self.results_file)
        elif ext=='.txt':
            data=pandas.read_csv(self.results_file,sep='\t')
        data=data.rename(columns={'TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value':'RSS'})
        return data
        
    def _parse_datadir(self):
        '''
        Parse PE results from a list of text files in a directory called results_dir
        Do not specify results_file at the same time as results_dir
        '''
        df_list=[]
        count=0
        if self.results_dir!=None:
            os.chdir(self.results_dir)
            for i in glob.glob('*.txt'):
                count+=1
                data=pandas.read_csv(os.path.join(self.results_dir,i),sep='\t')
                data=data.rename(columns={'TaskList[Parameter Estimation].(Problem)Parameter Estimation.Best Value':'RSS'})
                df_list.append(data)
        df=pandas.concat(df_list) #flatten list
        return df
        
    def _parse_data(self):
        '''
        Automatically detect type of data input (direcotry or as file)
        and parse data into pandas dataframe. Also sorts in order of increasing RSS values
        '''
        if self.results_dir!=None:
            data=self._parse_datadir()
        if self.results_file!=None:
            data=self._parse_datafile()
        return data.sort('RSS',axis=0).reset_index()

    def _get_parameter_sets(self):
        '''
        Get parameter sets from index to input into copasi to calcualte PLs for
        '''
        return self.data.iloc[self.index]
        
    def write_parameter_sets_xlsx(self):
        name=os.path.join(os.path.dirname(self.copasi_file),'Parameter_sets.xlsx')
        self.parameter_sets.to_excel(name)
        print 'parameter sets written to {}'.format(name)
        return name
    
    def write_PE_xlsx(self):
        '''
        Write parameter estimation results to xlsx file
        '''
        name=os.path.join(os.path.dirname(self.copasi_file),'PE_Results.xlsx')
        self.data.to_excel(name)
        print 'parameter sets written to {}'.format(name)
        return name
        
    def insert_copasi_parameters(self):
        '''
        use the InsertCopasiParameters module to insert parameters from PE results into the cps files
        '''
        #Doing all this in one loop does not work!
        for i in range(len(self.index)):
            ICP=insert_copasi_parameters.InsertCopasiParameters(self.cps_dirs[i],i,pandas_df=self.parameter_sets)
            ICP.insert_local()
        for i in range(len(self.index)):
            ICP=insert_copasi_parameters.InsertCopasiParameters(self.cps_dirs[i],i,pandas_df=self.parameter_sets)
            ICP.insert_global()
        for i in range(len(self.index)):
            ICP=insert_copasi_parameters.InsertCopasiParameters(self.cps_dirs[i],i,pandas_df=self.parameter_sets)
            ICP.insert_ICs()
        for i in range(len(self.index)):
            ICP=insert_copasi_parameters.InsertCopasiParameters(self.cps_dirs[i],i,pandas_df=self.parameter_sets)
            ICP.insert_fit_items()
            

    def setup_profile_likelihoods(self):
        '''
        
        Note: don't need to run this code in the constructor because
        you are running it when you use the MLP.run method
        '''
        multi_IA_dirs=[]
        for i in self.cps_dirs:
            s=Setup(i,lb=self.lb,ub=self.ub,intervals=self.intervals,verbose=self.verbose)
            s.setup_all()
            multi_IA_dirs.append(s.I.IA_dir)
        return multi_IA_dirs

    def run(self,mode='slow'):
        '''
        Run the profile likelihood calcualtions for each parameter set in index
        if mode:
            slow:    uses only one process to do all calcualtions
            fast:    uses all computer power via the subprocess module. Only use if you don't need to use your computer while your running the simulations
            SGE:     Submits jobs to SGE cluster
        
        '''
        assert mode in ['slow','fast','SGE'],'mode must be slow,fast or SGE'
        for i in self.multi_IA_dirs:
            r=Run(i)
            if mode=='slow':
                r.copasiSE_batch_run()
            elif mode=='fast':
                r.copasiSE_batch_run_subprocess()
        if mode=='SGE':
            SubmitCopasiMultiJob(self.copasi_file)
                
    def multiplot(self,extra_title=None,interpolation_kind='slinear',show=False,multiplot=True,savefig=False,title_wrap_size=30,fontsize=15,ylimit=None,xlimit=None,alpha=0.95):
        '''
        extra_title:                    Append extra string to back of file name of savefig=True   
        interpolation_kind:             same as Plot.plot1
        multiplot:                      if True, plots each profile likelihood run the same graph for each parameter. \
        because of the iterative nature of this process, when savefig=True with multiplot=True, final plots are in the\
        profile likelihood run with the largest index
        savefig:                        Save figures to file
        title_wrap_size:                How many characters to use to wrap the title text
        fontsize:                       fontsize for all labels
        ylimit:                         boundaries for the plot y axis. Must be a 2 element list [ymin,ymax]
        xlimit:                         boundaries for the plot x axis. Must be a 2 element list [xmin,xmax]
        alpha:                          Chi squared  confidence intervaldefault = 0.95 = 95%
        '''




        for i,j in zip(self.cps_dirs,self.parameter_sets['RSS']):
            p=Plot(i,j)
            p.plot_all(extra_title=extra_title,interpolation_kind=interpolation_kind,show=show,multiplot=multiplot,savefig=savefig,title_wrap_size=title_wrap_size,fontsize=fontsize,ylimit=ylimit,xlimit=xlimit,alpha=alpha)


class MultiPlot():
    '''
    submit cps multi profile likelihood analysis to SGE. 
    Will submit all PLs in MPL if they are there. Therefore if you have 8 parameters and are
    submitting 3 times, you expect 24 submissions in total. However if you do another MPL analysis
    but this time only 2 MPLs are being submitted, then you still submit 24, because you have also submitted the third again!
    '''
    def __init__(self,copasi_file,results):
        self.copasi_file=copasi_file
        self.data=ParseData(results).data
        self.cps_dir=self.get_cps_dir()
        self.MPL_dir=self.get_MPL_dir()
        self.index_dirs=self.get_index_dirs()
        self.PL_dirs=self.get_PL_dirs()
        self.index=self.get_index()
        self.sub_cps=self.get_sub_cps_files()

    def get_cps_dir(self):
        '''
        get Parent CPS file directory
        '''
        return os.path.dirname( self.copasi_file)

    def get_cps_filename(self):
        '''
        gets the name of the parent CPS file without the cps
        '''
        assert os.path.isfile(self.copasi_file),'{} is not a file'.format(self.copasi_file)
        return os.path.split(self.copasi_file)[1][:-4]
        
        
    def get_MPL_dir(self):
        '''
        gets path to overall multiprofile likelihood analysis
        '''
        MPL_dir=self.get_cps_filename()+'_MPL'
        MPL_dir= os.path.join(self.cps_dir,MPL_dir)
        assert os.path.isdir(MPL_dir),'{} is not a directory'.format(MPL_dir)
        return MPL_dir

    def get_index(self):
        '''
        Get index from file paths
        
        '''
        PL_dirs=[os.path.join(self.MPL_dir,i) for i in os.listdir(self.MPL_dir)]
        temp= [os.path.split(i)[1] for i in PL_dirs]
        return [int(i) for i in temp]
    def get_index_dirs(self):
        '''
        gets path to indexed directories, indexed by rank best fit from PE results
        '''
        return [ os.path.join(self.MPL_dir,i) for i in os.listdir(self.get_MPL_dir())]

    def get_PL_dirs(self):
        '''
        get the PL directory for each index
        '''
        PL_name=self.get_cps_filename()+'_PL'
        PL_dirs= [os.path.join(i,PL_name) for i in self.get_index_dirs()]
        for i in PL_dirs:
            assert os.path.isdir(i),'{} is not a real directory'.format(i)
        return PL_dirs
        
    def get_sub_cps_files(self):
        '''
        get list of all CPS files for subsequent submission to SGE
        
        '''
        cps_dirs=[]
        for i in self.PL_dirs:
            for j in os.listdir(i):
                if j.endswith('.cps'):
                    cps_dirs.append( os.path.join(i,j))
        for i in cps_dirs:
            assert os.path.isfile(i),'{} is not a real file'.format(i)
        return list(set(cps_dirs))
        
        
    def get_child_cps(self):
        '''
        get paths to the middle cps dir. i.e. the one that has the parameters from index and \
        not the ones that actually perform the simulations)
        '''
        l=[]
        for i in self.get_index_dirs():
            l.append(os.path.join(i,self.get_cps_filename()+'.cps'))
        for i in l:
            assert os.path.isfile(i),"'{}' is not a file".format(i)
        return zip(self.index,l)
        
    def plot_index(self,index,extra_title=None,axis_size=18,show=False,multiplot=False,interpolation_kind='slinear',interp_res=1000,savefig=False,dpi=100,title_wrap_size=30,fontsize=20,ylimit=None,xlimit=None,alpha=0.95):
        '''
        takes valid index as input
        '''
        assert index in self.index,'\'{}\' is not a valid index'.format(index)
        RSS_for_theta= self.data.iloc[index]['RSS']
        for i in self.get_child_cps():
            if index==i[0]:
                child_cps_file= i[1]
        p=Plot(child_cps_file, RSS_for_theta)
        for i in p.list_parameters():
            if multiplot == True:
                plt.figure(i)
            else:
                plt.figure()
            p.plot1(i,extra_title=extra_title,show=show,multiplot=multiplot,axis_size=axis_size,interpolation_kind=interpolation_kind,interp_res=interp_res,savefig=savefig,dpi=dpi,title_wrap_size=title_wrap_size,fontsize=fontsize,ylimit=ylimit,xlimit=xlimit,alpha=alpha)
        
    def plot_all_indexes(self,extra_title=None,multiplot=False,show=False,axis_size=18,interpolation_kind='slinear',interp_res=1000,savefig=False,dpi=100,title_wrap_size=30,fontsize=20,ylimit=None,xlimit=None,alpha=0.95):
        for i in self.index:
            self.plot_index(i,extra_title=extra_title,show=show,axis_size=axis_size,multiplot=multiplot,interpolation_kind=interpolation_kind,interp_res=interp_res,savefig=savefig,dpi=dpi,title_wrap_size=title_wrap_size,fontsize=fontsize,ylimit=ylimit,xlimit=xlimit,alpha=alpha)




#f=r'D:\MPhil\Model_Building\Models\Exercises\pydentify_examples\Vilar2006\Vilar_example\ProfileLikelihoodFromCurrentParmeters\Vilar2006.cps'
#
#
#PL=ProfileLikelihood(f)
#PL.run('slow')
##













