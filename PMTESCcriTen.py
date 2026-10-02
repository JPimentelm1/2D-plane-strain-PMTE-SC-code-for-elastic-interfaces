"""
# Modificaciones: Jose M. Pimentel
"""
# ********************************************************************************

# ********************************************************************************
#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir,path,mkdir
from shutil import move, rmtree
from odbAccess import*
from  math import sqrt #para raiz cuadrada
from pickle import dump, load
from copy import deepcopy
import sys
import numpy as np
import random
import math

# Redirect stdoutput to the command prompt
sys.stdout = sys.__stdout__
# np.random.seed() #the sequence of generated random numbers will be different 
                # each time you run the code, as it will depend on the exact moment the seed is set,
                # i.e. it is dependent on the machine time.
# to obtain the same random sequence for each program run:
np.random.seed(1357111317)
# np.random.seed(int(math.pi * 1E6))

def PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T):
    """
    

    Parameters
    ----------
    name_files : TYPE
        DESCRIPTION.
    working_directory : TYPE
        DESCRIPTION.
    setnodeInt : TYPE
        DESCRIPTION.
    dicc_NeL_T : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    def sigmac_parameter(inp_lines):
        for line in inp_lines:
            if line.startswith('*User Material'):
                # Assuming the first parameter is on the next line
                next_line = inp_lines[inp_lines.index(line) + 1]
                # Split the line by commas (assuming comma-separated values)
                parameters = next_line.split(', ')
                if len(parameters) > 0:
                    try:
                        first_param = float(parameters[0])
                        brittleness_num=float(parameters[-1])
                        GIc=float(parameters[1])
                        h=float(parameters[-2])
                        xi=float(parameters[3])
                        lambdhs=float(parameters[2])
                        
                        return first_param, GIc, brittleness_num, h, xi, lambdhs
                    except ValueError:
                        print("Error: First parameter is not numeric.")
                        return None
        print("Error: User material section not found.")
        return None
    fileINPUT = open('inputFFMLEBIM_adaptivef.txt','r')
    flag = fileINPUT.readline()
    name_INP = fileINPUT.readline().rstrip()
    fileINPUT.close()

    inp_file_path = working_directory+'/'+name_INP+'.inp'
    with open(inp_file_path, 'r') as inp_file:
        inp_lines = inp_file.readlines()
    first_param, GIc, mu_const, interfh, xi, lambdhs = sigmac_parameter(inp_lines)
    
    
    #%%
    #-------------------------------------------------------
    #abrimos los 3 archivos del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w')
    #Fichero del dano actual k para N1 todo sano 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w') 
    #Fichero del dano actual k para N2 todo dagnado 
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w')
    #Fichero del dano actual k para N3 todo dagnado con ecuacion 
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w')
    #FIchero del dano actual k para N4 todos los elementos activos
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4] #
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
    path_SDV13=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV13'].\
    	getSubset(region=InterElementSet).values
    path_SDV14=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV14'].\
    	getSubset(region=InterElementSet).values
    path_SDV19=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV19'].\
    	getSubset(region=InterElementSet).values	
       
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00
    	return z
    def n2(dist,longitud):
    	z=0.00
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./sqrt(longitud))*sqrt(dist) 
    	except ZeroDivisionError:
    		1.
    	return z #DAMAGE VARIABLE
    def n4(dist,longitud):
        z=1.00
        return z
    listafunN=[n1,n2,n3,n4]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]; Gclst=[];
    for k in range(intpoint): 
        damage=path_SDV1[k].data
        GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
        GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
        ip=path_SDV2[k].integrationPoint
        NeG=path_SDV2[k].data
        psi_g=math.atan2(path_SDV14[k].data*(math.sqrt(1/xi)), path_SDV13[k].data)
        GcE=float(GIc)*(1+(math.tan(psi_g*(1-lambdhs)))**2)*(mu_const/interfh); psi_gc=(math.pi)/(2*(1-lambdhs));
        x=path_SDV10[k].data; y=path_SDV11[k].data
        if abs(psi_g)>=psi_gc: GcE=GIc*1E8
        if x>0:
            Gclst.append([math.atan(y/x), GcE])
        else:
            Gclst.append([float(180) - math.atan(y/abs(x)), GcE])
        
            
        if damage!=0.00 and GtotT>=GcT: #damage=0 yes damage by CT.
            NeL=path_SDV2[k].elementLabel
            NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
            # GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
        
        		#saco el area de cada elemento dividida entre 4
        		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
        		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
        		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
        		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
        		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
        		#si quiero el valor en su CDG lo deberia dividir por el Area total 
            jacobElm=dicc_NeL[NeL2][2]/4   
        		#fcip=sqrt(GtotT/GcT)  
        		#fcelm=fcip*jacobElm     
        		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
        		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
        		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
            dicc_NeL[NeL2][1]=int(NeG)
            dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
            dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0
        		#sumo el valor de cada PI de todas las energias multiplicado por
        		#el jacobiano=Area total del elemento/4
            dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
            dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
            dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm
        		#sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento	
            dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip; dicc_NeL[NeL2][11]=int(NeL)
        if damage==0.00: #damage=0 yes damage
        		#guardo en una lista los PI rotos para despues escribrir en archivos 
        		#si finalmente hay algun elemento dagnado
              NeL=path_SDV2[k].elementLabel; dagnokm1.append([ip,NeG,damage,int(NeL)])
        #        for n in range(len(listarchivos)):
        			#listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
        #-----------------------------------------------------------------------------------------------------------------------
    Gclst.sort(key=lambda Gclst:Gclst[0], reverse=False)
    			
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    # esto no hace falta si no obligamos a que rompan todos los PI por CT
    # listaElem.sort(key=lambda listaElem:listaElem[10],reverse=True)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    # for elem in range(elementos):
    	# if listaElem[elem][10]<10:
    		# break
    	# else:
    		# #fc=sqrt(GtotT/GcT)
    		# listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7]) 
    		# dameleCT.append(listaElem[elem])
    		
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    for elem in listaElem:
       	if elem[6]>elem[7] and elem[10]==10:
            elem[9]=sqrt(elem[6]/elem[7])
            dameleCT.append(elem)
            #dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario dicc_NeL de ese elemento
    # for elem in range(elementos):
    #    	if listaElem[elem][6]>listaElem[elem][7] and listaElem[elem][10]==10:
    #         listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7])
    #         dameleCT.append(listaElem[elem])
    		
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    for elem in range(len(dameleCT)):
    	# xa=dameleCT[0][3]
    	# xb=dameleCT[elem][3]
    	# ya=dameleCT[0][4]
    	# yb=dameleCT[elem][4]
    	# dist=sqrt(((xa-xb)**2)+((ya-yb)**2))
     dist=dameleCT[elem][6]
    # dameleCT[elem][5]=dist
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    if len(dameleCT)>1:
    	longitud=dameleCT[-1][7]
    else:
    	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    #escribo en todos los archivo Ns y en Km1 el dagno de km1
    if len(dameleCT)!=0:
    	for n in range(len(listarchivos)):
            for elem in dagnokm1:
                listarchivos[n].write('%d %d %d %d\n' 
                              % (elem[0],elem[1],elem[2],elem[-1]))
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,elem[1],1.0))
    		# for elem in dagnokm1:
    		# 	listarchivos[n].write('%d %d %e \n' 
    		# 				% (elem[0],elem[1],elem[2]))
    #escribo los nuevos danos del criterio tensional
    # cntinterf=0 
    # cntinterf1=0
    # cntinterf2=0
    # dam2CT=[]; 
    # dfraction=1.0 # factor used for the symmetrical interface debond
    for n in range(len(listarchivos)): 
    	for elem in range(len(dameleCT)):
            # N = 1
            
            if n==1 and abs(dameleCT[elem][3])>0:
                if dameleCT[elem][0].endswith('_INTERFACE1-1'):
                    damage=0; #listafunN[1](dameleCT[elem][5],longitud);
                    # cntinterf1+=1;\
                
                # for i in range(elem + 1, len(dameleCT)):
                # Check if the element ends with the target string
                elif dameleCT[elem][0].endswith('_INTERFACE2-1'):
                    # If it does, append it to the filtered list
                    damage=1.0
                    # dameleCT[elem].append(dam2);
                    # NeGi=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n+1].write('%d %d %e \n' % (ip,NeGi,dam2))
                
            # N = 2        
            if n==2 and abs(dameleCT[elem][3])>0:
                if dameleCT[elem][0].endswith('_INTERFACE2-1'):
                    #rompe el resorte del PI
                    damage=0; #listafunN[n](dameleCT[elem][5],longitud);
                    # cntinterf2+=1;
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n+1].write('%d %d %e \n' % (ip,NeG,damage))
                # Check if the element ends with the target string        
                elif dameleCT[elem][0].endswith('_INTERFACE1-1'):    
                        # If it does, append it to the filtered list
                        damage=1.0;
                        # dameleCT[elem].append(dam2);
                        # NeGi=dameleCT[elem][1]
                        # for ip in range(1,5):
                        #     listarchivos[n+1].write('%d %d %e \n' % (ip,NeGi,dam2))
            
            # #*** N = 3 ***            
            if n==3: 
                # and elem <= round(len(dameleCT)*dfraction)
                damage=0; #listafunN[1](dameleCT[elem][5],longitud)
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1]
                # # print('\n');\
                # # print((dameleCT[elem][0],damage));\
                # # print('\n');
                # for ip in range(1,5):
                #     listarchivos[n+1].write('%d %d %e \n' % (ip,NeG,damage))
                
            # N = 4 
            if n > 3: # and abs(dameleCT[elem][3])>0:
                damage=1.0 #listafunN[3](dameleCT[elem][5],longitud)
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1]
                # for ip in range(1,5):
                #     listarchivos[n+1].write('%d %d %e \n' % (ip,NeG,damage))
                
            dameleCT[elem].append(damage);
            NeG=dameleCT[elem][1];
            for ip in range(1,5):
                listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,dameleCT[elem][11]))
                 
                
    #cierro archivos  
    for n in range(len(listarchivos)):
    	listarchivos[n].close()
    
    # def log(message):
    #     print (message)
    # log((cntinterf,cntinterf2,len(dameleCT)))
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------    
    
    damageTen=[] #!!
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))			
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8],dameleCT[elem][11]])
    		
    		for n in range(len(listafunN)):
     			archDamTen.write(' %e' % (dameleCT[elem][12+n]))
     			damageTen[elem].append(dameleCT[elem][12+n])
    		archDamTen.write('\n')
    archDamTen.close()
    #-----------------------------------------------------------------------------------------------------------------------
    Nsnumber = len(listarchivos)-1
    odb.close()
    return damageTen, Nsnumber, Gclst

def PMTESCcriTenRand(name_files, working_directory, setnodeInt, dicc_NeL_T, prand):
    """
    

    Parameters
    ----------
    name_files : TYPE
        DESCRIPTION.
    working_directory : TYPE
        DESCRIPTION.
    setnodeInt : TYPE
        DESCRIPTION.
    dicc_NeL_T : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    #working_directory='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\odbS'
    #working_directory_Ten='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\criterioTen'
    #chdir(working_directory)
    #odb = openOdb('D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\odbS\DLJCARGA_k3m1n0j0.odb')
    #Eset='EINTERFACE'
    
    #%%
    #-------------------------------------------------------
    #abrimos los archivos N del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w+')
    #Fichero del dano actual k para N1 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w+') 
    #Fichero del dano actual k para N2  
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w+')
    #Fichero del dano actual k para N3  
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w+')
    #FIchero del dano actual k para N4 
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w+')
    #FIchero del dano actual k para N5 
    archivoN5=open(working_directory_Ten+'/damageN5.txt','w+')
    #Fichero del dano actual k para N6 
    archivoN6=open(working_directory_Ten+'/damageN6.txt','w+')
    #Fichero del dano actual k para N7 
    archivoN7=open(working_directory_Ten+'/damageN7.txt','w+')
    #Fichero del dano actual k para N8 
    archivoN8=open(working_directory_Ten+'/damageN8.txt','w+')
    #Fichero del dano actual k para N9
    archivoN9=open(working_directory_Ten+'/damageN9.txt','w+')
    archivoN10=open(working_directory_Ten+'/damageN10.txt','w+')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4,archivoN5,archivoN6,archivoN7,archivoN8,archivoN9,archivoN10]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
    
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00
    	return z
    def n2(dist,longitud):
    	z=0.00
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./sqrt(longitud))*sqrt(dist) 
    	except ZeroDivisionError:
    		1.
    	return z #DAMAGE VARIABLE
    def n4(dist,longitud):
        z=1.00
        return z
    def n5(dist,longitud):
        z=0.00
        return z
    def n6(dist,longitud):
        z=0.00
        return z
    def n7(dist,longitud):
        z=0.00
        return z
    def n8(dist,longitud):
        z=0.00
        return z
    def n9(dist,longitud):
        z=0.00
        return z
    def n10(dist,longitud):
        z=0.00
        return z
    listafunN=[n1,n2,n3,n4,n5,n6,n7,n8,n9,n10]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    Aset=[]
    for k in range(intpoint): 
    	damage=path_SDV1[k].data; 
    	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
    	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
    	ip=path_SDV2[k].integrationPoint; tval=path_SDV15[k].data; tcval=path_SDV16[k].data; valA=tval/tcval
    	NeG=path_SDV2[k].data; NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        # path_SDV2[k].data = global element number
        # path_SDV2[k].elementLabel = local element number associated to the part instance
    	if damage!=0.00 and GtotT>=GcT: #damage=0 yes damage by CT.
    		NeL=path_SDV2[k].elementLabel; Aset.append([NeG, NeL, tval, tcval, ip, valA])
    		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
    		GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
    		x=path_SDV10[k].data
    		y=path_SDV11[k].data
                
    		#saco el area de cada elemento dividida entre 4
    		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
    		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
    		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
    		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
    		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
    		#si quiero el valor en su CDG lo deberia dividir por el Area total
    		jacobElm=dicc_NeL[NeL2][2]/4   
    		#fcip=sqrt(GtotT/GcT)  
    		#fcelm=fcip*jacobElm     
    		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
    		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
    		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
    		dicc_NeL[NeL2][1]=int(NeG)
    		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
    		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0
    		#sumo el valor de cada PI de todas las energias multiplicado por
    		#el jacobiano=Area total del elemento/4
    		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
    		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
    		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm
    		#sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento	
    		dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip; dicc_NeL[NeL2][11]=int(NeL)
    	if damage==0.00: #damage=0 yes damage
    		#guardo en una lis los PI rotos para despues escribrir en archivos 
    		#si finalmente hay algun elemento dagnado
    		NeL=path_SDV2[k].elementLabel; dagnokm1.append([ip,NeG,damage,int(NeL)])
    #        for n in range(len(listarchivos)):
    			#listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
    			
    #-----------------------------------------------------------------------------------------------------------------------
    #para guardar desde abaqus y porder abrir en pyhton y hacer pruebas
    #correr en abaqus
    #filedicc=open(working_directory_Ten+'/dicc_NeL.pkl','wb')    
    #dump(dicc_NeL,filedicc)
    #filedicc.close()
    #correr en python         
    #filedicc=open(working_directory_Ten+'/dicc_NeL.pkl','rb')
    #dicc_NeL=load(filedicc)
    #filedicc.close()
    			
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    # esto no hace falta si no obligamos a que rompan todos los PI por CT
    # listaElem.sort(key=lambda listaElem:listaElem[10],reverse=True)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    # for elem in range(elementos):
    	# if listaElem[elem][10]<10:
    		# break
    	# else:
    		# #fc=sqrt(GtotT/GcT)
    		# listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7]) 
    		# dameleCT.append(listaElem[elem])
    		
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    for elem in listaElem:
       	if elem[6]>elem[7] and elem[10]==10:
            elem[9]=sqrt(elem[6]/elem[7])
            #dameleCT es una lista de cada elemento dagnado con toda la informacion 
        	   #que tiene el diccionario dicc_NeL de ese elemento
            dameleCT.append(elem)
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    # for elem in range(len(dameleCT)):
    # 	# xa=dameleCT[0][3]
    # 	# xb=dameleCT[elem][3]
    # 	# ya=dameleCT[0][4]
    # 	# yb=dameleCT[elem][4]
    # 	# dist=sqrt(((xa-xb)**2)+((ya-yb)**2))
    #     dist=dameleCT[elem][6]
    # dameleCT[elem][5]=dist
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    # if len(dameleCT)>1:
    # 	longitud=dameleCT[-1][7]
    # else:
    # 	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    #escribo en todos los archivo Ns y en Km1 el dagno de km1
    if len(dameleCT)!=0:
    	for n in range(len(listarchivos)):
            for elem in dagnokm1:
                listarchivos[n].write('%d %d %d %d\n' 
                              % (elem[0],elem[1],elem[2],elem[-1]))
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,elem[1],1.0))
                
    #escribo los nuevos danos del criterio tensional
    # sorting the Aset list in descending order of tval:
    Aset.sort(key=lambda Aset:Aset[2],reverse=True)
    Asetcrit=[]
    # [NeG, NeL, tval, tcval, ip, valA]
    for ipoint in Aset:
        # ipoint[0] = global element number
        # ipoint[1] = local element number associated to part instance
        # ipoint[2] = int. point traction vector t(x)
        # ipoint[3] = path_SDV16[k].data: critical traction vector tc(x)
        # ipoint[4] = integration point number
        # ipoint[5] = ratio of t(x) to t_c(x)
        if ipoint[-1] >= 1.0: #fills the Asetcrit array with data of the A_sigma set
            Asetcrit.append([ipoint[0], ipoint[1], ipoint[2], ipoint[3], ipoint[4], ipoint[5]])
            
    # FUNCTION FOR SEQUENCES:
        # random.shuffle(x): Shuffle the sequence x in place
    # (A FEW) REAL-VALUED DISTRIBUTIONS:
        # random.uniform(a, b)
        # random.gammavariate(alpha, beta)
        # random.gauss(mu=0.0, sigma=1.0)
        # random.lognormvariate(mu, sigma)
        # random.normalvariate(mu=0.0, sigma=1.0)
        # random.paretovariate(alpha)
        # random.weibullvariate(alpha, beta): Weibull distribution. 
        #   alpha is the scale parameter and beta is the shape parameter.
    
    #ESCRIBO EN TODOS LOS ARCHIVOS NS Y EN KM1 EL DAGNO DE KM1
    if len(dameleCT)!=0:
        # sorting the Asetcrit list by descending order of t(x)/tc(x)
        Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
        # ***RANDOM SHUFFLING OF ROWS IN THE ASETCRIT LIST***:
        # Asetcrit=random.sample(Asetcrit,len(Asetcrit))
        # convert the list into a numpy data array:
        Asetcritres=np.array(Asetcrit)
        
        # numpy random normal distribution:
        # p=prand # 0.2, 0.3,... constant of multiplication
        sigma=1.0 #standard deviation: 0.25, 0.5, 1,...
            # It may be preferable to change the std.dev. of chirandom to e.g., 0.10e-5
            # and also change the random method
        # chirandom = np.random.normal(0,np.std(Asetcrit[:][2]),len(Asetcrit))
        chirandomv2 = np.random.normal(0,sigma,len(Asetcrit))
        chirandomv2[chirandomv2<0] = 1E-4
        tc_rand = np.array(Asetcritres[:,3]) * (np.ones(len(Asetcrit)) + float(prand)*chirandomv2)
        t2tcx = Asetcritres[:,2]/tc_rand # 

        # Make a new Asetcrit array and concatenate the t2tcx 1D vector on the last
        #  column; then convert the array into a list and sort it using the new t/tc data
        Asetcrit_new = np.concatenate([Asetcritres, t2tcx.reshape(len(t2tcx),1)], axis=1)
        Asetcrit=list(Asetcrit_new)
        # sort the new list in descending order of Asetcritres[:,1]/tc_rand
        Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
        
        # Asetcritnp=np.array(Asetcrit)
        for n in range(len(listarchivos)):
            for elem in range(len(Asetcrit)):
                # N = 0
                # if n==0:
                #     damage=1.0
                #     NeG=int(Asetcrit[elem][0])
                #     # damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                #     # if damelei!=None:
                #     #     dameleCT[damelei].append(damage)
                #         # print(dameleCT[damelei])
                #     for ip in range(1,5):
                #         listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                
                # N = 1, deactivates %? of the most stressed elements
                if n==1 and elem>=0:
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.10*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                    # print(np.array(Asetcrit))
                    # print(dameleCT[:][1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                        # print(dameleCT[damelei])
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON VARIABLE DAMA ***!
                    
                # COMPLETAR LISTA DE P.I. EN C/INICIO CON DANO = 1.0 
                # elif n==1 and elem > round(0.90*len(Asetcrit)):
                # #     print(n,Asetcrit[elem][1])
                #     damage=1;
                #     NeG=int(Asetcrit[elem][0])
                #     damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                #     if damelei!=None:
                #         dameleCT[damelei].append(damage)
                #     for ip in range(1,5):
                #         listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                
                if n==2 and elem <= round(0.90*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.20*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(0.10)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    #     # print(dameleCT[damelei])
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                        
                # N = 3, deactivates 70% of the most stressed elements        
                if n==3 and elem <= round(0.70*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.350*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                if n==4 and elem <= round(0.60*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.50*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                # elif n==2 and ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.70:
                #     print(n,Asetcrit[elem][1])
                #     damage=1;
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                            
                # N = 5, deactivates approx. 40% of the most stressed elements; ***try with <= np.mean(tc_rand)
                if n==5 and elem <= round(0.50*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # dameleCT[elem].append(damage);
                
                # N = 6, deactivates approx. 30% of most stressed elements;
                if n==6 and elem <= round(0.40*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # N = 7, deactivates approx. 20% of most stressed elements;
                if n==7 and elem <= round(0.30*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # N = 8, deactivates approx. 10% of most stressed elements;
                if n==8 and elem <= round(0.20*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # HECHO: ANADIR MAS INICIOS DEL CRITERIO ENERGETICO Y CREAR DISTRIBUCION ALEATORIA PARA TC:
                if n==9 and elem <= round(0.10*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                #*** N = 9 ***, keeps Asigma springs active
                if n > 9:
                    # print(n,tc_rand[elem])
                    damage=1.0
                    NeG=Asetcrit[elem][0]
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d\n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # dameleCT[elem].append(damage);
                    
                # with open('log_criTen.txt', 'a') as f:
                #     f.write(str(name_files)) #ODB name
                #     f.write('\t')
                #     f.write(str(n)) #energy criterion N-th start
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][9])) #factor
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][10])) #sum i.p.
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][1])) #NelGlobal
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][-1])) #dama
                #     f.write('\n')
                # f.close()
            
        # cierro archivos  
        for n in range(len(listarchivos)):
            listarchivos[n].close()
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------    
    
    damageTen=[] #!!
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))			
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8],dameleCT[elem][11]])
    		
    		for n in range(len(listafunN)):
     			archDamTen.write(' %e' % (dameleCT[elem][1+n]))
     			damageTen[elem].append(dameleCT[elem][1+n])
    		archDamTen.write('\n')
    archDamTen.close()
    #-----------------------------------------------------------------------------------------------------------------------
    Nsnumber = len(listarchivos)-1
    odb.close()
    return damageTen, Nsnumber, Asetcrit
# %%

def PMTESCcriTen2Fibers(name_files, working_directory, setnodeInt, dicc_NeL_T, Asigma_new):
    """
    def PMTESCcriTen2Fibers()

    Function that returns the damageTen list for the model with 2 fibers embedded in a matrix.
    Each energy criterion Nth-start is based on a percentage of the user material's most stressed 
    elements satisfying the stress criterion. N-starts are applied to the 30, 45, 50, 70 and 90
    percent of the most stressed elements in the set, plus a final N-start leaving all the interface
    springs active.
    
    Returns *damageTen: a list with all elements fulfilling the stress criterion
            *Nsnumber: number of possible crack paths implemented by this function
            *Asetcrit: a Numpy array with element and integration point information
                of the A_sigma set.
    """    
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    
    #%%
    #-------------------------------------------------------
    #abrimos los archivos N del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w+')
    #Fichero del dano actual k para N1 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w+') 
    #Fichero del dano actual k para N2  
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w+')
    #Fichero del dano actual k para N3  
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w+')
    #FIchero del dano actual k para N4 
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w+')
    #FIchero del dano actual k para N5 
    archivoN5=open(working_directory_Ten+'/damageN5.txt','w+')
    #Fichero del dano actual k para N6 
    archivoN6=open(working_directory_Ten+'/damageN6.txt','w+')
    #Fichero del dano actual k para N7 
    archivoN7=open(working_directory_Ten+'/damageN7.txt','w')
    #Fichero del dano actual k para N8 
    archivoN8=open(working_directory_Ten+'/damageN8.txt','w')
    #Fichero del dano actual k para N9
    archivoN9=open(working_directory_Ten+'/damageN9.txt','w')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4,archivoN5,archivoN6]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
       
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00
    	return z
    def n2(dist,longitud):
    	z=0.00
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./sqrt(longitud))*sqrt(dist) 
    	except ZeroDivisionError:
    		1.
    	return z #DAMAGE VARIABLE
    def n4(dist,longitud):
        z=1.00
        return z
    def n5(dist,longitud):
        z=0.00
        return z
    def n6(dist,longitud):
        z=0.00
        return z
    def n7(dist,longitud):
        z=0.00
        return z
    def n8(dist,longitud):
        z=0.00
        return z
    def n9(dist,longitud):
        z=0.00
        return z
    listafunN=[n1,n2,n3,n4,n5,n6]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    Aset=[]
    Ipoint=[]
    for k in range(intpoint): 
       	damage=path_SDV1[k].data
       	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
       	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
       	ip=path_SDV2[k].integrationPoint
       	NeG=path_SDV2[k].data
        NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        tval=path_SDV15[k].data
        tcval=path_SDV16[k].data
        valA=tval/tcval
        
       	if damage!=0.00 and GtotT>=GcT: #damage=0 damage by CT. Hemos quitado la restrinccion de romper PI a PI
       		NeL=path_SDV2[k].elementLabel; Aset.append([NeG, tval, tcval, ip, valA]);
       		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
       		GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
       		x=path_SDV10[k].data
       		y=path_SDV11[k].data
               
       		#saco el area de cada elemento dividida entre 4
       		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
       		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
       		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
       		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
       		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
       		#si quiero el valor en su CDG lo deberia dividir por el Area total
       		jacobElm=dicc_NeL[NeL2][2]/4 
       		#fcip=sqrt(GtotT/GcT)  
       		#fcelm=fcip*jacobElm     
       		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
       		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
       		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
       		dicc_NeL[NeL2][1]=int(NeG); 
       		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
       		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0; dicc_NeL[NeL2][5]=ip;
       		#sumo el valor de cada PI de todas las energias multiplicado por
       		#el jacobiano=Area total del elemento/4
           
       		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
       		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
       		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm; dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip;
            #sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento	
      		 
       	if damage==0.00: #damage=0 yes damage
            #guardo en una lista los PI rotos para despues escribrir en archivos 
       		#si finalmente hay algun elemento dagnado
       		NeL=path_SDV2[k].elementLabel; dagnokm1.append([ip,NeG,damage])
    #-----------------------------------------------------------------------------------------------------------------------
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Bucle que guarda el dagno si queremos obligar a romper por CT todos los PI
    # Aqui podemos controlar que rompa elemento a elemento -->>
    for elem in listaElem:
       	if elem[6]>elem[7] and elem[10]==10:
            elem[9]=sqrt(elem[6]/elem[7])
            dameleCT.append(elem)
    		#dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario dicc_NeL de ese elemento
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenamos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    # for elem in range(len(dameleCT)):
    #  dist=dameleCT[elem][6]
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    if len(dameleCT)>1:
    	longitud=dameleCT[-1][7]
    else:
    	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    
    # sorting the Aset list in descending order of tval/tcval:
    Aset.sort(key=lambda Aset:Aset[1],reverse=True)
    Asetcrit=[]
 
    #ESCRIBO EN TODOS LOS ARCHIVOS NS Y EN KM1 EL DAGNO DE KM1
    if len(dameleCT)!=0:
        for ipoint in Aset:
            # ipoint[0] = global element number
            # ipoint[1] = int. point traction vector t(x)
            # ipoint[2] = path_SDV16[k].data: critical traction vector tc(x)
            # ipoint[3] = integration point number
            # ipoint[4] = ratio of t(x) to t_c(x)
            indip=np.where((Asigma_new[:,0] == ipoint[0]) & (Asigma_new[:,1] == ipoint[3]))
            # data appended to the Asetcrit array with data of the A_sigma set:
            if ipoint[4] >= 1.0: #fills the Asetcrit array with data of the A_sigma set
                tcx_rnd=Asigma_new[indip,-1]
                # print(indip, tcx_rnd)
                Asetcrit.append([ipoint[0], ipoint[1], ipoint[2], ipoint[3], ipoint[4], ipoint[1]/float(tcx_rnd)])
        # sorting the Asetcrit list by descending order of t(x)/tc(x)
        Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
        for n in range(len(listarchivos)):
            for elem in dagnokm1:
                listarchivos[n].write('%d %d %e \n' 
                              % (elem[0],elem[1],elem[2]))
                
            # for elem in dameleCT:
            #     listarchivos[n].write('%d %d %e \n' % (elem[5],elem[1],1.0))
        
        # convert the list into a numpy data array:
        Asetcritres=np.array(Asetcrit)
        print(Asetcritres)
    # REORDENAMIENTO ALEATORIO DE LA LISTA dameleCT:
    # dameleCT=random.sample(dameleCT, len(dameleCT))
    # random.shuffle(dameleCT) #modifies the original list by shuffling its elements
     
    #Escribo los nuevos danos del criterio tensional
    # *HECHO: HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON DISTINTOS
    # VALORES DE VARIABLE DAMA **!
    # *HECHO: CAMBIAR EL PORCENTAJE DE LOS ELEMENTOS MAS TENSIONADOS P/CADA N.
    for n in range(len(listarchivos)):
    	 for elem in range(len(dameleCT)):
            # N = 0  
            if n==0:
                damage=1.0;
                dameleCT[elem].append(damage);
                NeG=dameleCT[elem][1];
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage));
            # N = 1, deactivates elements in the top 90% of the list:
            if n==1 and elem <= round(0.90*len(dameleCT)):
                # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) <= 0.90:
                # print(n,dameleCT[elem])
                damage=0;
                # HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON IGUAL VARIABLE DAMA **!
                dameleCT[elem].append(damage);
                NeG=dameleCT[elem][1];
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage));
            # COMPLETAR LISTA DE P.I. EN C/INICIO CON DANO = 1.0 
            
            if n==2 and elem <= round(0.70*len(dameleCT)):
                # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.90:
                # print(n,dameleCT[elem])
                damage=0;
                dameleCT[elem].append(damage);
                NeG=dameleCT[elem][1];
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # N = 3, deactivates elements in the top 50% of the list:      
            if n==3 and elem <= round(0.50*len(dameleCT)):
                # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) <= 0.50:
                # print(n,dameleCT[elem])
                damage=0;
                dameleCT[elem].append(damage);
                NeG=dameleCT[elem][1];
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            if n==4 and elem <= round(0.45*len(dameleCT)):
            # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.50:
                # print(n,dameleCT[elem])
                damage=0;
                dameleCT[elem].append(damage);
                NeG=dameleCT[elem][1];
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                        
            # N = 5, deactivates elements in the top 30% of the list:
            if n==5 and elem <= round(0.30*len(dameleCT)):
            # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) <= 0.30:
                # print(n,dameleCT[elem])
                damage=0
                dameleCT[elem].append(damage)
                NeG=dameleCT[elem][1]
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            if n > 5:
            # ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.30:
                # print(n,dameleCT[elem])
                damage=1
                dameleCT[elem].append(damage)
                NeG=dameleCT[elem][1]
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))

                
            # with open('log_criTen.txt', 'a') as f:
            #     f.write(str(name_files)) #ODB name
            #     f.write('\t')
            #     f.write(str(n)) #energy criterion N-th start
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][9])) #factor
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][10])) #sum i.p.
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][1])) #NelGlobal
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][-1])) #dama
            #     f.write('\n')
            # f.close()
            
    # cierro archivos  
    for n in range(len(listarchivos)):
        listarchivos[n].close()
    #-----------------------------------------------------------------------------------------------------------------------
    
    #-----------------------------------------------------------------------------------------------------------------------    
    damageTen=[] #!!   --->>
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))		
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]])
    		# print(dameleCT[elem][10], dameleCT[elem][9])
    		for n in range(len(listafunN)):
     			archDamTen.write(' %e' % (dameleCT[elem][5+n]))
     			damageTen[elem].append(dameleCT[elem][5+n])
    		archDamTen.write('\n')
    archDamTen.close()
    
    #-----------------------------------------------------------------------------------------------------------------------
    Nsnumber = len(listarchivos)-1
    return damageTen, Nsnumber, Asetcrit
    odb.close()  
def PMTESCcriTen2FibersRand(name_files, working_directory, setnodeInt, dicc_NeL_T, k, m, iter_count, eps0, prand):
    """
    def PMTESCcriTen2FibersRand()

    # This function returns the damageTen list for the model with 2 fibers embedded in a matrix.
    # Energy criterion Nth-start is based on a subset of the interface most stressed 
    # integration points satisfying the stress criterion.
    # A random distribution of multiplicative factors is used for every N-start.

    """    
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    def fiber2XYcoord(inp_lines):
        for line in inp_lines:
            if line.startswith('*Instance, name=Interface-2, '):
                # Assuming the first parameter is on the next line
                next_line = inp_lines[inp_lines.index(line) + 1]
                # Split the line by commas (assuming comma-separated values)
                parameters = next_line.split(', ')
                if len(parameters) > 0:
                    try:
                        xcoordf2 = float(parameters[0])
                        ycoordf2 = float(parameters[1])
                        return xcoordf2, ycoordf2
                    except ValueError:
                        print("Error: First parameter is not numeric.")
                        return None
        print("Error: Second instance not found.")
        return None
    
    def sigmac_parameter(inp_lines):
        for line in inp_lines:
            if line.startswith('*User Material'):
                # Assuming the first parameter is on the next line
                next_line = inp_lines[inp_lines.index(line) + 1]
                # Split the line by commas (assuming comma-separated values)
                parameters = next_line.split(', ')
                if len(parameters) > 0:
                    try:
                        first_param = float(parameters[0])
                        brittleness_num=float(parameters[-1])
                        GIc=float(parameters[1])
                        h=float(parameters[-2])
                        xi=float(parameters[3])
                        lambdhs=float(parameters[2])
                        
                        return first_param, GIc, brittleness_num, h, xi, lambdhs
                    except ValueError:
                        print("Error: First parameter is not numeric.")
                        return None
        print("Error: User material section not found.")
        return None
    fileINPUT = open('inputFFMLEBIM_adaptivef.txt','r')
    flag = fileINPUT.readline()
    name_INP = fileINPUT.readline().rstrip()
    fileINPUT.close()

    inp_file_path = working_directory+'/'+name_INP+'.inp'
    with open(inp_file_path, 'r') as inp_file:
        inp_lines = inp_file.readlines()
    first_param, GIc, mu_const, interfh, xi, lambdhs = sigmac_parameter(inp_lines)
    xcf2, ycf2 = fiber2XYcoord(inp_lines)
    #%%
    #-------------------------------------------------------
    #abrimos los archivos N del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w+')
    #Fichero del dano actual k para N1 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w+') 
    #Fichero del dano actual k para N2  
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w+')
    #Fichero del dano actual k para N3  
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w+')
    #FIchero del dano actual k para N4 
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w+')
    #FIchero del dano actual k para N5 
    archivoN5=open(working_directory_Ten+'/damageN5.txt','w+')
    #Fichero del dano actual k para N6 
    archivoN6=open(working_directory_Ten+'/damageN6.txt','w+')
    #Fichero del dano actual k para N7 
    archivoN7=open(working_directory_Ten+'/damageN7.txt','w+')
    #Fichero del dano actual k para N8 
    archivoN8=open(working_directory_Ten+'/damageN8.txt','w+')
    #Fichero del dano actual k para N9
    archivoN9=open(working_directory_Ten+'/damageN9.txt','w+')
    archivoN10=open(working_directory_Ten+'/damageN10.txt','w+')
    archivoN11=open(working_directory_Ten+'/damageN11.txt','w+')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4,archivoN5,archivoN6,archivoN7,archivoN8,archivoN9,\
                  archivoN10,archivoN11]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w+')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
    path_SDV13=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV13'].\
    	getSubset(region=InterElementSet).values
    path_SDV14=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV14'].\
    	getSubset(region=InterElementSet).values
    path_SDV15=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV15'].\
    	getSubset(region=InterElementSet).values
    path_SDV16=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV16'].\
    	getSubset(region=InterElementSet).values   
    # area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    # 	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(region=InterElementSet, position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------          
    listafunN=[]
    for val in range(len(listarchivos)-1):
        if val==(len(listarchivos)-1):
            listafunN.append(1)
        else:
            listafunN.append(0)
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    # elementos=len(area)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    Aset=[]; Gclst=[]
    # Ipoint=[]
    for k in range(intpoint): 
        damage=path_SDV1[k].data
        GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
        GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
        ip=path_SDV2[k].integrationPoint
        NeG=path_SDV2[k].data
        # x=path_SDV10[k].data; y=path_SDV11[k].data
        psi_g=math.atan2(path_SDV14[k].data*(math.sqrt(1/xi)), path_SDV13[k].data)
        GcE=float(GIc)*(1+(math.tan(psi_g*(1-lambdhs)))**2)*(mu_const/interfh); psi_gc=(math.pi)/(2*(1-lambdhs));
        if abs(psi_g)>=psi_gc: GcE=GIc*1E8
        # NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        tval=path_SDV15[k].data
        tcval=path_SDV16[k].data
        valA=tval/tcval
        # # flow control structure to save the critical fracture energy of each interface:
        # if x>0 and str(path_SDV2[k].instance.name).endswith('INTERFACE-1'):
        #     Gclst.append([math.atan(y/x), GcE])
        # elif str(path_SDV2[k].instance.name).endswith('INTERFACE-2'):
        #     Gclst.append([float(180) - math.atan(y/abs(x)), GcE])
            
        if damage!=0.00 and GtotT>=GcT: #damage=0 damage by CT. Hemos quitado la restrinccion de romper PI a PI
       		NeL=path_SDV2[k].elementLabel; 
       		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name); 
       		GcE=path_SDV6[k].data #la Gc del criterio energetico 
       		x=path_SDV10[k].data
       		y=path_SDV11[k].data
       		#saco el area de cada elemento dividida entre 4
       		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
       		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
       		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
       		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
       		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
       		#si quiero el valor en su CDG lo deberia dividir por el Area total
       		jacobElm=dicc_NeL[NeL2][2]/4 
       		#fcip=sqrt(GtotT/GcT)  
       		#fcelm=fcip*jacobElm     
       		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
       		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
       		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
       		dicc_NeL[NeL2][1]=int(NeG); 
       		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
       		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0; dicc_NeL[NeL2][5]=ip;
       		#sumo el valor de cada PI de todas las energias multiplicado por
       		#el jacobiano=Area total del elemento/4
           
       		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
       		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
            #sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento
       		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm; dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip; dicc_NeL[NeL2][11]=int(NeL)
            
        if damage!=0.00 and GtotT>=GcT and dicc_NeL[NeL2][10]==10:
            # da lo mismo que se escriba cualquier etiqueta del p.i., lo que
            # importa es que el numero de elementos en la lista Aset sea igual
            # que en la lista de elementos seleccionados por el CTensional!:
            # dameleCT.
            # Por esto es que esta lista es luego filtrada para evitar duplicados
            Aset.append([NeG, NeL, tval, tcval, 1, valA]);
                
        if damage==0.0: #damage=0 yes damage
           #guardo en una lista los PI rotos para despues escribrir en archivos 
           NeL=path_SDV2[k].elementLabel
           dagnokm1.append([ip,NeG,damage,int(NeL)])
           
    #-----------------------------------------------------------------------------------------------------------------------
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Bucle que guarda el dagno si queremos obligar a romper por CT todos los PI
    # Aqui podemos controlar que rompa elemento a elemento -->>
    for elem in listaElem:
       	if elem[6]>elem[7] and elem[10]==10:
            elem[9]=sqrt(elem[6]/elem[7])
            dameleCT.append(elem)
    		#dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario dicc_NeL de ese elemento
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenamos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    
    Asetcrit=[]            
    # FUNCTION FOR SEQUENCES:
        # random.shuffle(x): Shuffle the sequence x in place
    # (A FEW) REAL-VALUED DISTRIBUTIONS:
        # random.uniform(a, b)
        # random.gammavariate(alpha, beta)
        # random.gauss(mu=0.0, sigma=1.0)
        # random.lognormvariate(mu, sigma)
        # random.normalvariate(mu=0.0, sigma=1.0)
        # random.paretovariate(alpha)
        # random.weibullvariate(alpha, beta): Weibull distribution. 
        #   alpha is the scale parameter and beta is the shape parameter.
    
    #ESCRIBO EN TODOS LOS ARCHIVOS NS Y EN KM1 EL DAGNO DE KM1
    if len(dameleCT)!=0:
        # filter and sort the Aset list in descending order of tval:
        Aset = [row for row in Aset if row[4]==1] #avoid element duplicates
        Aset.sort(key=lambda Aset:Aset[2],reverse=True)
        for ipoint in Aset:
            # ipoint[0] = global element number
            # ipoint[1] = local element number
            # ipoint[2] = int. point traction vector t(x)
            # ipoint[3] = path_SDV16[k].data: critical traction vector tc(x)
            # ipoint[4] = integration point number
            # ipoint[5] = ratio of t(x) to t_c(x)
            if ipoint[5] >= 1.0: #fills the Asetcrit array with data of the A_sigma set
                Asetcrit.append([ipoint[0], ipoint[1], ipoint[2], ipoint[3], ipoint[4], ipoint[5]])
        # sorting the Asetcrit list by descending order of t(x)/tc(x)
        # Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
        
        # ***RANDOM SHUFFLING OF ROWS IN THE ASETCRIT LIST***:
        # Asetcrit=random.sample(Asetcrit,len(Asetcrit))
        # convert the list into a numpy data array:
        Asetcritres=np.array(Asetcrit)
        # numpy random normal distribution:
        # p=0.0 # 0, 0.1, 0.2, 0.3,... constant of multiplication
        sigma=1 #standard deviation: 0.25, 0.5, 1,...
            
        chirandomv2 = np.random.normal(0,sigma,len(Asetcrit))
        tc_rand = np.array(Asetcritres[:,3]) * (np.ones(len(Asetcrit)) + float(prand)*chirandomv2)
        tc_rand[tc_rand < 0]=1E-5
        t2tcx = Asetcritres[:,2]/(tc_rand)
        # Make a new Asetcrit array and concatenate the t2tcx 1D vector on the last
        #  column; then convert the array into a list and sort it using the new t/tc data
        Asetcrit_new = np.concatenate([Asetcritres, t2tcx.reshape(len(t2tcx),1)], axis=1)
        Asetcrit=list(Asetcrit_new)
        
        # if iter_count==1:
        #     np.random.shuffle(Asetcrit)
        #     print('Shuffled integration point list: ', Asetcrit)
        #     print(iter_count, eps0)
        
        print('List of elements which satisfy the stress condition: ')
        print(np.array(Asetcrit))
        #THIS IS FOR DEBUGGING ANY INDEXERROR
        # print(Asetcritres.shape, len(Asetcrit))
        #escribo en todos los archivo Ns y en Km1 el dagno de km1
       	for n in range(len(listarchivos)):
               for elem in dagnokm1:
                   listarchivos[n].write('%d %d %d %d\n' 
                                 % (elem[0],elem[1],elem[2],elem[-1]))
    
    # list comprehension of Asetcrit:
    # Asetcrit = np.array(Asetcrit)
    # Asetcrit = [val for val in Asetcrit if val[4]==1]
    # Asetcrit = list(Asetcrit)
    # SORT THE NEW LIST IN DESCENDING ORDER OF T_X/TC_RAND
    Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
    for n in range(len(listarchivos)):
    	for elem in range(len(Asetcrit)):
            # N = 0
            # if n==0:
            #     damage=1.0
            #     NeG=int(Asetcrit[elem][0])
            #     # damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
            #     # if damelei!=None:
            #     #     dameleCT[damelei].append(damage)
            #         # print(dameleCT[damelei])
            #     for ip in range(1,5):
            #         listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            # THE CRITERIA TO WRITE DATA TO LISTARCHIVOS[N] NEEDS TO CHANGE!
            
            # N = 1, deactivates %? of the most stressed elements
                if n==1:
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.10*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                        # print(dameleCT[damelei])
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON VARIABLE DAMA **!
                
                # COMPLETAR LISTA DE P.I. EN C/INICIO CON DANO = 1.0 
                # elif n==1 and elem > round(0.90*len(Asetcrit)):
                # #     print(n,Asetcrit[elem][1])
                #     damage=1;
                #     NeG=int(Asetcrit[elem][0])
                #     damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                #     if damelei!=None:
                #         dameleCT[damelei].append(damage)
                #     for ip in range(1,5):
                #         listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
                if n==2 and elem <= round(0.90*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.20*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                    # tc_rand[elem] >= np.mean(tc_rand) - float(0.10)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    #     # print(dameleCT[damelei])
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    
                # N = 3, deactivates 80% of the most stressed elements        
                if n==3 and elem <= round(0.80*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.350*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                            listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
            
                if n==4 and elem <= round(0.70*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.50*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                        
                if n==5 and elem <= round(0.60*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.50*(Aset_max-Aset_min)):
                    # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                # elif n==2 and ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.70:
                #     print(n,Asetcrit[elem][1])
                #     damage=1;
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                            
                # N = 5, deactivates approx. 50% of the most stressed elements; ***try with <= np.mean(tc_rand)
                if n==6 and elem <= round(0.50*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # dameleCT[elem].append(damage);
                
                # N = 6, deactivates approx. 40% of most stressed elements;
                if n==7 and elem <= round(0.40*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # N = 7, deactivates approx. 30% of most stressed elements;
                if n==8 and elem <= round(0.30*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # N = 8, deactivates approx. 20% of most stressed elements;
                if n==9 and elem <= round(0.20*len(Asetcrit)):
                # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                    # print(n, Asetcrit[elem][-1])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                
                # HECHO: ANADIR MAS INICIOS DEL CRITERIO ENERGETICO Y CREAR DISTRIBUCION ALEATORIA PARA TC:
                #*** N = 9 ***, keeps Asigma springs active
                if n == 10 and elem <= round(0.10*len(Asetcrit)):
                    # print(n,tc_rand[elem])
                    damage=0
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                    # dameleCT[elem].append(damage);
                
                if n > 10:
                    # print(n,tc_rand[elem])
                    damage=1
                    NeG=int(Asetcrit[elem][0])
                    damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                    if damelei!=None:
                        dameleCT[damelei].append(damage)
                    for ip in range(1,5):
                        listarchivos[n].write('%d %d %d %d \n' % (ip,NeG,damage,Asetcrit[elem][1]))
                        
                # with open('log_criTen.txt', 'a') as f:
                #     f.write(str(name_files)) #ODB name
                #     f.write('\t')
                #     f.write(str(n)) #energy criterion N-th start
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][9])) #factor
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][10])) #sum i.p.
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][1])) #NelGlobal
                #     f.write('\t')
                #     f.write(str(dameleCT[elem][-1])) #dama
                #     f.write('\n')
                # f.close()        
    # cierro archivos  
    for n in range(len(listarchivos)):
        listarchivos[n].close()
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------    
    damageTen=[] #!! --->>
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))		
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8],dameleCT[elem][11]])
    		# print(dameleCT[elem][10], dameleCT[elem][9])
    		for n in range(len(listafunN)):
     			archDamTen.write(' %e' % (dameleCT[elem][1+n]))
     			damageTen[elem].append(dameleCT[elem][1+n])
    		archDamTen.write('\n')
    archDamTen.close()

    #-----------------------------------------------------------------------------------------------------------------------
    Nsnumber = len(listarchivos)-1
    return damageTen, Nsnumber, Asetcrit
    odb.close()

def PMTESCcriTen2FibersRandK0(name_files, working_directory, setnodeInt, dicc_NeL_T, Asigma_new):
    """
    def PMTESCcriTen2FibersRandK0()
    A random distribution of tc(x) for the entire interface set is defined once at the end of load step K0.
    
    This function returns the damageTen list for the model with 2 fibers embedded in an infinite matrix.
    Energy criterion Nth-start is based on a subset of the interface most stressed 
    integration points satisfying the t(x)/tc(x) criterion. All user material integration
    points are sampled with a random normal distribution for the critical traction
    vector, tc(x), which are later evaluated by the energetic fracture criteria.

    """    
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    
    #%%
    #-------------------------------------------------------
    #abrimos los archivos N del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w+')
    #Fichero del dano actual k para N1 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w+') 
    #Fichero del dano actual k para N2  
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w+')
    #Fichero del dano actual k para N3  
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w+')
    #FIchero del dano actual k para N4 
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w+')
    #FIchero del dano actual k para N5 
    archivoN5=open(working_directory_Ten+'/damageN5.txt','w+')
    #Fichero del dano actual k para N6 
    archivoN6=open(working_directory_Ten+'/damageN6.txt','w+')
    #Fichero del dano actual k para N7 
    archivoN7=open(working_directory_Ten+'/damageN7.txt','w')
    #Fichero del dano actual k para N8 
    archivoN8=open(working_directory_Ten+'/damageN8.txt','w')
    #Fichero del dano actual k para N9
    archivoN9=open(working_directory_Ten+'/damageN9.txt','w')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4,archivoN5,archivoN6]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
       
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00
    	return z
    def n2(dist,longitud):
    	z=0.00
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./sqrt(longitud))*sqrt(dist) 
    	except ZeroDivisionError:
    		1.
    	return z #DAMAGE VARIABLE
    def n4(dist,longitud):
        z=1.00
        return z
    def n5(dist,longitud):
        z=0.00
        return z
    def n6(dist,longitud):
        z=0.00
        return z
    def n7(dist,longitud):
        z=0.00
        return z
    def n8(dist,longitud):
        z=0.00
        return z
    def n9(dist,longitud):
        z=0.00
        return z
    listafunN=[n1,n2,n3,n4,n5,n6]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    Aset=[]
    Ipoint=[]
    for k in range(intpoint): 
       	damage=path_SDV1[k].data
       	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
       	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
       	ip=path_SDV2[k].integrationPoint
       	NeG=path_SDV2[k].data
        NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        tval=path_SDV15[k].data
        tcval=path_SDV16[k].data
        valA=tval/tcval
        # Aset.append([NeG, valA, tcval, ip, damage])
        
       	if damage!=0.00 and GtotT>=GcT: #damage=0 damage by CT. Hemos quitado la restrinccion de romper PI a PI
       		NeL=path_SDV2[k].elementLabel; Aset.append([NeG, tval, tcval, ip, valA]);
       		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name); 
       		GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
       		x=path_SDV10[k].data
       		y=path_SDV11[k].data
               
       		#saco el area de cada elemento dividida entre 4
       		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
       		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
       		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
       		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
       		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
       		#si quiero el valor en su CDG lo deberia dividir por el Area total
       		jacobElm=dicc_NeL[NeL2][2]/4 
       		#fcip=sqrt(GtotT/GcT)  
       		#fcelm=fcip*jacobElm     
       		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
       		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
       		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
       		dicc_NeL[NeL2][1]=int(NeG); 
       		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
       		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0; dicc_NeL[NeL2][5]=ip;
       		#sumo el valor de cada PI de todas las energias multiplicado por
       		#el jacobiano=Area total del elemento/4
           
       		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
       		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
       		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm; dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip;
            #sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento
      		 
       	if damage==0.00: #damage=0 yes damage
            #guardo en una lista los PI rotos para despues escribrir en archivos 
       		#si finalmente hay algun elemento dagnado
       		NeL=path_SDV2[k].elementLabel; dagnokm1.append([ip,NeG,damage])
    #-----------------------------------------------------------------------------------------------------------------------
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Bucle que guarda el dagno si queremos obligar a romper por CT todos los PI
    # Aqui podemos controlar que rompa elemento a elemento -->>
    for elem in listaElem:
       	if elem[6]>elem[7] and elem[10]==10:
            elem[9]=sqrt(elem[6]/elem[7])
            dameleCT.append(elem)
    		#dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario listaElem de ese elemento
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenamos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    for elem in range(len(dameleCT)):
     dist=dameleCT[elem][6]
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    if len(dameleCT)>1:
    	longitud=dameleCT[-1][7]
    else:
    	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    # sorting the Aset list in descending order of tval:
    Aset.sort(key=lambda Aset:Aset[1],reverse=True)
    Asetcrit=[]
    
    # FUNCTION FOR SEQUENCES:
        # random.shuffle(x): Shuffle the sequence x in place
    # (A FEW) REAL-VALUED DISTRIBUTIONS:
        # random.uniform(a, b)
        # random.gammavariate(alpha, beta)
        # random.gauss(mu=0.0, sigma=1.0)
        # random.lognormvariate(mu, sigma)
        # random.normalvariate(mu=0.0, sigma=1.0)
        # random.paretovariate(alpha)
        # random.weibullvariate(alpha, beta): Weibull distribution. 
        #   alpha is the scale parameter and beta is the shape parameter.
    
    #ESCRIBO EN TODOS LOS ARCHIVOS NS Y EN KM1 EL DAGNO DE KM1
    if len(dameleCT)!=0:   
        for ipoint in Aset:
            # ipoint[0] = global element number
            # ipoint[1] = int. point traction vector t(x)
            # ipoint[2] = path_SDV16[k].data: critical traction vector tc(x)
            # ipoint[3] = integration point number
            # ipoint[4] = ratio of t(x) to t_c(x)
            
            indip=np.where((Asigma_new[:,0] == ipoint[0]) & (Asigma_new[:,1] == ipoint[3]))
            # data appended to the Asetcrit array with data of the A_sigma set:
            if ipoint[4] >= 1.0: #and ipoint[0]==Asigma_new[iNeG] and ipoint[3]==Asigma_new[indip]:
                tcx_rnd=Asigma_new[indip,-1]
                # print(indip, tcx_rnd)
                Asetcrit.append([ipoint[0], ipoint[1], ipoint[2], ipoint[3], ipoint[4], ipoint[1]/float(tcx_rnd)])
        
        # sort the new list in descending order of Asetcritres[:,1]/tc_rand
        Asetcrit.sort(key=lambda Asetcrit:Asetcrit[-1],reverse=True)
        
        #THIS IS FOR DEBUGGING OF ANY INDEXERROR
        # print(Asetcritres.shape, len(Asetcrit))
        # ********************************************
        # random.shuffle(Asetcrit) #
        # convert the list into a numpy data array:
        Asetcritres=np.array(Asetcrit)
        print(Asetcritres)
        # ********************************************
        for n in range(len(listarchivos)):
            for elem in dagnokm1:
                listarchivos[n].write('%d %d %e \n' % (elem[0],elem[1],elem[2]))
    #escribo los nuevos danos del criterio tensional
    # *HECHO: EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON DISTINTOS
    # VALORES DE VARIABLE DAMA **!
    for n in range(len(listarchivos)):
    	for elem in range(len(Asetcrit)):
            # N = 0
            # THE CRITERIA TO WRITE DATA TO LISTARCHIVOS[N] NEEDS TO CHANGE!
            
            # N = 1, deactivates %? of the most stressed elements
            if n==1 and elem <= round(0.675*len(Asetcrit)):
            # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.10*(Aset_max-Aset_min)):
                # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                # print(n, Asetcrit[elem][-1])
                damage=0
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage)
                    # print(dameleCT[damelei])
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                # HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON VARIABLE DAMA **!
                
            # COMPLETAR LISTA DE P.I. EN C/INICIO CON DANO = 1.0 
            # elif n==1 and ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.90:
            #     print(n,Asetcrit[elem][1])
            #     damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            if n==2 and elem <= round(0.60*len(Asetcrit)):
            # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.20*(Aset_max-Aset_min)):
                # tc_rand[elem] >= np.mean(tc_rand) - float(2)*np.std(tc_rand):
                # tc_rand[elem] >= np.mean(tc_rand) - float(0.10)*(np.max(tc_rand)-np.min(tc_rand)):
                # print(n, Asetcrit[elem][-1])
                damage=0
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage)
                    # print(dameleCT[damelei])
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # N = 3, deactivates %? of the most stressed elements        
            if n==3 and elem <= round(0.50*len(Asetcrit)):
            # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.350*(Aset_max-Aset_min)):
                # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                # print(n, Asetcrit[elem][-1])
                damage=0;
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage);
                for ip in range(1,5):
                        listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            if n==4 and elem <= round(0.45*len(Asetcrit)):
            # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.50*(Aset_max-Aset_min)):
                # tc_rand[elem] >= np.min(tc_rand) + float(0.50)*(np.max(tc_rand)-np.min(tc_rand)):
                # print(n, Asetcrit[elem][-1])
                damage=0;
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage);
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            # elif n==2 and ((Asetcrit_range-Asetcrit[elem][1])/(Asetcrit_range-Aset_min)) > 0.70:
            #     print(n,Asetcrit[elem][1])
            #     damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                        
            # N = 5, deactivates approx. %? of the most stressed elements; ***try with <= np.mean(tc_rand)
            if n==5 and elem <= round(0.30*len(Asetcrit)):
            # Asetcrit[elem][1]/tc_rand[elem] >= (Aset_min + 0.70*(Aset_max-Aset_min)):
                # print(n, Asetcrit[elem][-1])
                damage=0;
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage);
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                # dameleCT[elem].append(damage);
                
            # HECHO: ANADIR MAS INICIOS DEL CRITERIO ENERGETICO Y CREAR DISTRIBUCION ALEATORIA PARA TC:
            #*** N = 5 ***, keeps Asigma springs active
            if n > 5:
                # print(n,tc_rand[elem])
                damage=1;
                NeG=int(Asetcrit[elem][0])
                damelei=dameleCT[:][1].index(NeG) if NeG in dameleCT[:][1] else None
                if damelei!=None:
                    dameleCT[damelei].append(damage);
                for ip in range(1,5):
                    listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                # dameleCT[elem].append(damage);
                
            # with open('log_criTen.txt', 'a') as f:
            #     f.write(str(name_files)) #ODB name
            #     f.write('\t')
            #     f.write(str(n)) #energy criterion N-th start
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][9])) #factor
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][10])) #sum i.p.
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][1])) #NelGlobal
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][-1])) #dama
            #     f.write('\n')
            # f.close()
            
    # cierro archivos  
    for n in range(len(listarchivos)):
        listarchivos[n].close()
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------    
    damageTen=[] #!! --->>
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))		
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]])
    		# print(dameleCT[elem][10], dameleCT[elem][9])
    		for n in range(len(listafunN)):
     			archDamTen.write(' %e' % (dameleCT[elem][5+n]))
     			damageTen[elem].append(dameleCT[elem][5+n])
    		archDamTen.write('\n')
    archDamTen.close()

    #-----------------------------------------------------------------------------------------------------------------------
    Nsnumber = len(listarchivos)-1
    return damageTen, Nsnumber, Asetcrit
    odb.close()
    
def PMTESCcriTen2FibreNpow(name_files, working_directory, setnodeInt, dicc_NeL_T, xcf2, ycf2):
    """
    def PMTESCcriTen2FibreNpow()

    # This function returns the damageTen list for the model with 2 fibers embedded in a matrix
    # 2 components combinatorics: 2^N, amount of the energy criterion N-starts.

    """    
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    
    #%%
    #-------------------------------------------------------
    #abrimos los archivos N del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w+')
    #Fichero del dano actual k para N1 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w+') 
    #Fichero del dano actual k para N2  
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w+')
    #Fichero del dano actual k para N3  
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w+')
    #FIchero del dano actual k para N4 
    archivoN4=open(working_directory_Ten+'/damageN4.txt','w+')
    #FIchero del dano actual k para N5 
    archivoN5=open(working_directory_Ten+'/damageN5.txt','w+')
    #Fichero del dano actual k para N6 
    archivoN6=open(working_directory_Ten+'/damageN6.txt','w+')
    #Fichero del dano actual k para N7 
    archivoN7=open(working_directory_Ten+'/damageN7.txt','w+')
    #Fichero del dano actual k para N8 
    archivoN8=open(working_directory_Ten+'/damageN8.txt','w+')
    #Fichero del dano actual k para N9
    archivoN9=open(working_directory_Ten+'/damageN9.txt','w+')
    # 
    archivoN10=open(working_directory_Ten+'/damageN10.txt','w+')
    archivoN11=open(working_directory_Ten+'/damageN11.txt','w+')
    archivoN12=open(working_directory_Ten+'/damageN12.txt','w+')
    archivoN13=open(working_directory_Ten+'/damageN13.txt','w+')
    archivoN14=open(working_directory_Ten+'/damageN14.txt','w+')
    archivoN15=open(working_directory_Ten+'/damageN15.txt','w+')
    archivoN16=open(working_directory_Ten+'/damageN16.txt','w+')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3,archivoN4,archivoN5,
                  archivoN6,archivoN7,archivoN8,archivoN9,archivoN10,archivoN11,
                  archivoN12,archivoN13,archivoN14,archivoN15,archivoN16]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    # key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
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
       
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #--------------------------------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00
    	return z
    def n2(dist,longitud):
    	z=0.00
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./sqrt(longitud))*sqrt(dist) 
    	except ZeroDivisionError:
    		1.
    	return z #DAMAGE VARIABLE
    def n4(dist,longitud):
        z=1.00
        return z
    def n5(dist,longitud):
        z=0.00
        return z
    def n6(dist,longitud):
        z=0.00
        return z
    def n7(dist,longitud):
        z=0.00
        return z
    def n8(dist,longitud):
        z=0.00
        return z
    def n9(dist,longitud):
        z=0.00
        return z
    listafunN=[n1,n2,n3,n4]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    Aset=[]
    for k in range(intpoint): 
       	damage=path_SDV1[k].data
       	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
       	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
       	ip=path_SDV2[k].integrationPoint
       	NeG=path_SDV2[k].data
        NeInstance=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
        tval=path_SDV15[k].data
        tcval=path_SDV16[k].data
        valA=tval/tcval
        Aset.append([NeInstance, valA, path_SDV10[k].data, path_SDV11[k].data])
        
       	if damage!=0.00: #and GtotT>=GcT: #damage=0 damage by CT. Hemos quitado la restrinccion de romper PI a PI
       		# NeL=path_SDV2[k].elementLabel
       		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
       		GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
       		x=path_SDV10[k].data
       		y=path_SDV11[k].data
               
       		#saco el area de cada elemento dividida entre 4
       		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
       		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
       		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
       		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
       		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
       		#si quiero el valor en su CDG lo deberia dividir por el Area total
       		jacobElm=dicc_NeL[NeL2][2]/4 
       		#fcip=sqrt(GtotT/GcT)  
       		#fcelm=fcip*jacobElm     
       		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
       		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
       		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
       		dicc_NeL[NeL2][1]=int(NeG)
       		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x
       		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y
       		#sumo el valor de cada PI de todas las energias multiplicado por
       		#el jacobiano=Area total del elemento/4
       		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
       		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
       		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm
       		#sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento	
       		dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip
       	if damage==0.00: #damage=0 yes damage
       		#guardo en una lista los PI rotos para despues escribrir en archivos 
       		#si finalmente hay algun elemento dagnado
       		dagnokm1.append([ip,NeG,damage])
    
    #-----------------------------------------------------------------------------------------------------------------------
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    # esto no hace falta si no obligamos a que rompan todos los PI por CT
    # listaElem.sort(key=lambda listaElem:listaElem[10],reverse=True)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nueva lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    		
    # Bucle que guarda el dagno si queremos obligar a romper por CT todos los PI
    # Aqui podemos controlar que rompa elemento a elemento -->>
    for elem in range(len(listaElem)):
       	if listaElem[elem][6]>listaElem[elem][7]:
            listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7])
            dameleCT.append(listaElem[elem])
    		#dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario dicc_NeL de ese elemento
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    for elem in range(len(dameleCT)):
     dist=dameleCT[elem][6]
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    if len(dameleCT)>1:
    	longitud=dameleCT[-1][7]
    else:
    	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #dagnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    
    # sorting the Aset list in descending order of tval/tcval:
    Aset.sort(key=lambda Aset:Aset[1],reverse=True)
    Asetcrit=[]
    for ipoint in Aset:
        # ipoint[0] = NeInstance
        # ipoint[1] = t(x)/tc(x)
        # ipoint[2] = i.p. xcoord
        # ipoint[3] = i.p. ycoord
        if ipoint[1] >= 1.0:
            Asetcrit.append([ipoint[0], ipoint[1], ipoint[2], ipoint[3]])
    # sorting the most stressed I.P. by descending order of t/t_c:
    Asetcrit.sort(key=lambda Asetcrit:Asetcrit[1],reverse=True)    
    
    #ESCRIBO EN TODOS LOS ARCHIVO NS Y EN KM1 EL DAGNO DE KM1
    if len(dameleCT)!=0:
        # Asetcrit_range=Asetcrit[0][1]; # maximo de t/tc
        # Aset_min=Asetcrit[-1][1]; # minimo de t/tc
        for n in range(len(listarchivos)):
            for elem in dagnokm1:
               listarchivos[n].write('%d %d %e \n' % (elem[0],elem[1],elem[2]))
           
    #escribo los nuevos danos del criterio tensional
    # *HECHO: HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON DISTINTOS
    # VALORES DE VARIABLE DAMA **!
    for n in range(len(listarchivos)): 
    	for elem in range(len(dameleCT)):
            # 
            # N = 1
            if n==1 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] < 0:
                    # print(n,Asetcrit[elem][1])
                    damage=0;
                    # HAY QUE EVITAR DUPLICADOS DE PUNTOS DE INTEGRACION CON VARIABLE DAMA **!
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==1 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            # COMPLETAR LISTA DE P.I. EN C/ININCIO CON DANO = 1.0 
                    
            # N = 2        
            if n==2 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] > 0:
                    damage=0;
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==2 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                        
            #*** N = 3 ***            
            if n==3 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] > 0:
                    damage=0;
                    # dameleCT[elem].append(damage);
                    # NeG=dameleCT[elem][1];
                    # for ip in range(1,5):
                    #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==3 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            #*** N = 4 ***    
            if n==4 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] < 0: 
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==4 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            # *** N = 5 *** 
            if n==5 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==5 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            # *** N = 6 *** 
            if n==6 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==6 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            # *** N = 7 *** 
            if n==7 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==7 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))  
            
            # *** N = 8 *** 
            if n==8 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==8 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 9 *** 
            if n==9 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==9 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 10 *** 
            if n==10 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==10 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 11 *** 
            if n==11 and dameleCT[elem][0].endswith('_INTERFACE-1'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==11 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 12 *** 
            if n==12 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==12 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 13 *** 
            if n==13 and dameleCT[elem][0].endswith('_INTERFACE-2'):
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            elif n==13 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 14 *** 
            if n==14 and dameleCT[elem][0].endswith('_INTERFACE-1') and dameleCT[elem][3] > 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                    
            # *** N = 15 *** 
            if n==15 and dameleCT[elem][0].endswith('_INTERFACE-2') and (abs(dameleCT[elem][3])-abs(xcf2)) < 0:
                damage=0;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            # *** N = 16 *** 
            if n==16 and dameleCT[elem][0].endswith(('_INTERFACE-1','_INTERFACE-2')):
                damage=1;
                # dameleCT[elem].append(damage);
                # NeG=dameleCT[elem][1];
                # for ip in range(1,5):
                #     listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
            
            dameleCT[elem].append(damage);
            NeG=dameleCT[elem][1];
            for ip in range(1,5):
                listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
                
            # with open('log_criTen.txt', 'a') as f:
            #     f.write(str(name_files)) #ODB name
            #     f.write('\t')
            #     f.write(str(n)) #energy criterion N-th start
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][9])) #factor
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][10])) #sum i.p.
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][1])) #NelGlobal
            #     f.write('\t')
            #     f.write(str(dameleCT[elem][-1])) #dama
            #     f.write('\n')
            # f.close()
            
    # cierro archivos  
    for n in range(len(listarchivos)):
     	listarchivos[n].close()
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    
    #-----------------------------------------------------------------------------------------------------------------------    
    damageTen=[] #!!   --->>
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))		
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]])
    		print(dameleCT[elem][10], dameleCT[elem][9])
    		for n in range(len(listarchivos)-1):
     			archDamTen.write(' %e' % (dameleCT[elem][11+n]))
     			damageTen[elem].append(dameleCT[elem][11+n])
    		archDamTen.write('\n')
    archDamTen.close()
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    odb.close()
    return damageTen