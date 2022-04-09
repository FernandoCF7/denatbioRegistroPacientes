# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 15:43:59 2021

@author: Paulina Santiago
"""

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
#sys.exit("ahi se ven prrs")

#-----------------------------------------------------------------------------#
day='010321'
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set path
currentPath=os.path.dirname(os.path.abspath(__file__))
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
csvFile=(pd.read_csv(filePath_registro,sep='*'))

columnas=["firstname", "secondname", "thirdName", "age", "sex", "telphone",
          "estate", "delegation", "symptomatic"]

#set as upper
csvFile["firstName"]=csvFile["firstName"].str.upper()
csvFile["secondName"]=csvFile["secondName"].str.upper()



#set without acents
csvFile["firstName"]=csvFile["firstName"].str.normalize('NFKD').str.encode(
    'ascii', errors='ignore').str.decode('utf-8')
csvFile["secondName"]=csvFile["secondName"].str.normalize('NFKD').str.encode(
    'ascii', errors='ignore').str.decode('utf-8')
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read codeEnterprise file
filePath_codeEnterprise=os.path.join("{0}","..","empresas",
                                     "codeEnterprise.csv").format(currentPath)
codeEnterpriseFile=(pd.read_csv(filePath_codeEnterprise, encoding='latin-1'))

#set as upper
codeEnterpriseFile["empresa"]=codeEnterpriseFile["empresa"].str.upper()

#set without acents
codeEnterpriseFile["empresa"]=codeEnterpriseFile[
    "empresa"].str.normalize('NFKD').str.encode('ascii',
                                           errors='ignore').str.decode('utf-8')
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read pd_listExam file
filePath_listExam=os.path.join("{0}","..","listadoDeExamenes",
                               "listExam.csv").format(currentPath)
pd_listExam=(pd.read_csv(filePath_listExam, usecols=["COD INT","EXAMEN"]))

#set index of pd_listExam as COD INT column
pd_listExam.set_index("COD INT", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read clavesNombresEmpresa file
filePath_pd_listExam=os.path.join("{0}","..","empresas",
                               "clavesNombresEmpresa.csv").format(currentPath)
df_enterpriseNames=(pd.read_csv(filePath_pd_listExam))

#set index of enterpriseNames as clave column
df_enterpriseNames.set_index("clave", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read enterprice price files

#Standar
filePath_listPrice=os.path.join("{0}","..","listadoDePrecios",
                              "listadoPreciosEstandar.csv").format(currentPath)
df_listPriceStandar=(pd.read_csv(filePath_listPrice))

#Urgent
filePath_listPrice=os.path.join("{0}","..","listadoDePrecios",
                              "listadoPreciosUrgentes.csv").format(currentPath)
df_listPriceUrgent=(pd.read_csv(filePath_listPrice))


#set index of COD INT as clave column
df_listPriceStandar.set_index("COD INT", inplace=True)
df_listPriceUrgent.set_index("COD INT", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read spetial costs permissions by enterprise file
filePath_persmisosCostosEspeciales=os.path.join("{0}","..","listadoDePrecios",
             "listadoPermisosCostosEspecialesEmpresas.csv").format(currentPath)
df_permisosCostosEspeciales=(pd.read_csv(filePath_persmisosCostosEspeciales))

#set index of EMPRESA INT as clave column
df_permisosCostosEspeciales.set_index("EMPRESA", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#define error mesages

#Precio no definido archivo urgentes (listadoPreciosUrgent.csv)
PNDAU="""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosUrgent.csv para la empresa \"{0}\" con el examen \"{1}\" """

#Precio no definido archivo standar (listadoPreciosEtandar.csv)
PNDAS="""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosStandar.csv para la empresa \"{0}\" con el examen \"{1}\" """

#Not autorized for assign spetial price
NAFASP="""OPERACION FALLIDA\nLa empresa \"{0}\" no está autorizada para \
ofertar precios especiales; retire el precio especial del archivo de ingreso\ 
de pacientes (.txt), o modifique el permiso asignado a dicha empresa en el \ 
archivo listadoPermisosCostosEspecialesEmpresas.csv"""

#Code of exam nor defined
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
#get the enterprise names and set in enterpriseNames
#get the enterprise codecs and set in enterpriseCodecs
enterpriseNames=[]
enterpriseCodecs=[]
for val in idx_enterprise:#for each enterprise
    
    #get the enterprise name
    enterprise_name=patern.search(csvFile["firstName"][val]).group()
    
    #search enterprise_name in codeEnterpriseFile
    logicTMP=enterprise_name==codeEnterpriseFile['empresa'].str.upper()
    
    #not defined enterprise mesage error
    if not(any(logicTMP)):
        print('''OPERACION FALLIDA\nEmpresa no definida: {0} en el archivo\
codeEnterprise.csv'''.format(enterprise_name))
        sys.exit("")
    
    #get enterprise code of clavesNombresEmpresa
    enterprise_code=codeEnterpriseFile.clave[logicTMP==True].item()
    
    #append enterpriseCodecs
    enterpriseCodecs.append(enterprise_code)
    
    #append enterprise_code
    enterpriseNames.append(df_enterpriseNames.loc[enterprise_code].item())
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set the enterprise name by patient
listEnterpriseNameByPatient=[]
for idx, val in enumerate(idx_enterprise[:-1]):
    for val0 in range(val,idx_enterprise[idx+1]):
        listEnterpriseNameByPatient.append(enterpriseNames[idx])
else:
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
#search for especial prices
idx_spetialPrice=[]
patern=re.compile(r'([\d\.-]+)-([\d\.-]+)')
for val in idx_patients:
    
    priceValue=csvFile.thirdName[val]
    if priceValue.find("-")!=-1:
        idx_spetialPrice.append(val)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#validate if enterprises can apply special prices
for val in idx_spetialPrice:
    
    enterprise=listEnterpriseNameByPatient[val]
    
    if df_permisosCostosEspeciales.COSTO_ESPECIAL[enterprise]==0:
        print(NAFASP.format(enterprise)) 
        sys.exit()
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the idx in the exams by patient of the spetial prices
idx_IEBPSP=dict()#idx_IEBPSP-->idx InExamsByPatientSpetialPrice
for val in idx_spetialPrice:#for each patien with spetial prices
    exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
    exams=exams.split()#Split the string and put it in a list
    
    tmp=[]#positions of spetial prices
    for idx0, val0 in enumerate(exams):
        if val0.find("-")!=-1:
            tmp.append(idx0)
    idx_IEBPSP[val]=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get the spetial prices
SPBPBE=dict()#IEBPSP-->SpetialPriceByPatienByExam
for val in idx_spetialPrice:#for each patien with spetial prices
    
    exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
    exams=exams.split()#Split the string and put it in a list
    
    tmp=[]#spetial prices
    for val0 in idx_IEBPSP[val]:#for each exam with spetial price
        price=patern.search(exams[val0]).group(2)
        tmp.append(price)
    SPBPBE[val]=tmp
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#remove the special price of csvFile
for val in idx_spetialPrice:#for each patien with spetial prices
    
    exams=csvFile.thirdName[val]#get the string examCodecs and spetialPrices
    exams=exams.split()#Split the string and put it in a list
    
    for val0 in idx_IEBPSP[val]:#for each exam with spetial price
        examCode=patern.search(exams[val0]).group(1)
        exams[val0]=examCode
    
    #Set the exams as string
    tmp=" "
    csvFile.thirdName[val]=tmp.join(exams)
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
#set the exams name
examNameList=dict()
for val in idx_patients:#for each patien with spetial prices
    
    #ensure exams are recored
    try: 
        examsName=pd_listExam.EXAMEN[ECBP[val]].tolist()
    except KeyError:
        print(CEND.format(csvFile.firstName[val],csvFile.secondName.iloc[val]))        
        sys.exit()
    
    tmp="\n"
    examNameList[val]=tmp.join(examsName)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#check enterprice existence in listadoPreciosUrgent.csv/listadoPreciosStandar.csv
for val in idx_patients:#for each patien
    
    #urgent/standar
    urgent=False
    if val in idx_urgentes:
        urgent=True
    
    #enterprise name
    enterprise=listEnterpriseNameByPatient[val]
    
    if urgent:
        try:
            df_listPriceUrgent[enterprise]
        except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
            print("""OPERACION FALLIDA:\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosUrgent.csv""".format(enterprise))        
            sys.exit()
    else:#Standar
        try:
            df_listPriceStandar[enterprise]
        except KeyError:#enterprise NOT defined at  listadoPreciosStandar.csv
            print("""OPERACION FALLIDA:\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosStandar.csv""".format(enterprise))        
            sys.exit()
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Asign price
pricesList=dict()
for val in idx_patients:#for each patien
    
    enterprise=listEnterpriseNameByPatient[val]
    
    #urgent/standar
    urgent=False
    if val in idx_urgentes:
        urgent=True
    
    prices=[]
    for val0 in ECBP[val]:#for each exam
        
        if urgent:
            price=df_listPriceUrgent[enterprise][val0]
            
        else:#Standar
            price=df_listPriceStandar[enterprise][val0]
        
        #check existence of price (not NaN)
        if np.isnan(np.float(price)):#not exist
            if urgent:
                print(PNDAU.format(enterprise,val0))
            else:
                print(PNDAS.format(enterprise,val0))
            sys.exit()
        
        #check maquila or general
        if np.float(price)==1:#maquila
            if urgent: price=float(df_listPriceUrgent["MAQUILA"][val0])
            else: price=float(df_listPriceStandar["MAQUILA"][val0])
        elif np.float(price)==2:#general
            if urgent: price=float(df_listPriceUrgent["GENERAL"][val0])
            else: price=float(df_listPriceStandar["GENERAL"][val0])
            
        #append price in prices
        prices.append(price)
    
    #change spetial prices
    if val in idx_spetialPrice:
         
        for idx0, val0 in enumerate(idx_IEBPSP[val]):
            prices[val0]=float(SPBPBE[val][idx0])
    
    #append prices at dictionary
    pricesList[val]=prices
#-----------------------------------------------------------------------------#
         
         
#-----------------------------------------------------------------------------#
#set pricesList as list of str´s
pricesList_str=dict()
for val in pricesList.items():
    
    tmp=list(map(str,val[1]))
    pricesList_str[val[0]]="\n".join(tmp)  
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#make inter code
codeIntLab=dict()
codeIntCob=dict()
for idx, val in enumerate(idx_patients):

    urgent="U" if val in idx_urgentes else "N"
    
    codeIntCob[val]=day+'-'+str(idx+1).zfill(3)
    
    codeIntLab[val]=day+'-'+str(idx+1).zfill(3)+urgent+listEnterpriseCodeByPatient[
        val]+listShiftByPatient[val]+"P"+str(EPCBP[val]).zfill(5)
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
                         'PRECIO':pricesList_str,
                         'URGENTE':np.NaN,
                         ' ':np.NaN,
                         'EMPRESA':listEnterpriseNameByPatient})
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel",
                        "{1}","{2}_cobranza.xlsx").format(currentPath,
                                  yymmddPath,day,time.strftime("%H_%M_%S"))

writer=pd.ExcelWriter(pathTosave, engine='xlsxwriter')

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
worksheet.set_column('F:F', 7, widthColumn)

border_format=workbook.add_format({'border': 1})
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#urgent_index
urgent_index=[]
for val in idx_urgentes:
    urgent_index.append(np.argwhere(idx_patients==val).item())

for tmp in urgent_index:
    
    worksheet.merge_range('G'+str(tmp+2)+':H'+str(tmp+2),"URGENTE",
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
#save df_toExcel file
writer.save()
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#Export to excel-->laboratorio
df_toExcel=pd.DataFrame({'OSR':np.NaN,
                         'COD INT':codeIntLab,
                         'NOMBRE':csvFile['firstName'].str.strip(),
                         'APELLIDO':csvFile['secondName'].str.strip(),
                         'EXAMEN':examNameList,
                         'COD':ECBP_str,
                         'URGENTE':np.NaN,
                         'RESUL':np.NaN
                         })
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#set the OSR code in df_toExcel
df_toExcel.loc[idx_enterprise,"OSR"]=csvFile["secondName"][idx_enterprise].str.strip()
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel","{1}",
                        "{2}_laboratorio.xlsx").format(currentPath,
                                    yymmddPath,day,time.strftime("%H_%M_%S"))

writer=pd.ExcelWriter(pathTosave, engine='xlsxwriter')

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
                                    'bg_color': 'orange'})

#Wrap EXAMEN and PRECIO column
widthColumn = workbook.add_format({'text_wrap': True})
worksheet.set_column('E:E', 40, widthColumn)
worksheet.set_column('F:F', 6, widthColumn)

border_format=workbook.add_format({'border': 1})
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Set urgents format
for tmp in idx_urgentes:
    
    worksheet.merge_range('G'+str(tmp+2)+':H'+str(tmp+2),"URGENTE",
                          merge_urgentFormat)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Add border
numRows=len(df_toExcel)

worksheet.conditional_format('A1:H'+str(numRows+1),{'type':'no_blanks',
                                      'format':border_format})

worksheet.conditional_format('A1:H'+str(numRows+1),{'type':'blanks',
                                      'format':border_format})
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Set format to enterprise
merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                    'bold': True, 'font_color': 'white',
                                    'bg_color': 'black'})

for idx, val, in enumerate(idx_enterprise):
    worksheet.merge_range('B'+str(val+2)+':H'+str(val+2),enterpriseNames[idx],
                          merge_format)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#save df_toExcel file
writer.save()
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







#if val.upper().find("EMPRESA")!=-1:
#encoding='latin-1'

#df_patientList.set_index("FOLIO INTERNO").to_csv("borra.csv",columns=["NOMBRE",
#                   
#                     "APELLIDO","RESULTADO"],header=True)
#dtype={'thirdName': 'string'}