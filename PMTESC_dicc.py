# ********************************************************************************
# POSTPROCESADO ODB PARA ORDENAR NODOS

# ********************************************************************************

#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir,path,mkdir
from odbAccess import*
from pickle import dump, load
import numpy as np
import random

random.seed()
np.random.seed() #the sequence of random numbers generated will be different 
                # each time you run the code, as it will depend on the exact moment the seed is set.
# random.seed(1234567): to obtain the same random sequence for each program run

def PMTESC_dicc(name_files, working_directory, setnodeInt):
    
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    
    key_step = odb.steps.keys()
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
		getSubset(region=InterElementSet).values       
	#-----------------------------------------------------------------------------------------------------------------------
	#creacion de diccionarios y listas
	#-----------------------------------------------------------------------------------------------------------------------
	#hago un diccionario (dicc_NeL_E) para el criterio Energetico donde 
    #la clave sea el NeL y los datos una lista con:
	#0='NeL',1='NeG',2='area',3='Greal',4='Gdamage',5='GUndamage', 6=damage
	#el diccionario vacio lo hago una sola vez y lo cargo el resto de veces    
    elementos=len(area)
    dicc_NeL_E={}
    dicc_NeL_T={}
    for ele in range(elementos):
        NeL2=str(area[ele].elementLabel)+'_'+str(area[ele].instance.name)
        dicc_NeL_E.update({NeL2:[NeL2,0,area[ele].data,0,0,0,0,0]})	
        dicc_NeL_T.update({NeL2:[NeL2,0,area[ele].data,0,0,0,0,0,0,0,0,0]})
	#hago un diccionario (dicc_NeL_T) para el criterio Energetico donde 
    #la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    odb.close()	
    return dicc_NeL_T, dicc_NeL_E