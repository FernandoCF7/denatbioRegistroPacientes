# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:17:14 2021

@author: Fernando Castillo Flores --> fernandocastilloflores@gmail.com
"""

# -*- coding: utf-8 -*-
#denatLab

"""
Spyder Editor

This is a temporary script file.
"""

from os import path as os_path
from sys import exit as sys_exit, path as sys_path
from numpy import NaN as np_NaN
from pandas import Index as pd_Index, concat as pd_concat, DataFrame as pd_DataFrame


sys_path.append("./modulos")
import projectmodule
import imp
imp.reload(projectmodule)

#-----------------------------------------------------------------------------#
#local variables
currentPath = os_path.dirname(os_path.abspath(__file__))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#get parameters from make_excel_file.py
def set_daily_parameters(day, exel_enterprises, subsidiary, inlineEF):
    
    global idx_patients, idx_enterprise, idx_patients_antigenCovit, idx_patients_antibodyCovit, codeIntCob, yymmddPath, codeIntLab, csvFile, ECBP, ECBP_str, idx_urgentes, idx_vuelo, examNameList, examNameList_nested, day_
    global ECBNC, ECBAC, ECBABC, ECBCABC, ECBSP, enterpriseNames_asDict, idx_patients_noCovits, idx_enterprise_patients_noCovits, listEnterpriseNameByPatient, idx_patients_enterprise_forExclusiveExcel_asDict, idx_enterprise_enterprise_forExclusiveExcel_asDict
    global enterpriseNames_forExclusiveExcel, enterpriseCodecs_forExclusiveExcel

    day_ = day

    #set parameters to projectmodule
    projectmodule.set_projectmodule_parameters(currentPath, inlineEF)

    #day, month and year
    dayy = day[0:2]
    month = day[2:4]
    year = day[4:6]
    
    #date as save file format
    yymmddPath = os_path.join('____'+year,'__'+month+year,day)

    #read csv patients file
    csvFile = projectmodule.get_csvFile(currentPath, yymmddPath)

    #search for enterprise; extract index of the enterprises
    idx_enterprise = projectmodule.get_idx_enterprise(csvFile["firstName"])

    #search for patients; extract index of the patients
    idx_patients = csvFile.index[~csvFile.index.isin(idx_enterprise)]

    #get the OSR code --> orden de servicio de referencia
    OSR = dict(csvFile["secondName"][idx_enterprise].str.strip())

    #-----------------------------------------------------------------------------#
    #check fill values in all patients entries
    projectmodule.checkFilledfiels(0, csvFile, idx_patients, day)
    projectmodule.checkFilledfiels(1, csvFile, idx_patients, day)
    projectmodule.checkFilledfiels(2, csvFile, idx_patients, day)
    #-----------------------------------------------------------------------------#

    #get enterprise names and codecs
    enterpriseNames, enterpriseCodecs = projectmodule.get_enterpriseNames(OSR, csvFile, idx_enterprise, day)

    #get the enterprise names and codecs forExclusiveExcel
    enterpriseNames_forExclusiveExcel, enterpriseCodecs_forExclusiveExcel = projectmodule.get_enterpriseNames_exclusiveExcel(exel_enterprises, day)

    #set idx_enterprise and enterpriseNames as dict
    enterpriseNames_asDict = dict(zip(idx_enterprise, enterpriseNames))

    #set the enterprise name by patient
    listEnterpriseNameByPatient = projectmodule.get_listEnterpriseNameByPatient(idx_enterprise, enterpriseNames, idx_patients, len(csvFile))

    #set the enterprise code by patient
    listEnterpriseCodeByPatient = projectmodule.get_listEnterpriseCodeByPatient(idx_enterprise, enterpriseCodecs, idx_patients, len(csvFile))

    #get shift (turno)
    shift = projectmodule.get_shift(idx_enterprise, csvFile, OSR, day)

    #set the enterprise code by patient
    listShiftByPatient = projectmodule.get_listShiftByPatient(idx_enterprise, idx_patients, shift, len(csvFile))

    #search for urgents examns
    idx_urgentes = projectmodule.get_idx_urgentes(idx_patients, csvFile)

    #update csvFile.firstName cuting the "urgente" part
    projectmodule.update_csvFile_firstName_urgent(idx_urgentes, csvFile)

    #search for vuelo examns
    idx_vuelo = projectmodule.get_idx_vuelo(idx_patients, csvFile)

    #update csvFile.firstName cuting the "vuelo" part
    projectmodule.update_csvFile_firstName_vuelo(idx_vuelo, csvFile)

    #get the exam code by patient as dictionary
    ECBP = projectmodule.get_ECBP(idx_patients, csvFile)

    #set ECBP as list of str´s
    ECBP_str = projectmodule.get_ECBP_str(ECBP)

    #examn product code by patient
    EPCBP = projectmodule.get_EPCBP(ECBP)

    #-----------------------------------------------------------------------------#
    #set color as each study
    #ECBNC --> Exam color by no PCR covits
    #ECBAC --> Exam color by antigen covit
    #ECBABC --> Exam color by anti body covit
    #ECBCABC --> Exam color by cuantitative anti body covit
    #ECBSP --> Exam color by sars plus
    ECBNC, ECBAC, ECBABC, ECBCABC, ECBSP = projectmodule.get_color_as_study(ECBP)
    #-----------------------------------------------------------------------------#

    #set the exams name
    examNameList = projectmodule.get_examNameList(idx_patients, csvFile, ECBP, "as_str", day)

    #set the exams name nested list
    examNameList_nested = projectmodule.get_examNameList(idx_patients, csvFile, ECBP, "as_list", day)

    #make inter code
    codeIntLab, codeIntCob = projectmodule.get_codeInt_Lab_Cob(idx_patients, idx_urgentes, day, subsidiary, ECBP, listEnterpriseCodeByPatient, listShiftByPatient, EPCBP)
    
    #asociate, as dict, each patient with its corresponding enterprise
    dict_pattient_enterprise = projectmodule.get_dict_pattient_enterprise(idx_patients, idx_enterprise)
    
    #get the index's of no covit patients
    idx_patients_noCovits, idx_enterprise_patients_noCovits = projectmodule.get_idx_noCovits(idx_patients, ECBP, dict_pattient_enterprise)
    
    #index's for antigen patients
    idx_patients_antigenCovit, idx_enterprise_patients_antigenCovit = projectmodule.get_idx_antigenCovit(idx_patients, ECBP, dict_pattient_enterprise)
    
    #index's for antibody patients
    idx_patients_antibodyCovit, idx_enterprise_patients_antibodyCovit = projectmodule.get_idx_antibodyCovit(idx_patients, ECBP, dict_pattient_enterprise)
    
    #get the index's of list_enterprise_forExclusiveExcel patients
    idx_patients_enterprise_forExclusiveExcel_asDict, idx_enterprise_enterprise_forExclusiveExcel_asDict = projectmodule.get_idx_enterpriseExclusive(enterpriseCodecs_forExclusiveExcel, idx_patients, listEnterpriseCodeByPatient, dict_pattient_enterprise)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
def join_month_parameters(dummy_counter):

    if dummy_counter == 0:

        #_m --> mounth
        global idx_patients_m, idx_enterprise_m, idx_enterprise_patients_noCovits_m
        global codeIntLab_m, csvFile_m, ECBP_str_m, idx_urgentes_m, idx_vuelo_m
        global examNameList_m, examNameList_nested_m, ECBP_m, enterpriseNames_asDict_m
        global ECBNC_m, ECBAC_m, ECBABC_m, ECBCABC_m, ECBSP_m
        global codeIntCob_m, listEnterpriseNameByPatient_m
        global day_list_m, day_list_antigenCovit_m, day_list_antibodyCovit_m
        global idx_patients_antigenCovit_m, idx_patients_antibodyCovit_m, idx_patients_noCovits_m
        global idx_patients_enterprise_forExclusiveExcel_asDict_m, idx_enterprise_enterprise_forExclusiveExcel_asDict_m, day_list_enterprises_excel_m

        idx_patients_m = pd_Index(data=[])
        idx_patients_antigenCovit_m = pd_Index(data=[])
        idx_patients_antibodyCovit_m = pd_Index(data=[])
        idx_patients_noCovits_m = pd_Index(data=[])
        idx_enterprise_m = []
        idx_enterprise_patients_noCovits_m = []
        codeIntLab_m = {}
        csvFile_m = pd_DataFrame()
        ECBP_str_m = {}
        idx_urgentes_m = []
        idx_vuelo_m = []
        examNameList_m = {}
        examNameList_nested_m = {}
        ECBP_m = {}
        ECBNC_m = {}
        ECBAC_m = {}
        ECBABC_m = {}
        ECBCABC_m = {}
        ECBSP_m = {}
        enterpriseNames_asDict_m = {}
        codeIntCob_m = {}
        listEnterpriseNameByPatient_m = {}
        day_list_m = {}
        day_list_antigenCovit_m = {}
        day_list_antibodyCovit_m = {}
        idx_patients_enterprise_forExclusiveExcel_asDict_m, idx_enterprise_enterprise_forExclusiveExcel_asDict_m = projectmodule.get_idx_enterpriseExclusive(enterpriseCodecs_forExclusiveExcel, pd_Index(data=[]), {}, {})
        day_list_enterprises_excel_m = {x:{} for x in enterpriseCodecs_forExclusiveExcel}
    
    for key, value in idx_enterprise_enterprise_forExclusiveExcel_asDict.items():
        idx_enterprise_enterprise_forExclusiveExcel_asDict_m[key] += [tmp+dummy_counter for tmp in value]
    
    for key, value in idx_patients_enterprise_forExclusiveExcel_asDict.items():
        idx_patients_enterprise_forExclusiveExcel_asDict_m[key] = (idx_patients_enterprise_forExclusiveExcel_asDict_m[key]).union(value + dummy_counter) 
    
    idx_patients_m = idx_patients_m.union(idx_patients+dummy_counter)
    idx_patients_antigenCovit_m = idx_patients_antigenCovit_m.union(idx_patients_antigenCovit+dummy_counter)
    idx_patients_antibodyCovit_m = idx_patients_antibodyCovit_m.union(idx_patients_antibodyCovit+dummy_counter)
    idx_patients_noCovits_m = idx_patients_noCovits_m.union(idx_patients_noCovits+dummy_counter)
    idx_enterprise_m.extend([tmp+dummy_counter for tmp in idx_enterprise])
    idx_enterprise_patients_noCovits_m.extend([tmp+dummy_counter for tmp in idx_enterprise_patients_noCovits])
    idx_urgentes_m.extend([tmp+dummy_counter for tmp in idx_urgentes])
    idx_vuelo_m.extend([tmp+dummy_counter for tmp in idx_vuelo])

    tmp = {x:day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6] for x in idx_patients}
    for key, value in tmp.items():
        day_list_m[key+dummy_counter] = value

    tmp = {x:day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6] for x in idx_patients_antigenCovit}
    for key, value in tmp.items():
        day_list_antigenCovit_m[key+dummy_counter] = value
    
    tmp = {x:day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6] for x in idx_patients_antibodyCovit}
    for key, value in tmp.items():
        day_list_antibodyCovit_m[key+dummy_counter] = value

    for key, value in idx_patients_enterprise_forExclusiveExcel_asDict.items():

        tmp = {x:day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6] for x in value}
        for key1, value1 in tmp.items():
            day_list_enterprises_excel_m[key][key1+dummy_counter] = value1

    for key, value in codeIntLab.items():
        codeIntLab_m[key+dummy_counter] = value

    for key, value in ECBP_str.items():
        ECBP_str_m[key+dummy_counter] = value
    
    for key, value in examNameList.items():
        examNameList_m[key+dummy_counter] = value

    for key, value in examNameList_nested.items():
        examNameList_nested_m[key+dummy_counter] = value

    for key, value in ECBP.items():
        ECBP_m[key+dummy_counter] = value

    for key, value in ECBNC.items():
        ECBNC_m[key+dummy_counter] = value
    
    for key, value in ECBAC.items():
        ECBAC_m[key+dummy_counter] = value
    
    for key, value in ECBABC.items():
        ECBABC_m[key+dummy_counter] = value
    
    for key, value in ECBCABC.items():
        ECBCABC_m[key+dummy_counter] = value
    
    for key, value in ECBSP.items():
        ECBSP_m[key+dummy_counter] = value
    
    for key, value in enterpriseNames_asDict.items():
        enterpriseNames_asDict_m[key+dummy_counter] = value

    for key, value in codeIntCob.items():
        codeIntCob_m[key+dummy_counter] = value

    for key, value in listEnterpriseNameByPatient.items():
        listEnterpriseNameByPatient_m[key+dummy_counter] = value
    
    csvFile_m = pd_concat([ csvFile_m, csvFile.set_index(csvFile.index+dummy_counter) ])
#-----------------------------------------------------------------------------#

def antigen_excel():
    projectmodule.make_excel_antigen_antibody(idx_patients_antigenCovit, {'RESULTADO':np_NaN}, "Antígeno SARS CoV-2", "_antigenSARS_COV2", day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6], day_, codeIntCob, yymmddPath, currentPath)

def antybody_excel():
    projectmodule.make_excel_antigen_antibody(idx_patients_antibodyCovit, {'IgG':np_NaN, 'IgM':np_NaN}, "IgG IgM SARS CoV-2", "_antibodySARS_COV2", day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6], day_, codeIntCob, yymmddPath, currentPath)

def laboratory_excel():
    projectmodule.make_laboratory_excel(idx_patients, idx_enterprise, codeIntLab, csvFile, ECBP_str, currentPath, yymmddPath, day_, idx_urgentes, idx_vuelo, examNameList, ECBNC, ECBAC, ECBABC, ECBCABC, ECBSP, enterpriseNames_asDict, "")

def laboratoryNoCovid_excel():
    projectmodule.make_no_covid_excel(idx_patients_noCovits, idx_enterprise_patients_noCovits, codeIntLab, csvFile, currentPath, os_path.join(yymmddPath,"byExamCategory"), day_, idx_urgentes, idx_vuelo, examNameList_nested, ECBP, enterpriseNames_asDict, "")

def cobranza_excel():
    projectmodule.make_excel_cobranza(idx_patients, codeIntCob, day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6], csvFile, examNameList, ECBP_str, listEnterpriseNameByPatient, day_, currentPath,  yymmddPath, idx_urgentes)

def enterprises_excel():

    for codeEnterprise_ in idx_patients_enterprise_forExclusiveExcel_asDict:
        
        projectmodule.make_excel_enterprise_forExclusiveExcel(
            idx_patients_enterprise_forExclusiveExcel_asDict[codeEnterprise_], "_{}".format(codeEnterprise_),
            day_[0:2]+'/'+day_[2:4]+'/'+day_[4:6], day_, codeIntLab, csvFile, examNameList, currentPath, yymmddPath, idx_urgentes
            )
    
def laboratory_excel_m():
    projectmodule.make_laboratory_excel(idx_patients_m, idx_enterprise_m, codeIntLab_m, csvFile_m, ECBP_str_m, currentPath, os_path.join(yymmddPath[:-6],"byMonth"), yymmddPath[7:-7], idx_urgentes_m, idx_vuelo_m, examNameList_m, ECBNC_m, ECBAC_m, ECBABC_m, ECBCABC_m, ECBSP_m, enterpriseNames_asDict_m, "")

def cobranza_excel_m():
    projectmodule.make_excel_cobranza(idx_patients_m, codeIntCob_m, day_list_m, csvFile_m, examNameList_m, ECBP_str_m, listEnterpriseNameByPatient_m, yymmddPath[7:-7], currentPath, os_path.join(yymmddPath[:-6],"byMonth"), idx_urgentes_m)
        
def antigen_excel_m():
    projectmodule.make_excel_antigen_antibody(idx_patients_antigenCovit_m, {'RESULTADO':np_NaN}, "Antígeno SARS CoV-2", "_antigenSARS_COV2", day_list_antigenCovit_m, yymmddPath[7:-7], codeIntCob_m, os_path.join(yymmddPath[:-6],"byMonth"), currentPath)

def antybody_excel_m():
    projectmodule.make_excel_antigen_antibody(idx_patients_antibodyCovit_m, {'IgG':np_NaN, 'IgM':np_NaN}, "IgG IgM SARS CoV-2", "_antibodySARS_COV2", day_list_antibodyCovit_m, yymmddPath[7:-7], codeIntCob_m, os_path.join(yymmddPath[:-6],"byMonth"), currentPath)

def laboratoryNoCovid_excel_m():
    projectmodule.make_no_covid_excel(idx_patients_noCovits_m, idx_enterprise_patients_noCovits_m, codeIntLab_m, csvFile_m, currentPath, os_path.join(yymmddPath[:-6],"byMonth","byExamCategory"), yymmddPath[7:-7], idx_urgentes_m, idx_vuelo_m, examNameList_nested_m, ECBP_m, enterpriseNames_asDict_m, "_NoCovid")

def enterprises_excel_m():

    for codeEnterprise_ in idx_patients_enterprise_forExclusiveExcel_asDict_m:
        
        projectmodule.make_excel_enterprise_forExclusiveExcel(
            idx_patients_enterprise_forExclusiveExcel_asDict_m[codeEnterprise_], "_{}".format(codeEnterprise_),
            day_list_enterprises_excel_m[codeEnterprise_], yymmddPath[7:-7], codeIntLab_m, csvFile_m, examNameList_m, currentPath, os_path.join(yymmddPath[:-6],"byMonth"),
            idx_urgentes_m)

    



