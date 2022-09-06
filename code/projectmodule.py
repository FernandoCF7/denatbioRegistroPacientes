from pandas import read_csv as pd_read_csv, concat as pd_concat, isnull as pd_isnull, Index as pd_Index, DataFrame as pd_DataFrame, ExcelWriter as pd_ExcelWriter, Series as pd_Series
from os import path as os_path
from numpy import any as np_any, prod as np_prod, array as np_array, NaN as np_NaN, argwhere as np_argwhere, where as np_where
from re import compile as re_compile, IGNORECASE as re_IGNORECASE
from time import strftime as time_strftime
from unicodedata import normalize as unicodedata_normalize
from sys import exit as sys_exit
from copy import deepcopy as copy_deepcopy

#inline excell files
orig_url = 'https://github.com/FernandoCF7/denatbioRegistroPacientes/blob/main/'

#-----------------------------------------------------------------------------#
#setting variables from settings
def set_projectmodule_parameters(currentPath, inlineEF):

    #read pd_listExam file
    set_pd_listExam(currentPath, inlineEF)

    #read clavesNombresEmpresa file
    set_df_enterpriseNames(currentPath, inlineEF)

    #read codeEnterprise file
    set_codeEnterpriseFile(currentPath, inlineEF)

#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read registro file
def get_csvFile(currentPath, yymmddPath):
    
    filePath_registro = os_path.join("{0}","..","DB_ingresoPorVoz","{1}.txt").format(
        currentPath,yymmddPath)

    csvFile = (pd_read_csv(filePath_registro,sep='*', dtype={2: str}))

    csvFile.columns = ["firstName","secondName",'thirdName']

    #set as upper
    csvFile["firstName"]=csvFile["firstName"].str.upper()
    csvFile["secondName"]=csvFile["secondName"].str.upper()

    #quit blank's begin and end
    csvFile["firstName"] = csvFile["firstName"].str.strip()
    csvFile["secondName"] = csvFile["secondName"].str.strip()
    csvFile["thirdName"] = csvFile["thirdName"].str.strip()
    

    #enmascarar las Ñ´s con @@´s
    for idx, val in enumerate(csvFile["firstName"]):
        csvFile["firstName"][idx] = csvFile["firstName"][idx].replace("Ñ","@@")
        csvFile["secondName"][idx] = csvFile["secondName"][idx].replace("Ñ","@@")
    
    #set without acents
    csvFile["firstName"] = csvFile["firstName"].str.normalize('NFKD').str.encode(
        'ascii', errors='ignore').str.decode('utf-8')
    csvFile["secondName"] = csvFile["secondName"].str.normalize('NFKD').str.encode(
        'ascii', errors='ignore').str.decode('utf-8')

    #re-establecer las @@´s como Ñ´s
    for idx, val in enumerate(csvFile["firstName"]):
        csvFile["firstName"][idx] = csvFile["firstName"][idx].replace("@@","Ñ")
        csvFile["secondName"][idx] = csvFile["secondName"][idx].replace("@@","Ñ")
    
    return csvFile
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read pd_listExam file
def set_pd_listExam(currentPath, inlineEF):
    
    global pd_listExam

    if inlineEF:
        filePath_listExam = ("{0}"+"listadoDeExamenes/listExam.csv?raw=true").format(orig_url)
    else:
        filePath_listExam = os_path.join("{0}","..","listadoDeExamenes",
                                    "listExam.csv").format(currentPath)

    pd_listExam = (pd_read_csv(filePath_listExam, usecols=["COD INT","EXAMEN"]))

    #set index of pd_listExam as COD INT column
    pd_listExam.set_index("COD INT", inplace=True)


    #read listExam locally file
    filePath_listExam_tmp = os_path.join("{}","..","altas","listExam.csv").format(currentPath)
    listExam_locally = pd_read_csv(filePath_listExam_tmp, usecols=["COD INT","EXAMEN"])

    listExam_locally.set_index("COD INT", inplace=True)

    # append listExam_locally to pd_listExam
    for idx, row in listExam_locally.iterrows():
        
        if idx in pd_listExam.index:#update the Exam
            pd_listExam.EXAMEN[idx] = row["EXAMEN"]
        # else:#append examn
        #     pd_listExam = pd_concat([pd_listExam, listExam_locally.loc[idx]], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read clavesNombresEmpresa file
def set_df_enterpriseNames(currentPath, inlineEF):

    global df_enterpriseNames

    if inlineEF:
        filePath_clavesNombresEmpresa = ("{0}"+"empresas/clavesNombresEmpresa.csv?raw=true").format(orig_url)
        
    else:
        filePath_clavesNombresEmpresa = os_path.join("{0}","..","empresas", "clavesNombresEmpresa.csv").format(currentPath)

    df_enterpriseNames = pd_read_csv(filePath_clavesNombresEmpresa, keep_default_na=False)

    #set index of enterpriseNames as clave column
    df_enterpriseNames.set_index("clave", inplace=True)

    #read clavesNombresEmpresa locally file
    filePath_clavesNombresEmpresa_tmp = os_path.join("{}","..","altas","clavesNombresEmpresa.csv").format(currentPath)
    clavesNombresEmpresa_locally = pd_read_csv(filePath_clavesNombresEmpresa_tmp, encoding='latin-1', keep_default_na=False)

    clavesNombresEmpresa_locally.set_index("clave", inplace=True)

    #Concatenated df_enterpriseNames and clavesNombresEmpresa_locally
    df_enterpriseNames = pd_concat([df_enterpriseNames, clavesNombresEmpresa_locally], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#search for enterprise; extract index of the enterprises
def get_idx_enterprise(csvFile_firstName):

    idx_enterprise = []
    patern = re_compile(r'/.*?/')

    for idx, val in enumerate(csvFile_firstName):#for each field
        
        #search for "EMPRESA" word
        if val.find("EMPRESA") != -1:
            idx_enterprise.append(idx)

    return idx_enterprise
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#check fill values in all patients entries
def checkFilledfiels(columnIdx, csvFile, idx_patients):
    
    if np_any(pd_isnull(csvFile.iloc[idx_patients,columnIdx])) or np_any(csvFile.iloc[idx_patients,columnIdx]==""):
        
        tmp = np_where(pd_isnull(csvFile.iloc[idx_patients,columnIdx]))
        
        if not(np_any(tmp)):
            tmp = np_where(csvFile.iloc[idx_patients,columnIdx]=="")

        infoPatients = csvFile.iloc[idx_patients[tmp],:]
        sys_exit("""Registro no valido para el (los) paciente(s):\n {0}""".format(infoPatients))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get enterprise names and codecs
def get_enterpriseNames(OSR, csvFile, idx_enterprise):
    #idx_enterprise --> array, index of enterprice at CSV file
    
    patern = re_compile(r'/.*?/')

    enterpriseNames = []
    enterpriseCodecs = []
    
    for val in idx_enterprise:#for each enterprise
        
        #get the enterprise name
        enterprise_name = patern.search(csvFile["firstName"][val]).group()
        
        #search enterprise_name in codeEnterpriseFile
        logicTMP = enterprise_name == codeEnterpriseFile['empresa'].str.upper()
        
        #not defined enterprise mesage error
        if not(any(logicTMP)):
            print('''OPERACION FALLIDA\nEmpresa no definida: {0} en el archivo \
    codeEnterprise.csv; folio OSR: {1}'''.format(enterprise_name,OSR[val]))
            sys_exit("")
        
        #get enterprise code of clavesNombresEmpresa
        try:
            enterprise_code = codeEnterpriseFile.clave[logicTMP==True].item()
        except ValueError:
            print("""OPERACION FALLIDA\nLa empresa {0} se encuentra definida más \
    de una vez de la misma manera en el archivo codeEnterprise.csv""".format(
    enterprise_name))
            sys_exit()
            
        #append enterpriseCodecs
        enterpriseCodecs.append(enterprise_code)
        
        #append enterprise_code
        enterpriseNames.append(df_enterpriseNames.loc[enterprise_code].item())

    return enterpriseNames, enterpriseCodecs
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise names and codecs forExclusiveExcel
def get_enterpriseNames_exclusiveExcel(exel_enterprises):
    
    enterpriseNames_forExclusiveExcel = []
    enterpriseCodecs_forExclusiveExcel = []
    
    for enterprise_name_ in exel_enterprises:
            
        #set as upper
        enterprise_name = enterprise_name_.upper()
    
        #enmascarar las Ñ´s con @@´s
        enterprise_name = enterprise_name.replace("Ñ","@@")
        
        #set without acents
        enterprise_name = unicodedata_normalize('NFKD', enterprise_name)
        enterprise_name = enterprise_name.encode('ascii', errors='ignore').decode('utf-8')

        #re-establecer las @@´s como Ñ´s
        enterprise_name = enterprise_name.replace("@@","Ñ")
        
        #search enterprise_name in codeEnterpriseFile
        logicTMP = enterprise_name == codeEnterpriseFile['empresa'].str.upper()
        
        #not defined enterprise mesage error
        if not(any(logicTMP)):
            print('''OPERACION FALLIDA\n La empresa {0} del listado list_enterprise_forExclusiveExcel no está definida en el archivo codeEnterprise.csv'''.format(enterprise_name))
            sys_exit("")
        
        #get enterprise code of clavesNombresEmpresa
        try:
            enterprise_code = codeEnterpriseFile.clave[logicTMP==True].item()
        except ValueError:
            print("""OPERACION FALLIDA\nLa empresa {0} se encuentra definida más \
    de una vez de la misma manera en el archivo codeEnterprise.csv""".format(
    enterprise_name))
            sys_exit()
            
        #append enterpriseCodecs_forExclusiveExcel
        enterpriseCodecs_forExclusiveExcel.append(enterprise_code)
        
        #append enterpriseNames_forExclusiveExcel
        enterpriseNames_forExclusiveExcel.append(df_enterpriseNames.loc[enterprise_code].item())

    return enterpriseNames_forExclusiveExcel, enterpriseCodecs_forExclusiveExcel
    #-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read codeEnterprise file
def set_codeEnterpriseFile(currentPath, inlineEF):
    
    global codeEnterpriseFile

    #codeEnterpriseFile --> pd data frame, /empresa/ CODE

    if inlineEF:
        filePath_codeEnterprise = ("{0}"+"empresas/codeEnterprise.csv?raw=true").format(orig_url)
    else:
        filePath_codeEnterprise = os_path.join("{0}","..","empresas",
                                        "codeEnterprise.csv").format(currentPath)

    codeEnterpriseFile = pd_read_csv(filePath_codeEnterprise, encoding='latin-1',
                                keep_default_na=False)

    #set as upper
    codeEnterpriseFile["empresa"]=codeEnterpriseFile["empresa"].str.upper()

    #set without acents
    codeEnterpriseFile["empresa"]=codeEnterpriseFile[
        "empresa"].str.normalize('NFKD').str.encode('ascii',
                                            errors='ignore').str.decode('utf-8')

    #read codeEnterprise locally file
    filePath_codeEnterprise_tmp = os_path.join("{}","..","altas","codeEnterprise.csv").format(currentPath)


    codeEnterpriseFile_locally = pd_read_csv(filePath_codeEnterprise_tmp, encoding='latin-1',
                                keep_default_na=False)

    #set as upper
    codeEnterpriseFile_locally["empresa"] = codeEnterpriseFile_locally["empresa"].str.upper()

    #set without acents
    codeEnterpriseFile_locally["empresa"]=codeEnterpriseFile_locally[
        "empresa"].str.normalize('NFKD').str.encode('ascii',
                                            errors='ignore').str.decode('utf-8')

    #Concatenated codeEnterpriseFile and codeEnterpriseFile_locally
    codeEnterpriseFile = pd_concat([codeEnterpriseFile, codeEnterpriseFile_locally], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise name by patient
def get_listEnterpriseNameByPatient(idx_enterprise, enterpriseNames, idx_patients, len_csvFile):
    
    listEnterpriseNameByPatient = []
    
    for idx, val in enumerate(idx_enterprise[:-1]):
        for val0 in range(val,idx_enterprise[idx+1]):
            listEnterpriseNameByPatient.append(enterpriseNames[idx])
    else:
        if len(idx_enterprise)==1: idx=-1
        for val0 in range(idx_enterprise[idx+1], len_csvFile):
            listEnterpriseNameByPatient.append(enterpriseNames[idx+1])       

    #Convert listEnterpriseNameByPatient from list to dict
    tmp=dict()
    for val in idx_patients:
        tmp[val] = listEnterpriseNameByPatient[val]

    return tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise code by patient
def get_listEnterpriseCodeByPatient(idx_enterprise, enterpriseCodecs, idx_patients, len_csvFile):
    
    listEnterpriseCodeByPatient = []
    
    for idx, val in enumerate(idx_enterprise[:-1]):
        for val0 in range(val,idx_enterprise[idx+1]):
            listEnterpriseCodeByPatient.append(enterpriseCodecs[idx])
    else:
        try:
            for val0 in range(idx_enterprise[idx+1], len_csvFile):
                listEnterpriseCodeByPatient.append(enterpriseCodecs[idx+1])
        except:
            if idx_enterprise:
                for val0 in range(0, len(idx_patients)+1):
                    listEnterpriseCodeByPatient.append(enterpriseCodecs[0])

    #Convert listEnterpriseNameByPatient from list to dict
    tmp = dict()
    for val in idx_patients:
        tmp[val] = listEnterpriseCodeByPatient[val]

    return tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get shift (turno)
def get_shift(idx_enterprise, csvFile, OSR):

    shift = []

    #for each enterprise
    for val in idx_enterprise:
        
        #get shift
        tmp=""
        
        if csvFile["firstName"][val].find("VESPERTINO")!=-1:
            tmp="V"
        elif csvFile["firstName"][val].find("MATUTINO")!=-1:
            tmp="M"
        
        #not assigned shift
        if not tmp: sys_exit(NAS.format(OSR[val]))
        
        #append in shift dict
        shift.append(tmp)
    
    return shift
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise code by patient
def get_listShiftByPatient(idx_enterprise, idx_patients, shift, len_csvFile):

    listShiftByPatient = []
    
    for idx, val in enumerate(idx_enterprise[:-1]):
        for val0 in range(val,idx_enterprise[idx+1]):
            listShiftByPatient.append(shift[idx])
    else:

        try:
            for val0 in range(idx_enterprise[idx+1], len_csvFile):
                listShiftByPatient.append(shift[idx+1])
        except:
            if idx_enterprise:
                for val0 in range(0, len(idx_patients)+1):
                    listShiftByPatient.append(shift[0])


                

    #Convert listEnterpriseNameByPatient from list to dict
    tmp = dict()
    for val in idx_patients:
        tmp[val] = listShiftByPatient[val]

    return tmp
#-----------------------------------------------------------------------------#


#-----------------------------------------------------------------------------#
#search for urgents examns
def get_idx_urgentes(idx_patients, csvFile):

    patern_urgente = re_compile(r'URGENTE', flags=re_IGNORECASE)#'URGENTE' pattern
    
    idx_urgentes = []

    for val in idx_patients:#search for each patient
        
        #patient name
        patientName = csvFile.firstName[val]
        if patientName.find("URGENTE")!=-1:#search 'URGENTE' in patient
            idx_urgentes.append(val)
    
    return idx_urgentes
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#search for vuelo examns
def get_idx_vuelo(idx_patients, csvFile):

    patern_vuelo = re_compile(r'VUELO', flags=re_IGNORECASE)#'VUELO' pattern
    
    idx_vuelo = []

    for val in idx_patients:#search for each patient
        
        #patient name
        patientName = csvFile.firstName[val]
        if patientName.find("VUELO")!=-1:#search 'VUELO' in patient
            idx_vuelo.append(val)

    return idx_vuelo
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#update csvFile.firstName cuting the "urgente" part
def update_csvFile_firstName_vuelo(idx_vuelo, csvFile):

    patern_vuelo = re_compile(r'VUELO', flags=re_IGNORECASE)#'VUELO' pattern
    
    for val in idx_vuelo:
        
        patientName = csvFile.firstName[val]
        tmp = patern_vuelo.search(patientName)
        csvFile.firstName[val]=patientName[0:tmp.start()]+patientName[tmp.end():]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the exam code by patient as dictionary
def get_ECBP(idx_patients, csvFile):

    ECBP = dict()#ECBP-->ExamCodeByPatien

    for val in idx_patients:#for each patien
        
        exams = csvFile.thirdName[val]#get the string examCodecs
        exams = list(map(int, exams.split()))#Split the string and put it in a list
        ECBP[val] = exams
    
    return ECBP
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#update csvFile.firstName cuting the "urgente" part
def update_csvFile_firstName_urgent(idx_urgentes, csvFile):

    patern_urgente = re_compile(r'URGENTE', flags=re_IGNORECASE)#'URGENTE' pattern
    
    for val in idx_urgentes:
        
        patientName = csvFile.firstName[val]
        tmp = patern_urgente.search(patientName)
        csvFile.firstName[val] = patientName[0:tmp.start()]+patientName[tmp.end():]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set ECBP as list of str´s
def get_ECBP_str(ECBP):
    
    ECBP_str = dict()
    
    for val in ECBP.items():
        tmp = list(map(str,val[1]))
        ECBP_str[val[0]]="\n".join(tmp)
    
    return ECBP_str
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#examn product code by patient
def get_EPCBP(ECBP):
 
    EPCBP = dict()
 
    for val in ECBP:
        EPCBP[val] = np_prod(ECBP[val])
    
    return EPCBP
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set color set as each study
def get_color_as_study(ECBP):

    #ECBNC --> Exam color by no PCR covits
    ECBNC = dict()
    for idx, val in ECBP.items():
        if any(np_array(val)!=2):
            ECBNC[idx]=True

    #ECBAC --> Exam color by antigen covit
    ECBAC = dict()
    for idx, val in ECBP.items():
        if any(np_array(val)==487):
            ECBAC[idx]=True

    #ECBABC --> Exam color by anti body covit
    ECBABC = dict()
    for idx, val in ECBP.items():
        if any(np_array(val)==491):
            ECBABC[idx]=True

    #ECBCABC --> Exam color by cuantitative anti body covit
    ECBCABC = dict()
    for idx, val in ECBP.items():
        if any(np_array(val)==569):
            ECBCABC[idx]=True

    #ECBSP --> Exam color by sars plus
    ECBSP = dict()
    for idx, val in ECBP.items():
        if any(np_array(val)==1009):
            ECBSP[idx]=True
        
    return ECBNC, ECBAC, ECBABC, ECBCABC, ECBSP
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the exams name, 
def get_examNameList(idx_patients, csvFile, ECBP, format_):

    examNameList = dict()

    for val in idx_patients:#for each patien with spetial prices
        
        #ensure exams code are recored
        try:
            examsName = pd_listExam.EXAMEN[ECBP[val]].tolist()
        except KeyError:
            print(CEND.format(csvFile.firstName[val],csvFile.secondName.iloc[val]))        
            sys_exit()
        
        #ensure exams name are recored
        for tmp in examsName:
            if type(tmp) == float:#(nan is float)exam name is empty at the excel file
                print(CEND.format(csvFile.firstName[val], csvFile.secondName.iloc[val]))        
                sys_exit()

        if format_ == "as_str":
            tmp = "\n"
            examNameList[val] = tmp.join(examsName)
        elif format_ == "as_list":
            examNameList[val] = examsName
    
    return examNameList
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#make inter code
def get_codeInt_Lab_Cob(idx_patients, idx_urgentes, day, subsidiary, ECBP, listEnterpriseCodeByPatient, listShiftByPatient, EPCBP):

    codeIntLab = dict()
    codeIntCob = dict()
    
    for idx, val in enumerate(idx_patients):

        urgent = "U" if val in idx_urgentes else "N"
        
        codeIntCob[val] = day+'-'+subsidiary+'-'+str(idx+1).zfill(3)
        
        #Check if the exam is covid type
        examCovid = "C"
        if not [i for i in [2,487,491,492,569,1009] if  i in ECBP[val]]:
            examCovid = "O"
        
        codeIntLab[val] = day+'-'+subsidiary+'-'+str(idx+1).zfill(3)+urgent+examCovid+listEnterpriseCodeByPatient[
            val]+listShiftByPatient[val]+"P"+str(EPCBP[val]).zfill(5)
        
    return codeIntLab, codeIntCob
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#asociate, as dict, each patient with its corresponding enterprise
def get_dict_pattient_enterprise(idx_patients, idx_enterprise):

    counter = 0
    dict_pattient_enterprise = {}

    for idx, val in enumerate(idx_patients):
        
        if counter+1 < len(idx_enterprise):
            if idx_enterprise[counter+1] < val:
                counter += 1

        dict_pattient_enterprise[val] =  idx_enterprise[counter]
    
    return dict_pattient_enterprise
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of no covit patients
def get_idx_noCovits(idx_patients, ECBP, dict_pattient_enterprise):

    tmp = []

    for idx, val in enumerate(idx_patients):

        if not [i for i in [2,487,491,492,569,1009] if  i in ECBP[val]]:
            tmp.append(val)

    idx_patients_noCovits = pd_Index(data=tmp)#convert list into pd index

    #get the enterprise idx associated with idx_patients_noCovits
    idx_enterprise_patients_noCovits = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_noCovits]))

    return idx_patients_noCovits, idx_enterprise_patients_noCovits
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get index's for antigen patients
def get_idx_antigenCovit(idx_patients, ECBP, dict_pattient_enterprise):
    
    tmp = []

    for idx, val in enumerate(idx_patients):

        if [i for i in [487] if  i in ECBP[val]]:
            tmp.append(val)

    idx_patients_antigenCovit = pd_Index(data=tmp)#convert list into pd index

    #get the enterprise idx associated with idx_patients_antigenCovit
    idx_enterprise_patients_antigenCovit = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_antigenCovit]))

    return idx_patients_antigenCovit, idx_enterprise_patients_antigenCovit
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get index's for qualitative antybody covit patients
def get_idx_antibodyCovit(idx_patients, ECBP, dict_pattient_enterprise):
    
    tmp = []
    
    for idx, val in enumerate(idx_patients):

        if [i for i in [491] if  i in ECBP[val]]:
            tmp.append(val)

    idx_patients_antibodyCovit = pd_Index(data=tmp)#convert list into pd index

    #get the enterprise idx associated with idx_patients_antibodyCovit
    idx_enterprise_patients_antibodyCovit = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_antibodyCovit]))

    return idx_patients_antibodyCovit, idx_enterprise_patients_antibodyCovit
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of list_enterprise_forExclusiveExcel patients
def get_idx_enterpriseExclusive(enterpriseCodecs_forExclusiveExcel, idx_patients, listEnterpriseCodeByPatient, dict_pattient_enterprise):

    idx_patients_enterprise_forExclusiveExcel_asDict = {}
    idx_enterprise_enterprise_forExclusiveExcel_asDict = {}

    for codeEnterprise_ in enterpriseCodecs_forExclusiveExcel:
        
        tmp = []
        for idx, val in enumerate(idx_patients):

            if [i for i in [codeEnterprise_] if  i in listEnterpriseCodeByPatient[val]]:
                tmp.append(val)

        idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_] = pd_Index(data=tmp)

        #get the enterprise idx associated with codeEnterprise_
        idx_enterprise_enterprise_forExclusiveExcel_asDict [codeEnterprise_]= list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_]]))
    
    return idx_patients_enterprise_forExclusiveExcel_asDict, idx_enterprise_enterprise_forExclusiveExcel_asDict
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def make_laboratory_excel(idx_patients_, idx_enterprise_, codeIntLab, csvFile, ECBP_str, currentPath, yymmddPath, day, idx_urgentes, idx_vuelo, examNameList, ECBNC, ECBAC, ECBABC, ECBCABC, ECBSP, enterpriseNames_asDict, path_=""):
    #idx_patients_ --> pandas index, the index (in the CSV file) of patients to show
    #idx_enterprise --> list, the index (in the CSV file) of enterprises to show

    #----------------------------------------------------------------------------#
    #merge idx_patients_ and idx_enterprise_    
    idx = idx_patients_.tolist() + idx_enterprise_
    
    idx.sort()
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #Export to excel-->laboratori
    df_toExcel = pd_DataFrame({
                             'OSR':np_NaN,
                             'COD INT':{x:codeIntLab[x] for x in idx_patients_},
                             'NOMBRE':csvFile['firstName'][idx].str.strip(), 
                             'APELLIDO':csvFile['secondName'][idx].str.strip(),
                             'EXAMEN':{x:examNameList[x] for x in idx_patients_},
                             'COD':{x:ECBP_str[x] for x in idx_patients_},
                             'ESTATUS':np_NaN,
                             'RESULTADO':np_NaN,
                             'ENVIO':np_NaN,
                             'REVISO':np_NaN,
                             'HORA ENVIO':np_NaN
                             })
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #set the OSR code in df_toExcel
    df_toExcel.loc[idx_enterprise_,"OSR"] = csvFile["secondName"][idx_enterprise_].str.strip()
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave = os_path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "{2}{3}.xlsx").format(currentPath,
                                        yymmddPath,day,path_)

    with pd_ExcelWriter(pathTosave, engine='xlsxwriter') as writer:
                                                           
        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #Wrap EXAMEN and PRECIO column
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('E:E', 40, widthColumn)
        worksheet.set_column('F:F', 6, widthColumn)
        worksheet.set_column('H:H', 18, widthColumn)
        
        border_format = workbook.add_format({'border': 1})
        #-----------------------------------------------------------------------------#
    
        #-----------------------------------------------------------------------------#
        #Set urgents format
        
        #urgentes
        urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'black',
                                            'bg_color': 'orange'})
    
        for tmp in list(set(idx_urgentes) & set(idx_patients_.tolist())):
            tmp_ = idx.index(tmp)
            worksheet.write_string('G'+str(tmp_+2)+':G'+str(tmp_+2),"URGENTE",
                                  urgentFormat)
        #-----------------------------------------------------------------------------#
    
        #-----------------------------------------------------------------------------#
        #Set vuelo format
        
        #urgentes
        vueloFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'black',
                                            'bg_color': '#0080FF'})
        
        for tmp in  list(set(idx_vuelo) & set(idx_patients_.tolist())):
            tmp_ = idx.index(tmp)
            worksheet.write_string('H'+str(tmp_+2)+':H'+str(tmp_+2),"VUELO",
                                  vueloFormat)
        #-----------------------------------------------------------------------------#
    
        #-----------------------------------------------------------------------------#
        #Add cell color deppending of the exam
        
        #colors:
        cell_format_mostaza = workbook.add_format({'bg_color': '#FF9933'})
        cell_format_mostaza.set_text_wrap()
        cell_format_magenta = workbook.add_format({'bg_color': 'magenta'})
        cell_format_magenta.set_text_wrap()
        cell_format_yellow = workbook.add_format({'bg_color': 'yellow'})
        cell_format_yellow.set_text_wrap()
        cell_format_green = workbook.add_format({'bg_color': 'green'})
        cell_format_green.set_text_wrap()
        cell_format_lime = workbook.add_format({'bg_color': 'lime'})
        cell_format_lime.set_text_wrap()

        #ECBNC --> Exam color by no covits; Mostaza
        tmp = ECBNC.keys()
        tmp_ = [x for x in idx_patients_ if x in tmp]
        ECBNC_tmp = {x:ECBNC[x] for x in tmp_}
        for key in ECBNC_tmp:
            key_ = idx.index(key)
            worksheet.write_string('E'+str(key_+2)+':E'+str(key_+2),examNameList[key],
                            cell_format_mostaza)
        
        #ECBAC --> Exam color by antigen covit
        tmp = ECBAC.keys()
        tmp_ = [x for x in idx_patients_ if x in tmp]
        ECBAC_tmp = {x:ECBAC[x] for x in tmp_}
        for key in ECBAC_tmp:
            key_ = idx.index(key)
            worksheet.write_string('E'+str(key_+2)+':E'+str(key_+2),examNameList[key],
                            cell_format_yellow)
        
        #ECBABC --> Exam color by anti body covit
        tmp = ECBABC.keys()
        tmp_ = [x for x in idx_patients_ if x in tmp]
        ECBABC_tmp = {x:ECBABC[x] for x in tmp_}
        for key in ECBABC_tmp:
            key_ = idx.index(key)
            worksheet.write_string('E'+str(key_+2)+':E'+str(key_+2),examNameList[key],
                            cell_format_magenta)
        
        #ECBCABC --> Exam color by cuantitative anti body covit
        tmp = ECBCABC.keys()
        tmp_ = [x for x in idx_patients_ if x in tmp]
        ECBCABC_tmp = {x:ECBCABC[x] for x in tmp_}
        for key in ECBCABC_tmp:
            key_ = idx.index(key)
            worksheet.write_string('E'+str(key_+2)+':E'+str(key_+2),examNameList[key],
                            cell_format_magenta)
        
        #ECBSP --> Exam color by sars plus
        tmp = ECBSP.keys()
        tmp_ = [x for x in idx_patients_ if x in tmp]
        ECBSP_tmp = {x:ECBSP[x] for x in tmp_}
        for key in ECBSP_tmp:
            key_ = idx.index(key)
            worksheet.write_string('E'+str(key_+2)+':E'+str(key_+2),examNameList[key],
                            cell_format_lime)        
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Add border
        numRows=len(df_toExcel)
        
        worksheet.conditional_format('A1:K'+str(numRows+1),{'type':'no_blanks',
                                              'format':border_format})
        
        worksheet.conditional_format('A1:K'+str(numRows+1),{'type':'blanks',
                                              'format':border_format})
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Set format to enterprise
        merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'white',
                                            'bg_color': 'black'})
        
        for indx_, val, in enumerate(idx_enterprise_):
            val_ = idx.index(val)
            worksheet.merge_range('B'+str(val_+2)+':K'+str(val_+2),enterpriseNames_asDict[val],
                                  merge_format)
        #-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def make_no_covid_excel(idx_patients_, idx_enterprise_, codeIntLab, csvFile, currentPath, yymmddPath, day, idx_urgentes, examNameList_nested, enterpriseNames_asDict, path_=""):

    #idx_patients_ --> pandas index, the index (in the CSV file) of patients to show
    #idx_enterprise --> list, the index (in the CSV file) of enterprises to show

    idx_patients_ = idx_patients_.tolist()
    idx_patients_.sort()
    idx_enterprise_.sort()

    #----------------------------------------------------------------------------#
    #merge idx_patients_ and idx_enterprise_    
    idx = idx_patients_ + idx_enterprise_
    
    idx.sort()
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #set correlation pd index and idx
    excelIdx_pdIndx = {val:idx_ for idx_, val in enumerate(idx)}
    pdIndx_for_examList = [val for key, val in excelIdx_pdIndx.items() if key in idx_patients_]
    
    
    #update excelIdx_pdIndx considering there patients that have more than one exam
    ECBP_noCovids = {x:y for x,y in examNameList_nested.items() if x in idx_patients_}
    excelIdxExams_pdIndx = {}
    for key, value in ECBP_noCovids.items():
        
        if len(value) > 1:# --> more than one exam
            
            for key_, val_ in excelIdx_pdIndx.items():
                if key_ > key: excelIdx_pdIndx[key_] += (len(value)-1)

            excelIdxExams_pdIndx[key] = [excelIdx_pdIndx[key]+index_ for index_, value_ in enumerate(value)]
        else:
            excelIdxExams_pdIndx[key] = [excelIdx_pdIndx[key]]
    
    
    #----------------------------------------------------------------------------#
    
    #----------------------------------------------------------------------------#
    #Export to excel-->laboratori
    end_index = max(excelIdxExams_pdIndx.get(idx_patients_[-1]))+1 if idx else 0
    df_toExcel = pd_DataFrame(
        {
            'OSR':np_NaN,
            'COD INT':np_NaN,
            'NOMBRE':np_NaN,
            'APELLIDO':np_NaN,
            'EXAMEN':np_NaN,
            'ESTATUS':np_NaN,
            'FECHA RECEPCIÓN ESTUDIO':np_NaN,
            'ENVIÓ':np_NaN,
            'REVISÓ':np_NaN,
            'FECHA ENVÍO':np_NaN,
            'HORA ENVÍO':np_NaN
        }
        , index = range(0, end_index)
    )
    #----------------------------------------------------------------------------#
    
    #set valus at df_toExcel
    #OSR
    df_toExcel.loc[[excelIdx_pdIndx[tmp] for tmp in idx_enterprise_], ["OSR"]] = [csvFile["secondName"][[tmp]].str.strip() for tmp in idx_enterprise_]

    #COD INT
    df_toExcel.loc[[excelIdx_pdIndx[tmp] for tmp in idx_patients_],"COD INT"] = [codeIntLab[tmp] for tmp in idx_patients_]
    
    #NOMBRE
    df_toExcel.loc[[excelIdx_pdIndx[tmp] for tmp in idx_patients_], ["NOMBRE"]] = [csvFile["firstName"][[tmp]].str.strip() for tmp in idx_patients_]

    #APELLIDO
    df_toExcel.loc[[excelIdx_pdIndx[tmp] for tmp in idx_patients_], ["APELLIDO"]] = [csvFile["secondName"][[tmp]].str.strip() for tmp in idx_patients_]

    # #EXAMEN
    tmp_ = []
    for tmp in idx_patients_:
        tmp_.extend(examNameList_nested[tmp])
    
    tmp_0 = []
    for tmp in idx_patients_:
        tmp_0.extend(excelIdxExams_pdIndx[tmp])
    
    df_toExcel.loc[tmp_0, "EXAMEN"] = tmp_
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave = os_path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "{2}{3}.xlsx").format(currentPath,
                                        yymmddPath,day,path_)

    with pd_ExcelWriter(pathTosave, engine='xlsxwriter') as writer:
                                                           
        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #Wrap EXAMEN and PRECIO column
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('B:B', 27, widthColumn)
        worksheet.set_column('C:C', 30, widthColumn)
        worksheet.set_column('D:D', 30, widthColumn)
        worksheet.set_column('E:E', 40, widthColumn)
        worksheet.set_column('F:F', 15, widthColumn)
        worksheet.set_column('G:G', 25, widthColumn)
        worksheet.set_column('H:H', 25, widthColumn)
        worksheet.set_column('I:I', 25, widthColumn)
        worksheet.set_column('J:J', 20, widthColumn)
        worksheet.set_column('K:K', 20, widthColumn)
        
        border_format = workbook.add_format({'border': 1})
        #-----------------------------------------------------------------------------#
    
        #-----------------------------------------------------------------------------#
        #Set urgents format
        
        #urgentes
        urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'black',
                                            'bg_color': 'orange'})
    
        for tmp in list(set(idx_urgentes) & set(idx_patients_)):
            # tmp_ = idx.index(tmp)
            tmp_ = excelIdx_pdIndx[tmp] 
            worksheet.write_string('F'+str(tmp_+2)+':F'+str(tmp_+2),"URGENTE",
                                  urgentFormat)
        #-----------------------------------------------------------------------------#
    
        #-----------------------------------------------------------------------------#
        #Add border
        numRows=len(df_toExcel)
        
        worksheet.conditional_format('A1:K'+str(numRows+1),{'type':'no_blanks',
                                              'format':border_format})
        
        worksheet.conditional_format('A1:K'+str(numRows+1),{'type':'blanks',
                                              'format':border_format})
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Set format to enterprise
        merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'white',
                                            'bg_color': 'black'})
        
        for indx_, val, in enumerate(idx_enterprise_):
            worksheet.merge_range('B'+str(excelIdx_pdIndx[val]+2)+':K'+str(excelIdx_pdIndx[val]+2),enterpriseNames_asDict[val],
                                  merge_format)
        #-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#




#-----------------------------------------------------------------------------#
def make_excel_antigen_antibody(idx_patients_, resultadoColumn, exam, path_, day, day_to_save, codeIntCob, yymmddPath, currentPath):

    #----------------------------------------------------------------------------#
    #Export to excel-->antigen and antybody
    dictForDF = {
        'FECHA':day,
        'FOLIO': {x:codeIntCob[x] for x in idx_patients_},#codeIntLab
        #'PACIENTE':csvFile['firstName'][idx_patients_].str.strip()+' '+csvFile['secondName'][idx_patients_].str.strip(),
        'EXAMEN': exam,#{x:examNameList[x] for x in idx_patients_},
    }
    
    for key, value in resultadoColumn.items():
        dictForDF[key] = value
    
    dictForDF['VALIDO'] = np_NaN
    dictForDF['RECIBE RESULTADOS'] = np_NaN
    
    
    df_toExcel=pd_DataFrame(dictForDF)
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave = os_path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "byExamCategory","{2}_{3}.xlsx").format(currentPath,
                                        yymmddPath,day_to_save,path_)

    with pd_ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day_to_save, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day_to_save]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #Wrap EXAMEN
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('B:B', 20, widthColumn)
        #worksheet.set_column('C:C', 35, widthColumn)
        worksheet.set_column('C:C', 22, widthColumn)
        
        tmp = ["D","E","F","G","H","I","J","K","L","M","N"]
        for x in range(0,len(resultadoColumn)):
            worksheet.set_column('{}:{}'.format(tmp[x],tmp[x]), 10, widthColumn)

        worksheet.set_column('{}:{}'.format(tmp[x+1],tmp[x+1]), 25, widthColumn)
        worksheet.set_column('{}:{}'.format(tmp[x+2],tmp[x+2]), 25, widthColumn)
        
        border_format = workbook.add_format({'border': 1})
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Add border
        numRows=len(df_toExcel)
        
        dictt = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]
        
        
        worksheet.conditional_format('A1:{}'.format(dictt[len(dictForDF)-1])+str(numRows+1),{'type':'no_blanks',
                                            'format':border_format})
        
        worksheet.conditional_format('A1:{}'.format(dictt[len(dictForDF)-1])+str(numRows+1),{'type':'blanks',
                                            'format':border_format})
        #-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def make_excel_enterprise_forExclusiveExcel(idx_patients_, path_, day, day_to_save, codeIntLab, csvFile, examNameList, currentPath, yymmddPath, idx_urgentes):

    #----------------------------------------------------------------------------#
    #Export to excel-->antigen and antybody
    dictForDF = {
        'FECHA':day,
        'FOLIO': {x:codeIntLab[x] for x in idx_patients_},
        'PACIENTE':csvFile['firstName'][idx_patients_].str.strip()+' '+csvFile['secondName'][idx_patients_].str.strip(),
        'EXAMEN': {x:examNameList[x] for x in idx_patients_},
        'ESTATUS':np_NaN,
    }
    
    
    df_toExcel = pd_DataFrame(dictForDF)
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave = os_path.join("{0}","..","listadosGeneradosParaExel","{1}","byEnterprise",
                            "{2}{3}.xlsx").format(currentPath,
                                        yymmddPath,day_to_save,path_)

    with pd_ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day_to_save, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day_to_save]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #Wrap EXAMEN
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('B:B', 28, widthColumn)
        worksheet.set_column('C:C', 40, widthColumn)
        worksheet.set_column('D:D', 28, widthColumn)
        worksheet.set_column('E:E', 10, widthColumn)
        
        border_format = workbook.add_format({'border': 1})
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Set urgents format
        
        #urgentes
        urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'black',
                                            'bg_color': 'orange'})
    
        idx = idx_patients_.tolist()
        idx.sort()
        for tmp in list(set(idx_urgentes) & set(idx_patients_.tolist())):
            tmp_ = idx.index(tmp)
            worksheet.write_string('E'+str(tmp_+2)+':E'+str(tmp_+2),"URGENTE",
                                  urgentFormat)
        #-----------------------------------------------------------------------------#

        #-----------------------------------------------------------------------------#
        #Add border
        numRows=len(df_toExcel)

        worksheet.conditional_format('A1:E'+str(numRows+1),{'type':'no_blanks',
                                            'format':border_format})
        
        worksheet.conditional_format('A1:E'+str(numRows+1),{'type':'blanks',
                                            'format':border_format})
        #-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#excel-->cobranza
def make_excel_cobranza(idx_patients_, codeIntCob, day, csvFile, examNameList, ECBP_str, listEnterpriseNameByPatient, day_to_save, currentPath, yymmddPath, idx_urgentes):
    
    df_toExcel = pd_DataFrame({'COD INT':codeIntCob,
                            'FECHA':day,
                            'NOMBRE':csvFile['firstName'][idx_patients_].str.strip()
                            +' '+csvFile['secondName'][idx_patients_].str.strip(),
                            'EXAMEN':examNameList,
                            'COD':ECBP_str,
                            # 'PRECIO':pricesList_str,
                            'ESTATUS':np_NaN,
                            ' ':np_NaN,
                            'EMPRESA':listEnterpriseNameByPatient})
    #----------------------------------------------------------------------------#


    #----------------------------------------------------------------------------#
    pathTosave=os_path.join("{0}","..","listadosGeneradosParaExel",
                            "{1}","{2}_cobranza.xlsx").format(currentPath,
                                    yymmddPath,day_to_save)


    with pd_ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day_to_save, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day_to_save]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #urgentes
        merge_urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                            'bold': True, 'font_color': 'black',
                                            'bg_color': 'red'})
        
        #Wrap EXAMEN and PRECIO column
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('D:D', 40, widthColumn)
        worksheet.set_column('E:E', 6, widthColumn)
        # worksheet.set_column('F:F', 7, widthColumn)
        
        border_format = workbook.add_format({'border': 1})
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #urgent_index
        urgent_index=[]
        for val in idx_urgentes:
            urgent_index.append(np_argwhere(idx_patients_==val).item())
        
        for tmp in urgent_index:
            
            worksheet.merge_range('F'+str(tmp+2)+':G'+str(tmp+2),"URGENTE",
                                merge_urgentFormat)
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #Add border
        numRows=len(df_toExcel)
        
        worksheet.conditional_format('A1:I'+str(numRows+1),{'type':'no_blanks',
                                            'format':border_format})
        
        worksheet.conditional_format('A1:I'+str(numRows+1),{'type':'blanks',
                                            'format':border_format})
    #-----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#define error mesages

#Precio no definido archivo urgentes (listadoPreciosUrgent.csv)
PNDAU="""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosUrgent.csv para la empresa \"{0}\" con el examen \"{1}\"; \
paciente: \"{2}\", folio de paciente: \"{3}\""""

#Precio no definido archivo standar (listadoPreciosEtandar.csv)
PNDAS="""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosEtandar.csv para la empresa \"{0}\" con el examen \"{1}\"; \
paciente: \"{2}\", folio de paciente: \"{3}\" """

#Not autorized for assign spetial price
NAFASP="""OPERACION FALLIDA\nLa empresa \"{0}\" no está autorizada para \
ofertar precios especiales; retire el precio especial del archivo de ingreso\ 
de pacientes (.txt), o modifique el permiso asignado a dicha empresa en el \ 
archivo listadoPermisosCostosEspecialesEmpresas.csv"""

#Code of exam not defined
CEND='''OPERACION FALLIDA:\nCódigo de examen no definido; paciente: {0} {1}'''

#Not assigned shift
NAS="""OPERACION FALLIDA\nTurno no asignado a la OSR {0}; asigne turno \
MATUTINO/VESPERTINO"""
#-----------------------------------------------------------------------------#