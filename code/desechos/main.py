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
#sys.exit("ahi se ven prrs")

#-----------------------------------------------------------------------------#
day='271220'
folioInicial=21
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#set path
currentPath=os.path.dirname(os.path.abspath(__file__))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read registro file
filePath_registro=os.path.join("{0}","..","DB_ingresoPorVoz","{1}.txt").format(
    currentPath,day)
csvFile=(pd.read_csv(filePath_registro,sep='*'))

csvFile.columns=["firstName","secondName",'thirdName']

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
#read listExam file
filePath_listExam=os.path.join("{0}","..","listadoDeExamenes",
                               "listExam.csv").format(currentPath)
listExam=(pd.read_csv(filePath_listExam, usecols=["COD INT","EXAMEN"]))

#set index of listExam as COD INT column
listExam.set_index("COD INT", inplace=True)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#read clavesNombresEmpresa file
filePath_listExam=os.path.join("{0}","..","empresas",
                               "clavesNombresEmpresa.csv").format(currentPath)
df_enterpriseNames=(pd.read_csv(filePath_listExam))

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
#search for enterprise
idx_enterprise=[]
name_enterprise=[]
shift=[]#turno
patern=re.compile(r'/.*?/')
for idx, val in enumerate(csvFile["firstName"]):
    if val.find("EMPRESA")!=-1:
        idx_enterprise.append(idx)
        
        #append enterprise name
        name_enterprise.append(patern.search(val).group())
        
        #append shift
        tmp_shift='MATUTINO'
        if val.find('VESPERTINO')!=-1:
            tmp_shift='VESPERTINO'

        shift.append(tmp_shift)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#append folio_OSR
folio_OSR=[]
for val in idx_enterprise:
    folio_OSR.append(csvFile["secondName"][val])
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#odx patient list
idx_patients=csvFile.index[ ~csvFile.index.isin(idx_enterprise) ]
#-----------------------------------------------------------------------------#


#-----------------------------------------------------------------------------#
#search for especial prices
idx_spetialPrice=[]
idxExam_spetialPrice=[]
value_spetialPrice=[]
patern=re.compile(r'([\d\.-]+)-([\d\.-]+)')
justCodeExam=[]
for idx, val in enumerate(csvFile["thirdName"]):
    
    #Evaluate just the patients (not enterprises)
    if not(idx in idx_patients):
        continue
    
    examWithoutPrice=""
    flag=False
    for idx2, val2 in enumerate(val.split()):
        
        examTmp=val2
        if val2.find("-")!=-1:#search for "-"
            
            flag=True
            
            #append the index
            idx_spetialPrice.append(idx)
            
            #append the exam index
            idxExam_spetialPrice.append(idx2)
            
            #append the spetial price
            value_spetialPrice.append(patern.search(val2).group(2))            
            
            #set the 
            examTmp=patern.search(val2).group(1)
            
        #set the exam without the price
        if idx2==0:
            examWithoutPrice=examWithoutPrice+examTmp
        else:
            examWithoutPrice=examWithoutPrice+" "+examTmp
    
    #Actualize the csvFile["thirdName"] value
    if flag:
        csvFile["thirdName"].iloc[idx]=examWithoutPrice

idxExam_spetialPrice=np.asarray(idxExam_spetialPrice, dtype=object)
value_spetialPrice=np.asarray(value_spetialPrice, dtype=object)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#odx patient list
patientList=csvFile.take(idx_patients)
#-----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#digit code assign
folio=[tmp.zfill(3)+'NC' for tmp in
       list(map(str, range(folioInicial,folioInicial+idx_patients.size) ))]
folio=np.array(folio)
folio=folio.astype('U16')
#----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Urgents
idx_urgentes=[]
name_without_urgente=[]
patern_urgente=re.compile(r'URGENTE', flags=re.IGNORECASE)
for idx, val in enumerate(patientList["firstName"]):
    
    if val.find("URGENTE")!=-1:
        
        #append idx_urgentes
        idx_urgentes.append(idx)
        
        #cut "urgente" in the chain
        tmp=patern_urgente.search(val)
        name_without_urgente.append(val[0:tmp.start()]+val[tmp.end():])  
    
#assign
for tmp in idx_urgentes:
    folio[tmp]=np.char.add(folio[tmp][0:3],'UC')

idxDF_urgentes=patientList.index[idx_urgentes]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Exam assign
exam_list=[]
examCodecs_list=[]
for idx, val in enumerate(patientList.thirdName):
    examCodecs=list(map(int, val.split()))
    
    try: 
        examns=listExam.EXAMEN[examCodecs].tolist()
    except KeyError:
        print('''OPERACION FALLIDA\nCódigo de examen no definido;
              paciente: {0} {1}'''.format(patientList.firstName.iloc[idx],patientList.secondName.iloc[idx]))        
        sys.exit()
    
    for idxInt, valInt in enumerate(examns):
        if idxInt==0:
            str_examns=valInt
            str_examnsCodecs=str(examCodecs[idxInt])
        else:
            str_examns=str_examns+'\n'+valInt
            str_examnsCodecs=str_examnsCodecs+'\n'+str(examCodecs[idxInt])
    exam_list.append(str_examns)
    examCodecs_list.append(str_examnsCodecs)
#-----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#code enterprise and shift assign
tmp=-1
listEnterpriseNames=[]
for tmp in range(len(idx_enterprise)-1):
    
    #enterprise code
    logicTMP=name_enterprise[tmp].upper()==codeEnterpriseFile[
        'empresa'].str.upper()
    tmpCodEnterprise='XX'
    if logicTMP.any():
        tmpCodEnterprise=codeEnterpriseFile['clave'][logicTMP]
    else:
        print('''OPERACION FALLIDA\nEmpresa no definida: {0}'''.format(name_enterprise[tmp]))
        sys.exit("")
        
    logic=np.logical_and(idx_patients>idx_enterprise[tmp], idx_patients<idx_enterprise[tmp+1])
    folio[logic]=np.char.add(folio[logic],tmpCodEnterprise)
    
    #append enterprise name as normalized name
    listEnterpriseNames.append(df_enterpriseNames.empresa.loc[tmpCodEnterprise].item())
    
    #shift
    if shift[tmp]=='MATUTINO':
        folio[logic]=np.char.add(folio[logic],'M')
    else:
        folio[logic]=np.char.add(folio[logic],'V')
    
else:
    
    #set enterprise code
    logicTMP=name_enterprise[tmp+1]==codeEnterpriseFile['empresa']
    tmpCodEnterprise='XX'
    if logicTMP.any():
        tmpCodEnterprise=codeEnterpriseFile['clave'][logicTMP]
    
    logic=idx_patients>idx_enterprise[-1]
    folio[logic]=np.char.add(folio[logic],tmpCodEnterprise)
    
    #append enterprise name as normalized name
    listEnterpriseNames.append(df_enterpriseNames.empresa.loc[tmpCodEnterprise].item())
    
    #shift
    if shift[tmp+1]=='MATUTINO':
        folio[logic]=np.char.add(folio[logic],'M')
    else:
        folio[logic]=np.char.add(folio[logic],'V')
#----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#Price assign
exam_priceList=[]
for idx1, val1 in enumerate(idx_enterprise[0:-1]):#Asign by OSR
    
    codExamByOSR=csvFile.thirdName[val1+1:idx_enterprise[idx1+1]]
    
    for tmp1, idx2 in enumerate(codExamByOSR):#Asign by patient
        codExamByPatient=list(map(int, idx2.split()))
        
        for idx3, val3 in enumerate(codExamByPatient):#Asign by exam
            
            if list(codExamByOSR.index)[tmp1] in idxDF_urgentes:#urgent exam
                try:#enterprise defined at listadoPreciosUrgent.csv
                    
                    #search for spetial price                    
                    idxOfOSR=codExamByOSR.index.tolist()[tmp1]
                    logicSpetialPrices=list(map(lambda x: x ==idxOfOSR , idx_spetialPrice))
                    logicSpetialPrices=np.asarray(logicSpetialPrices)
                    
                    flagSpetialPrice=False
                    
                    if any(logicSpetialPrices):
                        
                        if df_permisosCostosEspeciales.COSTO_ESPECIAL[listEnterpriseNames[idx1]]==0:
                            print("""OPERACION FALLIDA\nLa empresa \"{0}\" no \
está autorizada para ofertar precios especiales; modifique el archivo de \
ingreso de pacientes, o modifique el estatus de la empresa en el archivo \
listadoPermisosCostosEspecialesEmpresas.csv""".format(listEnterpriseNames[idx1])) 
                            sys.exit()

                        if idx3 in idxExam_spetialPrice[logicSpetialPrices]:
                            idxExamInSpetialPrice = idx3==idxExam_spetialPrice                            
                            
                            price=value_spetialPrice[list(idxExamInSpetialPrice & logicSpetialPrices)].item()
                            price=str(float(price))
                            flagSpetialPrice=True
                            
                            
                    if np.isnan(df_listPriceUrgent[listEnterpriseNames[idx1]].loc[val3]) and not(flagSpetialPrice):#NaN price
                        print("""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosUrgent.csv para la empresa \"{0}\" con el examen \"{1}\" """.format(listEnterpriseNames[idx1],val3))        
                        sys.exit()
                    
                    if not(flagSpetialPrice):
                        price=str(df_listPriceUrgent[listEnterpriseNames[idx1]].loc[val3])
                        
                        if float(price)==1:#maquila
                            price=str(df_listPriceUrgent["MAQUILA"].loc[val3])
                        elif  float(price)==2:#general
                            price=str(df_listPriceUrgent["GENERAL"].loc[val3])
                    
                    if idx3==0:#first patient
                        str_examnsPrice=price
                    else:#Not first patient
                        
                        str_examnsPrice=str_examnsPrice+"\n"+price
                        
                except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
                    print("""OPERACION FALLIDA\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosUrgent.csv""".format(listEnterpriseNames[idx1]))        
                    sys.exit()
                    
            else:#Not urgent exam
                try:#enterprise defined at listadoPreciosEstandar.csv
                    
                    
                    #search for spetial price                    
                    idxOfOSR=codExamByOSR.index.tolist()[tmp1]
                    logicSpetialPrices=list(map(lambda x: x ==idxOfOSR , idx_spetialPrice))
                    logicSpetialPrices=np.asarray(logicSpetialPrices)
                    
                    flagSpetialPrice=False
                    
                    if any(logicSpetialPrices):
                        
                        if df_permisosCostosEspeciales.COSTO_ESPECIAL[listEnterpriseNames[idx1]]==0:
                            print("""OPERACION FALLIDA\nLa empresa \"{0}\" no \
está autorizada para ofertar precios especiales; modifique el archivo de \
ingreso de pacientes, o modifique el estatus de la empresa en el archivo \
listadoPermisosCostosEspecialesEmpresas.csv""".format(listEnterpriseNames[idx1])) 
                            sys.exit()

                        if idx3 in idxExam_spetialPrice[logicSpetialPrices]:
                            idxExamInSpetialPrice = idx3==idxExam_spetialPrice                            
                            
                            price=value_spetialPrice[list(idxExamInSpetialPrice & logicSpetialPrices)].item()
                            price=str(float(price))
                            flagSpetialPrice=True
                    
                    if np.isnan(df_listPriceStandar[listEnterpriseNames[idx1]].loc[val3]) and not(flagSpetialPrice):
                        print("""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosEstandar.csv para la empresa \"{0}\" con el examen \"{1}\" """.format(listEnterpriseNames[idx1],val3))        
                        sys.exit()
                    
                    if not(flagSpetialPrice):
                        price=str(df_listPriceStandar[listEnterpriseNames[idx1]].loc[val3])
                        
                        if float(price)==1:#maquila
                            price=str(df_listPriceStandar["MAQUILA"].loc[val3])
                        elif  float(price)==2:#general
                            price=str(df_listPriceStandar["GENERAL"].loc[val3])
                            
                    
                    if idx3==0:#first patient
                        str_examnsPrice=price
                    else:#Not first patient
                        str_examnsPrice=str_examnsPrice+"\n"+price
                
                except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
                    print("""OPERACION FALLIDA\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosEstandar.csv""".format(listEnterpriseNames[idx1]))        
                    sys.exit()
            
        exam_priceList.append(str_examnsPrice)

else:

        
    codExamByOSR=csvFile.thirdName[idx_enterprise[idx1+1]+1:]
    
    for tmp1, idx2 in enumerate(codExamByOSR):#Asign by patient
        codExamByPatient=list(map(int, idx2.split()))
        
        for idx3, val3 in enumerate(codExamByPatient):#Asign by exam
            
            if list(codExamByOSR.index)[tmp1] in idxDF_urgentes:#urgent exam
                try:#enterprise defined at listadoPreciosUrgent.csv
                    
                    #search for spetial price                    
                    idxOfOSR=codExamByOSR.index.tolist()[tmp1]
                    logicSpetialPrices=list(map(lambda x: x ==idxOfOSR , idx_spetialPrice))
                    logicSpetialPrices=np.asarray(logicSpetialPrices)
                    
                    flagSpetialPrice=False
                    
                    if any(logicSpetialPrices):
                        
                        if df_permisosCostosEspeciales.COSTO_ESPECIAL[listEnterpriseNames[idx1+1]]==0:
                            print("""OPERACION FALLIDA\nLa empresa \"{0}\" no \
está autorizada para ofertar precios especiales; modifique el archivo de \
ingreso de pacientes, o modifique el estatus de la empresa en el archivo \
listadoPermisosCostosEspecialesEmpresas.csv""".format(listEnterpriseNames[idx1+1])) 
                            sys.exit()

                        if idx3 in idxExam_spetialPrice[logicSpetialPrices]:
                            idxExamInSpetialPrice = idx3==idxExam_spetialPrice                            
                            
                            price=value_spetialPrice[list(idxExamInSpetialPrice & logicSpetialPrices)].item()
                            price=str(float(price))
                            flagSpetialPrice=True
                
                
                    if np.isnan(df_listPriceUrgent[listEnterpriseNames[idx1+1]].loc[val3]) and not(flagSpetialPrice):#NaN price
                        print("""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosUrgent.csv para la empresa \"{0}\" con el examen \"{1}\" """.format(listEnterpriseNames[idx1+1],val3))        
                        sys.exit()
                    
                    
                    if not(flagSpetialPrice):
                        price=str(df_listPriceUrgent[listEnterpriseNames[idx1+1]].loc[val3])
                        
                        if float(price)==1:#maquila
                            price=str(df_listPriceUrgent["MAQUILA"].loc[val3])
                        elif  float(price)==2:#general
                            price=str(df_listPriceUrgent["GENERAL"].loc[val3])
                    
                    if idx3==0:#first patient
                        str_examnsPrice=price
                    else:#Not first patient
                        str_examnsPrice=str_examnsPrice+"\n"+price
                    
                    
                except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
                    print("""OPERACION FALLIDA\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosUrgent.csv""".format(listEnterpriseNames[idx1+1]))        
                    sys.exit()
                    
            else:#Not urgent exam
                try:#enterprise defined at listadoPreciosEstandar.csv
                    
                
                    #search for spetial price                    
                    idxOfOSR=codExamByOSR.index.tolist()[tmp1]
                    logicSpetialPrices=list(map(lambda x: x ==idxOfOSR , idx_spetialPrice))
                    logicSpetialPrices=np.asarray(logicSpetialPrices)
                    
                    flagSpetialPrice=False
                    
                    if any(logicSpetialPrices):
                        
                        if df_permisosCostosEspeciales.COSTO_ESPECIAL[listEnterpriseNames[idx1+1]]==0:
                            print("""OPERACION FALLIDA\nLa empresa \"{0}\" no \
está autorizada para ofertar precios especiales; modifique el archivo de \
ingreso de pacientes, o modifique el estatus de la empresa en el archivo \
listadoPermisosCostosEspecialesEmpresas.csv""".format(listEnterpriseNames[idx1+1])) 
                            sys.exit()

                        if idx3 in idxExam_spetialPrice[logicSpetialPrices]:
                            idxExamInSpetialPrice = idx3==idxExam_spetialPrice                            
                            
                            price=value_spetialPrice[list(idxExamInSpetialPrice & logicSpetialPrices)].item()
                            price=str(float(price))
                            flagSpetialPrice=True

                    if np.isnan(df_listPriceStandar[listEnterpriseNames[idx1+1]].loc[val3]) and not(flagSpetialPrice):
                        print("""OPERACION FALLIDA\nPrecio no definido en archivo: \
listadoPreciosEstandar.csv para la empresa \"{0}\" con el examen \"{1}\" """.format(listEnterpriseNames[idx1+1],val3))        
                        sys.exit()
                    
                    if not(flagSpetialPrice):
                        price=str(df_listPriceStandar[listEnterpriseNames[idx1+1]].loc[val3])
                        
                        if float(price)==1:#maquila
                            price=str(df_listPriceStandar["MAQUILA"].loc[val3])
                        elif  float(price)==2:#general
                            price=str(df_listPriceStandar["GENERAL"].loc[val3])
                    
                    if idx3==0:#first patient
                        str_examnsPrice=price
                    else:#Not first patient
                        str_examnsPrice=str_examnsPrice+"\n"+price
                    
                
                except KeyError:#enterprise NOT defined at  listadoPreciosUrgent.csv
                    print("""OPERACION FALLIDA\nEmpresa \"{0}\" no \
definida en archivo: listadoPreciosEstandar.csv""".format(listEnterpriseNames[idx1+1]))        
                    sys.exit()
            
        #print(str_examnsPrice)
        exam_priceList.append(str_examnsPrice)
#-----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
#add 'P' to folio
folio=np.char.add(folio,'P')
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#add ddmmaa to folio
folio=np.char.add([day+'-'],folio)
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
urgenteText=[]
for idx, val in enumerate(patientList["firstName"]):
    if val.find("URGENTE")!=-1:
        urgenteText.append('URGENTE')
    else:
        urgenteText.append(' ')
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#pandas dataFrame considering patients
patientList['firstName'].iloc[idx_urgentes]=name_without_urgente
#patientList['firstName'].iloc[idx_otros]=name_without_otros

#patient list without blank spaces begining or at end
patientList['firstName']=patientList['firstName'].str.strip()
patientList['secondName']=patientList['secondName'].str.strip()


df_patientList=pd.DataFrame( {'FOLIO OSR':np.NaN, 'FOLIO INTERNO':folio,
                          'NOMBRE':patientList['firstName'],
                          'APELLIDO':patientList['secondName'],
                          'EXAMEN':exam_list,
                          'URGENTE':urgenteText,
                          'RESULTADO':np.NaN}, index=idx_patients )
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#pandas dataFrame considering enterprise
df_enterprise=pd.DataFrame( {'FOLIO OSR':folio_OSR, 'FOLIO INTERNO':np.NaN,
                          'NOMBRE':listEnterpriseNames,
                          'APELLIDO':np.NaN,
                          'EXAMEN':np.NaN,
                          'URGENTE':np.NaN,
                          'RESULTADO':np.NaN}, index=idx_enterprise )
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#attach patients and enterprise
csvToExport=df_patientList.append(df_enterprise).sort_index()
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#save csv
#csvToExport.to_csv( os.path.join("{0}","..","listadosGeneradosParaExel",
#                                 "{1}_{2}.csv").format(currentPath,day,
#                                 time.strftime("%H_%M_%S")), index=False)
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#Add format using xlsxwriter
#Create a Pandas Excel writer using XlsxWriter as the engine.

pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel",
             "{1}_{2}.xlsx").format(currentPath,day,time.strftime("%H_%M_%S"))

writer=pd.ExcelWriter(pathTosave, engine='xlsxwriter')

#Convert the dataframe to an XlsxWriter Excel object.
csvToExport.to_excel(writer, sheet_name=day, index=False)

#Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets[day]

#Set format to enterprise
merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                    'bold': True, 'font_color': 'white',
                                    'bg_color': 'black'})
for tmp in idx_enterprise:
    worksheet.merge_range('B'+str(tmp+2)+':G'+str(tmp+2), csvToExport.loc[tmp,
                                                    'NOMBRE'], merge_format)

#Set format to URGENTES
urgent_index=csvToExport.index[csvToExport['URGENTE'] == 'URGENTE'].tolist()

merge_urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                    'bold': True, 'font_color': 'black',
                                    'bg_color': 'orange'})
for tmp in urgent_index:
    worksheet.merge_range('F'+str(tmp+2)+':G'+str(tmp+2), csvToExport.loc[tmp,
                                                    'URGENTE'], merge_urgentFormat)


#Wrap the EXAMEN column
format = workbook.add_format({'text_wrap': True})
# Setting the format but not setting the column width.
worksheet.set_column('E:E', 40, format)

#Add border
border_format=workbook.add_format({'border': 1})
numRows=len(csvToExport)

worksheet.conditional_format('A1:G'+str(numRows+1),{'type':'no_blanks',
                                      'format':border_format})

worksheet.conditional_format('A1:G'+str(numRows+1),{'type':'blanks',
                                      'format':border_format})


#save as xlsx
writer.save()
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
#Excel to collection
df_patientList=pd.DataFrame( {'FOLIO INTERNO':folio,
                          'FECHA':day[0:2]+'/'+day[2:4]+'/'+day[4:6],
                          'NOMBRE':patientList['firstName']+' '+patientList['secondName'],
                          'EXAMEN':exam_list,
                          'COD':examCodecs_list,
                          'PRECIO':exam_priceList,
                          'URGENTE':urgenteText,
                          'RESUL':np.NaN,
                          'EMPRESA':np.NaN}, index=idx_patients )

#Enterprise name
for idx, val in enumerate(idx_enterprise[0:-1]):
    df_patientList.loc[idx_enterprise[idx]+1:idx_enterprise[idx+1]-1,
                    ['EMPRESA']]=listEnterpriseNames[idx]
else:
    df_patientList.loc[idx_enterprise[-1]+1:,['EMPRESA']]=listEnterpriseNames[-1]


pathTosave=os.path.join("{0}","..","listadosGeneradosParaExel",
             "{1}_{2}cobranza.xlsx").format(currentPath,day,time.strftime("%H_%M_%S"))

writer=pd.ExcelWriter(pathTosave, engine='xlsxwriter')

#Convert the dataframe to an XlsxWriter Excel object.
df_patientList.to_excel(writer, sheet_name=day, index=False)

#Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets[day]

#Set format to URGENTES
urgent_index=[i for i, x in enumerate(df_patientList['URGENTE'] == 'URGENTE') if x]

merge_urgentFormat = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                    'bold': True, 'font_color': 'black',
                                    'bg_color': 'red'})
for tmp in urgent_index:
    
    worksheet.merge_range('G'+str(tmp+2)+':H'+str(tmp+2),
                          df_patientList.URGENTE.iloc[tmp], merge_urgentFormat)


#Wrap EXAMEN and PRECIO column
format = workbook.add_format({'text_wrap': True})
# Setting the format but not setting the column width.
worksheet.set_column('D:D', 40, format)
worksheet.set_column('E:E', 5, format)
worksheet.set_column('F:F', 10, format)

#Add border
border_format=workbook.add_format({'border': 1})
numRows=len(df_patientList)

worksheet.conditional_format('A1:I'+str(numRows+1),{'type':'no_blanks',
                                      'format':border_format})

worksheet.conditional_format('A1:I'+str(numRows+1),{'type':'blanks',
                                      'format':border_format})


#save as xlsx
writer.save()
#----------------------------------------------------------------------------#






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