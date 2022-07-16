# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:17:14 2021

@author: Paulina Santiago
"""

# -*- coding: utf-8 -*-
#denatLab

"""
Spyder Editor

This is a temporary script file.
"""
    
import pandas as pd
import numpy as np
import os
import re
import time
import xlsxwriter
import sys
from datetime import datetime
import pdb#debug
import unicodedata


#-----------------------------------------------------------------------------#
day='010522'
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#list to generate the excel file by enterprise
list_enterprise_forExclusiveExcel = ['/en tu casa salud/', '/aj lab/']
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set subsidiary
subsidiary = '01'#hermita
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#inline excell files
inlineEF=True
orig_url = 'https://github.com/FernandoCF7/denatbioRegistroPacientes/blob/main/'
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set path
currentPath = os.path.dirname(os.path.abspath(__file__))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get day month year folder
dayy=day[0:2]
month=day[2:4]
year=day[4:6]
yymmddPath=os.path.join('____'+year,'__'+month+year,day)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read registro file
filePath_registro=os.path.join("{0}","..","DB_ingresoPorVoz","{1}.txt").format(
    currentPath,yymmddPath)

csvFile=(pd.read_csv(filePath_registro,sep='*', dtype={2: str}))

csvFile.columns=["firstName","secondName",'thirdName']

#set as upper
csvFile["firstName"]=csvFile["firstName"].str.upper()
csvFile["secondName"]=csvFile["secondName"].str.upper()

#enmascarar las Ñ´s con @@´s
for idx, val in enumerate(csvFile["firstName"]):
    csvFile["firstName"][idx]=csvFile["firstName"][idx].replace("Ñ","@@")
    csvFile["secondName"][idx]=csvFile["secondName"][idx].replace("Ñ","@@")
   
#set without acents
csvFile["firstName"]=csvFile["firstName"].str.normalize('NFKD').str.encode(
    'ascii', errors='ignore').str.decode('utf-8')
csvFile["secondName"]=csvFile["secondName"].str.normalize('NFKD').str.encode(
    'ascii', errors='ignore').str.decode('utf-8')

#re-establecer las @@´s como Ñ´s
for idx, val in enumerate(csvFile["firstName"]):
    csvFile["firstName"][idx]=csvFile["firstName"][idx].replace("@@","Ñ")
    csvFile["secondName"][idx]=csvFile["secondName"][idx].replace("@@","Ñ")
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read codeEnterprise file
if inlineEF:
    filePath_codeEnterprise=("{0}"+"empresas/codeEnterprise.csv?raw=true").format(orig_url)
else:
    filePath_codeEnterprise=os.path.join("{0}","..","empresas",
                                     "codeEnterprise.csv").format(currentPath)

codeEnterpriseFile=pd.read_csv(filePath_codeEnterprise, encoding='latin-1',
                               keep_default_na=False)

#set as upper
codeEnterpriseFile["empresa"]=codeEnterpriseFile["empresa"].str.upper()

#set without acents
codeEnterpriseFile["empresa"]=codeEnterpriseFile[
    "empresa"].str.normalize('NFKD').str.encode('ascii',
                                           errors='ignore').str.decode('utf-8')

#read codeEnterprise locally file
filePath_codeEnterprise_tmp = os.path.join("{}","..","altas","codeEnterprise.csv").format(currentPath)


codeEnterpriseFile_locally=pd.read_csv(filePath_codeEnterprise_tmp, encoding='latin-1',
                               keep_default_na=False)

#set as upper
codeEnterpriseFile_locally["empresa"]=codeEnterpriseFile_locally["empresa"].str.upper()

#set without acents
codeEnterpriseFile_locally["empresa"]=codeEnterpriseFile_locally[
    "empresa"].str.normalize('NFKD').str.encode('ascii',
                                           errors='ignore').str.decode('utf-8')

#Concatenated codeEnterpriseFile and codeEnterpriseFile_locally
codeEnterpriseFile = pd.concat([codeEnterpriseFile, codeEnterpriseFile_locally], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read pd_listExam file
if inlineEF:
    filePath_listExam=("{0}"+"listadoDeExamenes/listExam.csv?raw=true").format(orig_url)
else:
    filePath_listExam=os.path.join("{0}","..","listadoDeExamenes",
                                   "listExam.csv").format(currentPath)

pd_listExam=(pd.read_csv(filePath_listExam, usecols=["COD INT","EXAMEN"]))

#set index of pd_listExam as COD INT column
pd_listExam.set_index("COD INT", inplace=True)


#read listExam locally file
filePath_listExam_tmp = os.path.join("{}","..","altas","listExam.csv").format(currentPath)
listExam_locally = pd.read_csv(filePath_listExam_tmp, usecols=["COD INT","EXAMEN"])

listExam_locally.set_index("COD INT", inplace=True)

# append listExam_locally to pd_listExam
for idx, row in listExam_locally.iterrows():
    
    if idx in pd_listExam.index:#update the Exam
        pd_listExam.EXAMEN[idx] = row["EXAMEN"]
    # else:#append examn
    #     pd_listExam = pd.concat([pd_listExam, listExam_locally.loc[idx]], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read clavesNombresEmpresa file
if inlineEF:
    filePath_clavesNombresEmpresa=("{0}"+"empresas/clavesNombresEmpresa.csv?raw=true").format(orig_url)
    
else:
    filePath_clavesNombresEmpresa=os.path.join("{0}","..","empresas",
                               "clavesNombresEmpresa.csv").format(currentPath)

df_enterpriseNames=pd.read_csv(filePath_clavesNombresEmpresa, keep_default_na=False)

#set index of enterpriseNames as clave column
df_enterpriseNames.set_index("clave", inplace=True)

#read clavesNombresEmpresa locally file
filePath_clavesNombresEmpresa_tmp = os.path.join("{}","..","altas","clavesNombresEmpresa.csv").format(currentPath)
clavesNombresEmpresa_locally = pd.read_csv(filePath_clavesNombresEmpresa_tmp, encoding='latin-1', keep_default_na=False)

clavesNombresEmpresa_locally.set_index("clave", inplace=True)

#Concatenated df_enterpriseNames and clavesNombresEmpresa_locally
df_enterpriseNames = pd.concat([df_enterpriseNames, clavesNombresEmpresa_locally], axis=0)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #read enterprice price files
# if inlineEF:
#     #Standar
#     filePath_listPriceStandar=("{0}"+"listadoDePrecios/listadoPreciosEstandar.csv?raw=true").format(orig_url)
#     #Urgent
#     filePath_listPriceUrgent=("{0}"+"listadoDePrecios/listadoPreciosUrgentes.csv?raw=true").format(orig_url)
    
# else:
#     #Standar
#     filePath_listPriceStandar=os.path.join("{0}","..","listadoDePrecios",
#                               "listadoPreciosEstandar.csv").format(currentPath)
#     #Urgent
#     filePath_listPriceUrgent=os.path.join("{0}","..","listadoDePrecios",
#                               "listadoPreciosUrgentes.csv").format(currentPath)
        
# df_listPriceStandar=(pd.read_csv(filePath_listPriceStandar))
# df_listPriceUrgent=(pd.read_csv(filePath_listPriceUrgent))

# #set index of COD INT as clave column
# df_listPriceStandar.set_index("COD INT", inplace=True)
# df_listPriceUrgent.set_index("COD INT", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #read spetial costs permissions by enterprise file
# if inlineEF:
#     filePath_persmisosCostosEspeciales=("{0}"+
#                 "listadoDePrecios/listadoPermisosCostosEspecialesEmpresas.csv?raw=true").format(orig_url)
        
# else:
#     filePath_persmisosCostosEspeciales=os.path.join("{0}","..",
#                                                     "listadoDePrecios",
#              "listadoPermisosCostosEspecialesEmpresas.csv").format(currentPath)

# df_permisosCostosEspeciales=(pd.read_csv(filePath_persmisosCostosEspeciales))

# #set index of EMPRESA INT as clave column
# df_permisosCostosEspeciales.set_index("EMPRESA", inplace=True)
#-----------------------------------------------------------------------------#

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

#-----------------------------------------------------------------------------#
#search for enterprise; extract index of the enterprises
idx_enterprise=[]
patern=re.compile(r'/.*?/')
for idx, val in enumerate(csvFile["firstName"]):#for each field
    
    if val.find("EMPRESA")!=-1:#search for "EMPRESA" word
        idx_enterprise.append(idx)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#search for patients; extract index of the patients
idx_patients=csvFile.index[~csvFile.index.isin(idx_enterprise)]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the OSR code-->orden de servicio de referencia
OSR=dict(csvFile["secondName"][idx_enterprise].str.strip())
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#check fill values in all patients entries
def checkFilledfiels(columnIdx):
    if np.any( pd.isnull(csvFile.iloc[idx_patients,columnIdx]) ):
        tmp=np.where(pd.isnull(csvFile.iloc[idx_patients,columnIdx]))
        infoPatients=csvFile.iloc[idx_patients[tmp],:]
        sys.exit("""Registro no valido para el (los) paciente(s):\n 
{0}""".format(infoPatients))

checkFilledfiels(0)
checkFilledfiels(1)
checkFilledfiels(2)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise names and set it in enterpriseNames
#get the enterprise codecs and set it in enterpriseCodecs
enterpriseNames=[]
enterpriseCodecs=[]
for val in idx_enterprise:#for each enterprise
    
    #get the enterprise name
    enterprise_name=patern.search(csvFile["firstName"][val]).group()
    
    #search enterprise_name in codeEnterpriseFile
    logicTMP=enterprise_name==codeEnterpriseFile['empresa'].str.upper()
    
    #not defined enterprise mesage error
    if not(any(logicTMP)):
        print('''OPERACION FALLIDA\nEmpresa no definida: {0} en el archivo \
codeEnterprise.csv; folio OSR: {1}'''.format(enterprise_name,OSR[val]))
        sys.exit("")
    
    #get enterprise code of clavesNombresEmpresa
    try:
        enterprise_code=codeEnterpriseFile.clave[logicTMP==True].item()
    except ValueError:
        print("""OPERACION FALLIDA\nLa empresa {0} se encuentra definida más \
de una vez de la misma manera en el archivo codeEnterprise.csv""".format(
enterprise_name))
        sys.exit()
        
    #append enterpriseCodecs
    enterpriseCodecs.append(enterprise_code)
    
    #append enterprise_code
    enterpriseNames.append(df_enterpriseNames.loc[enterprise_code].item())
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise names and codecs, set it in enterpriseNames, enterpriseCodecs
enterpriseNames_forExclusiveExcel = []
enterpriseCodecs_forExclusiveExcel = []
for enterprise_name_ in list_enterprise_forExclusiveExcel:
        
    #set as upper
    enterprise_name = enterprise_name_.upper()
   
    #enmascarar las Ñ´s con @@´s
    enterprise_name = enterprise_name.replace("Ñ","@@")
    
    #set without acents
    enterprise_name = unicodedata.normalize('NFKD', enterprise_name)
    enterprise_name = enterprise_name.encode('ascii', errors='ignore').decode('utf-8')

    #re-establecer las @@´s como Ñ´s
    enterprise_name = enterprise_name.replace("@@","Ñ")
    
    #search enterprise_name in codeEnterpriseFile
    logicTMP = enterprise_name == codeEnterpriseFile['empresa'].str.upper()
    
    #not defined enterprise mesage error
    if not(any(logicTMP)):
        print('''OPERACION FALLIDA\n La empresa {0} del listado list_enterprise_forExclusiveExcel no está definida en el archivo codeEnterprise.csv'''.format(enterprise_name))
        sys.exit("")
    
    #get enterprise code of clavesNombresEmpresa
    try:
        enterprise_code = codeEnterpriseFile.clave[logicTMP==True].item()
    except ValueError:
        print("""OPERACION FALLIDA\nLa empresa {0} se encuentra definida más \
de una vez de la misma manera en el archivo codeEnterprise.csv""".format(
enterprise_name))
        sys.exit()
        
    #append enterpriseCodecs_forExclusiveExcel
    enterpriseCodecs_forExclusiveExcel.append(enterprise_code)
    
    #append enterpriseNames_forExclusiveExcel
    enterpriseNames_forExclusiveExcel.append(df_enterpriseNames.loc[enterprise_code].item())
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set idx_enterprise and enterpriseNames as dict  
enterpriseNames_asDict = dict(zip(idx_enterprise, enterpriseNames))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise name by patient
listEnterpriseNameByPatient=[]
for idx, val in enumerate(idx_enterprise[:-1]):
    for val0 in range(val,idx_enterprise[idx+1]):
        listEnterpriseNameByPatient.append(enterpriseNames[idx])
else:
    if len(idx_enterprise)==1: idx=-1
    for val0 in range(idx_enterprise[idx+1],len(csvFile)):
        listEnterpriseNameByPatient.append(enterpriseNames[idx+1])       

#Convert listEnterpriseNameByPatient from list to dict
tmp=dict()
for val in idx_patients:
    tmp[val]=listEnterpriseNameByPatient[val]

listEnterpriseNameByPatient=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise code by patient
listEnterpriseCodeByPatient=[]
for idx, val in enumerate(idx_enterprise[:-1]):
    for val0 in range(val,idx_enterprise[idx+1]):
        listEnterpriseCodeByPatient.append(enterpriseCodecs[idx])
else:
    for val0 in range(idx_enterprise[idx+1],len(csvFile)):
        listEnterpriseCodeByPatient.append(enterpriseCodecs[idx+1])       

#Convert listEnterpriseNameByPatient from list to dict
tmp=dict()
for val in idx_patients:
    tmp[val]=listEnterpriseCodeByPatient[val]

listEnterpriseCodeByPatient=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get shift (turno)
shift=[]
for val in idx_enterprise:#for each enterprise
    
    #get shift
    tmp=""
    if csvFile["firstName"][val].find("VESPERTINO")!=-1:
        tmp="V"
    elif csvFile["firstName"][val].find("MATUTINO")!=-1:
        tmp="M"
    
    #not assigned shift
    if not tmp: sys.exit(NAS.format(OSR[val]))
    
    #append in shift dict
    shift.append(tmp)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise code by patient
listShiftByPatient=[]
for idx, val in enumerate(idx_enterprise[:-1]):
    for val0 in range(val,idx_enterprise[idx+1]):
        listShiftByPatient.append(shift[idx])
else:
    for val0 in range(idx_enterprise[idx+1],len(csvFile)):
        listShiftByPatient.append(shift[idx+1])       

#Convert listEnterpriseNameByPatient from list to dict
tmp=dict()
for val in idx_patients:
    tmp[val]=listShiftByPatient[val]

listShiftByPatient=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#search for urgents examns
patern_urgente=re.compile(r'URGENTE', flags=re.IGNORECASE)#'URGENTE' pattern
idx_urgentes=[]

for val in idx_patients:#search for each patient
    
    #patient name
    patientName=csvFile.firstName[val]
    if patientName.find("URGENTE")!=-1:#search 'URGENTE' in patient
        idx_urgentes.append(val)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#cut the "urgente" part of the firstName
for val in idx_urgentes:
    
    patientName=csvFile.firstName[val]
    tmp=patern_urgente.search(patientName)
    csvFile.firstName[val]=patientName[0:tmp.start()]+patientName[tmp.end():]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#search for vuelo examns
patern_vuelo=re.compile(r'VUELO', flags=re.IGNORECASE)#'VUELO' pattern
idx_vuelo=[]

for val in idx_patients:#search for each patient
    
    #patient name
    patientName=csvFile.firstName[val]
    if patientName.find("VUELO")!=-1:#search 'VUELO' in patient
        idx_vuelo.append(val)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#cut the "vuelo" part of the firstName
for val in idx_vuelo:
    
    patientName=csvFile.firstName[val]
    tmp=patern_vuelo.search(patientName)
    csvFile.firstName[val]=patientName[0:tmp.start()]+patientName[tmp.end():]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #search for especial prices
# idx_spetialPrice=[]
# patern=re.compile(r'([\d\.-]+)-([\d\.-]+)')
# for val in idx_patients:
    
#     priceValue=csvFile.thirdName[val]
#     if priceValue.find("-")!=-1:
#         idx_spetialPrice.append(val)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #validate if enterprises can apply special prices
# for val in idx_spetialPrice:
    
#     enterprise=listEnterpriseNameByPatient[val]
    
#     if df_permisosCostosEspeciales.COSTO_ESPECIAL[enterprise]==0:
#         print(NAFASP.format(enterprise)) 
#         sys.exit()
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #get the idx in the exams by patient of the spetial prices
# idx_IEBPSP=dict()#idx_IEBPSP-->idx InExamsByPatientSpetialPrice
# for val in idx_spetialPrice:#for each patien with spetial prices
#     exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
#     exams=exams.split()#Split the string and put it in a list
    
#     tmp=[]#positions of spetial prices
#     for idx0, val0 in enumerate(exams):
#         if val0.find("-")!=-1:
#             tmp.append(idx0)
#     idx_IEBPSP[val]=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #get the spetial prices
# SPBPBE=dict()#IEBPSP-->SpetialPriceByPatienByExam
# for val in idx_spetialPrice:#for each patien with spetial prices
    
#     exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
#     exams=exams.split()#Split the string and put it in a list
    
#     tmp=[]#spetial prices
#     for val0 in idx_IEBPSP[val]:#for each exam with spetial price
#         price=patern.search(exams[val0]).group(2)
#         tmp.append(price)
#     SPBPBE[val]=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #remove the special price of csvFile
# for val in idx_spetialPrice:#for each patien with spetial prices
    
#     exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
#     exams=exams.split()#Split the string and put it in a list
    
#     for val0 in idx_IEBPSP[val]:#for each exam with spetial price
#         examCode=patern.search(exams[val0]).group(1)
#         exams[val0]=examCode
    
#     #Set the exams as string
#     tmp=" "
#     csvFile.thirdName[val]=tmp.join(exams)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the exam code by patient as dictionary
ECBP=dict()#ECBP-->ExamCodeByPatien
for val in idx_patients:#for each patien
     
    exams=csvFile.thirdName[val]#get the string examCodecs
    exams=list(map(int, exams.split()))#Split the string and put it in a list
    ECBP[val]=exams
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set ECBP as list of str´s
ECBP_str=dict()
for val in ECBP.items():
    tmp=list(map(str,val[1]))
    ECBP_str[val[0]]="\n".join(tmp)  
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set product of exams by patient
#examn product code by patient
EPCBP=dict()
for val in ECBP:
    EPCBP[val]=np.prod(ECBP[val])
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set color set as each study

#ECBNC --> Exam color by no PCR covits
ECBNC=dict()
for idx, val in ECBP.items():
    if any(np.array(val)!=2):
        ECBNC[idx]=True

#ECBAC --> Exam color by antigen covit
ECBAC=dict()
for idx, val in ECBP.items():
    if any(np.array(val)==487):
        ECBAC[idx]=True

#ECBABC --> Exam color by anti body covit
ECBABC=dict()
for idx, val in ECBP.items():
    if any(np.array(val)==491):
        ECBABC[idx]=True

#ECBCABC --> Exam color by cuantitative anti body covit
ECBCABC=dict()
for idx, val in ECBP.items():
    if any(np.array(val)==569):
        ECBCABC[idx]=True

#ECBSP --> Exam color by sars plus
ECBSP=dict()
for idx, val in ECBP.items():
    if any(np.array(val)==1009):
        ECBSP[idx]=True
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the exams name
examNameList=dict()
for val in idx_patients:#for each patien with spetial prices
    
    #ensure exams code are recored
    try: 
        examsName=pd_listExam.EXAMEN[ECBP[val]].tolist()
    except KeyError:
        print(CEND.format(csvFile.firstName[val],csvFile.secondName.iloc[val]))        
        sys.exit()
    
    #ensure exams name are recored
    for tmp in examsName:
        if type(tmp) == float:#(nan is float)el nombre del examen est'a vac'io en el archivo excel
            print(CEND.format(csvFile.firstName[val],csvFile.secondName.iloc[val]))        
            sys.exit()

    tmp="\n"
    examNameList[val]=tmp.join(examsName)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #check enterprice existence in listadoPreciosUrgent.csv/listadoPreciosStandar.csv
# for val in idx_patients:#for each patien
    
#     #urgent/standar
#     urgent=False
#     if val in idx_urgentes:
#         urgent=True
    
#     #enterprise name
#     enterprise=listEnterpriseNameByPatient[val]
    
#     if urgent:
#         try:
#             df_listPriceUrgent[enterprise]
#         except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
#             print("""OPERACION FALLIDA:\nEmpresa \"{0}\" no \
# definida en archivo: listadoPreciosUrgent.csv""".format(enterprise))        
#             sys.exit()
#     else:#Standar
#         try:
#             df_listPriceStandar[enterprise]
#         except KeyError:#enterprise NOT defined at  listadoPreciosStandar.csv
#             print("""OPERACION FALLIDA:\nEmpresa \"{0}\" no \
# definida en archivo: listadoPreciosEstandar.csv""".format(enterprise))        
#             sys.exit()
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# #Asign price
# pricesList=dict()
# for idx, val in enumerate(idx_patients):#for each patien
    
#     enterprise=listEnterpriseNameByPatient[val]
    
#     #urgent/standar
#     urgent=False
#     if val in idx_urgentes:
#         urgent=True
    
#     prices=[]
#     for val0 in ECBP[val]:#for each exam
        
#         if urgent:
#             price=df_listPriceUrgent[enterprise][val0]
            
#         else:#Standar
#             price=df_listPriceStandar[enterprise][val0]
        
#         #if not(isinstance(price, str)):
#         try:
            
#             #check existence of price (not NaN)
#             if np.isnan(np.float64(price)):#not exist
#                 if urgent:
#                     print(PNDAU.format(enterprise,val0,
#                                        csvFile.secondName[val],idx+1))
#                 else:
#                     print(PNDAS.format(enterprise,val0,
#                                        csvFile.secondName[val],idx+1))
#                     sys.exit()
            
#             #check maquila or general
#             if np.float64(price)==1:#maquila
#                 if urgent: price=float(df_listPriceUrgent["MAQUILA"][val0])
#                 else: price=float(df_listPriceStandar["MAQUILA"][val0])
#             elif np.float64(price)==2:#general
#                 if urgent: price=float(df_listPriceUrgent["GENERAL"][val0])
#                 else: price=float(df_listPriceStandar["GENERAL"][val0])
            
#         except ValueError:
#             pass
        
        
#         #append price in prices
#         prices.append(price)
    
#     #change spetial prices
#     if val in idx_spetialPrice:
         
#         for idx0, val0 in enumerate(idx_IEBPSP[val]):
#             prices[val0]=float(SPBPBE[val][idx0])
    
#     #append prices at dictionary
#     pricesList[val]=prices
#-----------------------------------------------------------------------------#
         
         
#-----------------------------------------------------------------------------#
# #set pricesList as list of str´s
# pricesList_str=dict()
# for val in pricesList.items():
    
#     tmp=list(map(str,val[1]))
#     pricesList_str[val[0]]="\n".join(tmp)  
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#make inter code
codeIntLab=dict()
codeIntCob=dict()
for idx, val in enumerate(idx_patients):

    urgent="U" if val in idx_urgentes else "N"
    
    codeIntCob[val]=day+'-'+subsidiary+'-'+str(idx+1).zfill(3)
    
    #Check if the exam is covid type
    examCovid="C"
    if not [i for i in [2,487,491,492,569,1009] if  i in ECBP[val]]:
        examCovid="O"
       
    codeIntLab[val]=day+'-'+subsidiary+'-'+str(idx+1).zfill(3)+urgent+examCovid+listEnterpriseCodeByPatient[
        val]+listShiftByPatient[val]+"P"+str(EPCBP[val]).zfill(5)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#asociate, as dict, each patient with its corresponding enterprise
counter = 0
dict_pattient_enterprise = {}
for idx, val in enumerate(idx_patients):
    
    if counter+1 < len(idx_enterprise):
        if idx_enterprise[counter+1] < val:
            counter += 1

    dict_pattient_enterprise[val] =  idx_enterprise[counter]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of no covit patients
tmp = []
for idx, val in enumerate(idx_patients):

    if not [i for i in [2,487,491,492,569,1009] if  i in ECBP[val]]:
        tmp.append(val)

idx_patients_noCovits = pd.Index(data=tmp)#convert list into pd index 
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise idx associated with idx_patients_noCovits
idx_enterprise_patients_noCovits = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_noCovits]))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of antigen covit patients
tmp = []
for idx, val in enumerate(idx_patients):

    if [i for i in [487] if  i in ECBP[val]]:
        tmp.append(val)

idx_patients_antigenCovit = pd.Index(data=tmp)#convert list into pd index
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise idx associated with idx_patients_antigenCovit
idx_enterprise_patients_antigenCovit = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_antigenCovit]))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of qualitative antybody covit patients
tmp = []
for idx, val in enumerate(idx_patients):

    if [i for i in [491] if  i in ECBP[val]]:
        tmp.append(val)

idx_patients_antibodyCovit = pd.Index(data=tmp)#convert list into pd index
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise idx associated with idx_patients_antibodyCovit
idx_enterprise_patients_antibodyCovit = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_antibodyCovit]))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of list_enterprise_forExclusiveExcel patients
idx_patients_enterprise_forExclusiveExcel_asDict = {}
idx_enterprise_enterprise_forExclusiveExcel_asDict = {}
for codeEnterprise_ in enterpriseCodecs_forExclusiveExcel:
    
    tmp = []
    for idx, val in enumerate(idx_patients):

        if [i for i in [codeEnterprise_] if  i in listEnterpriseCodeByPatient[val]]:
            tmp.append(val)

    idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_] = pd.Index(data=tmp)

    #get the enterprise idx associated with codeEnterprise_
    idx_enterprise_enterprise_forExclusiveExcel_asDict [codeEnterprise_]= list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_]]))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the index's of no covit patients
tmp = []
for idx, val in enumerate(idx_patients):

    if not [i for i in [2,487,491,492,569,1009] if  i in ECBP[val]]:
        tmp.append(val)

idx_patients_noCovits = pd.Index(data=tmp)#convert list into pd index 
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the enterprise idx associated with idx_patients_noCovits
idx_enterprise_patients_noCovits = list(set([dict_pattient_enterprise[tmp] for tmp in idx_patients_noCovits]))
#-----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#Create Excel
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#Export to excel-->cobranza
df_toExcel=pd.DataFrame({'COD INT':codeIntCob,
                         'FECHA':day[0:2]+'/'+day[2:4]+'/'+day[4:6],
                         'NOMBRE':csvFile['firstName'][idx_patients].str.strip()
                         +' '+csvFile['secondName'][idx_patients].str.strip(),
                         'EXAMEN':examNameList,
                         'COD':ECBP_str,
                         # 'PRECIO':pricesList_str,
                         'ESTATUS':np.NaN,
                         ' ':np.NaN,
                         'EMPRESA':listEnterpriseNameByPatient})
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel",
                        "{1}","{2}_cobranza.xlsx").format(currentPath,
                                  yymmddPath,day,time.strftime("%H_%M_%S"))


with pd.ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

    #Convert the dataframe to an XlsxWriter Excel object.
    df_toExcel.to_excel(writer, sheet_name=day, index=False)
    
    #Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets[day]
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
    
    border_format=workbook.add_format({'border': 1})
    #-----------------------------------------------------------------------------#
    
    #-----------------------------------------------------------------------------#
    #urgent_index
    urgent_index=[]
    for val in idx_urgentes:
        urgent_index.append(np.argwhere(idx_patients==val).item())
    
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


#-----------------------------------------------------------------------------#
def make_excel_antigen_antibody(idx_patients_,resultadoColumn,exam,path_):

    #----------------------------------------------------------------------------#
    #Export to excel-->antigen and antybody
    dictForDF = {
        'FECHA':day[0:2]+'/'+day[2:4]+'/'+day[4:6],
        'FOLIO': {x:codeIntCob[x] for x in idx_patients_},#codeIntLab
        #'PACIENTE':csvFile['firstName'][idx_patients_].str.strip()+' '+csvFile['secondName'][idx_patients_].str.strip(),
        'EXAMEN': exam,#{x:examNameList[x] for x in idx_patients_},
    }
    
    for key, value in resultadoColumn.items():
        dictForDF[key] = value
    
    dictForDF['VALIDO'] = np.NaN
    dictForDF['RECIBE RESULTADOS'] = np.NaN
    
    
    df_toExcel=pd.DataFrame(dictForDF)
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "{2}_laboratorio{3}.xlsx").format(currentPath,
                                        yymmddPath,day,path_)


    with pd.ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day]
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
        
        border_format=workbook.add_format({'border': 1})
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
def make_excel(idx_patients_, idx_enterprise_, path_=""):
    #idx_patients_ --> pandas index, the index (in the CSV file) of patients to show
    #idx_enterprise --> list, the index (in the CSV file) of enterprises to show

    #----------------------------------------------------------------------------#
    #merge idx_patients_ and idx_enterprise_    
    idx = idx_patients_.tolist() + idx_enterprise_
    
    idx.sort()
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #Export to excel-->laboratori
    df_toExcel=pd.DataFrame({
                             'OSR':np.NaN,
                             'COD INT':{x:codeIntLab[x] for x in idx_patients_},
                             'NOMBRE':csvFile['firstName'][idx].str.strip(), 
                             'APELLIDO':csvFile['secondName'][idx].str.strip(),
                             'EXAMEN':{x:examNameList[x] for x in idx_patients_},
                             'COD':{x:ECBP_str[x] for x in idx_patients_},
                             'ESTATUS':np.NaN,
                             'RESULTADO':np.NaN,
                             'ENVIO':np.NaN,
                             'REVISO':np.NaN,
                             'HORA ENVIO':np.NaN
                             })
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #set the OSR code in df_toExcel
    df_toExcel.loc[idx_enterprise_,"OSR"]=csvFile["secondName"][idx_enterprise_].str.strip()
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "{2}_laboratorio{3}.xlsx").format(currentPath,
                                        yymmddPath,day,path_)

    with pd.ExcelWriter(pathTosave, engine='xlsxwriter') as writer:
                                                           
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
        
        border_format=workbook.add_format({'border': 1})
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
def make_excel_enterprise_forExclusiveExcel(idx_patients_,path_):

    #----------------------------------------------------------------------------#
    #Export to excel-->antigen and antybody
    dictForDF = {
        'FECHA':day[0:2]+'/'+day[2:4]+'/'+day[4:6],
        'FOLIO': {x:codeIntLab[x] for x in idx_patients_},
        'PACIENTE':csvFile['firstName'][idx_patients_].str.strip()+' '+csvFile['secondName'][idx_patients_].str.strip(),
        'EXAMEN': {x:examNameList[x] for x in idx_patients_},
        'ESTATUS':np.NaN,
    }
    
    
    df_toExcel = pd.DataFrame(dictForDF)
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel","{1}",
                            "{2}_laboratorio{3}.xlsx").format(currentPath,
                                        yymmddPath,day,path_)

    with pd.ExcelWriter(pathTosave, engine='xlsxwriter') as writer:

        #Convert the dataframe to an XlsxWriter Excel object.
        df_toExcel.to_excel(writer, sheet_name=day, index=False)
        
        #Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets[day]
        #-----------------------------------------------------------------------------#
        
        #-----------------------------------------------------------------------------#
        #set formats
        
        #Wrap EXAMEN
        widthColumn = workbook.add_format({'text_wrap': True})
        worksheet.set_column('B:B', 28, widthColumn)
        worksheet.set_column('C:C', 30, widthColumn)
        worksheet.set_column('D:D', 28, widthColumn)
        worksheet.set_column('E:E', 10, widthColumn)
        
        border_format=workbook.add_format({'border': 1})
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

#-----------------------------------------------------------------------------#
#make excel

#antygen and antybody
make_excel_antigen_antibody(idx_patients_antigenCovit,{'RESULTADO':np.NaN},"Antígeno SARS CoV-2","_antigenSARS_COV2")
make_excel_antigen_antibody(idx_patients_antibodyCovit,{'IgG':np.NaN, 'IgM':np.NaN},"IgG IgM SARS CoV-2","_antibodySARS_COV2")

#laboratory
make_excel(idx_patients, idx_enterprise)

#no covits
make_excel(idx_patients_noCovits, idx_enterprise_patients_noCovits, "_otros")

#for list_enterprise_forExclusiveExcel
for codeEnterprise_ in idx_patients_enterprise_forExclusiveExcel_asDict:
    
    make_excel_enterprise_forExclusiveExcel(
        idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_], "_{}".format(codeEnterprise_)
        )
#-----------------------------------------------------------------------------#


# #----------------------------------------------------------------------------#
# #Update the historic DB

# #set the path
# historicDB_path=os.path.join("{0}","..","DB_historico",
#                              "borra.csv").format(currentPath)

# #make, if not exist, the csv file as empty 
# if os.path.isfile(historicDB_path)==False:
#     df_patientList.to_csv(historicDB_path, columns=["FOLIO INTERNO","NOMBRE",
#                                                 "APELLIDO","RESULTADO"],
#                       header=True, index=False)

# #read the csv file
# pd_historicPatientDB=pd.read_csv(historicDB_path, index_col="FOLIO INTERNO")

# tmp=pd_historicPatientDB.index.isin(df_patientList["FOLIO INTERNO"].tolist())
# tmp2=df_patientList["FOLIO INTERNO"].isin(pd_historicPatientDB.index)


# pd_historicPatientDB.loc[tmp]=np.array(
#     df_patientList.loc[tmp2,["NOMBRE","APELLIDO","RESULTADO"]])



# #append into pd_historicPatientDB
# A=df_patientList.loc[~tmp2,"FOLIO INTERNO"].values

# #pd_historicPatientDB.loc[ A.tolist() ]=df_patientList.loc[~tmp2,["NOMBRE","APELLIDO","RESULTADO"]].values[0]

# for tmp in A:
#     pd_historicPatientDB.loc[ tmp ]=["a","b","d"]



# #df_patientList.loc[~tmp2].to_string(
# #    index=False, header=False, columns=["NOMBRE","APELLIDO","RESULTADO"])
# #df_patientList.loc[~tmp2,["NOMBRE","APELLIDO","RESULTADO"]].to_list()




# #pd_historicPatientDB.to_csv(historicDB_path,header=True, index=False)

# #----------------------------------------------------------------------------#
