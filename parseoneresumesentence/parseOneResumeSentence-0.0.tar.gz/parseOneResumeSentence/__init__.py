def WHY_RESULT_DETAIL(df):       #the_db_v[:1000]
    df_final = pd.DataFrame(columns=['WHY','DETAIL','RESULT','desc'])
    for index,i in df.iterrows():
        print index, "out of", len(df)
        df_temp = pd.DataFrame(columns=['WHY','DETAIL','RESULT','desc'])
        
        NNP = i['NNP']
        NP_final = i['NP_final']
        
        PP = i['PP']
        VP = i['VP']
        SBAR = i['SBAR']

        ADJP = i['ADJP']
        ADVP = i['ADVP']
        CONJP = i['CONJP']
        #mixing_bowl = PP + VP + SBAR 

        WHY = []
        DETAIL = []
        RESULT = []
        #FINISHING = []

        ##################################
        # It's naive to classify result phrase based on it's starting words like "reducing"
        # Built a logistic regression model to predict the odds of a household reducing its frozen food consumption over timeless.
        ##################################


        for x1 in PP: 
            parsed = nltk.word_tokenize(x1)
            if x1.startswith(("of")):   # reallly, every "of" will be gone?
                pass
            elif x1.startswith(("in order to", "in an effort to" ,"due to", "for tracking", "for reporting")):
                WHY.append(x1)
            elif x1.startswith(("thereby","therefore", "yielding","resulted" ,"resulting",'which resulted','that enables','that provided','that provides','which allows','that increased','that raised','that enabled','which provides','which allowed','which reduced','that reduced','that helps','that led','that help','that helped','that provide','which improved','which led','which increased','which helped','that improved','that integrates','which provided','which enabled','which uses','that integrated','to ensure','that deliver','that drove','which enables','that generated')):    
                RESULT.append(x1)
            elif x1.startswith(("thereby", "resulting","achieving",'delivering','resulting','ensuring','improving','reducing','strengthening','enabling','increasing','adding','enhancing','producing','saving','bringing','promoting','expanding','capturing','minimizing','eliminating','consolidating','upgrading','securing','obtaining','acquiring','raising','boosting','cutting')):
                RESULT.append(x1)
            elif x1.startswith(("accodring to", "across", "for", "in", "including", "by",'that','which','how','where','while','who','when','what','whether','for','with','whose','after','until','why','since','like','whenever','project','on','once','wherein','of','whereby','using','through','but','if','as','even','though','internal','till','include','from','both','by','wherever',"accodring")): # SBAR_DETAIL
                DETAIL.append(x1)
            elif parsed[0][-3:] == 'ing':
                DETAIL.append(x1)
            elif hasNumbers(x1):
                DETAIL.append(x1)
                #FINISHING.append(x1)

        for x2 in VP:  
            parsed = nltk.word_tokenize(x2)
            x22 = x2.lower()
            ###########################################
            ### Don't convert x2 into LOWER CASE !! ### because?   -> using XXX is detail but some resume line starts with Using, Implementing
            ###########################################            
            if x22.startswith(("to", "in order to", "in an effort to" , "so that")):
                WHY.append(x2)
            # Verb that implies result


            # cutting but not cutting edge!
            # cutting cost, but not cutting-edge  <== where deep learning kicks in


            elif x22.startswith(("thereby","grow", "garnered","yielding","attracting","resulting","achieving",'delivering','resulting','ensuring','improving','improved','reducing','strengthening','enabling','increasing','adding','enhancing','producing','saving','bringing','promoting','expanding','capturing','minimizing','eliminating','consolidating','upgrading','securing','obtaining','acquiring','raising','boosting','cutting')):
                RESULT.append(x2)
            elif x22.startswith(("thereby","therefore", "enhanced","resulted" ,"reduced","resulting",'which resulted','that provided','that provides','which allows','that increased','that enabled','which provides','which allowed','which reduced','that reduced','that helps','that led','that help','that helped','that provide','which improved','which led','which increased','which helped','that improved','that integrates','which provided','which enabled','which uses','that integrated','to ensure','that deliver','that drove','which enables','that generated',"that allowed")):    
                RESULT.append(x2)
            elif parsed[0][-3:] == 'ing':
                DETAIL.append(x2)
            elif len(x2)> 90:
                pass
            #elif hasNumbers(x2):
                #FINISHING.append(x2)

        for x3 in SBAR: 
            x33=x3.lower()
            if len(x3)> 150:
                pass
            ##########################################
            # combining all wh+phrases + result_verb !       RESULT FIRST!!
            ########################################## 
            ### Linguist's help is much needed.
            elif x33.startswith(("thereby","therefore", "resulted" ,"resulting",'that raised','that enables','that increased',"which increased",'which resulted','that provided','that provides','which allows','that increased','that enabled','which provides','which allowed','which reduced','that reduced','that helps','that led','that help','that helped','that provide','which improved','which led','which increased','which helped','that improved','that integrates','which provided','which enabled','which uses','that integrated','to ensure','that deliver','that drove','which enables','that generated',"that allowed")):    
                RESULT.append(x3)



            elif x33.startswith(("thereby", "yielding","resulting","achieving",'delivering','resulting','ensuring','improving','reducing','strengthening','enabling','increasing','adding','enhancing','producing','saving','bringing','promoting','expanding','capturing','minimizing','eliminating','consolidating','upgrading','securing','obtaining','acquiring','raising','boosting','cutting')):
                RESULT.append(x3)
            elif x33.startswith(("to","in order to", "in an effort to" ,"because","so that")):
                WHY.append(x3)
            ### Come up with regex except for "to which":
            elif x33.startswith(('that','which','how','where','while','who','when','what','whether','for','with','whose','after','until','why','since','like','whenever','project','on','once','wherein','of','whereby','using','through','but','if','as','even','though','internal','till','include','from','both','by','wherever',"accodring")): # SBAR_DETAIL
                DETAIL.append(x3)
            #elif hasNumbers(x3):
                #FINISHING.append(x3)
        
        df_temp["desc"] = [i['desc']]
        df_temp["WHY"] = [WHY]
        df_temp['DETAIL'] = [DETAIL]
        df_temp['RESULT'] = [RESULT]
        df_final = df_final.append(df_temp,ignore_index=True)
    return df_final

