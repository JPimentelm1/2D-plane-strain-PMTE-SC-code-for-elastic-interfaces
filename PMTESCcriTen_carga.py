# ********************************************************************************
# POSTPROCESADO ODB PARA RETORNAR EL FACTOR DE CARGA, LA RESISTENCIA CRITICA DE
# LA INTERFASE, Y LA TENSION NORMAL MAXIMA EN LA INTERFASE
# ********************************************************************************
# Modificaciones: Jose Pimentel
#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir,path,mkdir
from shutil import move, rmtree
from odbAccess import*
from sys import argv
from  math import sqrt #para raiz cuadrada
from string import replace
#from pickle import dump
#import pickle

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
                    return first_param, brittleness_num
                except ValueError:
                    print("Error: First parameter is not numeric.")
                    return None
    print("Error: User material section not found.")
    return None

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

def PMTESCcriTen_carga(name_files, working_directory, carga, setnodeInt):
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    old_load=float(carga)
    Eset=setnodeInt
    
	###para revisar en ABAQUS CAE
	#working_directory='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V14_WIN_PC_CASA\FFM_optimizada01\odbS'
	#chdir(working_directory)
	#odb =openOdb('DCBISOFFMDESP_para_carga.odb')
	#old_load=1.0
	#load_file='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V14_WIN_PC_CASA/FFM_optimizada01/archivo_carga.txt'
	#Eset='NINTERFACE'
	#-------------------------------------------------------

	#--------------------------------------------------------------------------
	#|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
	#--------------------------------------------------------------------------
	# de LEBIMdefplanaFFM tomo:
		  # statev(1)=damage
		  # statev(2)=noel
		  # statev(3)=psig
		  # statev(4)=Gtot
		  # statev(5)=Gc 
		  # statev(6)=GcE
		  # statev(7)=GiE
		  # statev(8)=GiiE
		  # statev(9)=signoN
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
	 
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
		getSubset(region=InterElementSet).values 
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
		getSubset(region=InterElementSet).values
    # 
    path_SDV13=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV13'].\
		getSubset(region=InterElementSet).values
    # ITERATE HERE TO SAVE THE INTERFACE NORMAL STRESSES
    sdv13max_value = None
    for value in path_SDV13:
        if sdv13max_value is None or value.data > sdv13max_value:
            sdv13max_value = value.data #SAVE MAX. STRESS(1)
    
	#-----------------------------------------------------------------------------------------------------------------------
	#||||||||||||||||||CREACION DE TABLA CON LOS PUNTOS DE INTEGRACION A DANAR ORDENADOS|||||||||||||||||||
	#-----------------------------------------------------------------------------------------------------------------------
	#la lista prueba no sirva para nada. Solo era para revisar la nueva UMAT
	#se puede poner o quitar cuando queramos
    puntosintdamT=[]
	#prueba=[]
    pintegracion=len(path_SDV4)
    for k in range(pintegracion):
		#la G en cada punto de integracion del criterio tensional
        GtotT=path_SDV4[k].data
		#la Gc del criterio tensional
        GcT=path_SDV5[k].data
        if GcT!=0:
            fc=sqrt(GtotT/GcT)
        else:
            fc=0
        puntosintdamT.append(fc)
# 	    prueba.append([fc,GtotT,GcT])

    puntosintdamT.sort(key=lambda puntosintdamT:puntosintdamT, reverse=True)
	 #tomo la del ultimo punto de integracion del elemento para que rompa entero el
	 #elemento si no lo multiplico por nada mas:
    nPI=0 #4
    if puntosintdamT[nPI]==0:
        new_load=old_load
    else:
        new_load=old_load*puntosintdamT[nPI]
    		
	#---------------------------------------------------
	#escribir el fichero de datos
	#--------------------------------------------------
	# fich_carga= open(load_file,'w')
	# fich_carga.write(str(new_load))
	# fich_carga.write('\n')
	# fich_carga.close()

	#Guzman: Sacar argumentos en fichero log.txt
    # with open('log.txt', 'w') as f:
 		 # for myargument in argv:
    #      		 # f.write(str(myargument))
    #      		 f.write('\n')
    #      		 f.write('\n')
    #      		 f.write('\n')
    #      		 f.write(str(puntosintdamT[0]))
    #      		 f.write('\n')
    #      		 f.write(str(old_load))
    #      		 f.write('\n')
    #      		 f.write(str(len(path_SDV4)))
    #      		 f.write('\n')
    #      		 f.write(str(new_load))
    # f.close
    odb.close()
    return new_load, sdv13max_value