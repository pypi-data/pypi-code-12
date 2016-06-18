#just_dummy = pd.get_dummies(list_icn, dummy_na=True)
#pd.get_dummies(X, dummy_na=True)
#just_dummy1 = pd.get_dummies(list_ico, dummy_na=True)
####################
#Creating Dummies
####################
#FOR ICN VARIABLES
df = pd.DataFrame(df)
just_dummies = pd.get_dummies(df['icn_var_22'],prefix=['icn1'])
just_dummies1 = pd.get_dummies(df['icn_var_23'],prefix=['icn2'])
just_dummies2 = pd.get_dummies(df['icn_var_24'],prefix=['icn3'])
step_1 = pd.concat([df, just_dummies,just_dummies1,just_dummies2], axis=1) 
#DROP of initioals columns
step_1.drop(['icn_var_22', 'icn_var_23','icn_var_24'], inplace=True, axis=1)
#FOR ICO VARIABLES
just_dummies3 = pd.get_dummies(df['ico_var_25'],prefix=['ico1'])
just_dummies4 = pd.get_dummies(df['ico_var_26'],prefix=['ico2'])
just_dummies5 = pd.get_dummies(df['ico_var_27'],prefix=['ico3'])
just_dummies6 = pd.get_dummies(df['ico_var_28'],prefix=['ico4'])
just_dummies7 = pd.get_dummies(df['ico_var_29'],prefix=['ico5'])
just_dummies8 = pd.get_dummies(df['ico_var_30'],prefix=['ico6'])
just_dummies9 = pd.get_dummies(df['ico_var_31'],prefix=['ico7'])
just_dummies10 = pd.get_dummies(df['ico_var_32'],prefix=['ico8'])
just_dummies11 = pd.get_dummies(df['ico_var_33'],prefix=['ico9'])
just_dummies12 = pd.get_dummies(df['ico_var_34'],prefix=['ico10'])
just_dummies13 = pd.get_dummies(df['ico_var_35'],prefix=['ico11'])
just_dummies14 = pd.get_dummies(df['ico_var_36'],prefix=['ico12'])
just_dummies15 = pd.get_dummies(df['ico_var_37'],prefix=['ico13'])
just_dummies16 = pd.get_dummies(df['ico_var_38'],prefix=['ico14'])
just_dummies17 = pd.get_dummies(df['ico_var_39'],prefix=['ico15'])
just_dummies18 = pd.get_dummies(df['ico_var_40'],prefix=['ico16'])
just_dummies19 = pd.get_dummies(df['ico_var_41'],prefix=['ico17'])
just_dummies20 = pd.get_dummies(df['ico_var_42'],prefix=['ico18'])
just_dummies21 = pd.get_dummies(df['ico_var_43'],prefix=['ico19'])
just_dummies22 = pd.get_dummies(df['ico_var_44'],prefix=['ico20'])
just_dummies23 = pd.get_dummies(df['ico_var_45'],prefix=['ico21'])
just_dummies24 = pd.get_dummies(df['ico_var_46'],prefix=['ico22'])
just_dummies25 = pd.get_dummies(df['ico_var_47'],prefix=['ico23'])
just_dummies26 = pd.get_dummies(df['ico_var_48'],prefix=['ico24'])
just_dummies27 = pd.get_dummies(df['ico_var_49'],prefix=['ico25'])
just_dummies28 = pd.get_dummies(df['ico_var_50'],prefix=['ico26'])
just_dummies29 = pd.get_dummies(df['ico_var_51'],prefix=['ico27'])
just_dummies30 = pd.get_dummies(df['ico_var_52'],prefix=['ico28'])
just_dummies31 = pd.get_dummies(df['ico_var_53'],prefix=['ico29'])
just_dummies32 = pd.get_dummies(df['ico_var_54'],prefix=['ico30'])
just_dummies33 = pd.get_dummies(df['ico_var_55'],prefix=['ico31'])
just_dummies34 = pd.get_dummies(df['ico_var_56'],prefix=['ico32'])
just_dummies35 = pd.get_dummies(df['ico_var_57'],prefix=['ico33'])
just_dummies36 = pd.get_dummies(df['ico_var_58'],prefix=['ico34'])
just_dummies37 = pd.get_dummies(df['ico_var_59'],prefix=['ico35'])
just_dummies38 = pd.get_dummies(df['ico_var_60'],prefix=['ico36'])
just_dummies39 = pd.get_dummies(df['ico_var_61'],prefix=['ico37'])
just_dummies40 = pd.get_dummies(df['ico_var_62'],prefix=['ico38'])
just_dummies41 = pd.get_dummies(df['ico_var_63'],prefix=['ico39'])
just_dummies42 = pd.get_dummies(df['ico_var_64'],prefix=['ico40'])
#CONATINATIONG TWO NEW TABLES
step_2 = pd.concat([step_1, just_dummies3,just_dummies4,just_dummies5,just_dummies6,just_dummies7,just_dummies8,just_dummies9,just_dummies10,just_dummies11,just_dummies12,just_dummies13
                   ,just_dummies14,just_dummies15,just_dummies16,just_dummies17,just_dummies18,just_dummies19,just_dummies20,just_dummies21,just_dummies22
                   ,just_dummies23,just_dummies24,just_dummies25,just_dummies26,just_dummies27,just_dummies28,just_dummies29,just_dummies30,just_dummies31,just_dummies32,just_dummies33,just_dummies34,
                   just_dummies35,just_dummies36,just_dummies37,just_dummies38,just_dummies39,just_dummies40,just_dummies41,just_dummies42], axis=1)   
#DROP of initioals columns
step_2.drop(['ico_var_25',
 'ico_var_26',
 'ico_var_27',
 'ico_var_28',
 'ico_var_29',
 'ico_var_30',
 'ico_var_31',
 'ico_var_32',
 'ico_var_33',
 'ico_var_34',
 'ico_var_35',
 'ico_var_36',
 'ico_var_37',
 'ico_var_38',
 'ico_var_39',
 'ico_var_40',
 'ico_var_41',
 'ico_var_42',
 'ico_var_43',
 'ico_var_44',
 'ico_var_45',
 'ico_var_46',
 'ico_var_47',
 'ico_var_48',
 'ico_var_49',
 'ico_var_50',
 'ico_var_51',
 'ico_var_52',
 'ico_var_53',
 'ico_var_54',
 'ico_var_55',
 'ico_var_56',
 'ico_var_57',
 'ico_var_58',
 'ico_var_59',
 'ico_var_60',
 'ico_var_61',
 'ico_var_62',
 'ico_var_63',
 'ico_var_64'], inplace=True, axis=1)
step_2

#####################
#Creating Bins
#####################
#bins = [-.1, .2, .3, .4, 2]
bins = [-1.,   0.,   1., 2.,3.]
group_names = ['1', '2', '3', '4']
for i in range(len(df.columns)-1,0,-1):
    if df.iloc[:,i].min()==0 and df.iloc[:,i].max()==1:
        
        df[i] = pd.cut(df.iloc[:,i], bins, labels=group_names)
        #pd.value_counts(df[" ib_var_12_bin"]).plot.bar()
df
