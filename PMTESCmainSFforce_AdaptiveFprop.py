# ********************************************************************************
# SCRIPT: PMTESC.PY
# Autor: Mar
# Modificaciones: Jose M. Pimentel
# Notas: no poner ninguna tilde en los comentarios
# ********************************************************************************
#%%

#---------------------------------------------------
#Importacion modulos
from os import chdir, path, mkdir, getcwd, remove
import os
from shutil import rmtree, move,copy
from glob import glob
from subprocess import call
#from string import replace
import datetime
import collections
import math
import numpy as np
import sys
# Redirect stdout to the command prompt
sys.stdout = sys.__stdout__

#nuestros modulos
import PMTESC
import PMTESCcriTen_carga
import PMTESCcriTen
import PMTESCcritEne
import PMTESCsalDatos
import PMTESC_dicc
import CrackedInterSigmarr

from abaqus import *
from abaqusConstants import *
from odbAccess import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

#---------------------------------------------------
# datos para trabajar (LEER de inputFFMLEBIM_adaptivef.txt)
#---------------------------------------------------
fileINPUT = open('inputFFMLEBIM_adaptivef.txt','r')

flag = fileINPUT.readline()
name_INP = fileINPUT.readline().rstrip()

#flag = fileINPUT.readline()
#namefolder = fileINPUT.readline().rstrip() #quitar

flag = fileINPUT.readline()
name_UMAT = fileINPUT.readline().rstrip()

flag = fileINPUT.readline()
num_iteraciones = int(fileINPUT.readline().rstrip())

flag = fileINPUT.readline()
numiter = int(fileINPUT.readline().rstrip())
#tolerance for termination criteria:
flag = fileINPUT.readline()
toler = float(fileINPUT.readline().rstrip())

flag = fileINPUT.readline()
setnodeInt = fileINPUT.readline().rstrip()

#flag = fileINPUT.readline()
#sent_sust = fileINPUT.readline().rstrip()

flag = fileINPUT.readline()
carga = float(fileINPUT.readline().rstrip())

#flag = fileINPUT.readline()
#parametro = fileINPUT.readline().rstrip()

flag = fileINPUT.readline()
incre = float(fileINPUT.readline().rstrip())

flag = fileINPUT.readline()
salidaDatos = fileINPUT.readline().rstrip()

flag = fileINPUT.readline()
almacenarOdbs = int(fileINPUT.readline().rstrip())
#control en carga=1, control desplazamiento=0. 
flag = fileINPUT.readline()
control = int(fileINPUT.readline().rstrip())
#factor por el que multiplicar la primera carga de rotura de LEBIM para que no rompa. aprox 0.9
flag = fileINPUT.readline()
factorcarga = float(fileINPUT.readline().rstrip())
#este factor de carga se multiplica por la carga que romperia el primer PI por LEBIM puro
#por el criterio tensional
flag = fileINPUT.readline()
mstep = int(fileINPUT.readline().rstrip())
#los m pasos que vamos a imponer como maximo
#este int es 1 si quiero aumentar la carga en cada k, o 0 si empiezo desde 0 (como LEBIM)
flag = fileINPUT.readline()
aumentocarga = int(fileINPUT.readline().rstrip())
#numero de condiciones de contorno en desplazamiento a cambiar 
flag = fileINPUT.readline()
nBCD = int(fileINPUT.readline().rstrip())
#el orden, empezando por 1, de las CC en desplzamiento que queremos cambiar
flag = fileINPUT.readline()
flag = fileINPUT.readline()
flag = fileINPUT.readline()
oBCD=[]
fBCD=[]
for BC in range(nBCD):
    oBCD.append(fileINPUT.readline().rstrip())
    fBCD.append(float(fileINPUT.readline().rstrip()))
# factor multiplicador de dist. aleatoria
flag = fileINPUT.readline()
p = float(fileINPUT.readline().rstrip())
fileINPUT.close()

#%%

#-------------------------------------------------------------------------------------------------------------
# Orden para indicar cual es el directorio actual de trabajo (para poder usar en cluster)
actual_directory = getcwd()
start = datetime.datetime.now()
#---------------------------------------------------
# NOMBRES DE NUESTROS ARCHIVOS DE TRABAJO (MODIFICAR)
#---------------------------------------------------
# criTen_carga = 'PMTESCcriTen_ABQ_carga.py'
# criTen = 'PMTESCcriTen_ABQ2.py'
# criterioEne='PMTESCcritEne_ABQ2.py'
#if control==0:
#    #este salida de datos es para DCB con control en desplazamiento
#    #pero puede servis de guia para otro caso con control en desplazamiento
#    salidaDatos='salDatos_ABQ_Cdespla' + '.py'
#else:
#    #este salida de datos es para DCB con control en carga
#    #pero puede servis de guia para otro caso con control en carga
#    salidaDatos='salDatos_ABQ_Ccarga' + '.py'
working_directory=actual_directory
archivo_LEBIM=working_directory+'/datos_procesar.txt'
working_directory_FFM=working_directory+'/FFM_optimizada01'
working_directory_Ten=working_directory_FFM+'/criterioTen'
working_directory_Ene=working_directory_FFM+'/criterioEne'
working_directory_odbs=working_directory_FFM+'/odbS'
salida_datos1=working_directory_FFM+'/archivo_carga.txt'
salida_datos3=working_directory_FFM+'/archivo_salida.txt'
archivo_control=working_directory_FFM+'/archivo_control.txt'
archivo_energias=working_directory_FFM+'/archivo_energias.txt'
#El archivo de control es para saber que esta dagnando el codigo
#El archivo de energia es para graficar las energias en cada paso
#Ninguno de los dos archivos cambia nada del codigo. Son para el usuario
#En estos archivos, se debe tener en cuenta que los elementos dagnados 
#segun el CE despues del paso ii) del paso j, es lo que propone la minimizacion 
#de la energia segun el dagno del paso i) del paso j. Por tanto, al final de
#ese paso j, la energia calculada de Abaqus es con los elementos dagnados 
#del comienzo de ese paso j (en i), es decir, el dagno propuesto en el 
#paso ii) de j-1. Y si j=0, es el dagno inicial de ese n.
#Por tanto, la energia del dagno se actualiza en el siguiente paso j.


#%%
#-------------------------------------------------------------------------------------------------------------
# EMPIEZA EL PROGRAMA ABRIENDO CARPETAS
#-------------------------------------------------------------------------------------------------------------
call('cls',shell=True)
chdir(working_directory)
## Borrar carpeta de FFM si esxiste
if (path.exists(working_directory_FFM) == True):
    rmtree(working_directory_FFM)
##borrando archivos de otros calculos
list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
               '*.mtx','*.pes','*.par','*.pmg','*.odb','*.ipm','*.pyc','datos_procesar.txt')
PMTESC.borrar_archivos(list_delete)
   
# creando todas las carpetas  
mkdir(working_directory_FFM)
mkdir(working_directory_Ten)
mkdir(working_directory_Ene)
mkdir(working_directory_odbs)
   
## creando todos los archivos de salida 
data_file1=open(salida_datos1,'w')
data_file2=open(salida_datos3,'w')
data_file1.close()
data_file2.close()

## Por si quiero empezar con una zona danana dentro de la interfase LEBIM
##debo dejar en el working_directory el archivo datos_procesar.txt con los 
##elementos dagnanos
if (path.exists('datos_procesarinicio.txt') == True):
    iniciodano= (working_directory+ '/datos_procesarinicio.txt')
    move(iniciodano,working_directory_FFM)
    origen= (working_directory_FFM+ '/datos_procesarinicio.txt')
    destino= (working_directory+ '/datos_procesar.txt')
    PMTESC.cambiar_archivos(origen,destino)
else:
    fileLEBIM=open(archivo_LEBIM,'w')
    fileLEBIM.close()

##creando copias del inp y de la UMAT
#name_INP_P=name_INP+'_P'  #quitar
#copy (name_INP+'.inp',name_INP_P+'.inp')  #quitar
eumat = 'F_'+name_UMAT
copy (name_UMAT,eumat)

##cambiando directorio de la UMAT
vble_a_borrar, namefolder = path.split(getcwd())
PMTESC.cambiar_cadena(name_UMAT,eumat,'NAMEFOLDER',namefolder)

with open('elemCE_resumen.txt', 'w') as f:
    f.write('')

#%%    
#-------------------------------------------------------------------------------------------------------------
#COMENZAMOS MI BUCLE CON LOS STEP
#-------------------------------------------------------------------------------------------------------------
#inicializo las variables que almacenan el dagno para saber al incio si aumentamos la carga o no
#damageTen es para almacenar la lista de elementos dagnados por criterio tensional
damageTen=[]
#damageM almacena el dagno N con minima energia para cada M. Lo hace a traves de la variable damageN
#definida en el bucle j
damageM=[]
filedamii_lst=[]
kdownf=0.975; #factor de carga antes de la primera rotura de un paso kmni 

inp_file_path = actual_directory+'/'+name_INP+'.inp'
with open(inp_file_path, 'r') as inp_file:
    inp_lines = inp_file.readlines()
# llamada de fcn que retorna la resistencia de la interfase del fichero inp:
first_param, mu_const = PMTESCcriTen_carga.sigmac_parameter(inp_lines)
if first_param is not None:
    print('Interface critical strength; brittleness parameter: ',first_param, mu_const)
    print('Bisection algorithm limit tolerance: {:.3e}'.format(toler))
# Ratio of y-axis load and the x-axis load
tc2t = float(0)
m=0
iter_count = 1 #bisection iteration counter
loadfile_it=0.0 #bisection adaptive load
# 
eps0=1.0
kfrac_list = [] #Empty list that holds step value and broken interface elements
k=0
incre0 = incre
#fichero de energia:
#-------------------------------------------------------
def energy_file(file_name,pasok,pasom,pason,pasoj,newload,damageTen,listaene,thetad,gtotalt,sigmaxinf,deltaR,deltaPI,thetad2,gtr,gtl,PI_0,U1disp):
    control_file=open(file_name,'a')
    #escribimos k m n j
    control_file.write('%d\t %d\t %d\t %d\t'%(pasok,pasom,pason,pasoj))
    #escribimos el numero de elementos que se rompen por criterio tensional
    numeleten=len(damageTen)
    control_file.write('%d\t'%(numeleten))
    #escribimos el numero de elementos que se rompen por criterio energetico
    NelemtsD=listaene[1]
    control_file.write('%d\t'%(NelemtsD))
    #escribimos la carga o el desplazamiento impuesto
    control_file.write(str(newload)+'\t')
    # remote applied stress
    control_file.write(str(sigmaxinf)+'\t')
    # matrix U1 displacement at y=0 of right edge
    control_file.write(str(U1disp)+'\t')
    #escribimos la energia interna y la energia interna mas disipada (total)
    enerinterna=str(listaene[5])
    enerTotal=str(listaene[0])
    control_file.write(enerinterna+'\t')
    control_file.write(enerTotal+'\t') 
    control_file.write(thetad+'\t')
    control_file.write(thetad2+'\t')
    control_file.write(str(deltaPI)+'\t')
    control_file.write(str(deltaR)+'\t')
    control_file.write(str(gtr)+'\t')
    control_file.write(str(gtl)+'\t')
    control_file.write(str(deltaPI+deltaR)+'\t')
    control_file.write(str(PI_0)+'\n')
    control_file.close()
    #se debe tener en cuenta que los elementos dagnados segun el CE despues del 
    #paso ii del paso j, es lo que propone la minimizacion de la energia segun el dagno
    #pero al final de ese paso j la energia calculada es con los elementos
    #dagnados del paso j anterior
    #el dagno se actualiza en el siguiente paso 
    
# Steps, donde se ejecuta el CT
while iter_count <= numiter:
    
    if k==0:
        name_files = name_INP + '_para_carga'+ '_' + 'k' + str(k+1)
        # Read the model
        mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
        myModel = mdb.models[name_INP]
        myAssembly = myModel.rootAssembly
        # set1 = myAssembly.sets['RP1']
        # set2 = myAssembly.sets['RP2']
        region = myAssembly.surfaces['S_SURF-2']
        region2 = myAssembly.surfaces['S_SURF-3']
        # regiontop = myAssembly.surfaces['T_SURF']
        # Apply loads (as boundary conditions)
        # **Reminder: Abaqus python reads surface sets typed in CAPITAL letters only**
        for BC in range(nBCD):
            if BC==0:
                mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                    region=region, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*carga, 
                    amplitude=UNSET)
            elif BC==1:   
                mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                    region=region2, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*carga, 
                    amplitude=UNSET)
            elif BC==2:    
                mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                    # region=regiontop, distributionType=UNIFORM, field='', magnitude=tc2t*fBCD[BC]*carga, 
                    amplitude=UNSET)
        # Create the job
        mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=SINGLE, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
        # Run the job
        mdb.jobs[name_files].submit(consistencyChecking=OFF)

        # Do not return control till job is finished running
        mdb.jobs[name_files].waitForCompletion()
        

        # Tension criteria and define new load
        loadfile, sigma1 = PMTESCcriTen_carga.PMTESCcriTen_carga(name_files, working_directory, carga, setnodeInt)
        newload = factorcarga * loadfile
        
        if sigma1 < first_param:
            newload=(first_param/sigma1)*kdownf*loadfile*incre
            print('sigma1 < sigmac', newload)
        elif sigma1 > first_param:
            newload=(first_param/sigma1)*(kdownf*loadfile)*incre
            print('sigma1 > sigmac', newload)
            
        # diccionarios para el crierio tensional y energetico
        dicc_NeL_T, dicc_NeL_E, Asigma_new = PMTESC_dicc.PMTESC_dicc(name_files, working_directory, setnodeInt)
        print(np.array(Asigma_new))
        loadfile = newload + incre0
        
    if k!=0: #si k es distinto de 0
        if aumentocarga==1: #si seguimos aumentando la carga
            if sigma1 < first_param and k<=2:
                newload=(first_param/sigma1)*kdownf*newload + incre0
                loadfile = newload
                print('sigma1 < first_param, variable loadfile is: {}'.format(loadfile))
            if k==1:
                newload = newload + incre0
                loadfile = newload
                print('Step k=1, variable loadfile is: {}'.format(loadfile))
            if k>1 and iter_count<=numiter:
                if damageTen!=None and (loadfile_it is None or len(damageTen)==0):
                    # loadfile = newload
                    print('Variable loadfile_it is :{}'.format(loadfile))
                else: 
                    # newload = loadfile_it; loadfile = newload
                    print('Variable loadfile is: {}'.format(loadfile))
                    
            if k>1 and (eps0 < toler) and iter_count>numiter:
                newload = loadfile_it
                os._exit(0)
            
        else: #si empezamos en cada k desde 0 para un snap-back
            if len(damageTen)==0 or damageM[m][1]==0: #realmente esto se puede poner arriba con un triple or
                newload = newload + incre
            else:
                # import sys
                # print('\a')
                # from ctypes import windll
                # if not windll.powrprof.SetSuspendState(False, False, False):
                #     print("No se ha podido suspender el sistema.")
                # sys.exit()
                name_files = name_INP + '_para_carga'+ '_' + 'k' + str(k+1)
                # Read the model
                mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
                myModel = mdb.models[name_INP]
                myAssembly = myModel.rootAssembly
                # set1 = myAssembly.sets['RP1']
                # set2 = myAssembly.sets['RP2']
                region = myAssembly.surfaces['S_SURF-2']
                region2 = myAssembly.surfaces['S_SURF-3']
                # regiontop = myAssembly.surfaces['T_SURF']
                # Apply loads (as boundary conditions)
                ######################## NO SE QUE CARGA UTILIZAR AQUI!!!!!!
                ######################## carga or newload or what?              
                for BC in range(nBCD):
                    #mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*carga)
                    if BC==0:
                        mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                            region=region, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*newload, #originalmente fBCD[BC]*carga
                            amplitude=UNSET)
                    elif BC==1:    
                        mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                            region=region2, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*newload, 
                            amplitude=UNSET)
                    elif BC==2:    
                        mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                            region=regiontop, distributionType=UNIFORM, field='', magnitude=tc2t*fBCD[BC]*newload, 
                            amplitude=UNSET)
                # Create the job
                mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=SINGLE, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
                # Run the job
                mdb.jobs[name_files].submit(consistencyChecking=OFF)

                # Do not return control till job is finished running
                mdb.jobs[name_files].waitForCompletion()
                #si quiero revisar el inp del job no borrarlo:
                remove(name_files+'.inp')

                # Tension criteria and new load
                loadfile, sigma1 = PMTESCcriTen_carga.PMTESCcriTen_carga(name_files, working_directory, newload, setnodeInt)
                newload = factorcarga * loadfile
    # 
          
    # inicializar las variables que almacenan el dagno
    damageTen=[]
    damageM=[]
    PMTESC.write_load_file(salida_datos1,loadfile)
    print('Applied load for step k{}_m{}N: {}'.format(str(k+1), str(m+1), loadfile))
    
    for m in range(mstep):
        if m==0:
            name_files = name_INP + '_' + 'k' + str(k+1)+ 'm' + str(m+1)+ 'n0'+ 'j0'
            # Read the model
            mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
            myModel = mdb.models[name_INP]
            myAssembly = myModel.rootAssembly
            # set1 = myAssembly.sets['RP1']
            # set2 = myAssembly.sets['RP2']
            region = myAssembly.surfaces['S_SURF-2']
            region2 = myAssembly.surfaces['S_SURF-3']
            # regiontop = myAssembly.surfaces['T_SURF']
            # Apply loads (as boundary conditions)
            for BC in range(nBCD):
                #mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*loadfile)            
                if BC==0:
                    mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                        region=region, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*loadfile, 
                        amplitude=UNSET)
                elif BC==1:    
                    mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                        region=region2, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*loadfile,
                        amplitude=UNSET)
                elif BC==2:    
                    mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                        region=regiontop, distributionType=UNIFORM, field='', magnitude=tc2t*fBCD[BC]*loadfile, 
                        amplitude=UNSET)
            # Create the job
            mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=SINGLE, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
            # Run the job
            mdb.jobs[name_files].submit(consistencyChecking=OFF)

            # Do not return control till job is finished running
            mdb.jobs[name_files].waitForCompletion()
            #si quiero revisar el inp del job no borrarlo:
            # remove(name_files+'.inp')
            
            #aqui evaluo el criterio tensional. Es el unico lugar donde lo hago: criTen_ABQ       
            damageTen, Nsnumber, Gclst=PMTESCcriTen.PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T)
            # damageTen, Nsnumber=PMTESCcriTen.PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T)
            # EVALUATE THE POTENTIAL ENERGY (PI) FOR KM0:
            eleDamagei, enerHtotal, thet1=PMTESCcritEne.PMTESCcritEne(name_files, working_directory, setnodeInt, control, damageTen, dicc_NeL_E, str(0))
            PIkm0=enerHtotal
            #call('abaqus python' + ' ' + criTen + ' ' + name_files + ' ' + working_directory.replace(' ','*')\
            #     + ' '+setnodeInt,shell=True)
            factorcoord,GtT,sigma_inf,theta2,gt1,gt2,U1matrx=PMTESCsalDatos.PMTESCsalDatos_SFLoad(name_files, working_directory, salida_datos3, str(k+1), str(m+1), str(0), str(0), str(0), 0, filedamii_lst, Gclst)
	        #--------------------------------------------------------------------------------------
            #si no hay elementos dananos segun el CT salgo del bucle m:
            if len(damageTen)==0:
                kfrac_list.append([0.0, loadfile, k+1, m+1, 0, 0, 0])
                PMTESC.energy_file_CTO(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,factorcoord,GtT,sigma_inf)
                with open('elemCE_resumen.txt', 'a') as f:
                    f.write('%e %d %d %d %d %d \n' % (0.0, k+1, m+1, 0, 0, 0))
                if k+1==1:
                    loadfile = loadfile + abs(incre)
                if k>=1: 
                    indices = [i for i, row in enumerate(kfrac_list) if row[0] == 0.0]
                    last_idx = indices[-1] if indices else None
                    indices_crack = [i for i, row in enumerate(kfrac_list) if row[0] < 0.0]
                    last_idxcrack = indices_crack[-1] if indices_crack else None
                    if last_idxcrack!=None:
                        print('Last step with failure load: {}'.format(kfrac_list[last_idxcrack][1]))
                        loadfile = loadfile + (0.5 * (kfrac_list[last_idxcrack][1] - loadfile))
                    else:
                        Fkm1 = kfrac_list[last_idx][1]
                        incre = abs(loadfile - Fkm1)
                        print('Last step without failure, load: {}'.format(kfrac_list[last_idx][1]))
                        if incre == 0.0: 
                            loadfile = loadfile + (0.5 * loadfile)
                        else: loadfile = loadfile + (0.5 * kfrac_list[last_idx][1])
                print('Load NOT high enough to fulfill the strength condition: {}'.format(loadfile))
                break
            
            #--------------------------------------------------------------------------------------
            # si m!=0 el name_file es el elegido al final del paso m anterior
            print("{:.8e}".format(loadfile),"{:.8e}".format(U1matrx))
        elif m!=0:
            damageTen, Nsnumber, Gclst=PMTESCcriTen.PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T)
            # damageTen, Nsnumber=PMTESCcriTen.PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T)
            # EVALUATE THE POTENTIAL ENERGY (PI) FOR KM0:
            eleDamagei, enerHtotal, thet1=PMTESCcritEne.PMTESCcritEne(name_files, working_directory, setnodeInt, control, damageTen, dicc_NeL_E, str(0))
            PIkm0=enerHtotal
            #call('abaqus python' + ' ' + criTen + ' ' + name_files + ' ' + working_directory.replace(' ','*')\
            #     + ' '+setnodeInt,shell=True)
            fileLEBIMnp=np.loadtxt(working_directory+'/datos_procesar.txt', dtype=int)
            fileLEBIMlst=list(fileLEBIMnp)
            factorcoord,GtT,sigma_inf,theta2,gt1,gt2,U1matrx=PMTESCsalDatos.PMTESCsalDatos_SFLoad(name_files, working_directory, salida_datos3, str(k+1), str(m+1), str(0), str(0), 0, 0, fileLEBIMlst, Gclst)
            print("{:.8e}".format(loadfile),"{:.8e}".format(U1matrx))
            
        # Eliminar archivos innecesarios 
        list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                       '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
        PMTESC.borrar_archivos(list_delete)
        # saco los posibles elementos a danar en el criterio tensional
        #damageTen=PMTESC.get_list_file(working_directory_Ten+'/damageTen.txt')
        # escribo en ele archivo control los posibles dananos en el criterio tensional
        PMTESC.crontol_file_paso(archivo_control,damageTen,k+1,m+1)
        
        #--------------------------------------------------------------------------------------
        #si no hay elementos dananos segun el CT salgo del bucle m:
        # Load bisection algorithm for steps where Asigma set is empty:
        if len(damageTen)==0 and m!=0:
            PMTESC.energy_file_CTO(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,factorcoord,GtT,sigma_inf)
            if k+1==1:
                newload = loadfile + abs(incre)
            else:
                loadfile = loadfile_it + abs(incre)
                if incre==0.0: loadfile = loadfile_it + (0.5 * loadfile_it)
                
            print('Load NOT high enough to fulfill the strength condition, m-substep: {}'.format(m))
            break
        
        #--------------------------------------------------------------------------------------
        elif len(damageTen)!=0:
        #si hay elementos dananos segun el CT, empezamos la minimizacion
            #------------------------------------------------------------
            # LOS POSIBLES INICIOS N del criterio energetico. Esto tendria que cambiar
            #------------------------------------------------------------
            Ninicios=Nsnumber
            damageN=[]
            
            #####aqui vendria la funcion para elegir los posibles N
            ####ahora mismo esta dentro del script criTen = 'PMTESCcriTen.py'

            for n in range(Ninicios):
                #cambia el archivo de datos_procesar.txt para romper en abaqus
                origen= working_directory_Ten+ '/damageN'+str(n+1)+'.txt'
                destino= archivo_LEBIM
                PMTESC.cambiar_archivos(origen,destino)
                #------------------------------------------------------------
                # optimizo el criterio energetico con cada inicio n
                #------------------------------------------------------------
                #inicializando variables
                ene_damii=[]
                error=0             
                for j in range(50): #aqui poner un numero muy alto o un while
                    ##paso i
                    #minimizacion del campo de desplazamiento por FEM
                    name_files = name_INP + '_' + 'k' + str(k+1)+ 'm' + str(m+1)+ 'n' +str(n+1)+ 'j' + str(j+1)
                    ############ ABAQUS JOB
                    chdir(working_directory)
                  
                    # Read the model
                    mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
                    myModel = mdb.models[name_INP]
                    myAssembly = myModel.rootAssembly
                    # set1 = myAssembly.sets['RP1']
                    # set2 = myAssembly.sets['RP2']
                    region = myAssembly.surfaces['S_SURF-2']
                    region2 = myAssembly.surfaces['S_SURF-3']
                    # regiontop = myAssembly.surfaces['T_SURF']
                    # Apply loads (as boundary conditions)
                    
                    for BC in range(nBCD): #numero de condiciones de contorno del problema
                        #mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*loadfile)
                        if BC==0:
                            mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                                region=region, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*loadfile, 
                                amplitude=UNSET)
                        elif BC==1:    
                            mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                                region=region2, distributionType=UNIFORM, field='', magnitude=fBCD[BC]*loadfile, 
                                amplitude=UNSET)
                        elif BC==2:    
                            mdb.models[name_INP].Pressure(name='Load-'+oBCD[BC], createStepName='Step-1', 
                                region=regiontop, distributionType=UNIFORM, field='', magnitude=tc2t*fBCD[BC]*loadfile, 
                                amplitude=UNSET)
                    # Create the job
                    mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=FULL, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
                    # Run the job
                    mdb.jobs[name_files].submit(consistencyChecking=OFF)

                    # Do not return control till job is finished running
                    mdb.jobs[name_files].waitForCompletion()
                    #si quiero revisar el inp del job no borrarlo:
                    remove(name_files+'.inp')
                    # print("{:.10e}".format(loadfile))
                    
		            ############ ENERGY CRITERIA
                    eleDamagei, enerHtotal, thet1=PMTESCcritEne.PMTESCcritEne(name_files, working_directory, setnodeInt, control, damageTen, dicc_NeL_E, n+1)
   					#enerHtotal del paso i. La disipada se calcula en el bucle for nEd in eleDamagei
                    
                    #criEnergy.criEnergy(name_files, working_directory, working_directory_Ene, setnodeInt, str(k), str(control))		
                    #el archivo archivoEneH_paso_i es generado justo en la linea anterior con criterioEne desde abaqus
                    #enerHtotal=PMTESC.get_list_file(working_directory_Ene+'/archivoEneH_paso_i.txt')[0][0]
					
                    #la energia disipada se calcula desde fuera de abaqus porque la energia critica por elemento se hace con 
                    #la psi del criterio tensional, por eso la GcE se calcula con el criterio tensional. Se hace con la
                    #siguiente funcion:
                    ##eleDamagei:NeG(lista), NeL(lista), GelemReal(dicc), GelemUndamge(dicc), GelemDamge(dicc), GcE(lista), damage(dicc)
                    #eleDamagei=PMTESC.get_list_file2(working_directory_Ene+'/archivoEneElements_paso_i.txt')
                    
                    
                    ener_disi=0.0
                    for nEd in eleDamagei:
						#la energia disipada se calcula desde fuera de abaqus porque la energia critica por elemento se hace con 
					    #la psi del criterio tensional, por eso la GcE se calcula con el criterio tensional. 
						#la minimizazion del dagno es: zG+(z-1)GcE
					    #suponiendo z=0 dagnado y z=1 no dagnado
                        disipadaElem=nEd[5]*(1.0-nEd[6])
                        # print('Element deltaR={}, element damage_var={}'.format(nEd[5],nEd[6]))
                        ener_disi=ener_disi+disipadaElem #delta_R
                    print('Length of the eleDamagei array: {}'.format(len(eleDamagei)))
                    print('Energy dissipated by fracture: {} N-micrometer'.format(ener_disi))    
                    #-----------------------------------------------------------    
                    ##paso ii. Minimizacion de la funcion dagno       
                    #-----------------------------------------------------------
                    #copiamos los PI rotos del los pasos anteriores (k-1) para despues
                    #seguir anadiendo los de este paso j. En cada paso j este archivo se reescribe.
                    #cambia el archivo de datos_procesar.txt para romper en abaqus
                    origen= working_directory_Ten+ '/damageKm1.txt'
                    destino= working_directory_Ene+ '/damage_paso_ii.txt'
                    PMTESC.cambiar_archivos(origen,destino)
                    file_damageii=open(working_directory_Ene+'/damage_paso_ii.txt','a')
                    #-----------------------------------------------------------
                    eleDamage=[] #lista de elementos rotos despues de esta funcion
                    locelem=[]
                    #estas dos siguientes es solo para el archivo de control:
                    Gc_eleme=[] #lista de la GcE por elementos posibles a romper por el CT
                    G_eleme=[] #lista de la Gc por elementos posibles a romper por el CT
                    #-----------------------------------------------------------
                    #nos metemos en el blucle de los posibles elementos a romper desde el CT
                    #para comparar elemento por elemento
                    for nE in eleDamagei:
                        #energia critica por elemento
                        NeG=int(nE[0])          
                        enerEUndamage=nE[3]
                        enerEDamage=nE[4]
                        enerCrElem=nE[5]
                        #para control:
                        Gc_eleme.append(enerCrElem+enerEDamage)
                        G_eleme.append(enerEUndamage)
                        #comparacion: CRITERIO INCREMENTAL DE GRIFFITH
                        if enerEUndamage-enerEDamage>=enerCrElem:
                            eleDamage.append(NeG)
                            locelem.append(nE[-1])
                            for pi in range(1,5):
                                file_damageii.write('%d %d %d %d\n' % (pi , NeG, 0.0, nE[-1]))
                    file_damageii.close()
                    filedamii_np=np.loadtxt(working_directory_Ene+'/damage_paso_ii.txt', dtype=int)
                    filedamii_lst=list(filedamii_np)
                    #-----------------------------------------------------------
                    #-----------------------------------------------------------   
                    #almacenamiento de datos
                    #POSSIBLE FUNCTION CALL, TO OBTAIN INTERFACE PARAMETERS IN EACH J-th AMA Iteration:
                    factorcoord,GtT,sigma_inf,theta2,gt1,gt2,U1matrx=PMTESCsalDatos.PMTESCsalDatos_SFLoad(name_files, working_directory, salida_datos3, str(k+1), str(m+1), str(len(eleDamage)), str(enerHtotal), str(len(damageTen)), n+1, filedamii_lst, Gclst)
                                        
                    if m>=0 and j>=0:
                        # Evaluate Delta_PI
                        deltaPI=enerHtotal-PIkm0
                    ene_damii.append([enerHtotal+ener_disi, len(eleDamage), eleDamage, G_eleme, Gc_eleme, enerHtotal, ener_disi, deltaPI+ener_disi, locelem])
                    print(enerHtotal, deltaPI+ener_disi)
                    PMTESC.crontol_file(archivo_control,ene_damii[j],n+1,j+1)
                    energy_file(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                    
                    if j!=0:
                        #if abs(ene_damii[j-1][1]-ene_damii[j][1])==error:#deberia cambiarlo por el dano de cada elemento
                        if(collections.Counter(ene_damii[j-1][2])==collections.Counter(ene_damii[j][2])):
                            damageN.append([ene_damii[j][0],ene_damii[j][1],ene_damii[j][2],n+1,j+1,enerHtotal,ene_damii[j][7],ene_damii[j][-1]])
                            #damageN[0:enerHtotal+ener_disi, 1:suma de elementos dagnado, 2:lista de NeG de elementos dagnados,  
                            #3:lista de energia por de elemento dagnados, 4:lista de energia critica por de elemento dagnados
                            #5:enerHtotal]
                            break
                    #--------------------------------------------------------------------------------------
                    #para intentar evitar que se meta en un bucle
                    contador=ene_damii.count(ene_damii[j])
                    if contador!=1:
                        print('peligro bucle j=', j)
                        exit
                    #--------------------------------------------------------------------------------------                   
                    origen=working_directory_Ene+ '/damage_paso_ii.txt'
                    destino=archivo_LEBIM
                    PMTESC.cambiar_archivos(origen,destino)                                   
                    #borrando archivos. Poner o quitar odb dependiendo de lo que se quiera
                    # list_delete = ('abaqus.*', '*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com'\
                    #                , '*.log', '*.jnl','*.pes','*.par','*.pmg','*.mtx','*.ipm')
                    list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                                   '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
                    #list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com','*.jnl','*.pes','*.par','*.pmg','*.mtx')
                    
                    PMTESC.borrar_archivos(list_delete)
                    
            #------------------------------------------------------------
            #comparacion de las N y tomar la de menor energia
            #------------------------------------------------------------
            damageN.sort(key=lambda damageN:damageN[0]) # correct
            # redundant reverse key:
            # damageN.sort(key=lambda damageN:damageN[6],reverse=False) 
            origen= working_directory_Ten+ '/damageKm1.txt'
            destino=archivo_LEBIM
            enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6,7])
            kstepindx=enerfilenp[:,0]==k
            fkstepindx=enerfilenp[:,0]==k+1
            Fkm1 = enerfilenp[kstepindx,6][0]
            Fk = loadfile
            
            #Guardo en archivo para postprocesar
            kfrac_list.append([damageN[0][6], loadfile, k+1, m+1, damageN[0][3], damageN[0][4], damageN[0][1]])
            # kfrac list must be populated also for steps where damageTen array is empty
            with open('elemCE_resumen.txt', 'a') as f:
                f.write('%e %d %d %d %d %d \n' % (damageN[0][6], k+1, m+1, damageN[0][3], damageN[0][4], damageN[0][1]))
            # with open('elemCE_resumen.txt', 'r') as f:
            #     for line in f:
            #         line = line.split()
            #         if line:
            #             line = [i for i in line]
            #             kfrac_list.append(line)
            
            incre=abs(Fk-Fkm1)
            eps0=abs(incre)/Fk 
            print(np.array(kfrac_list))
            indices = [i for i, row in enumerate(kfrac_list) if row[-1] == 0]
            last_idx = indices[-1] if indices else None
            indices_crack = [i for i, row in enumerate(kfrac_list) if row[-1] > 0]
            last_idxcrack = indices_crack[-1] if indices_crack else None
            
            if damageN[0][1]>0 and damageN[0][6]<float(0) and k>=1 and iter_count<=numiter and m==0 and (incre/Fk)>toler:
                # damageN[:][1]=0
                if last_idx!=None:
                    Fk = loadfile
                    Fkm1 = kfrac_list[last_idx][1]
                    incre = abs(Fk - Fkm1)
                    loadfile_it = Fk - (0.5 * incre)
                elif last_idx==None:
                    Fk = loadfile
                    loadfile_it = Fk - (0.5 * Fk)
                print(loadfile_it, damageN[0][1], iter_count, damageN[0][6])
                iter_count+=1
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG, NeLoc in zip(damageN[0][2], damageN[0][-1]):
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %d %d\n' % (pi , NeG, 1.0, NeLoc))
                fileLEBIM.close()
                fileLEBIMnp=np.loadtxt(working_directory+'/datos_procesar.txt', dtype=int)
                fileLEBIMlst=list(fileLEBIMnp)
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                energy_file(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                damageM.append(damageN[0])
                # break #termina el actual bucle-m
                                
            #si no hay ningun elemento danano, salgo del bucle
            if damageN[0][1]==0 and damageN[0][6]>=float(0) and k>=1 and iter_count<=numiter and m==0:
                
                if last_idxcrack!=None:
                    Fkm1 = kfrac_list[last_idxcrack][1]
                    incre = abs(Fk-Fkm1)
                    if incre == 0.0: 
                        incre = 0.5 * abs(Fk)
                        loadfile_it = Fk + incre
                    else:
                        loadfile_it = loadfile + abs(0.5*incre)
                # 
                else:
                    if incre == 0.0 or incre is None:
                        incre = 0.5 * abs(loadfile)
                        loadfile_it = loadfile + incre
                    else:
                        loadfile_it = loadfile + (1.25*incre)
                print(loadfile_it, damageN[0][1], iter_count, damageN[0][6])
                iter_count+=1
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG, NeLoc in zip(damageN[0][2], damageN[0][-1]):
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %d %d\n' % (pi , NeG, 1.0, NeLoc))
                fileLEBIM.close()
                fileLEBIMnp=np.loadtxt(working_directory+'/datos_procesar.txt', dtype=int)
                fileLEBIMlst=list(fileLEBIMnp)
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                energy_file(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                damageM.append(damageN[0])
                # break
            
            if damageN[0][1]!=0 and damageN[0][6]<float(0) and k>=1 and m>=0 and iter_count<=numiter and (abs(incre)/Fk)<toler:
                
                print(loadfile, damageN[0][1], iter_count, damageN[0][6])
                # 
                loadfile_it = loadfile
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG, NeLoc in zip(damageN[0][2], damageN[0][-1]):
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %d %d\n' % (pi , NeG, 0.0, NeLoc))
                fileLEBIM.close()
                fileLEBIMnp=np.loadtxt(working_directory+'/datos_procesar.txt', dtype=int)
                fileLEBIMlst=list(fileLEBIMnp)
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                energy_file(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                damageM.append(damageN[0])    
                # os._exit(0)
                
            if damageN[0][1]!=0 and damageN[0][6]<float(0) and k>=1 and iter_count>numiter and m==0:
                print(loadfile, damageN[0][1], iter_count)
                # iter_count+=1
                # incre=(loadfile-Fkm1)/2
                loadfile_it = loadfile - incre/2
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG, NeLoc in zip(damageN[0][2], damageN[0][-1]):
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %d %d\n' % (pi , NeG, 0.0, NeLoc))
                fileLEBIM.close()
                fileLEBIMnp=np.loadtxt(working_directory+'/datos_procesar.txt', dtype=int)
                fileLEBIMlst=list(fileLEBIMnp)
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                energy_file(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                damageM.append(damageN[0])
                os._exit(0)  # Exit with a status code (1 indicates an error)
            
            #------------------------------------------------------------
            #abro el odb con menor energia y saco los datos que quiera graficar
            #este script puede cambiar dependiendo lo que yo quiera sacar
            #------------------------------------------------------------
            # SI EL PASO KMNi DANA ELEMENTOS POR CT Y EL CE:
            if (damageN[0][1])>0 and len(damageTen)>0:
                #name_files para graficar o para el siguiente m
                name_files=name_INP+'_'+'k'+str(k+1)+'m'+str(m+1)+'n'+str(damageN[0][3])+'j'+str(damageN[0][4])
                factorcoord,GtT,sigma_inf,theta2,gt1,gt2,U1matrx=PMTESCsalDatos.PMTESCsalDatos_SFLoad(name_files, working_directory, salida_datos3, str(k+1), str(m), str(damageN[0][1]), str(damageN[0][0]), str(len(damageTen)), n+1, fileLEBIMnp, Gclst)
                energy_file(archivo_energias,k+1,m+1,0,0,loadfile,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2,PIkm0,U1matrx)
                
                # AsetcritNpy=np.array(Asetcrit)
                # # Save the array into a text file:
                #     # Specify the format for each column
                # fmt = ['%d', '%d', '%.15e', '%.6e', '%d', '%.6e', '%.6e']
                # # header='NeGlobal\t t(x)\t tc(x) real\t elem. i.p.\t (t/tc) real\t (t/tc) random'
                # np.savetxt(working_directory_FFM+'\\'+name_files+'-Asetcrit.txt', AsetcritNpy, fmt=fmt, delimiter='\t')
                
            if m>0 and damageM[m][1]==0: #si no hay ningun elemento danano salgo
                newload = loadfile_it + incre
                print('m-substep: {}; applied load: {}'.format(m,loadfile_it))
                break
            #------------------------------------------------------------
            #evaluo m para seguir dentro del bucle o salir
            #------------------------------------------------------------
            #SI QUIERO CAPTAR UN SNAP-BACK DEBERIA PONER MAXIMO M=1 EN EL ARCHIVO DE ENTRADA
            if (abs(incre)/Fk)<toler and damageN[0][1]>0 and len(kfrac_list)>=2 and m>=0:
                loadfile = loadfile_it
                print(damageN[0][1], iter_count, (abs(incre)/Fk))
                os._exit(0)
                # break
            
            if (abs(incre)/Fk)<toler and m>0 and damageN[0][1]==0 and len(kfrac_list)>=2:
                loadfile = loadfile_it
                print(incre, (abs(Fk-Fkm1)/Fk))
                break
            
            if damageN[0][1]==0 and k>=1 and m==0: #si no hay ningun elemento danano salgo
                print(incre, (abs(incre)/Fk))
                print(damageN[0][1], iter_count)
                loadfile = loadfile_it
                
                break
            
            if (abs(incre)/Fk)>toler and damageN[0][1]>0 and m==0:
                print(damageN[0][1], iter_count, eps0)
                loadfile = loadfile_it
                
                break
            
    #--------------------------------------------------------------------------------------
    #almaceno los odbs si lo pido en el archivo de entrada
    if almacenarOdbs==1:
        list_odbs=glob.glob('*.odb')
        for files in list_odbs:
            move(files,working_directory_odbs)
        
    elif almacenarOdbs==2:
        name_files_movido=name_INP+'_'+'k'+str(k+1)+'m1n0j0.odb'
        move(name_files_movido,working_directory_odbs)
         
    # list_delete = ('abaqus.*', '*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.log', '*.jnl',\
    #                '*.pes','*.par','*.pmg','*.odb','*.ipm')
    list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                   '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
    #list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl','*.pes','*.par','*.pmg')
    PMTESC.borrar_archivos(list_delete)
    
    if k+1 > num_iteraciones and iter_count > numiter:
        enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6,7])
        kstepindx=enerfilenp[:,0]==k
        fkstepindx=enerfilenp[:,0]==k+1
        Fkm1 = enerfilenp[kstepindx,6][0]
        Fk = enerfilenp[fkstepindx,6][0]
        print(k+1, abs(Fk-Fkm1)/Fk)
        os._exit(1)  # Exit with a status code (1 indicates an error)
    # 
    # THE NEXT STEP SHOULD BE PROGRAMMING THE CRACK PROPAGATION SUBSTEPS:
    if k+1 > 1:
        enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6,7])
        kstepindx=enerfilenp[:,0]==k
        fkstepindx=enerfilenp[:,0]==k+1
        Fkm1 = enerfilenp[kstepindx,6][0]
        Fk = enerfilenp[fkstepindx,6][0]
        if (abs(Fk-Fkm1)/Fk)<toler and damageN[0][1]==0 and m!=0:
            print(incre, (abs(Fk-Fkm1)/Fk))
            stressdist_dir=working_directory+'/'+name_INP+'_S'+str(int(first_param*10e5))+'SFinterftraction_elemCE'+'mu'+str(mu_const)
            if (path.exists(stressdist_dir) == True):
                rmtree(stressdist_dir)

            mkdir(stressdist_dir)
            # kfrac_list = [] #Empty list with step value and broken interface elements
            # with open('elemCE_resumen.txt', 'r') as f:
            #     for line in f:
            #         line = line.split()
            #         if line:
            #             line = [i for i in line]
            #             kfrac_list.append(line)

            Gtf1evo=[]
            for line in kfrac_list:
                k1frac=line
                if line[-1]>=0:
                    name_files = name_INP + '_' + 'k' + str(line[1])+ 'm' + str(line[2])+ 'n' +str(line[3])+ 'j' + str(line[4])
                    thetaf1=CrackedInterSigmarr.CrackedInterSigmarr(name_INP, k1frac, working_directory, stressdist_dir, working_directory_odbs, first_param)
            #         srrf1arr=thetaf1[thetaf1[:,1]!=0]
            #         gtf1arr=thetaf1[thetaf1[:,3]!=0]; gif1arr=thetaf1[thetaf1[:,4]!=0]; giif1arr=thetaf1[thetaf1[:,5]!=0];
            #         gtf1max_ind=np.where(thetaf1[:,1]==np.max(srrf1arr[:,1]))[0]; 
            #         if thetaf1[gtf1max_ind,0] < 90.0:
            #             # print(thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], giif1arr[gtf1max_ind,5])
            #             Gtf1evo.append([thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], gif1arr[gtf1max_ind,4], giif1arr[gtf1max_ind,5]])
            #         if thetaf1[gtf1max_ind,0] > 90.0 and thetaf1[0,0] <= 180.0:
            #             # print(180.0-thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], giif1arr[gtf1max_ind,5])
            #             Gtf1evo.append([180.0-thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], gif1arr[gtf1max_ind,4], giif1arr[gtf1max_ind,5]])
            #         if thetaf1[gtf1max_ind,0] >= 180 and thetaf1[-1,0] < 270.0:
            #             # print(thetaf1[gtf1max_ind,0]-180.0, gtf1arr[gtf1max_ind,3], giif1arr[gtf1max_ind,5])
            #             Gtf1evo.append([thetaf1[gtf1max_ind,0]-180, gtf1arr[gtf1max_ind,3], gif1arr[gtf1max_ind,4], giif1arr[gtf1max_ind,5]])
            #         if thetaf1[gtf1max_ind,0] > 270 and thetaf1[-1,0] < 360.0:
            #             # print(360.0-thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], giif1arr[gtf1max_ind,5])
            #             Gtf1evo.append([360.0-thetaf1[gtf1max_ind,0], gtf1arr[gtf1max_ind,3], gif1arr[gtf1max_ind,4], giif1arr[gtf1max_ind,5]])
            #         Gtf1evonp=np.array(Gtf1evo)
                                                
            # np.savetxt(working_directory_FFM+'\\'+name_INP+'_SFinterftraction_evo.txt', Gtf1evonp, delimiter='\t')
            odbDir = working_directory_odbs
            # Loop through the files in the directory 
            for filename in os.listdir(odbDir):
                # Check if the file has a .lck extension 
                if filename.endswith('.lck'):
                    # Construct the full file path 
                    file_path = os.path.join(odbDir, filename)
                    # Remove the .lck file 
                    os.remove(file_path)
                    
            end = datetime.datetime.now()
            timediff=end-start
            print('\n')
            print('El programa ha terminado en %.2f' %(timediff.total_seconds()/60)+' min')
            os._exit(0)  # Exit with a status code (1 indicates an error)
            # break
    k+=1
    
end = datetime.datetime.now()
timediff=end-start
print('\n')
print('El programa ha terminado en %.2f' %(timediff.total_seconds()/60)+' min')