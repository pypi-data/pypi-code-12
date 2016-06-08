try:
    from lxml import etree 
except ImportError:
    'The lxml module is required. Use \'pip install lxml\' at command line with admin rights if you have pip. If you do not have pip, install pip'

try:
    import argparse
except ImportError:
        'The argparse module is required. Use \'pip install argparse\' at command line with admin rights if you have pip. If you do not have pip, install pip'
import pandas
import os
import re






#-----------------------------------------------------------------------------------------------------------------

'''




lxml and argparse are needed for this program. 
'''

#---------------------------------------------------------------------------------------------------------------------
class InputError(Exception):
    pass


class InsertCopasiParameters(object):
    def __init__(self,copasi_file,row_to_insert=0,parameter_file=None,pandas_df=None):
        '''
        copasi_file: Copasi file to enter and input parameters
        row_to_insert: the index of the parameter estimation run (row) you want to insert
        parameter_file: a csv or excel file. Rows are parameter estimation data, columns are variables with the same name as in the model 
        pandas_df : a pandas dataframe. Rows and columns same as above   
        '''
        self.copasi_file=copasi_file
        os.chdir(os.path.dirname(self.copasi_file))
        self.tree=etree.parse(self.copasi_file)
        self.parameter_file=parameter_file
        self.pandas_df=pandas_df      
        
#        self.copasiML=self._input_from_xml_parser()
        self.row=row_to_insert
        self.param_df=self.truncate_param_df_names()
        self.units_dct=self._get_model_units()
#        self.insert_local() #doesn't work if you add these to the constructor. Must call these methods separately 
#        self.insert_ICs()
#        self.insert_global()


        
    def _read_copasiML_as_string_deprecated(self):
        with open(self.copasi_file) as f:
            r= f.read()
            f.flush()
        return r
        
    def get_copasiML(self):
        return self.tree.getroot()
        
    def write_copasi_file_deprecated(self,copasiML):
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
            f.flush()
        return 
        
    def write_copasi_file(self,copasiML):
        '''
        Often you need to delete a copasi file and rewrite it
        directly from the string. This function does this.
        
        copasi_filename = a valid .cps file
        copasiML = an xml string. Convert to xml string
        before using this function using etree.fromstring(xml_string)
        '''
        os.remove(self.copasi_file)
        self.tree.write(self.copasi_file)
        return  
        
        
    def _parse_parameters_from_file(self):
        '''
        takes a properly formatted parameter estimation
        resutls file and a row number as input 
        or
        a pandas dataframe containing parameters to input into copasi
        returns a pandas series
        '''
        if self.pandas_df is None:
            assert os.path.isfile(self.parameter_file)==True,'Parameter results file must exist'
            assert self.pandas_df is None,'Cannot specify both a pandas dataframe or a parameter esitmation results file'
            filename,extention=os.path.splitext(self.parameter_file)
            if extention=='xlsx' or 'xls':
                df=pandas.read_excel(self.parameter_file)
#                self.logger.info('parameters have been read from {}'.format(self.parameter_file))
            return df.iloc[self.row]
        if self.parameter_file is None:
            assert self.pandas_df is not None,'cannot specify both a pandas dataframe and a parameter estimation results file'
            assert self.parameter_file is None,'Cannot specify both a pandas dataframe or a parameter esitmation results file'
            assert self.row<=self.pandas_df.shape[0],'row must be smaller than number of rows in dataframe'            
            return self.pandas_df.iloc[self.row]
        if self.pandas_df is not None and  self.parameter_file is not None:
            raise InputError('can\'t specify both pandas dataframe and a parameter estimation results file at the same time') 
        assert self.parameter_file!=None and self.pandas_df!=None,'Must specify either a parameter esitmation results file or a pandas dataframe containing parameters, not both'
            
    def truncate_param_df_names(self):
        df=pandas.DataFrame(self._parse_parameters_from_file()).transpose()
        for i in range(len(df.keys())):
            trunc=re.findall('\[(.*)\]',df.keys()[i])
            if trunc != []:
                trunc=trunc[0]
                df=df.rename(columns={str(df.keys()[i]):str(trunc)})
        return df
    
    def _get_model_units(self):
        copasiML=self.get_copasiML()
        query="//*[@timeUnit]"
        dct={}
        for i in copasiML.xpath(query):
            dct['model_name']= i.attrib['name']
            dct['time_unit']=i.attrib['timeUnit']
            dct['volume_unit']=i.attrib['volumeUnit']
            dct['quantity_unit']=i.attrib['quantityUnit']
            dct['type']=i.attrib['type']
            dct['avogadro_constant']=i.attrib['avogadroConstant']
        return dct
        
        
    def convert_particles_to_molar(self,particles,mol_unit,vol_unit):
        '''
        Converts particle numbers to Molarity. 
        particles=number of particles you want to convert
        mol_unit=one of, 'fmol, pmol, nmol, umol, mmol or mol'
        vol_unit= one of 'l,ml,um,nl,pl,fl'
        '''

        mol_dct={
            'fmol':1e-15,
            'pmol':1e-12,
            'nmol':1e-9,
            '\xb5mol':1e-6,
            'mmol':1e-3,
            'mol':float(1),
            'dimensionless':float(1),
            '#':float(1)}
        vol_dct={
            'l':float(1),
            'ml':1e-3,
            '\xb5l':1e-6,
            'nl':1e-9,
            'pl':1e-12,
            'fl':1e-15,
            'dimensionless':1,
            u'm\xb3':1000}
        mol_unit_value=mol_dct[mol_unit]
        vol_unit_value=vol_dct[vol_unit]
        avagadro=6.02214179e+023
        molarity=float(particles)/(mol_unit_value/vol_unit_value*avagadro)
        if mol_unit=='dimensionless' or '#':
            molarity=particles
        if mol_unit=='#':
            molarity=particles
        return molarity
        
        
        
    def convert_molar_to_particles(self,moles,mol_unit,vol_unit):
        '''
        Converts particle numbers to Molarity. 
        particles=number of particles you want to convert
        mol_unit=one of, 'fmol, pmol, nmol, umol, mmol or mol'
        vol_unit= one of 'l,ml,um,nl,pl,fl'
        '''

        mol_dct={
            'fmol':1e-15,
            'pmol':1e-12,
            'nmol':1e-9,
            u'\xb5mol':1e-6,
            'mmol':1e-3,
            'mol':float(1),
            'dimensionless':1,
            '#':1}
        vol_dct={
            'l':float(1),
            'ml':1e-3,
            u'\xb5l':1e-6,
            'nl':1e-9,
            'pl':1e-12,
            'fl':1e-15,
            'dimensionless':1,
            u'm\xb3':1000}
        mol_unit_value=mol_dct[mol_unit]
        vol_unit_value=vol_dct[vol_unit]
        avagadro=6.02214179e+023
        particles=(mol_unit_value/vol_unit_value*avagadro)*float(moles)
        if mol_unit=='dimensionless':# or '#':
            particles=moles
        if mol_unit=='#':
            particles=moles
        return particles
        
        


    def insert_local(self):
#        copasiML=etree.fromstring(self.copasiML_str) 
        copasiML=self.get_copasiML()
        query="//*[@cn='String=Kinetic Parameters']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.getchildren():
                    if k.attrib['simulationType']=='fixed':
                        p='Vector=Reactions\[(.*)\],ParameterGroup=Parameters,Parameter=(.*)'
                        reaction,parameter=re.findall(p,k.attrib['cn'])[0]
                        local_parameters = '({}).{}'.format(reaction,parameter)
#                        print self.param_df.keys()
                        if local_parameters in self.param_df.keys():
                            k.attrib['value']=str(float(self.param_df[local_parameters]))
                        if local_parameters not in self.param_df.keys():
                            self.logger.info('The "{}" parameter does not appear in the data file and therefore is not an observable'.format(local_parameters))
        self.write_copasi_file(copasiML)
                    
    def insert_global(self):
        copasiML=self.get_copasiML()
        query="//*[@cn='String=Initial Global Quantities']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in self.param_df.keys():
                    pattern='Values\[(.*)\]'
                    global_p= re.findall(pattern,j.attrib['cn'])[0]
                    if global_p==k:
                        j.attrib['value']=str(float(self.param_df[global_p]))
        self.write_copasi_file(copasiML)        
        
        
    def insert_ICs(self):
        copasiML=self.get_copasiML()
        query="//*[@cn='String=Initial Species Values']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                p='Vector=Metabolites\[(.*)\]'
                species=re.findall(p,j.attrib['cn'])[0]
                for k in self.param_df.keys():
                    if species ==k:
                        particles = self.convert_molar_to_particles(self.param_df[k],self.units_dct['quantity_unit'],self.units_dct['volume_unit'])
                        particles=float(particles)
                        assert isinstance(particles,float),'something wrong in insert_copasi_parameters.InsertCopasiParameters().insert_ICs()'
                        j.attrib['value']=str(particles)
        self.write_copasi_file(copasiML)


    def insert_fit_items_deprecated(self):
        '''
        This function doesn't work for local parameters!
        '''
#        print self.param_df
        query="//*[@name='OptimizationItemList']"
        for i in self.copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.getchildren():
                    if k.attrib['name']=='ObjectCN':
                        pattern='Vector=.*\[(.*)\]'
                        search= re.findall(pattern,k.attrib['value'])[0]
                    if k.attrib['name']=='StartValue':
                        k.attrib['value']=str(float(self.param_df[search]))
        self.write_copasi_file(copasiML)



    def insert_fit_items(self):
        '''
        insert parameters into fit items
        '''
#        print self.param_df
        copasiML=self.get_copasiML()
        query="//*[@name='OptimizationItemList']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.getchildren():
                    if k.attrib['name']=='ObjectCN':
                        pattern1='Vector=(?!Reactions).*\[(.*)\]'#match global and IC parameters but not local
                        search1= re.findall(pattern1,k.attrib['value'])
                        ICs_and_global=None
                        if search1 !=[]:
                            ICs_and_global=search1[0]
#                            print ICs_and_global
                    if k.attrib['name']=='StartValue':
                        if ICs_and_global !=None:
                            assert ICs_and_global in self.param_df.keys(),'The {} parameter is not in your estimation data'.format(ICs_and_global)
                            k.attrib['value']=str(float(self.param_df[ICs_and_global]))

                    #now again for local parameters
                    if k.attrib['name']=='ObjectCN':
                        pattern2='Vector=Reactions\[(.*)\].*Parameter=(.*),'
                        search2= re.findall(pattern2,k.attrib['value'])
                        reaction=None
                        parameter=None
                        if search2!=[]:
                            reaction,parameter= search2[0]
                            local= '({}).{}'.format(reaction,parameter)
                    if k.attrib['name']=='StartValue':
                        if reaction != None and parameter !=None:
                            k.attrib['value']=str(float(self.param_df[local]))
        self.write_copasi_file(copasiML)
        
    def insert_all(self):
        #locals
        copasiML=self.get_copasiML()
        query="//*[@cn='String=Kinetic Parameters']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.getchildren():
                    if k.attrib['simulationType']=='fixed':
                        p='Vector=Reactions\[(.*)\],ParameterGroup=Parameters,Parameter=(.*)'
                        reaction,parameter=re.findall(p,k.attrib['cn'])[0]
                        local_parameters = '({}).{}'.format(reaction,parameter)
#                        print self.param_df.keys()
                        if local_parameters in self.param_df.keys():
                            k.attrib['value']=str(float(self.param_df[local_parameters]))
                        if local_parameters not in self.param_df.keys():
                            self.logger.info('The "{}" parameter does not appear in the data file and therefore is not an observable'.format(local_parameters))
        #globals
        query="//*[@cn='String=Initial Global Quantities']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in self.param_df.keys():
                    pattern='Values\[(.*)\]'
                    global_p= re.findall(pattern,j.attrib['cn'])[0]
                    if global_p==k:
                        j.attrib['value']=str(float(self.param_df[global_p]))
        #ICs
        query="//*[@cn='String=Initial Species Values']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                p='Vector=Metabolites\[(.*)\]'
                species=re.findall(p,j.attrib['cn'])[0]
                for k in self.param_df.keys():
                    if species ==k:
                        particles = self.convert_molar_to_particles(self.param_df[k],self.units_dct['quantity_unit'],self.units_dct['volume_unit'])
                        particles=float(particles)
                        assert isinstance(particles,float),'something wrong in insert_copasi_parameters.InsertCopasiParameters().insert_ICs()'
                        j.attrib['value']=str(particles)
        #fit items
        query="//*[@name='OptimizationItemList']"
        for i in copasiML.xpath(query):
            for j in i.getchildren():
                for k in j.getchildren():
                    if k.attrib['name']=='ObjectCN':
                        pattern1='Vector=(?!Reactions).*\[(.*)\]'#match global and IC parameters but not local
                        search1= re.findall(pattern1,k.attrib['value'])
                        ICs_and_global=None
                        if search1 !=[]:
                            ICs_and_global=search1[0]
#                            print ICs_and_global
                    if k.attrib['name']=='StartValue':
                        if ICs_and_global !=None:
                            assert ICs_and_global in self.param_df.keys(),'The {} parameter is not in your estimation data'.format(ICs_and_global)
                            k.attrib['value']=str(float(self.param_df[ICs_and_global]))

                    #now again for local parameters
                    if k.attrib['name']=='ObjectCN':
                        pattern2='Vector=Reactions\[(.*)\].*Parameter=(.*),'
                        search2= re.findall(pattern2,k.attrib['value'])
                        reaction=None
                        parameter=None
                        if search2!=[]:
                            reaction,parameter= search2[0]
                            local= '({}).{}'.format(reaction,parameter)
                    if k.attrib['name']=='StartValue':
                        if reaction != None and parameter !=None:
                            k.attrib['value']=str(float(self.param_df[local]))
        self.write_copasi_file(copasiML)
#=============================================

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='''
    \n\nInsert parameters from csv into into a copasi file. \
    Make sure the parameter file has ONLY the matrix of parameter \
    estimation resutls within \n 
    ''')
    parser.add_argument('copasi_file',help='Suply a Copasi_file')
    parser.add_argument('parameter_estimation_result_file',help='supply a properly formatted xlsx file containing copasi parameter estimation results')
    parser.add_argument('row',type=int,help='which row would you like to insert into copasi_file? (0 is the top row')
    parser.add_argument('-l',help='insert locals only',action='store_true')
    parser.add_argument('-g',help='insert globals only',action='store_true')
    parser.add_argument('-i',help='insert ICs only',action='store_true')
    parser.add_argument('-f',help='insert fit items only',action='store_true')   
    args = parser.parse_args()
    ICP=InsertCopasiParameters(args.copasi_file,args.parameter_estimation_result_file,args.row)   
    #ICP=InsertCopasiParameters(f,d,1)   
    
    if args.l==True:
        ICP.insert_local()
    if args.g==True:
        ICP.insert_global()
    if args.i==True:
        ICP.insert_ICs()
    if args.f==True:
        ICP.insert_fit_items()





