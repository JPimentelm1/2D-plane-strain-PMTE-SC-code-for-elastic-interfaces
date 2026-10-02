# ********************************************************************************
# CREACION DE LOS DICCIONARIOS Y CALCULO DEL INDICE DE LIBERACION DE ENERGIA
# EN BASE AL CRITERIO ENERGETICO, POR ELEMENTO.
# ********************************************************************************
# Modificaciones: Jose Pimentel
#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir, path, mkdir
from odbAccess import*
from pickle import dump, load
from copy import deepcopy
import sys
import numpy as np
import math
# Redirect stdout to the command prompt
sys.stdout = sys.__stdout__

def PMTESCcritEne(name_files, working_directory, setnodeInt, control, elementosTen, dicc_NeL_E, nstart):

    working_directory_Ene=working_directory+'/FFM_optimizada01/criterioEne'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_E)
    
    #working_directory='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V14_WIN_PC_CASA'
    #working_directory_Ene=working_directory+'\FFM_optimizada01\criterioEne'
    #working_directory_Ten=working_directory+'\FFM_optimizada01\criterioTen'
    #chdir(working_directory)
    #odb = openOdb('DCBISOFFMDESP_k2m1n1j1.odb')
    #Eset='NINTERFACE'
    #control=0
    
    #%%
    #-------------------------------------------------------
    #abrimos los 2 archivos para optimizar el dagno 
    archivoEne=open(working_directory_Ene+'/archivoEneH_paso_i.txt','w')
    archivoEneEle=open(working_directory_Ene+'/archivoEneElements_paso_i.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #||||||||||||| DEFINICION DE CAMINOS DE VARIABLES EN ABAQUS         |||||||||||||||
    #--------------------------------------------------------------------------
    
    key_step = odb.steps.keys()
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    
    #path_despl=odb.steps[key_step[0]].frames[-1].fieldOutputs['U'].\
    #    getSubset(region=InterNodeSet).values
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    	getSubset(region=InterElementSet).values
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    path_SDV7=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV7'].\
    	getSubset(region=InterElementSet).values
    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
    	getSubset(region=InterElementSet).values 
    path_SDV9=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV9'].\
    	getSubset(region=InterElementSet).values     
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
        	getSubset(region=InterElementSet).values  
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    path_HisRegEne = odb.steps[key_step[0]].historyRegions[key_HisReg[0]]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV1)
    
    #damageKm1=[]
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionarios y listas
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='Greal',4='Gdamage',5='GUndamage', 6=damage
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    	
    ###cargo tambien como lista el archivo damageTen.txt que esta en
    ##en la carpeta criterioTen para saber cuales son los elementos en juego
    ##desde el criterio tensional
    ## en la lista elementosTen tenemos para cada elemento susceptible de romper por CT:
    ## NeG, NeL, GcE, z(n1), z(n2), z(n3)
    #elementosTen=PMTESC.get_list_file2(working_directory_Ten+'/damageTen.txt')
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario de todos los elementos de la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    for k in range(intpoint):
    	damage=path_SDV1[k].data
    	#ip=path_SDV2[k].integrationPoint
    	NeG=path_SDV2[k].data
    	#NeL=path_SDV2[k].elementLabel
    	NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
    	dicc_NeL[NeL2][1]=int(NeG)
    	#saco el area de cada elemento dividida entre 4
    	#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
    	#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
    	#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
    	#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
    	#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
    	#si quiero el valor en su CDG lo deberia dividir por el Area total
    	jacobElm=dicc_NeL[NeL2][2]/4 #EVOL/4 = IVOL
    	#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
    	#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
    	#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
    	GiE=path_SDV7[k].data
    	GiiE=path_SDV8[k].data
    	signoN=path_SDV9[k].data
    	#la Greal es para calcular la energia total al principio del paso
    	#justo despues de haber minimizado el campo de desplazamientos con
    	#con el dagno z que viene impuesto con su N
    	#al principio del bucle N (para j=1) z puede estar dentro de [0,1]
    	#pero en el resto de j, z solo puede ser igual a 0 o 1
    	GrealPI=GiE*(1.0-((1.0-damage)/2)*(1.0+signoN))+GiiE*(damage)
    	#para hacer la comparacion elemento a elemento  entre G y GcE
    	#calculo el elemento como si no tuviera dagno, independientemente de que 
    	#lo tenga. Es decir, siempre se calcula con z=1
    	#GundamagePI=GiE*(1-(1-1/2)*(1+signoN))+GiiE*(1):
    	GundamagePI=GiE+GiiE
    	#para hacer la comparacion elemento a elemento  entre G y GcE
    	#calculo el elemento como si SI tuviera dagno, independientemente de que 
    	#lo tenga. Es decir, siempre se calcula con z=0
    	#GundamagePI=GiE*(1-(1-0/2)*(1+signoN))+GiiE*(0):
    	GdamagePI=GiE*(1-(1.0/2)*(1+signoN))
    	#sumo el valor de cada PI de todas las energias multiplicado por
    	#el jacobiano=Area total del elemento/4
    	dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+(GrealPI*jacobElm)
    	dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+(GundamagePI*jacobElm)
    	dicc_NeL[NeL2][5]=dicc_NeL[NeL2][5]+(GdamagePI*jacobElm)
    	dicc_NeL[NeL2][6]=damage;
    thet1=0.0
    #%%
    sumaenerinter=0.00
    for elem in dicc_NeL.keys():
    	sumaenerinter=sumaenerinter+dicc_NeL[elem][3]
    ##itero entre los elemntos que rompen por CT, es decir la lista elementosTen:
    ##NeG, NeL, GcE, z(n1), z(n2), z(n3)
    ##y escribo en archivoEneElements_paso_i.txt
    ##NeG(lista), NeL(lista), GelemReal(dicc), GelemUndamge(dicc), GelemDamge(dicc), GcE(lista), damage(dicc)
    ##esto es para despues el paso ii y no escribo todos los elementos de interfases
        
    eleDamagei=[]
    for elem in elementosTen:
          archivoEneEle.write('%d %s %e %e %e %e %e\n'
      		% (elem[0],elem[1],dicc_NeL[elem[1]][3],dicc_NeL[elem[1]][4],dicc_NeL[elem[1]][5],elem[2],dicc_NeL[elem[1]][6]))	
          eleDamagei.append([elem[0],elem[1],dicc_NeL[elem[1]][3],dicc_NeL[elem[1]][4],dicc_NeL[elem[1]][5],elem[2],dicc_NeL[elem[1]][6],elem[3]])
          # eleDamagei.append(NeLoc, NeG, GrealPI*jacobElm, GundamagePI*jacobElm, GdamagePI*jacobElm, GcElem, damage_var)
          # SON CORRECTOS LOS INDICES EN ESTA LISTA
    archivoEneEle.close()
    
    #%%
    #Energia de todo el sistema en el step=j
    Work = 2*(path_HisRegEne.historyOutputs['ALLWK'].data[-1][1])
    eneDefSolidos = path_HisRegEne.historyOutputs['ALLSE'].data[-1][1]
    #tomamos 'ALLSE' en lugar de 'ALLIE' porque estrictamente es la energia de deformacion
    #pero podemos replantearnos poner la otra por el hourglassing
    if control==1: #load control
    	enerHtotal = -(eneDefSolidos+sumaenerinter)
    else: #fixed-grips loading
    	enerHtotal = eneDefSolidos+sumaenerinter
    
    # with open('borrar.txt', 'w') as f:
    #     f.write(str(eneDefSolidos))
    #     f.write('\n')
    #     f.write(str(sumaenerinter))
    #     f.write('\n')
    #     f.write(str(Work))
    #     f.write('\n')
    #     f.write(str(enerHtotal))
    #     f.write('\n')
    #     f.write(str(path_HisRegEne.historyOutputs['ALLSE'].data[-1][1]))
    #     f.write('\n')
    
    #%%
    
    archivoEne.write('%e\n'% (enerHtotal))
    #archivoEne2.write('%e\n'
    #		% (eneCompr))
    archivoEne.close()
    odb.close()
    print('Total potential energy: {} [N-micrometer] \n Debond angle: {}, deg.'.format(enerHtotal, thet1))
    print('Interface stored strain energy: {} N-micrometer'.format(sumaenerinter))
    return eleDamagei, enerHtotal, thet1

def PMTESCcritEneMF(name_files, working_directory, setnodeInt, control, elementosTen, dicc_NeL_E, nstart):


    working_directory_Ene=working_directory+'/FFM_optimizada01/criterioEne'
    #working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_E)
    
    #working_directory='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V14_WIN_PC_CASA'
    #working_directory_Ene=working_directory+'\FFM_optimizada01\criterioEne'
    #working_directory_Ten=working_directory+'\FFM_optimizada01\criterioTen'
    #chdir(working_directory)
    
    #%%
    #-------------------------------------------------------
    #abrimos los 2 archivos para optimizar el dagno 
    archivoEne=open(working_directory_Ene+'/archivoEneH_paso_i.txt','w')
    archivoEneEle=open(working_directory_Ene+'/archivoEneElements_paso_i.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #||||||||||||| DEFINICION DE CAMINOS DE VARIABLES EN ABAQUS         |||||||||||||||
    #--------------------------------------------------------------------------
    
    key_step = odb.steps.keys()
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    
    #path_despl=odb.steps[key_step[0]].frames[-1].fieldOutputs['U'].\
    #    getSubset(region=InterNodeSet).values
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    	getSubset(region=InterElementSet).values
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    path_SDV7=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV7'].\
    	getSubset(region=InterElementSet).values
    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
    	getSubset(region=InterElementSet).values 
    path_SDV9=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV9'].\
    	getSubset(region=InterElementSet).values     
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
        	getSubset(region=InterElementSet).values  
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    path_HisRegEne = odb.steps[key_step[0]].historyRegions[key_HisReg[0]]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    
    #damageKm1=[]
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionarios y listas
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='Greal',4='Gdamage',5='GUndamage', 6=damage
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    	
    ###cargo tambien como lista el archivo damageTen.txt que esta en
    ##en la carpeta criterioTen para saber cuales son los elementos en juego
    ##desde el criterio tensional
    ## en la lista elementosTen tenemos para cada elemento susceptible de romper por CT:
    ## NeG, NeL, GcE, z(n1), z(n2), z(n3)
    #elementosTen=PMTESC.get_list_file2(working_directory_Ten+'/damageTen.txt')
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario de todos los elementos de la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    for k in range(intpoint):
    	damage=path_SDV1[k].data
    	#ip=path_SDV2[k].integrationPoint
    	NeG=path_SDV2[k].data
    	#NeL=path_SDV2[k].elementLabel
    	NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
    	dicc_NeL[NeL2][1]=int(NeG)
    	#saco el area de cada elemento dividida entre 4
    	#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
    	#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
    	#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
    	#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
    	#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
    	#si quiero el valor en su CDG lo deberia dividir por el Area total
    	jacobElm=dicc_NeL[NeL2][2]/4
    	#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
    	#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
    	#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
    	GiE=path_SDV7[k].data
    	GiiE=path_SDV8[k].data
    	signoN=path_SDV9[k].data
    	#la Greal es para calcular la energia total al principio del paso
    	#justo despues de haber minimizado el campo de desplazamientos con
    	#con el dagno z que viene impuesto con su N
    	#al principio del bucle N (para j=1) z puede estar dentro de [0,1]
    	#pero en el resto de j, z solo puede ser igual a 0 o 1
    	GrealPI=GiE*(1.0-((1.0-damage)/2)*(1.0+signoN))+GiiE*(damage)
    	#para hacer la comparacion elemento a elemento  entre G y GcE
    	#calculo el elemento como si no tuviera dagno, independientemente de que 
    	#lo tenga. Es decir, siempre se calcula con z=1
    	#GundamagePI=GiE*(1-(1-1/2)*(1+signoN))+GiiE*(1):
    	GundamagePI=GiE+GiiE
    	#para hacer la comparacion elemento a elemento  entre G y GcE
    	#calculo el elemento como si SI tuviera dagno, independientemente de que 
    	#lo tenga. Es decir, siempre se calcula con z=0
    	#GundamagePI=GiE*(1-(1-0/2)*(1+signoN))+GiiE*(0):
    	GdamagePI=GiE*(1-(1.0/2)*(1+signoN))
    	#sumo el valor de cada PI de todas las energias multiplicado por
    	#el jacobiano=Area total del elemento/4
    	dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+GrealPI*jacobElm
    	dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+GundamagePI*jacobElm
    	dicc_NeL[NeL2][5]=dicc_NeL[NeL2][5]+GdamagePI*jacobElm
    	dicc_NeL[NeL2][6]=damage;
    #%%
    sumaenerinter=0.00
    for elem in dicc_NeL.keys():
    	sumaenerinter=sumaenerinter+dicc_NeL[elem][3]
    ##itero entre los elemntos que rompen por CT, es decir la lista elementosTen:
    ##NeG, NeL, GcE, z(n1), z(n2), z(n3)
    ##y escribo en archivoEneElements_paso_i.txt
    ##NeG(lista), NeL(lista), GelemReal(dicc), GelemUndamge(dicc), GelemDamge(dicc), GcE(lista), damage(dicc)
    ##esto es para despues el paso ii y no escribo todos los elementos de interfases
    
    eleDamagei=[]
    # convertir la lista de elementos al tipo tuple, que es immutable
    # elementosTen=tuple(elementosTen)
    # dicc_NeL=tuple(dicc_NeL)
    indx0=0
    for elem in elementosTen:
        archivoEneEle.write('%d %s %e %e %e %e %e\n'
    		% (elem[0],elem[1],dicc_NeL[elem[1]][3],dicc_NeL[elem[1]][4],dicc_NeL[elem[1]][5],elem[2],dicc_NeL[elem[1]][6]))	
        eleDamagei.append([elem[0],elem[1],dicc_NeL[elem[1]][3],dicc_NeL[elem[1]][4],dicc_NeL[elem[1]][5],elem[2],dicc_NeL[elem[1]][6]])
        indx0=indx0+1
       	# archivoEneEle.write('%d %s %e %e %e %e %e\n'
       	# 	% (elem[0],elem[1],dicc_NeL[elem][3],dicc_NeL[elem][4],dicc_NeL[elem][5],elem[2],dicc_NeL[elem][6]))	
        # eleDamagei.append([dicc_NeL[elem][3],dicc_NeL[elem][4],dicc_NeL[elem][5],elem[2],dicc_NeL[elem][6]])
    archivoEneEle.close() # 
    
    #%%
    #Energia de todo el sistema en el step=j
    Work = 2*(path_HisRegEne.historyOutputs['ALLWK'].data[-1][1])
    eneDefSolidos = path_HisRegEne.historyOutputs['ALLSE'].data[-1][1]
    #tomamos 'ALLSE' en lugar de 'ALLIE' porque estrictamente es la energia de deformacion
    #pero podemos replantearnos poner la otra por el hourglassing
    
    if control==1: #load control
    	enerHtotal = eneDefSolidos+sumaenerinter-Work
    else: #fixed-grips loading
    	enerHtotal = eneDefSolidos+sumaenerinter
    
    # with open('borrar.txt', 'w') as f:
    #     f.write(str(eneDefSolidos))
    #     f.write('\n')
    #     f.write(str(sumaenerinter))
    #     f.write('\n')
    #     f.write(str(Work))
    #     f.write('\n')
    #     f.write(str(enerHtotal))
    #     f.write('\n')
    #     f.write(str(path_HisRegEne.historyOutputs['ALLSE'].data[-1][1]))
    #     f.write('\n')
    
    #%%
    
    archivoEne.write('%e\n'% (enerHtotal))
    #archivoEne2.write('%e\n'
    #		% (eneCompr))
    archivoEne.close()
    odb.close()
    return eleDamagei, enerHtotal