from distutils.core import setup



#version
MAJOR = 1
MINOR = 2
MICRO = 1
__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

setup(
  name = 'pydentify',
  packages = ['pydentify'], # this must be the same as the name above
  version = __version__,
  description = 'A python module for performing identifiability analysis using copasi',
  author = 'Ciaran Welh',
  requires=['lxml','argparse','pandas','numpy','scipy','matplotlib.pyplot'],
  package_data={'pydentify': ['Documentation/*.pdf','Documentation/*.html','*.7z']},#,'Examples':['*.pdf' ,'*.txt' ,'*.cps' ,'*.py', '*.jpeg' ,'*.png', '*.tiff']},
  author_email = 'c.welsh2@newcastle.ac.uk',
  url = 'https://github.com/b3053674/pydentify', # use the URL to the github repo
#  download_url = 'https://github.com/b3053674/pydentify/tarball/0.1',
  keywords = ['systems biology','modelling','biological','networks','copasi','identifiability analysis','profile likelihood'],
  include_package_data=False,
  licence='go for it',
  platform=['windows','linux'],
  long_description='''
  
Installation 

Use:
    pip install pydentify 
at command prompt or download and use:
    >>>python setup.py install 
from the downloaded directory
  
  
Author: Ciaran Welsh. Email: c.welsh2@newcastle.ac.uk

Pydentify is a python package intended for use by systems biologists that 
are looking to fit experimental data to their models. Because of the dimensionality of the
models in question the optimization process is diffult. Often parameters
cannot be uniquely defined by the optimization problem. This is called a non-identifiability. 
COPASI (Mendes et al 2009) is a software package that enables one to easily perform parameter estimation. 
Pydentify uses COPASI as a 'parameter estimation engine' in order to calculate the profile likelihood 
method of identifiability analysis (Schaber, Biosystems 20012). 


Instructions 


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

#Note that for some reason this program will not run from a Dropbox (or similar) directory
    
#Also, if you have to stop running the script half way through and attempt to restart, 

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

    References
    Mendes, P., Hoops, S., Sahle, S., Gauges, R., Dada, J. and Kummer, U. (2009) 'Computational modeling of biochemical networks using COPASI', Systems Biology, pp. 17-59.
    Schaber, J. (2012) 'Easy parameter identifiability analysis with COPASI', Biosystems, 110(3), pp. 183-185.
''')