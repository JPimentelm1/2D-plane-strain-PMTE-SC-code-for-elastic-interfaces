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
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    #path_SDV3=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV3'].\
    	#getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values 
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
    	getSubset(region=InterElementSet).values 
    path_SDV6=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV6'].\
    	getSubset(region=InterElementSet).values 
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values 
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
    	getSubset(region=InterElementSet).values
    path_SDV15=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV15'].\
    	getSubset(region=InterElementSet).values
    path_SDV16=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV16'].\
    	getSubset(region=InterElementSet).values
	#-----------------------------------------------------------------------------------------------------------------------
	#creacion de diccionarios y listas
	#-----------------------------------------------------------------------------------------------------------------------
	#hago un diccionario (dicc_NeL_E) para el criterio Energetico donde 
    #la clave sea el NeL y los datos una lista con:
	#0='NeL',1='NeG',2='area',3='Greal',4='Gdamage',5='GUndamage', 6=damage
	#el diccionario vacio lo hago una sola vez y lo cargo el resto de veces    
    elementos=len(area)
    ptosint=len(path_SDV4)
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
    AsigmaT=[]
    for indx in range(ptosint):
        # GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
        # GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
        ip=path_SDV2[indx].integrationPoint
        NeG=path_SDV2[indx].data
        # NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        # tval=path_SDV15[k].data
        tcval=path_SDV16[indx].data
        # valA=tval/tcval
        # se llena la lista AsigmaT con el valor de tc(x) en cada p.int., para
        # luego adjuntarle la columna de tc(x) aleatoria.
        AsigmaT.append([NeG, ip, tcval])
    
    #
    AsigmaNpy=np.array(AsigmaT)
    # numpy random normal distribution:
    p=0.0 # 0.2, 0.3,... constant of multiplication
    sigma=0.25 #standard deviation: 0.25, 0.5, 1,...
        # It may be preferable to change the std.dev. of chirandom to e.g., 0.10e-5
        # and also change the random method
    # chirandom = np.random.normal(0,np.std(Asetcrit[:][2]),len(Asetcrit))
    chirandom = np.random.normal(0,sigma,len(AsigmaT))
    tcx_rand = np.array(AsigmaNpy[:,-1]) * (np.ones(len(AsigmaT)) + float(p)*chirandom)
    
    # Make a new Asigma array and concatenate the tcx 1D vector on the last
    #  column; then convert the array into a list
    Asigma_new = np.concatenate([AsigmaNpy, tcx_rand.reshape(len(tcx_rand), 1)], axis=1)

    odb.close()
    return dicc_NeL_T, dicc_NeL_E, Asigma_new