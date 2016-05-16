
# coding: utf-8

"""
Description:
    Purpose of this tool is to validate the tool.json file. The validation is done in terms of lexical best practices such as
    uppercasing, lowercasing, labels and important fields existance.

Options:

    --help 				Show this message.

    --version			Tool version.

    --json-file			path to json file.

Author:
    Mohamed Marouf, Bix team, SBG.

Last modified:
    Mohamed Marouf, 12/05/2016
"""

import json
import os
import sys
import argparse
import time



def save_query():
    user_input = query_yes_no('Do you want to save your changes in the json file?')
    if (user_input):
        return 0
    else:
        sys.stdout.write('Are you sure you want to discard your changes?')
        choice = raw_input().lower()
        if(choice in {'n','no'}):
            ret = save_query();
            while (ret==1):
                return 1;
            return ret;
        else:
            return 2



# ### Yes/No query
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


# ### Check label function

# label should be inserted, descriptive test
def check_label( string, entry, st_corr):

    Warning_no =0;

    #empty label
    if(not string or len(string)<4):
        if(st_corr==1):
            sys.stdout.write('The ' + entry + ' entry is empty or too short,please enter new more descriptive \n')
            string = raw_input()
            if ((not string) or (len(string) < 4)):
                print 'Warning: The ' + entry + ' entry is still empty or too short'
        else:
            Warning_no = Warning_no+1
            print 'Warning: The ' + entry + ' entry is empty or too short'

    else:
        # starting with lowercase
        if (string and string[0].islower()):
            if(st_corr==1):
                string = string.capitalize()
            else:
                Warning_no = Warning_no + 1
                print 'Warning: The ' + entry + ' entry started with lower case letter'


        # full stop removal
        if (string and string[-1]=='.'):
            if(st_corr==1):
                string = string[0:-1]
            else:
                Warning_no = Warning_no + 1
                print 'Warning: The ' + entry + ' entry ended with full stop.'

    if (st_corr == 1):
        return string
    else:
        return Warning_no


# ### Tool Description
def check_desc( string, entry,st_corr):

    Warning_no = 0

    #empty desc
    if(not string or  len(string)<5):
        if(st_corr==1):
            sys.stdout.write('Warning: The ' + entry + ' entry is empty ,please enter new description: \n')
            string = raw_input()
            if ((not string) or (len(string) < 5)):
                print 'Warning: The ' + entry + ' entry is still empty or too short'
            else:
                # starting with lowercase
                if (string[0].islower()):
                    if (st_corr == 1):
                        string = string.capitalize()
                    else:
                        Warning_no = Warning_no + 1
                        print 'Warning: The ' + entry + ' entry started with lower case letter'

                # full stop removal
                if (string and string[-1] != '.'):
                    if (st_corr == 1):
                        string = string + '.'
                    else:
                        Warning_no = Warning_no + 1
                        print 'Warning: The ' + entry + ' entry has no full stop'
        else:
            Warning_no = Warning_no + 1
            print 'Warning: The ' + entry + ' entry is empty or too short'




    else:
        # starting with lowercase
        if (string[0].islower()):
            if(st_corr==1):
                string = string.capitalize()
            else:
                Warning_no = Warning_no + 1
                print 'Warning: The ' + entry + ' entry started with lower case letter'

        # full stop removal
        if (string and string[-1]!='.'):
            if(st_corr==1):
                string = string+'.'
            else:
                Warning_no = Warning_no + 1
                print 'Warning: The ' + entry + ' entry has no full stop'

    if (st_corr == 1):
        return string
    else:
        return Warning_no


# ###Tool Author

def check_auth( string,st_corr):

    Warning_no = 0

    #empty author
    if(not string or len(string)<3):
        if(st_corr==1):
            sys.stdout.write('The author entry is empty, please enter new author(s)\n')
            string = raw_input()
            if ((not string) or (len(string) < 2)):
                print 'Warning: The author entry is still empty'

            # starting with lowercase
            string = string.capitalize()
        else:
            Warning_no = Warning_no + 1
            print 'Warning: The author entry is empty'
            if(string and string.islower(string[0])):
                Warning_no = Warning_no + 1
                print 'Warning: The author entry started with lowercase'

    if (st_corr == 1):
        return string
    else:
        return Warning_no


# ### check empty fields

def check_field( string, entry, st_corr):

    Warning_no = 0

    #empty desc
    if(not string or len(string)==0):
        if(st_corr==1):
            sys.stdout.write('The field ' +  entry + ' is empty, please insert new one\n')
            string = raw_input()
            if ((not string) or (len(string) < 2)):
                print 'Warning: The field '+ entry + ' is still empty'
        else:
            Warning_no = Warning_no + 1
            print 'Warning: The field ' +  entry + ' is empty'

    if (st_corr == 1):
        return string
    else:
        return Warning_no


# ### Check the input file type

def check_file_type( string,st_corr):

    Warning_no = 0

    #empty file type
    if(not string or len(string)==0):
        if(st_corr==1):
            sys.stdout.write('The file type is empty, please insert new file type\n')
            string = raw_input()
            if((not string) or (len(string)<2)):
                print 'Warning: The file type is still empty'
        else:
            Warning_no = Warning_no + 1
            print 'Warning: The file type is empty'

    if(st_corr==1):
        string = string.replace('|',',')
        string = string.replace('&',',')
        string = string.replace('+',',')

    if (st_corr == 1):
        return string
    else:
        return Warning_no


# ### Check links
def check_link( link_label, link_id,st_corr):

    Warning_no = 0

    #empty desc
    if((not link_id) or len(link_id)==0):
        if(st_corr==1):
            user_input = query_yes_no('The link ' +  link_label + ' is empty, would you like fill it?')
            if(user_input):
                sys.stdout.write('Please enter new\t '+ entry+ ': \n')
                string = raw_input()
            if((not user_input) or (len(string)==0)):
                print 'Warning: The tool\'s ' + link_label + ' is still empty'
        else:
            Warning_no = Warning_no + 1
            print 'Warning: The link ' +  link_label + ' is empty'
    else:
        string = link_id

    if (st_corr == 1):
        return string
    else:
        return Warning_no


def main():

    # parase arguments
    parser = argparse.ArgumentParser(prog='json_validation.py',description= "Purpose of this tool is to validate the tool."
                                     "json file. The validation is done in terms of lexical best practices such as uppercasing, lowercasing, labels and important fields existance.")
    parser.add_argument('--version', '-v','-V', action='version', version='%(prog)s 0.1.5')
    parser.add_argument('--json', '-j','-J', metavar='path/file_name.json', type=str, help='The json file to be validated')
    parser.add_argument('--report', '-r','-R' ,action='store_true', help= 'This is used to creat the report.txt file. This is default option.')
    parser.add_argument('--correct', '-c', '-C',action='store_true', help= 'This is used to correct the json file using stin, stdout prompts')


    args = parser.parse_args()
    if(args.json):
        with open(args.json) as file:
            json_file = str(args.json)
    else:
        print 'Please enter the file name of json file'
        return

    #in case report parameter is used the script will creat a report.txt file

    if (args.correct and (not args.report) ):
        st_corr = 1
    else:
        st_corr = 0



        # Print the header of this report
        sys.stdout.write('\nPlease enter your name to be inserted in the report:\n')
        user_name = raw_input()

        sys.stdout = open(json_file+'.report.txt', 'w')
        print "\nThis report is created by:" + user_name +'\n'
        print "Current date & time " + time.strftime("%d/%m/%Y") + ' '+time.strftime("%I:%M:%S")
        print "---------------------------------------------------------------------------------"


    # ### Read the Json file content

    # type 0 if yout want only report from json file and 1 if you want to edit it

    json_data=open(json_file).read()

    # read the json content as list of json main entries #
    json_content = json.loads(json_data)

    wf_flag = False
    tested_json = "tool's"
    if(json_content["class"] == "Workflow"):
        wf_flag = True
        tested_json = "workflow's"


    # ###For integers ranking
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])




    # ### print the Json entries statistics
    print '\nThe '+ tested_json +' '+ json_content['id'] + ' has:\n'
    # check the inputs and print their No.
    if not json_content.has_key('inputs'):
        input_fields_NO = 0
    else:
        input_fields_NO = len(json_content['inputs'])

    print str(input_fields_NO) + '\t inputs fields'


    # check the outputs and print their No.
    if not json_content.has_key('outputs'):
        output_fields_NO = 0
    else:
        output_fields_NO = len(json_content['outputs'])

    print str(output_fields_NO) + '\t output fields\n'



    if not wf_flag:
        # check tool's docker
        print '\n----------Tool\'s docker image is being processed--------------'
        hints = list(json_content["hints"])
        for item in hints:
            if (item.has_key('dockerPull')):
                if(not item.has_key("dockerPull")):
                    print "Warning, the dokcer image is not set \n"
                else:
                    docker_img = item["dockerPull"]
                    if(not docker_img.split(":")[0].split("/")[0] == "images.sbgenomics.com"):
                        print "Warning, your image repository should be images.sbgenomics.com/user_name/toolkit_name:version"
                    print ' The tool\'s dokcer image is Ok!'
            

    # ### label, author, and description

    # check tool label
    print '\n----------The '+ tested_json + ' label is being processed--------------'
    if not json_content.has_key('label'):
        new_label = check_label('', 'label',st_corr)
    else:
        new_label = check_label(json_content['label'], 'label', st_corr)
    if(st_corr):
        json_content.update({'label': new_label})
    else:
        if(new_label==0):
            print ' The '+ tested_json + ' label is Ok!'


    # check tool's description
    print '\n----------The '+ tested_json + ' description is being processed ----------'
    if not json_content.has_key('description'):
        new_desc = check_desc('', json_content.has_key('id'), 'description',st_corr)
    else:
        new_desc = check_desc( json_content['description'], 'description',st_corr)
    if(st_corr):
        json_content.update({'description': new_desc})
    else:
        if(new_desc==0):
            print ' The '+ tested_json + ' description is Ok!'




    # check tool's Author
    print '\n----------The '+ tested_json + ' author is  being processed---------- '
    if not json_content.has_key('sbg:toolAuthor'):
        new_auth = check_auth('',st_corr)
    else:
        new_auth = check_auth(json_content['sbg:toolAuthor'],st_corr)

    if(st_corr):
        json_content.update({'sbg:toolAuthor': new_auth})
    else:
        if(new_auth==0):
            print ' The '+ tested_json + ' author is Ok!'



    # check tool's sbg:toolkit
    print '\n----------The '+ tested_json + ' toolkit is  being processed----------'
    if not json_content.has_key('sbg:toolkit'):
        new_field = check_field('', 'sbg:toolkit', st_corr)
    else:
        new_field = check_field(json_content['sbg:toolkit'], 'sbg:toolkit',st_corr)

    if(st_corr):
        json_content.update({'sbg:toolkit': new_field})
    else:
        if (new_field == 0):
            print 'The '+ tested_json +' toolkit is Ok!'


    # check tool's version
    print  '\n----------The '+ tested_json + ' toolkitVersion is  being processed----------'
    if not json_content.has_key('sbg:toolkitVersion'):
        new_field = check_field('', 'sbg:toolkitVersion',st_corr)
    else:
        new_field = check_field(json_content['sbg:toolkitVersion'], 'sbg:toolkitVersion',st_corr)
    if(st_corr):
        json_content.update({'sbg:toolkitVersion': new_field})
    else:
        if (new_field == 0):
            print ' The '+ tested_json + ' toolkitVersion is Ok!'


    # check tool's sbg:license
    print '\n----------The '+ tested_json + ' license is  being processed---------- '
    if not json_content.has_key('sbg:license'):
        new_field = check_field('', 'sbg:license',st_corr)
    else:
        new_field = check_field(json_content['sbg:license'], 'sbg:license',st_corr)

    if(st_corr):
        json_content.update({'sbg:license': new_field})
    else:
        if (new_field == 0):
            print 'The '+ tested_json + ' toolkitVersion is Ok!'


    # check tool's sbg:categories
    print '\n----------The '+ tested_json + ' categories is  being processed---------- '
    if not json_content.has_key('sbg:categories'):
        new_field = check_field('', 'sbg:categories',st_corr)
    else:
        new_field = check_field(json_content['sbg:categories'], 'sbg:categories',st_corr)
    if(st_corr):
        json_content.update({'sbg:categories': new_field})
    else:
        if (new_field == 0):
            print 'The '+ tested_json + ' categories is Ok!'

    # ### Check tool's links
    # check tool's sbg:links
    print '\n----------The '+ tested_json + ' links is  being processed ----------'
    if not json_content.has_key('sbg:links'):
        print 'Warning: The '+ tested_json + ' additional links are empty, it is best practice to add:\n (1)Homepage,    \n (2)Source Code,\n (3) Download, and \n (4)Publication\n'
        links_NO = 0
    else:
        links_NO = len(json_content['sbg:links'])

        # Check the existance of best practice links
        best_practice_links = ['homepage','source code','download','publication','wiki']
        for i in range(0,links_NO):
            if(st_corr==1):
                json_content['sbg:links'][i]['id'] = check_link( json_content['sbg:links'][i]['label'], json_content['sbg:links'][i]['id'],st_corr)
                print json_content['sbg:links'][i]['label']+ '\t' + '\t is processed'

            link_label = json_content['sbg:links'][i]['label']

            if(link_label.lower() in best_practice_links):
                if(st_corr==1):
                    json_content['sbg:links'][i]['label'] = link_label.capitalize()

                best_practice_links.remove(link_label.lower() )

        if(len(best_practice_links)!=0):
            for i in range(0,len(best_practice_links)):
                print 'Warning: The '+ tested_json + ' does not have: \t' + str(best_practice_links[i].capitalize()) + ' or it is not labeled correctly.'
        else:
            print json_content['sbg:links'][i]['label']
            print json_content['sbg:links'][i]['id']
            print 'The '+ tested_json + ' links are Ok!'



    # ### Check the inputs
    if not wf_flag:
        print '\n\n**********************************************************************'
        print 'Tool\'s input fields is being processed...'
        print '**********************************************************************\n'

        # check the inputs
        for i in range(0,input_fields_NO):

            #in case some ID revision is needed
            print  json_content['inputs'][i]['id']  + ' \t is being processed ...\n'

            #input label
            if(not json_content['inputs'][i].has_key('label')):
                new_label = check_label('', 'label',st_corr)
            else:
                new_label = check_label(json_content['inputs'][i]['label'],'label',st_corr)
            if(st_corr == 1):
                json_content['inputs'][i].update({'label': new_label})
            else:
                if(new_label == 0):
                    print 'the input label is OK!\n'


            #input description
            if(not json_content['inputs'][i].has_key('description')):
                new_desc = check_desc('', 'description',st_corr)
            else:
                new_desc = check_desc(json_content['inputs'][i]['description'], 'description',st_corr)
            if(st_corr == 1):
                json_content['inputs'][i].update({'description': new_desc})
            else:
                if (new_desc == 0):
                    print 'the input  description is OK!\n'


            # parser the type entry
            if (len(json_content['inputs'][i]['type'])==1):
                # the file is required
                input_type = json_content['inputs'][i]['type'][0]
            #the input parameter is not required
            else:
                # the input paramter is boolean, int, string, File,double, long or float
                if(len(json_content['inputs'][i]['type'][1])==1):
                    input_type = json_content['inputs'][i]['type'][1]
                #the input parameter is enum, array,map , or record
                else:
                    if( type(json_content['inputs'][i]['type'][1])==unicode):
                        input_type = json_content['inputs'][i]['type'][1]
                    else:
                        input_type = json_content['inputs'][i]['type'][1]['type']


            # in case it is file or files array
            if ( ((input_type == 'array') and (json_content['inputs'][i]['type'][1].get('items') == 'File') ) or (input_type == 'File')):
                if (not json_content['inputs'][i].has_key('sbg:fileTypes')):
                    new_file_type = check_file_type('', st_corr)
                else:
                    #separator should be ',' without space or |
                    new_file_type = check_file_type(json_content['inputs'][i]['sbg:fileTypes'], st_corr)

                if(st_corr == 1):
                    json_content['inputs'][i].update({'sbg:fileTypes': new_file_type})
                else:
                    if (new_file_type == 0):
                        print 'the input file type description is OK!\n'



            # print the sbg:category and show Warnings and suggestions of category
            if (not json_content['inputs'][i].has_key('sbg:category')):
                # It should be File input
                # print   "The input category" +json_content['inputs'][i]['id']+  " is prefered to be:\n\
                # File input: for input files needed by the tool\n\
                # Configuration: for paramters used to control the tool execution and options\n\
                # Execution paramter : for parameters used by the platform computation engine (e.g. total_memory, threads )\n "
                if (((input_type == 'array') and (json_content['inputs'][i]['type'][1].get('items') == 'File')) or (input_type == 'File')):
                    if (st_corr == 1):
                        new_field = 'File input'
                    else:
                        new_field = check_field('', 'category', st_corr)
                else:
                    new_field = check_field('', 'category', st_corr)
            else:
                # Warning there is no file category
                # print  " The input category \t " + json_content['inputs'][i]['id'] +  " is prefered to be:\n\
                # File input: for input files needed by the tool\n\
                # Configuration: for paramters used to control the tool execution and options\n\
                # Execution paramter : for parameters used by the platform computation engine (e.g. total_memory, threads)\n"
                if (((input_type == 'array') and (json_content['inputs'][i]['type'][1].get('items') == 'File')) or (input_type == 'File')):
                    if (st_corr == 1):
                        new_field = 'File input'
                    else:
                        new_field = check_field(json_content['inputs'][i]['sbg:category'], ' category ', st_corr)
                else:
                    new_field = check_field(json_content['inputs'][i]['sbg:category'], 'category', st_corr)

            if (st_corr == 1):
                json_content['inputs'][i].update({'sbg:category': new_field})
            else:
                if (new_field == 0):
                    print 'the input category is OK!\n'



                # Other fields from input as file or array
                #json_content['inputs'][i]['inputBinding']['secondaryFiles']
                #json_content['inputs'][i]['sbg:stageInput'

            # Other filed could be later checked
            #json_content['inputs'][i]['inputBinding']['sbg:cmdInclude']
            #json_content['inputs'][i]['inputBinding']['secondaryFiles']
            #json_content['inputs'][i]['inputBinding']['position']
            #json_content['inputs'][i]['inputBinding']['valueFrom']
            #json_content['inputs'][i]['sbg:toolDefaultValue']
            print '-------------------------------------------\n'



        # ### check the outputs

        # In[132]:

        print '\n\n**********************************************************************'
        print 'Tool\'s output fields is being processed...'
        print '**********************************************************************'

        for i in range(0,output_fields_NO):
            #in case some ID revision is needed
            print  json_content['outputs'][i]['id']  + '\t is being processed...\n'

            #output label
            if(not json_content['outputs'][i].has_key('label')):
                new_label = check_label('', 'label',st_corr)
            else:
                new_label = check_label(json_content['outputs'][i]['label'], 'label',st_corr)

            if(st_corr==1):
                json_content['outputs'][i].update({'label': new_label})
            else:
                if (new_label == 0):
                    print 'the output label is OK!\n'



            #output description
            if(not json_content['outputs'][i].has_key('description')):
                new_desc = check_desc('', 'description',st_corr)
            else:
                new_desc = check_desc(json_content['outputs'][i]['description'], 'description',st_corr)

            if(st_corr==1):
                json_content['outputs'][i].update({'description': new_desc})
            else:
                if (new_desc == 0):
                    print 'the output description is OK!\n'

            # parser the type entry
            if (len(json_content['outputs'][i]['type'])==1):
                # the file is required
                output_type = json_content['outputs'][i]['type'][0]
            #the input parameter is not required
            else:
                # the input paramter is boolean, int, string, File,double, long or float
                if(len(json_content['outputs'][i]['type'][1])==1):
                    output_type = json_content['outputs'][i]['type'][1]
                #the input parameter is enum, array,map , or record
                else:
                    if( type(json_content['outputs'][i]['type'][1])==unicode):
                        output_type = json_content['outputs'][i]['type'][1]
                    else:
                        output_type = json_content['outputs'][i]['type'][1]['type']



            # in case it is file or files array
            if ( ((output_type == 'array') and (json_content['outputs'][i]['type'][1].get('items') == 'File') ) or (output_type == 'File')):
                if (not json_content['outputs'][i].has_key('fileTypes')):
                    new_file_type = check_file_type('', st_corr)
                else:
                    #separator should be ',' without space or |
                    new_file_type = check_file_type(json_content['outputs'][i]['fileTypes'],st_corr)

                if(st_corr==1):
                    json_content['outputs'][i].update({'fileTypes': new_file_type})
                else:
                    if (new_file_type == 0):
                        print 'the output fileTypes is OK!\n'


            print '------------------------------------------------------------\n'


    # ### save the json dictionary structure back to json

    # In[133]:
    if(st_corr==1):
        json_file_name = str(json_file)
        pos = json_file_name.rfind('.')
        new_json_file = json_file_name[0:pos] + '_new.json'
        if save_query()==0:
            with open(new_json_file, 'w') as fp:
                json.dump(json_content, fp, sort_keys=True, indent=4)
            sys.stdout.write('Your changes is saved to '+ new_json_file +' and a report is generated for it \n')
            os.system("SBG_CWL_validation --json " + new_json_file + " -R")

        else:
             print 'Your changes are discarded'



if __name__ == '__main__':
    main()