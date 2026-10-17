# 
"""
Created on Mon May 27 14:50:21 2024

# ********************************************************************************
# SCRIPT: PMTESC.PY
# Autor: Mar
# Modificaciones: Jose Pimentel
# Notas: no poner ninguna tilde en los comentarios
# ********************************************************************************
# 
"""

#---------------------------------------------------
#Importacion modulos
from os import chdir, path, mkdir, getcwd, remove
import os
from shutil import rmtree, move, copy
from glob import glob
from subprocess import call
import time
import collections
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
# datos para trabajar (LEER de inputFFMLEBIM.txt)
#---------------------------------------------------
fileINPUT = open('inputDCB2D_FFMLEBIM.txt','r')

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
start = time.time()
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
working_directory_FFM=working_directory+'/FFM_optimizada01_'+str(name_INP)+'Ctrl'+str(control)+'_BISTOL%.2e' %toler
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
filedamii_lst=[]
#damageM almacena el dagno N con minima energia para cada M. Lo hace a traves de la variable damageN
#definida en el bucle j
damageM=[]
kdownf=float(1) #factor de carga antes de la primera rotura de un paso kmni 

# *************************************************************************************
inp_file_path = actual_directory+'/'+name_INP+'.inp'
with open(inp_file_path, 'r') as inp_file:
    inp_lines = inp_file.readlines()
# llamada de fcn que retorna la resistencia de la interfase del fichero inp:
first_param, mu_const = PMTESCcriTen_carga.sigmac_parameter(inp_lines)
if first_param is not None:
    print('Interface critical strength; brittleness parameter: ',first_param, mu_const)
    print('\n')
print('Random variate distribution multiplicative factor, pRand, 0<=pRand<=1: ',p)
# xcoordf2, ycoordf2 = PMTESCcriTen_carga.fiber2XYcoord(inp_lines)
# *************************************************************************************
if control==1:
    carga=float(10)
else: 
    carga=float(1E-2)
    incre=5E-2

m=0
iter_count = 1 #bisection iteration counter
loadfile_it=0.0 #bisection adaptive load
# 
eps0=1.0
kfrac_list = [] #list that holds step value and broken interface elements
k=0

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
    #pero al FINAL DE ESE PASO J LA ENERGIA CALCULADA ES CON LOS ELEMENTOS
    #DAGNADOS DEL PASO J ANTERIOR, EL DAGNO SE ACTUALIZA EN EL SIGUIENTE PASO     

# Steps, donde se ejecuta el CT
while iter_count <= numiter:
#    #damageTen es para almacenar la lista de elementos dagnados por criterio tensional
#    damageTen=[]
#    #damageM almacena el dagno N con minima energia para cada M. Lo hace a traves de la variable damageN
#    #definida en el bucle j
#    damageM=[]
    # Bisection termination criterion after reaching the limit tolerance
    if eps0<toler and kfrac_list[-1][-1]!=0:
        print(eps0)
        break
    
    if k==0:        
        name_files = name_INP + '_para_carga'+ '_' + 'k' + str(k+1)
        # Read the model
        mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
        myModel = mdb.models[name_INP]
        myAssembly = myModel.rootAssembly
        print("Assembly sets:", myAssembly.sets.keys())
        print("Assembly instances:", myAssembly.instances.keys())
        region1 = myAssembly.sets['TOPBCNODE']
        region2 = myAssembly.sets['BOTTOMBCNODE']
        # Apply loads (as boundary conditions)
        for BC in range(nBCD):
            if control==1:
                if BC==0:
                    mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC],
                                        createStepName='Step-1', 
                                        region=region1, 
                                        cf2=fBCD[BC]*carga,
                                        distributionType=UNIFORM, 
                                        field='', 
                                        localCsys=None,
                                        # --- MODIFICATION HERE ---
                                        amplitude='AMP-1')
                if BC==1:
                    mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                        createStepName='Step-1', region=region2, cf2=-fBCD[BC]*carga, 
                        distributionType=UNIFORM, field='', localCsys=None, amplitude='AMP-1')
            elif control==0:
                if BC==0:
                    # Apply the Displacement Boundary Condition
                    mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                       createStepName='Step-1', 
                                                       region=region1, 
                                                       u2=fBCD[BC]*carga, 
                                                       distributionType=UNIFORM, localCsys=None,
                                                       amplitude='AMP-1')
                if BC==1:
                    mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                       createStepName='Step-1', 
                                                       region=region2, 
                                                       u2=-fBCD[BC]*carga, 
                                                       distributionType=UNIFORM, localCsys=None,
                                                       amplitude='AMP-1')
        # Create the job
        mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=FULL, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
        # Run the job
        mdb.jobs[name_files].submit(consistencyChecking=OFF)

        # Do not return control till job is finished running
        mdb.jobs[name_files].waitForCompletion()
        #si quiero revisar el inp del job no borrarlo:
        move(name_files+'.inp', working_directory_FFM)
        # Tension criteria and definition of the new load
        loadfile, sigma1 = PMTESCcriTen_carga.PMTESCcriTen_carga(name_files, working_directory, carga, setnodeInt)
        newload = factorcarga * loadfile
        # while sigma1 > first_param:
        #     loadfile=loadfile-incre
        #     if loadfile<0.0:
        #         print("Error: applied load cannot be negative, check the input data file.")
        #         break
        #     newload=(first_param/sigma1)*kdownf*loadfile
        
        if sigma1 < first_param:
            newload=(first_param/sigma1)*(kdownf*loadfile)
            print('sigma1 < sigmac', newload)
        elif sigma1 > first_param:
            newload=(first_param/sigma1)*(kdownf*loadfile)
            print('sigma1 > sigmac', newload)
        # diccionarios para el crierio tensional y energetico
        dicc_NeL_T, dicc_NeL_E = PMTESC_dicc.PMTESC_dicc(name_files, working_directory, setnodeInt)
        # print(np.array(Asigma_new))

    if k!=0: #si k es distinto de 0
        if aumentocarga==1: #si seguimos aumentando la carga
            # newload = newload + incre
            if k==1:
                newload = newload + incre
            if k>1 and iter_count<=numiter:
                newload = newload
            if (eps0 < toler) and (iter_count>numiter):
                newload = newload
                os._exit(0)
                
        else: #si empezamos en cada k desde 0 para un snap-back
            if len(damageTen)==0 or damageM[m][1]==0: #realmente esto se puede poner arriba con un triple or
                newload = loadfile + incre
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
                region1 = myAssembly.sets['TOPBCNODE']
                region2 = myAssembly.sets['BOTTOMBCNODE']
                # Apply loads (as boundary conditions)
                ######################## NO SE QUE CARGA UTILIZAR AQUI!!!!!!
                ######################## carga or newload or what?              
                
                for BC in range(nBCD):
                    #mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*carga)
                    if control==1:
                        if BC==0:
                            mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                                createStepName='Step-1', region=region1, cf2=fBCD[BC]*newload,
                                distributionType=UNIFORM, field='', localCsys=None, amplitude='AMP-1')
                        if BC==1:
                            mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                                createStepName='Step-1', region=region2, cf2=-fBCD[BC]*newload, 
                                distributionType=UNIFORM, field='', localCsys=None, amplitude='AMP-1')
                    elif control==0:
                        if BC==0:
                            # Apply the Displacement Boundary Condition
                            mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                               createStepName='Step-1', 
                                                               region=region1, 
                                                               u2=fBCD[BC]*newload, 
                                                               distributionType=UNIFORM, localCsys=None,
                                                               amplitude='AMP-1')
                        if BC==1:
                            mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                               createStepName='Step-1', 
                                                               region=region2, 
                                                               u2=-fBCD[BC]*newload, 
                                                               distributionType=UNIFORM, localCsys=None,
                                                               amplitude='AMP-1')
                
                # Create the job
                mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=FULL, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
                # Run the job
                mdb.jobs[name_files].submit(consistencyChecking=OFF)

                # Do not return control till job is finished running
                mdb.jobs[name_files].waitForCompletion()
                #si quiero revisar el inp del job no borrarlo:
                move(name_files+'.inp', working_directory_FFM)
                # remove(name_files+'.inp')

                # Tension criteria and new load
                loadfile = PMTESCcriTen_carga.PMTESCcriTen_carga(name_files, working_directory, newload, setnodeInt)
                newload = factorcarga * loadfile
    
                
    #vuelvo a inicializar las variables que almacenan el dagno
    damageTen=[]
    damageM=[]
    # damageTen=PMTESCcriTen.PMTESCcriTen2Fibers(name_files, working_directory, setnodeInt, dicc_NeL_T)
    
    ####esto siempre se hace:definir una nueva carga   
    #def_new_param=parametro+'='+str(newload)
    #PMTESC.cambiar_cadena(name_INP+'.inp',name_INP_P+'.inp',sent_sust,def_new_param)
    PMTESC.write_load_file(salida_datos1,newload)
    loadfile = newload
    #################
    
    for m in range(mstep):
        
        if m==0:
            name_files = name_INP + '_' + 'k' + str(k+1)+ 'm' + str(m+1)+ 'n0'+ 'j0'
            
            # Read the model
            m0=mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
            myModel = mdb.models[name_INP]
            myAssembly = myModel.rootAssembly
            region1 = myAssembly.sets['TOPBCNODE']
            region2 = myAssembly.sets['BOTTOMBCNODE']
            # print(name_files, name_INP)
            # Apply loads (as boundary conditions)
            # for BC in range(nBCD):
            #     mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*loadfile)            
            for BC in range(nBCD):
                if control==1:
                    if BC==0:
                        mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                            createStepName='Step-1', region=region1, cf2=fBCD[BC]*newload,
                            distributionType=UNIFORM, field='', localCsys=None,
                            amplitude='AMP-1')
                    if BC==1:
                        mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                            createStepName='Step-1', region=region2, cf2=-fBCD[BC]*newload, 
                            distributionType=UNIFORM, field='', localCsys=None,
                            amplitude='AMP-1')
                elif control==0:
                    if BC==0:
                        # Apply the Displacement Boundary Condition
                        mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                           createStepName='Step-1', 
                                                           region=region1, 
                                                           u2=fBCD[BC]*newload, 
                                                           distributionType=UNIFORM, localCsys=None,
                                                           amplitude='AMP-1')
                    if BC==1:
                        mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                           createStepName='Step-1', 
                                                           region=region2, 
                                                           u2=-fBCD[BC]*newload, 
                                                           distributionType=UNIFORM, localCsys=None,
                                                           amplitude='AMP-1')

            # Create the job
            mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=DOUBLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=100, memoryUnits=PERCENTAGE, model=name_INP, modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=FULL, numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, userSubroutine=eumat, waitHours=0, waitMinutes=0)
            # Run the job
            mdb.jobs[name_files].submit(consistencyChecking=OFF)

            # Do not return control till job is finished running
            mdb.jobs[name_files].waitForCompletion()
            #si quiero revisar el inp del job no borrarlo:
            remove(name_files+'.inp')
            
        PMTESCsalDatos.PMTESCsalDatos_CdesplaDCB(name_files, working_directory, salida_datos3, str(k+1), str(m), str(0), str(0), str(0))
	           
        damageTen=PMTESCcriTen.PMTESCcriTenDCB(name_files, working_directory, setnodeInt, dicc_NeL_T, working_directory_FFM)
        eleDamagei, enerHtotal, dummyvar = PMTESCcritEne.PMTESCcritEne(name_files, working_directory, setnodeInt, control,damageTen,dicc_NeL_E,working_directory_FFM)
        PI_0 = enerHtotal
        # Eliminar archivos innecesarios 
        list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                       '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.res','*.mdl','*.stt')      
        PMTESC.borrar_archivos(list_delete)
        # saco los posibles elementos a danar en el criterio tensional
        #damageTen=PMTESC.get_list_file(working_directory_Ten+'/damageTen.txt')
        # escribo en ele archivo control los posibles dananos en el criterio tensional
        PMTESC.crontol_file_paso(archivo_control,damageTen,k+1,m+1)
        #--------------------------------------------------------------------------------------
        #
        print(len(damageTen))
        # Load bisection algorithm for steps where Asigma set is empty:
        if len(damageTen)==0:
            PMTESC.energy_fileDCB_CTO(archivo_energias,k+1,m+1,0,0,loadfile,damageTen)
            newload = loadfile + abs(incre)
            break
        #--------------------------------------------------------------------------------------
        else:
        #si hay elementos dananos segun el CT almacenamos empezamos la miniminizacion
            #------------------------------------------------------------
            # LOS POSIBLES INICIOS N del criterio energetico. Esto tendria que cambiar
            #------------------------------------------------------------
            Ninicios=3
            damageN=[]
            #####aqui vendria la funcion para elegir los posibles N
            ####ahora mismo esta dentro del script criTen = 'PMTESCcriTen_ABQ.py' 

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
                    #minimizacion de la energia total por FEM
                    name_files = name_INP + '_' + 'k' + str(k+1)+ 'm' + str(m+1)+ 'n' +str(n+1)+ 'j' + str(j+1)
                    ############ ABAQUS JOB
                    chdir(working_directory)
                    
                    # Read the model
                    mdb.ModelFromInputFile(inputFileName=name_INP+'.inp', name=name_INP)
                    myModel = mdb.models[name_INP]
                    myAssembly = myModel.rootAssembly
                    region1 = myAssembly.sets['TOPBCNODE']
                    region2 = myAssembly.sets['BOTTOMBCNODE']
                    # Apply loads (as boundary conditions)
                    
                    # for BC in range(nBCD):
                    #     mdb.models[name_INP].boundaryConditions['Disp-BC-'+oBCD[BC]].setValues(u2=fBCD[BC]*loadfile)
                    for BC in range(nBCD):
                        if control==1:
                            if BC==0:
                                mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                                    createStepName='Step-1', region=region1, cf2=fBCD[BC]*newload,
                                    distributionType=UNIFORM, field='', localCsys=None,
                                    amplitude='AMP-1')
                            if BC==1:
                                mdb.models[name_INP].ConcentratedForce(name='Load-'+oBCD[BC], 
                                    createStepName='Step-1', region=region2, cf2=-fBCD[BC]*newload, 
                                    distributionType=UNIFORM, field='', localCsys=None,
                                    amplitude='AMP-1')
                        elif control==0:
                            if BC==0:
                                # Apply the Displacement Boundary Condition
                                mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                                   createStepName='Step-1', 
                                                                   region=region1, 
                                                                   u2=fBCD[BC]*newload, 
                                                                   distributionType=UNIFORM, localCsys=None,
                                                                   amplitude='AMP-1')
                            if BC==1:
                                mdb.models[name_INP].DisplacementBC(name='BC-Displacement-'+oBCD[BC], 
                                                                   createStepName='Step-1', 
                                                                   region=region2, 
                                                                   u2=-fBCD[BC]*newload, 
                                                                   distributionType=UNIFORM, localCsys=None,
                                                                   amplitude='AMP-1')

                    # Create the job
                    mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, 
                            getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model=name_INP, 
                            modelPrint=OFF, multiprocessingMode=DEFAULT, name=name_files, nodalOutputPrecision=FULL, 
                            numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch=actual_directory, type=ANALYSIS, 
                            userSubroutine=eumat, waitHours=0, waitMinutes=0)
                    # add_urdfil_output(name_files+'.inp')
                    # Run the job
                    mdb.jobs[name_files].submit(consistencyChecking=OFF)

                    # Do not return control till job is finished running
                    mdb.jobs[name_files].waitForCompletion()
                    #si quiero revisar el inp del job no borrarlo:
                    copy(name_files+'.inp', working_directory_FFM)
                    remove(name_files+'.inp')

		            ############ ENERGY CRITERIA
                    eleDamagei, enerHtotal, dummyvar=PMTESCcritEne.PMTESCcritEne(name_files, working_directory, setnodeInt, control,damageTen,dicc_NeL_E,working_directory_FFM)
                    deltaPI_j = enerHtotal-PI_0
					
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
                        ener_disi=ener_disi+disipadaElem
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
                    #estas dos siguientes es solo para el archivo de control:
                    Gc_eleme=[] #lista de la GcE por elementos posibles a romper por el CT
                    G_eleme=[] #lista de la Gc por elementos posibles a romper por el CT
                    #-----------------------------------------------------------
                    #nos metemos en el blucle de los posibles elementos a romper desde el CT
                    #para compara elemento por elemento
                    for nE in eleDamagei:
                        #energia critica por elemento
                        NeG=int(nE[0])           
                        enerEUndamage=nE[3]
                        enerEDamage=nE[4]
                        enerCrElem=nE[5]
                        #para control:
                        Gc_eleme.append(enerCrElem+enerEDamage)
                        G_eleme.append(enerEUndamage)
                        #comparacion:
                        if enerEUndamage>=enerCrElem+enerEDamage:
                            eleDamage.append(NeG)
                            for pi in range(1,5):
                                file_damageii.write('%d %d %e\n' % (pi , NeG, 0.0))
                    file_damageii.close()
                    #-----------------------------------------------------------
                    #-----------------------------------------------------------   
                    #almacenamiento de datos
                    
                    ene_damii.append([enerHtotal+ener_disi, len(eleDamage), eleDamage,G_eleme,Gc_eleme,enerHtotal,deltaPI_j,deltaPI_j+ener_disi,ener_disi])
                    PMTESC.crontol_file(archivo_control,ene_damii[j],n+1,j+1)
                    PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,newload,damageTen,ene_damii[j])
                    
                    if j!=0:                   
                        #if abs(ene_damii[j-1][1]-ene_damii[j][1])==error:#deberia cambiarlo por el dano de cada elemento
                        if(collections.Counter(ene_damii[j-1][2])==collections.Counter(ene_damii[j][2])):
                            damageN.append([ene_damii[j][0],ene_damii[j][1],ene_damii[j][2],n+1,j+1,enerHtotal])
                            #damageN[0:enerHtotal+ener_disi, 1:suma de elementos dagnado, 2:lista de NeG de elementos dagnados,  
                            #3:lista de energia por de elemento dagnados, 4:lista de energia critica por de elemento dagnados
                            #5:enerHtotal]
                            for outp_file in range(1,j+1):
                                filen = name_INP + '_' + 'k' + str(k+1)+ 'm' + str(m+1)+ 'n' +str(n+1)+ 'j' + str(outp_file)
                                filenlst=[filen+'.odb',
                                filen+'.mdl',
                                filen+'.res',
                                filen+'.stt']
                                for file in filenlst:
                                    try:
                                    # if file.endswith('.odb') and outp_file!=j:
                                    #     os.remove(file)
                                        if file.endswith('.odb') and outp_file==j:
                                            copy(file,working_directory_FFM)
                                            os.remove(file)
                                    except FileNotFoundError:
                                        print("Error: The file {} does not exist.".format(file))
                            break
                    #--------------------------------------------------------------------------------------
                    #para intentar evitar que se meta en un bucle
                    contador=ene_damii.count(ene_damii[j])
                    if contador!=1:
                        print('peligro bucle j=', j)
                        exit
                    #--------------------------------------------------------------------------------------                   
                    origen= working_directory_Ene+ '/damage_paso_ii.txt'
                    destino=archivo_LEBIM
                    PMTESC.cambiar_archivos(origen,destino)                                   
                    #borrando archivos. Poner o quitar odb dependiendo de lo que se quiera
                    list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                                   '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
                    
                    PMTESC.borrar_archivos(list_delete)
            #------------------------------------------------------------
            #comparacion de las N y tomar la menor energia
            #------------------------------------------------------------
            damageN.sort(key=lambda damageN:damageN[0],reverse=False)
            origen= working_directory_Ten+ '/damageKm1.txt'
            destino=archivo_LEBIM
            # PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,0,0,newload,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2)
            enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6])
            kstepindx=enerfilenp[:,0]==k
            fkstepindx=enerfilenp[:,0]==k+1
            if k==0:
                Fkm1=0
            else:
                Fkm1 = enerfilenp[kstepindx,6][0]
            Fk = abs(enerfilenp[fkstepindx,6][0])
            
            #Guardo en archivo para postprocesar
            with open('elemCE_resumen.txt', 'a') as f:
                f.write('%d %d %d %d %d \n' % (k+1, m+1, damageN[0][3], damageN[0][4], damageN[0][1]))
                # f.write(str(damageN[0][2])+'\n')  
            
            with open('elemCE_resumen.txt', 'r') as f:
                for line in f:
                    line = line.split()
                    if line:
                        line = [int(i) for i in line]
                        kfrac_list.append(line)
            incre=abs(Fk-Fkm1)
            eps0=abs(incre)/Fk 
            if damageN[0][1]>0 and k>=1 and m==0 and iter_count<=numiter and (abs(incre)/Fk)>toler:
                print(damageN[0][1], iter_count)
                damageN[:][1]=0
                # incre=(loadfile-Fkm1)/2
                if len(kfrac_list)>1 and kfrac_list[-2][-1]!=0:
                    loadfile_it = loadfile - incre
                if len(kfrac_list)>1 and kfrac_list[-2][-1]==0:
                    loadfile_it = loadfile - incre/2
                else:
                    loadfile_it = loadfile - incre/2
                iter_count+=1
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG in damageN[0][2]:
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %e\n' % (pi , NeG, 1.0))
                fileLEBIM.close()
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j])
                damageM.append(damageN[0])
                # break #termina el actual bucle-m
                
            #si no hay ningun elemento danano, salgo del bucle
            if damageN[0][1]==0 and m==0 and k>=1 and iter_count<=numiter and ((abs(incre)/Fk)<toler or (abs(incre)/Fk)>toler):
                print(damageN[0][1], iter_count)
                iter_count+=1
                damageN[:][1]=0
                # incre=(loadfile-Fkm1)/2
                if len(kfrac_list)>1 and kfrac_list[-2][-1]==0:
                    loadfile_it = loadfile + incre
                if len(kfrac_list)>1 and kfrac_list[-2][-1]!=0:
                    loadfile_it = loadfile + incre/2
                else:
                    loadfile_it = loadfile + incre
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG in damageN[0][2]:
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %e\n' % (pi , NeG, 1.0))
                fileLEBIM.close()
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j])
                damageM.append(damageN[0])
                # break
            if damageN[0][1]>=0 and m==0 and k>=1 and iter_count>numiter:
                print(damageN[0][1], iter_count)
                # iter_count+=1
                # incre=(loadfile-Fkm1)/2
                loadfile_it = loadfile - incre/2
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG in damageN[0][2]:
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %e\n' % (pi , NeG, 0.0))
                fileLEBIM.close()
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j])
                damageM.append(damageN[0])
                os._exit(0)  # Exit with a status code (1 indicates an error)
                
            if damageN[0][1]!=0 and k>=1 and m>=0 and iter_count<=numiter and (abs(incre)/Fk)<toler:
                print(damageN[0][1], iter_count)
                loadfile_it = loadfile
                PMTESC.cambiar_archivos(origen,destino)
                fileLEBIM=open(archivo_LEBIM,'a')
                for NeG in damageN[0][2]:
                    for pi in range(1,5):
                        fileLEBIM.write('%d %d %e\n' % (pi , NeG, float(0.0)))
                fileLEBIM.close()
                PMTESC.crontol_file_final(archivo_control,damageN[0],k+1,m+1)
                PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j])
                damageM.append(damageN[0])
                
                with open(archivo_LEBIM, 'r') as src, open(working_directory_Ten+ '/damageKm1.txt', 'a') as dst:
                    dst.write(src.read())
                
                # This is the name of the Abaqus worker script
                # worker_script = 'run_job.bat' 
                # define the new .inp and directory name
                nameinp_k_mas_1=name_files+'_crackprop'+'_m'+str(1)
                work_dirkm = os.path.join(actual_directory, 
                             os.path.basename(name_files+'_crackprop'+'_m'+str(0) + '_scratch'))
                
                # create a new crack propagation working directory
                # os.mkdir(work_dirkm)
                # copy the worker script into the new work directory
                # shutil.copy(worker_script, work_dirkm)
                nameSUBR = eumat
                subr_advance = 'LEBIMdefplanaFFM.for'
                # files we need to export
                inp_file = os.path.join(working_directory_FFM+'\\'+name_files + '.inp')
                mdl_file = os.path.join(actual_directory+'\\'+name_files + '.mdl')
                prt_file = os.path.join(actual_directory+'\\'+name_files + '.prt')
                res_file = os.path.join(actual_directory+'\\'+name_files + '.res')
                odb_file = os.path.join(actual_directory+'\\'+name_files + '.odb')
                stt_file = os.path.join(actual_directory+'\\'+name_files + '.stt')
                dam_record = 'elemCE_resumen.txt'
                # export_fil = [mdl_file,prt_file,odb_file,nameSUBR,name_UMAT,inp_file,
                #               res_file,stt_file,archivo_LEBIM,dam_record,eumat,subr_advance]
                
                def PMTESCcriTenV2(name_files, working_directory, setnodeInt, dicc_NeL_T):  
                    # Redirect stdout to the command prompt
                    sys.stdout = sys.__stdout__
                    chdir(working_directory)
                    working_directory_Ten='criterioTen'
                    odb = openOdb(name_files + '.odb')
                    Eset=setnodeInt
                    dicc_NeL=deepcopy(dicc_NeL_T)
                    
                    
                    #%%
                    #-------------------------------------------------------
                    #abrimos los 3 archivos del dagno para prepara los inicios del criterio energetico
                    #Fichero del dano anterior k-1 
                    archivoKm1=open('FFM_optimizada01/'+working_directory_Ten+'/damageKm1.txt','w')
                    #Fichero del dano actual k para N1 todo sano 
                    archivoN1=open('FFM_optimizada01/'+working_directory_Ten+'/damageN1.txt','w') 
                    #Fichero del dano actual k para N2 todo dagnado 
                    archivoN2=open('FFM_optimizada01/'+working_directory_Ten+'/damageN2.txt','w')
                    #Fichero del dano actual k para N3 todo dagnado con ecuacion 
                    archivoN3=open('FFM_optimizada01/'+working_directory_Ten+'/damageN3.txt','w')
                    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3]
                    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
                    #elementos dagnados
                    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
                    archDamTen=open('FFM_optimizada01/'+working_directory_Ten+'/damageTen.txt','w')
                    #%%
                    #--------------------------------------------------------------------------
                    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
                    #--------------------------------------------------------------------------
                    InterElementSet = odb.rootAssembly.elementSets[Eset]
                    key_step = odb.steps.keys()
                      
                    key_step = odb.steps.keys()
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
                    	
                       
                    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
                    	getSubset(region=InterElementSet).values
                    	
                      
                    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
                    #    getSubset(position=CENTROID).values
                    	
                    #%%    
                    #--------------------------------------------------------------------------
                    #funciones N
                    #---------------------------------------------------       
                    def n1(dist,longitud):
                    	z=1.00 #nada roto
                    	return z
                    def n2(dist,longitud):
                    	z=0.00 #todo roto
                    	return z
                    def n3(dist,longitud):
                    	try:
                    		z=1.-(1./longitud)*dist
                    	except ZeroDivisionError:
                    		1.
                    	return z
                    
                    listafunN=[n1,n2,n3]
                    
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
                    for k in range(intpoint): 
                    	damage=path_SDV1[k].data
                    	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
                    	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
                    	ip=path_SDV2[k].integrationPoint
                    	NeG=path_SDV2[k].data
                    	if damage!=0.00: #and GtotT>=GcT: #damage=0 yes damage by CT. Hemos quitado la restrinccion de romper PI a PI
                            NeL=path_SDV2[k].elementLabel
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
                            dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip
                    
                    for k in range(intpoint):
                        damage=path_SDV1[k].data
                        ip=path_SDV2[k].integrationPoint
                        NeG=path_SDV2[k].data
                        if damage==float(0):
                            print('Message from the PMTESCcriTenV2 function:')
                            print('Stress criterion damageKm1 global element label: {}, {}\n'.format(NeG, damage))
                            #guardo en una lis los PI rotos para despues escribrir en archivos 
                            # finalmente hay algun elemento dagnado
                            dagnokm1.append([ip,NeG,damage])
                    
                    # with open('FFM_optimizada01/'+ working_directory_Ten + '/damageKm1.txt', 'r') as f:
                    #     for line in f:
                    #         # Split line into columns
                    #         row = line.split()
                    #         # Convert strings to floats (or ints if appropriate)
                    #         row = [float(x) for x in row]
                    #         # Append row to data list
                    #         dagnokm1.append(row)   
                    
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
                    #hago una nuev lista con los elementos dagnados dameleCT=[]
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
                    for elem in range(elementos):
                    	if listaElem[elem][6]>listaElem[elem][7] and listaElem[elem][10]==10:
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
                    	xa=dameleCT[0][3]
                    	xb=dameleCT[elem][3]
                    	ya=dameleCT[0][4]
                    	yb=dameleCT[elem][4]
                    	dist=sqrt(((xa-xb)**2)+((ya-yb)**2))
                    	dameleCT[elem][5]=dist
                    	
                    #%%    
                    #-----------------------------------------------------------------------------------------------------------------------
                    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
                    #-----------------------------------------------------------------------------------------------------------------------
                    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
                    
                    #el parametro longitud NO SE MUY BIEN como jugar con el 
                    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
                    #y si solo hay un elemento da error la funcion n3
                    if len(dameleCT)>1:
                    	longitud=dameleCT[-1][5]
                    else:
                    	longitud=1.0
                    
                    #%%
                    #-----------------------------------------------------------------------------------------------------------------------
                    #agnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
                    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
                    #elementos dagnados
                    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
                    #-----------------------------------------------------------------------------------------------------------------------
                    #escribo en todos los archivo Ns y en Km1 el dagno de km1
                    if len(dameleCT)!=0:
                    	for n in range(len(listarchivos)):
                    		for elem in dagnokm1:
                    			listarchivos[n].write('%d %d %e \n' 
                    						% (elem[0],elem[1],elem[2]))
                    #escribo los nuevos danos del criterio tensional       
                    for n in range(len(listafunN)):
                    	for elem in range(len(dameleCT)):  
                    		if n+1<3:
                    			damage=listafunN[n](dameleCT[elem][5],longitud)
                    		else:
                    			if elem+1 <= len(dameleCT)*0.5:
                    				damage=0
                    			else:
                    				damage=1
                    		dameleCT[elem].append(damage)
                    		NeG=dameleCT[elem][1]
                    		for ip in range(1,5):
                    			listarchivos[n+1].write('%d %d %e \n' % (ip,NeG,damage))
                    #cierro archivos  
                    for n in range(len(listarchivos)):
                    	listarchivos[n].close()	
                    	
                    #%%
                    #-----------------------------------------------------------------------------------------------------------------------
                    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
                    #elementos dagnados
                    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
                    #-----------------------------------------------------------------------------------------------------------------------    
                    
                    # with open('log_criTen.txt', 'w') as f:
                    #     #f.write(str(dagnokm1[0]))
                    #     f.write(str('prueba'))
                    #     f.write('\n')
                    #     f.write(str(dameleCT[0]))
                    #     f.write('\n')
                    #     f.write(str(dameleCT[0][9]))
                    #     f.write('\n')
                    #     f.write(str(dameleCT))
                    #     f.write('\n')
                    #     f.write(str(dagnokm1))
                    #     f.write('\n')
                    #     f.write(str(listaElem[0][0]))
                    #     f.write(str(listaElem[0][9]))
                    #     f.write('\n')
                    #     f.write(str(range(len(dameleCT))))
                    #     f.write(str(len(dameleCT)))
                    
                    damageTen=[]
                    for elem in range(len(dameleCT)):
                    		archDamTen.write('%d %s %e'
                    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))			
                    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]])
                    		
                    		for n in range(len(listafunN)):   
                    			archDamTen.write(' %e' % (dameleCT[elem][11+n]))
                    			damageTen[elem].append(dameleCT[elem][11+n])
                    		archDamTen.write('\n')
                    archDamTen.close()
                    #%%
                    #-----------------------------------------------------------------------------------------------------------------------
                    odb.close() 
                    return damageTen
                def PMTESCcritEneV2(name_files, working_directory, setnodeInt, control, elementosTen, dicc_NeL_E):
                    # Redirect stdout to the command prompt
                    sys.stdout = sys.__stdout__
                    chdir(working_directory)
                    working_directory_Ene='FFM_optimizada01/'+'criterioEne'
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
                    path_SDV7=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV7'].\
                    	getSubset(region=InterElementSet).values
                    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
                    	getSubset(region=InterElementSet).values 
                    path_SDV9=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV9'].\
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
                    ## en la lista elementosTen tenemos para cada elemento suceptible de romper por CT:
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
                    	#la Greal es para calcular lar energia total al principio del paso
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
                    	dicc_NeL[NeL2][6]=damage
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
                    	eleDamagei.append([elem[0],elem[1],dicc_NeL[elem[1]][3],dicc_NeL[elem[1]][4],dicc_NeL[elem[1]][5],elem[2],dicc_NeL[elem[1]][6]])
                    archivoEneEle.close()
                    
                    #%%
                    #Energia de todo el sistema en el setp=j
                    Work = 2*(path_HisRegEne.historyOutputs['ALLWK'].data[-1][1])
                    eneDefSolidos = path_HisRegEne.historyOutputs['ALLSE'].data[-1][1]
                    #tomamos 'ALLSE' en lugar de 'ALLIE' porque estrictamente es la energia de deformacion
                    #pero podemos replantearnos poner la otra por el hourglassing
                    if control==1:
                    	enerHtotal = -(eneDefSolidos+sumaenerinter)
                    else:
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
                
                if control==0:
                    sys.exit()
                    # DISPLACEMENT CONTROLLED CRACK ADVANCE
                    """
                    # Execute a restart job simulation for each step, then 
                    # proceed with classical PMTE-SC algorithm for each load
                    # step, until convergence tolerance falls below a treshold,
                    # BUT only if the crack advance condition is met at the 
                    # end of the kmiNij_last simulation step.
                    """
                    if bis_option==1:
                    # commands that copy the winner input file and 
                    # create/launch restart analysis files
                        
                        # name of the Abaqus worker script
                        worker_script = 'runrestart_job.bat' 
                        common_file = 'my_common.inc'
                        
                        # define the new .inp and directory name
                        # nameinp_k_mas_1=name_files+'_crackprop'+'_m'+str(1)
                        # work_dirkm = os.path.join(actual_directory, 
                        #              os.path.basename(name_files+'_crackprop'+'_m'+str(0) + '_scratch'))
                        # copy the worker script into the new work directory
                        # shutil.copy(worker_script, work_dirkm)
                        # shutil.copy(common_file, work_dirkm)
                        # move the control files into the new work directory
                        # shutil.move(archivo_control, work_dirkm)
                        # shutil.move(archivo_energias, work_dirkm)
                        # shutil.move(salida_datos1, work_dirkm)
                        # shutil.move(salida_datos3, work_dirkm)                        
                        load_list = []
                        load_list.append([loadfile, 0])
                        numiter_max = 30
                        loadfile_it = loadfile
                        # number of crack advance steps
                        nsteps = 30
                        for indx in range(nsteps):
                            bisiter = 1
                            epsb2 = float(1)
                            if indx==0 and bisiter==1: 
                                
                                nstep = 2
                                inpfil_name = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)
                                inp_filename = create_crack_restart_inp(inpfil_name, nstep, loadfile_it)
                                # add_urdfil_output(inp_filename)
                                # 
                                archivo_LEBIM = 'datos_procesar.txt'
                                working_directory_Ten = working_directory_FFM+'/criterioTen'
                                work_dirkm1 = os.path.join(working_directory_Ten, 'damageKm1.txt')
                                # shutil.copyfile('datos_procesar.txt', work_dirkm1)
                                with open(archivo_LEBIM, 'r') as src, open(work_dirkm1, 'w') as dst:
                                    dst.write(src.read())
                            if indx>0 and bisiter==1:
                                nstep += 1
                                with open(archivo_LEBIM, 'r') as src, open(work_dirkm1, 'w') as dst:
                                    dst.write(src.read())
                                #
                            """
                            
                            START OF ADVANCE BISECTION ALGORITHM
                            
                            """
                            
                            while bisiter < numiter_max:
                                if indx==0 and bisiter==1: 
                                    # PRINT A DEBUG CHECKPOINT HERE
                                    newld_iter = loadfile_it
                                    print('indx=={} and bisection iter.=={}, applied load={}'.format(indx,bisiter,loadfile_it))
                                    print('Load record: {}'.format(load_list))
                                    old_load=loadfile
                                    odb_file = name_files
                                    oldjob_name = name_files
                                if indx==0 and bisiter>1:
                                    loadfile_it = newld_iter
                                    # old_load=load_list[-1][0]
                                    # load_list.append(newld_iter)
                                if indx>0 and bisiter>=1:
                                    # 
                                    # oldjob_name = odb_file
                                    loadfile_it = newld_iter
                                    old_load = load_list[-1][0]
                                                          
                                print("START OF ADVANCE BISECTION ALGORITHM: base job {}".format(oldjob_name))
                                # oldjob_name is the last converged job after the 
                                # nucleation bisection algorithm 
                                
                                # initialization of damage arrays
                                damageTen=[]
                                damageM=[]
                                PMTESC.write_load_file(salida_datos1,loadfile_it)
                                
                                # LAUNCH JOB DEFINING THE ELEMENTS IN A_SIGMA SET:
                                if indx>=0:
                                    inpfil_name = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)+'Asigma'
                                    
                                inp_filename = create_crack_restart_inp(inpfil_name, nstep, loadfile_it)
                                # add_urdfil_output(inp_filename)
                                # Call the .bat file and pass the job_name as an argument
                                command = [
                                    worker_script,
                                    inpfil_name, # current job name
                                    oldjob_name, # restart base analysis
                                    subr_advance     # subroutine.for file
                                ]
                                print("Submitting job via Worker .bat file...")
                                # We use .call() because the .bat file is fast
                                # and will exit as soon as the job is submitted.
                                subprocess.call(command, cwd=actual_directory)
                                
                                # POSTPROCESS FOR INDX>=0:
                                damageTen=PMTESCcriTenV2(inpfil_name, actual_directory, setnodeInt, dicc_NeL_T)
                                print(damageTen)
                                eleDamagei,enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control, damageTen, dicc_NeL_E)
                                PI_0 = enerHtotal
                                
                                # Start of the Dn j_ama loop that minimizes the
                                # energy functional PI+deltaR
                                #--------------------------------------------------------------------------------------
                                
                                # Load bisection algorithm for steps where Asigma set is empty:
                                if len(damageTen)==0:
                                    print('Stress criterion not fulfilled for the load {}'.format(loadfile_it))
                                    PMTESC.energy_fileDCB_CTO(archivo_energias,k+1,m+1,0,0,loadfile_it,damageTen)
                                    incre = abs(newld_iter-load_list[-1][0])
                                    loadfile_it = load_list[-1][0] + 2.0*incre
                                    nstep += 1
                                    with open(archivo_LEBIM, 'r') as src, open(work_dirkm1, 'w') as dst:
                                        dst.write(src.read())
                                    break
                                #--------------------------------------------------------------------------------------
                                else:
                                    print('{} elements define the A_sigma set'.format(len(damageTen)))
                                    #empezamos la miniminizacion
                                    #------------------------------------------------------------
                                    # LOS POSIBLES INICIOS N del criterio energetico. Esto tendria que cambiar
                                    #------------------------------------------------------------
                                    Ninicios=2
                                    damageN=[]
                                    archivo_LEBIM='datos_procesar.txt'
                                    # working_directory_Ten = 'criterioTen'
                                    # working_directory_Ene = 'criterioEne'
                                    
                                    for n in range(Ninicios): 
                                        #cambia el archivo de datos_procesar.txt para romper en abaqus
                                        origen=working_directory_Ten+'/damageN'+str(n+1)+'.txt'
                                        destino=archivo_LEBIM
                                        
                                        PMTESC.cambiar_archivos(origen,destino)
                                        #------------------------------------------------------------
                                        # optimizo el criterio energetico con cada inicio n
                                        #------------------------------------------------------------
                                        #inicializando variables
                                        ene_damii=[]
                                        error=0             
                                        for j in range(50): #aqui poner un numero muy alto o un while
                                            # PASO I
                                            # MINIMIZACION DE LA ENERGIA TOTAL POR FEM
                                            inpfil_name = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)+'N'+str(n+1)+'j'+str(j+1)
                                            inp_filename = create_crack_restart_inp(inpfil_name, nstep, loadfile_it)
                                            # add_urdfil_output(inp_filename)
                                            # # --- THIS IS THE COMMAND LIST ---
                                            # Call the .bat file and pass the job_name as an argument
                                            command = [
                                                worker_script,
                                                inpfil_name, # current job name
                                                oldjob_name, # restart base analysis
                                                subr_advance     # subroutine.for file
                                            ]
                                            print("Submitting job via Worker .bat file...")
                                            # We use .call() because the .bat file is fast
                                            # and will exit as soon as the job is submitted.
                                            subprocess.call(command, cwd=actual_directory)
                                            print ("--- Iteration {} complete, base job: {} ---".format(inpfil_name, oldjob_name))

                        		            ############ ENERGY CRITERIA
                                            if j==0:
                                                eleDamagei, enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control,damageTen,dicc_NeL_E)
                                                deltaPI_j = enerHtotal-PI_0
                                                print('Iteration {}, deltaPI_jama = {}\n'.format(j,deltaPI_j))
                                            else:
                                                # inpfil_namejm1 = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)+'N'+str(n+1)+'j'+str(j+1)
                                                eleDamagei, enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control,damageTen,dicc_NeL_E)
                                                deltaPI_j = enerHtotal-PI_0
                                                print('Iteration {}, deltaPI_jama = {}\n'.format(j,deltaPI_j))
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
                                                ener_disi=ener_disi+disipadaElem
                                            #-----------------------------------------------------------    
                                            ##paso ii. Minimizacion de la funcion dagno       
                                            #-----------------------------------------------------------
                                            #copiamos los PI rotos del los pasos anteriores (k-1) para despues
                                            #seguir anadiendo los de este paso j. En cada paso j este archivo se reescribe.
                                            #cambia el archivo de datos_procesar.txt para romper en abaqus
                                            origen=working_directory_Ten+'/damageKm1.txt'
                                            destino=working_directory_Ene+'/damage_paso_ii.txt'
                                            PMTESC.cambiar_archivos(origen,destino)
                                            file_damageii=open(working_directory_Ene+'/damage_paso_ii.txt','a')
                                            #-----------------------------------------------------------
                                            eleDamage=[] #lista de elementos rotos despues de esta funcion
                                            #estas dos siguientes es solo para el archivo de control:
                                            Gc_eleme=[] #lista de la GcE por elementos posibles a romper por el CT
                                            G_eleme=[] #lista de la Gc por elementos posibles a romper por el CT
                                            #-----------------------------------------------------------
                                            #nos metemos en el blucle de los posibles elementos a romper desde el CT
                                            #para compara elemento por elemento
                                            for nE in eleDamagei:
                                                damelem_count=[]
                                                # energia critica por elemento
                                                NeG=int(nE[0])           
                                                enerEUndamage=nE[3]
                                                enerEDamage=nE[4]
                                                enerCrElem=nE[5]
                                                # para control:
                                                Gc_eleme.append(enerCrElem+enerEDamage)
                                                G_eleme.append(enerEUndamage)
                                                # comparacion: CRITERIO INCREMENTAL DE GRIFFITH
                                                if enerEUndamage-enerEDamage>=enerCrElem:
                                                    damelem_count.append(NeG)
                                                    eleDamage.append(NeG)
                                                    for pi in range(1,5):
                                                        file_damageii.write('%d %d %e\n' % (pi , NeG, 0.0))
                                            file_damageii.close()
                                            #-----------------------------------------------------------
                                            #-----------------------------------------------------------   
                                            #almacenamiento de datos
                                            ene_damii.append([enerHtotal+ener_disi,len(damelem_count),eleDamage,G_eleme,Gc_eleme,enerHtotal,deltaPI_j,deltaPI_j+ener_disi,ener_disi])
                                            # PMTESC.crontol_file(archivo_control,ene_damii[j],n+1,j+1)
                                            # PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,newload,damageTen,ene_damii[j])
                                            print(j,len(eleDamage),enerHtotal,deltaPI_j,deltaPI_j+ener_disi,ener_disi)
                                            if j!=0:                   
                                                #
                                                if(collections.Counter(ene_damii[j-1][2])==collections.Counter(ene_damii[j][2])):
                                                    damageN.append([ene_damii[j][7],len(ene_damii[j][2]),ene_damii[j][2],n+1,j+1,enerHtotal])
                                                    print('eleDamage, iter j-1={}, iter j={}'.format(len(ene_damii[j-1][2]), len(ene_damii[j][2])))
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
                                            origen=working_directory_Ene+'/damage_paso_ii.txt'
                                            destino=archivo_LEBIM
                                            PMTESC.cambiar_archivos(origen,destino)                                   
                                            #borrando archivos. Poner o quitar odb dependiendo de lo que se quiera
                                            list_delete = ('*.sta', '*.sim', '*.msg', '*.com', '*.jnl',\
                                                           '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
                                            PMTESC.borrar_archivos(list_delete)
                                            #------------------------------------------------------------
                                            #comparacion de las N y tomar energia minima
                                            #------------------------------------------------------------
                                            damageN.sort(key=lambda damageN:damageN[0],reverse=False)
                                            origen= working_directory_Ten+ '/damageKm1.txt'
                                            destino=archivo_LEBIM
                                            # PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,0,0,newload,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2)
                                            enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6])
                                            kstepindx=enerfilenp[:,0]==k
                                            fkstepindx=enerfilenp[:,0]==k+1
                                            
                                if indx>=0 and bisiter==1: epsb2=1.0
                                if indx==0 and bisiter>1: epsb2=abs(newld_iter-load_list[-1][0])/abs(newld_iter)
                                if indx>0 and bisiter>1:
                                    epsb2=abs(newld_iter-load_list[-1][0])/abs(newld_iter)
                                
                                if epsb2==0:
                                    print('eps0 should NOT be {}\n'.format(epsb2))
                                    print('Model: {}, load={}, previous load={}'.format(inpfil_name, newld_iter, load_list[-1][0]))
                                    print('substep {}, bisection iteration {}'.format(indx, bisiter))
                                    print('Load history records: [load, damage]\n')
                                    for val in load_list:
                                        print(val)
                                    print('Script terminated for debugging\n')
                                    sys.exit()
                                # sys.exit()
                                if damageN[0][1]>0 and epsb2>advbis_toler:
                                    print('CRACK ADVANCES WITH EPSB2 {}>{} BIS_TOLER'.format(epsb2,advbis_toler))
                                    print(damageN[0][1],damageN[0][0], bisiter)
                                    # bisiter += 1
                                    fail_load = newld_iter
                                    if indx==0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load = last_row[0]
                                        newld_iter = newld_iter-0.5*abs(newld_iter-old_load)
                                    if indx==0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        if last_row==None:
                                            last_row=next((row for row in reversed(load_list) if row[1] == 1), None)
                                        old_load=load_list[0][0]
                                        newld_iter = newld_iter - 0.5*abs(newld_iter-old_load)
                                    if indx==0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=load_list[0][0]
                                        newld_iter = old_load + 0.5*abs(newld_iter-old_load)
                                    if indx>0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        newld_iter = newld_iter - 0.5*abs(newld_iter-last_row[0])
                                    if indx>0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 1), None)
                                        old_load=last_row[0]
                                        newld_iter = newld_iter - 0.5*abs(newld_iter-old_load)
                                    if indx>0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 1), None)
                                        old_load=last_row[0]
                                        newld_iter = newld_iter - 0.5*abs(newld_iter-old_load)
                                    load_list.append([fail_load, 1])
                                    if bisiter > 1:
                                        # Remove unnecessary files for each iteration but the last one
                                        for iterindx in range(1,bisiter):
                                            for dn in range(1,Ninicios+1):
                                                for jama in range(1,j+1):
                                                    iter_filename=name_files+'_m'+str(indx+1)+'_bisiter_'+str(iterindx)+'N'+str(dn)+'j'+str(jama)
                                                    if iter_filename==oldjob_name:
                                                        print('Base job files {} are kept in the dir.\n'.format(oldjob_name))
                                                    else:
                                                        
                                                        del_list = [iter_filename+'.prt',iter_filename+'.mdl',
                                                                    iter_filename+'.odb',iter_filename+'.inp',iter_filename+'.stt']
                                                        for file in del_list:
                                                            try:
                                                                os.remove(file)
                                                                print("Deleted:", file)
                                                            except OSError:  # covers missing file and other OS-related issues
                                                                print("File not found or cannot be deleted:", file)
                                    bisiter += 1
                                if damageN[0][1]==0 and epsb2>advbis_toler:
                                    print('NO CRACK ADVANCE FOR EPSB2 {}>{} BIS_TOLER'.format(epsb2,advbis_toler))
                                    print(damageN[0][1],damageN[0][0], bisiter)
                                    # bisiter += 1
                                    fail_load=newld_iter
                                    if indx==0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        newld_iter=last_row[0] + 0.0125*abs(load_list[0][0])
                                    if indx==0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=last_row[0]
                                        newld_iter = old_load + 0.5*abs(load_list[-1][0]-old_load)
                                    if indx==0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=load_list[0][0]
                                        newld_iter = old_load + 1.5*abs(newld_iter-old_load)
                                    if indx>0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        newld_iter = last_row[0] + 1.5*abs(newld_iter-last_row[0])
                                    if indx>0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 1), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=last_row[0]
                                        newld_iter = newld_iter + 0.5*abs(old_load-newld_iter)
                                    if indx>0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 1), None)
                                        old_load=last_row[0]
                                        newld_iter = old_load + 1.5*abs(newld_iter-old_load)
                                    load_list.append([fail_load, 0])
                                    if bisiter > 1:
                                        # Remove unnecessary files for each iteration but the last one
                                        for iterindx in range(1,bisiter):
                                            for dn in range(1,Ninicios+1):
                                                for jama in range(1,j+1):
                                                    iter_filename=name_files+'_m'+str(indx+1)+'_bisiter_'+str(iterindx)+'N'+str(dn)+'j'+str(jama)
                                                    if iter_filename==oldjob_name:
                                                        print('Base job files {} are kept in the dir.\n'.format(oldjob_name))
                                                    else:
                                                        
                                                        del_list = [iter_filename+'.prt',iter_filename+'.mdl',
                                                                    iter_filename+'.odb',iter_filename+'.inp',iter_filename+'.stt']
                                                        for file in del_list:
                                                            try:
                                                                os.remove(file)
                                                                print("Deleted:", file)
                                                            except OSError:  # covers missing file and other OS-related issues
                                                                print("File not found or cannot be deleted:", file)
                                    bisiter += 1
                                if damageN[0][1]==0 and epsb2<advbis_toler:
                                    print('NO CRACK ADVANCE FOR EPSB2 {}<{} BIS_TOLER'.format(epsb2,advbis_toler))
                                    print(damageN[0][1], damageN[0][0], bisiter)
                                    # bisiter += 1
                                    fail_load=newld_iter
                                    
                                    if indx==0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        newld_iter=load_list[0][0] + 1.25*abs(newld_iter-load_list[0][0])
                                    if indx==0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 1), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=load_list[0][0]
                                        newld_iter = old_load + 0.5*abs(load_list[-1][0]-old_load)
                                    if indx==0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=load_list[0][0]
                                        newld_iter = old_load + 1.5*abs(newld_iter-old_load)
                                    if indx>0 and bisiter==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        newld_iter = last_row[0] + 1.5*abs(newld_iter-last_row[0])
                                    if indx>0 and bisiter>1 and load_list[-1][1]==1:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 1), None)
                                        # if last_row==None:
                                        #     last_row=next((row for row in reversed(load_list) if row[1] == 0), None)
                                        old_load=last_row[0]
                                        newld_iter = newld_iter + 0.5*abs(newld_iter-old_load)
                                    if indx>0 and bisiter>1 and load_list[-1][1]==0:
                                        last_row = next((row for row in reversed(load_list) if row[1] == 0), None)
                                        # 
                                        old_load=last_row[0]
                                        newld_iter = newld_iter + 1.5*abs(newld_iter-old_load)
                                    load_list.append([fail_load, 0])
                                    if bisiter > 1:
                                        # Remove unnecessary files for each iteration but the last one
                                        for iterindx in range(1,bisiter):
                                            for dn in range(1,Ninicios+1):
                                                for jama in range(1,j+1):
                                                    iter_filename=name_files+'_m'+str(indx+1)+'_bisiter_'+str(iterindx)+'N'+str(dn)+'j'+str(jama)
                                                    if iter_filename==oldjob_name:
                                                        print('Base job files {} are kept in the dir.\n'.format(oldjob_name))
                                                    else:
                                                        
                                                        del_list = [iter_filename+'.prt',iter_filename+'.mdl',
                                                                    iter_filename+'.odb',iter_filename+'.inp',iter_filename+'.stt']
                                                        for file in del_list:
                                                            try:
                                                                os.remove(file)
                                                                print("Deleted:", file)
                                                            except OSError:  # covers missing file and other OS-related issues
                                                                print("File not found or cannot be deleted:", file)
                                    bisiter += 1
                                if damageN[0][1]>0 and epsb2<advbis_toler:
                                    # 
                                    with open('elemCE_resumen.txt', 'a') as f:
                                        f.write('%d %d %d %d %d \n' % (k+1, indx+1, damageN[0][3], damageN[0][4], damageN[0][1]))
                                    print('CRACK ADVANCES WITH EPSB2 {}<{} BIS_TOLER'.format(epsb2,advbis_toler))
                                    print(damageN[0][1], bisiter)
                                    # bisiter += 1
                                    fail_load = newld_iter
                                    load_list.append([fail_load, 0])
                                    incre = abs(newld_iter-old_load)
                                    if incre==float(0):
                                        newld_iter = newld_iter + (0.025*newld_iter)
                                    else:
                                        newld_iter = newld_iter + float(1)*incre
                                    oldjob_name = inpfil_name
                                    # List of file extensions to delete
                                    extensions_to_delete = ['*.sim', '*.com', '*.jnl','*.png','*.dat'\
                                                    '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.fil']
                                    for ext in extensions_to_delete:
                                        # glob.glob finds all files matching the pattern
                                        files_to_remove = glob.glob(ext)
                                        for f in files_to_remove:
                                            try:
                                                os.remove(f)
                                                "  - Deleted: {}".format(f)
                                            except OSError as e:
                                                "  - Error deleting file {}: {}".format(f, e)
                                    # Remove unnecessary files for each iteration but the last one
                                    for iterindx in range(1,bisiter):
                                        for dn in range(1,Ninicios+1):
                                            for jama in range(1,j+1):
                                                iter_filename=name_files+'_m'+str(indx+1)+'_bisiter_'+str(iterindx)+'N'+str(dn)+'j'+str(jama)
                                                if iter_filename==oldjob_name:
                                                    print('Base job files {} are kept in the dir.\n'.format(oldjob_name))
                                                else:
                                                    
                                                    del_list = [iter_filename+'.prt',iter_filename+'.mdl',
                                                                iter_filename+'.odb',iter_filename+'.inp',iter_filename+'.stt']
                                                    for file in del_list:
                                                        try:
                                                            os.remove(file)
                                                            print("Deleted:", file)
                                                        except OSError:  # covers missing file and other OS-related issues
                                                            print("File not found or cannot be deleted:", file)
                                                        
                                    break
                                if damageN[0][1]>=0 and bisiter==numiter_max:
                                    # List of file extensions to delete
                                    extensions_to_delete = ['*.dat', '*.sim', '*.com', '*.jnl'\
                                                    '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.fil']
                                    for ext in extensions_to_delete:
                                        # glob.glob finds all files matching the pattern
                                        files_to_remove = glob.glob(ext)
                                        for f in files_to_remove:
                                            try:
                                                os.remove(f)
                                                "  - Deleted: {}".format(f)
                                            except OSError as e:
                                                "  - Error deleting file {}: {}".format(f, e)
                                    
                                    print("Simulation terminated after {} advance bisection iterations, EXIT".format(bisiter))
                                    sys.exit()
                            
                        """
                        END OF ADVANCE BISECTION ALGORITHM
                        """
                        # List of file extensions to delete
                        extensions_to_delete = ['*.sim', '*.com', '*.jnl','*.stt','*.prt','*.mdl','*.res','*.msg'\
                                        '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.for','*.sta']
                        for ext in extensions_to_delete:
                            # glob.glob finds all files matching the pattern
                            files_to_remove = glob.glob(ext)
                            for f in files_to_remove:
                                try:
                                    os.remove(f)
                                    "  - Deleted: {}".format(f)
                                except OSError as e:
                                    "  - Error deleting file {}: {}".format(f, e)
                        sys.exit()
                    
                    else: 
                    # BIS_OPTION==0
                        """
                        # CRACK ADVANCE SUBJECT TO PRESCRIBED LOAD INCREMENTS
                        
                        # Execute a restart job simulation for each step, then 
                        # proceed with classical PMTE-SC algorithm for each load
                        # step, until convergence tolerance falls below a treshold,
                        # BUT only if the crack advance condition is met at the 
                        # end of the kmiNij_last simulation step.
                        """    
                        # 
                        # Number of crack advance steps
                        nsteps = 40
                        print('CRACK ADVANCE SUBJECT TO {} PRESCRIBED LOAD INCREMENTS'.format(nsteps))
                        # name of the Abaqus worker script
                        worker_script = 'runrestart_job.bat' 
                        common_file = 'my_common.inc'
                                               
                        load_list = []
                        # load_list.append([loadfile, 0])
                        # job preparation:
                        start = loadfile + float(0.025*loadfile)
                        end = 2.7*loadfile
                        num = nsteps
                        power = float(2)  # Bias toward the start
                        # 1. Create a normalized linear space (0 to 1)
                        if num == 1:
                            linear_norm = [start]
                        else:
                            linear_norm = [float(i) / (num - 1) for i in range(num)]
                        # Apply the power and scale, all inside the comprehension
                        load_vector = [start + (end - start) * (norm_val ** power) for norm_val in linear_norm]
                        print("DEBUG VECTOR:", load_vector)
                        
                        for indx, val in enumerate(load_vector):
                            # commands that copy the winner input file and 
                            # create/launch restart analysis files
                            print("Index: {}, Value: {}".format(indx, val))
                            nstep = 2 + indx
                            # inpfil_name = name_files+'_m'+str(indx+1)
                            # inp_filename = create_crack_restart_inp(inpfil_name, nstep, val)
                            # add_urdfil_output(inp_filename)
                            # 
                            archivo_LEBIM = 'datos_procesar.txt'
                            working_directory_Ten = working_directory_FFM+'/criterioTen'
                            work_dirkm1 = os.path.join(working_directory_Ten, 'damageKm1.txt')
                            # shutil.copyfile('datos_procesar.txt', work_dirkm1)
                            with open(archivo_LEBIM, 'r') as src, open(work_dirkm1, 'w') as dst:
                                dst.write(src.read())
                            # initialization of damage arrays
                            damageTen=[]
                            damageM=[]
                            PMTESC.write_load_file(salida_datos1,loadfile_it)
                            
                            # LAUNCH JOB DEFINING THE ELEMENTS IN A_SIGMA SET:
                            inpfil_name = name_files+'_m'+str(indx+1)+'_Asigma'
                            inp_filename = create_crack_restart_inp(inpfil_name, nstep, val)
                            if indx==0: 
                                oldjob_name = name_files
                            print("START OF ADVANCE LOAD STEP: {}, base job {}".format(indx, oldjob_name))
                            # oldjob_name is the last converged job after the 
                            # nucleation bisection algorithm 
                            
                            # Call the .bat file and pass the job_name as an argument
                            command = [
                                worker_script,
                                inpfil_name, # current job name
                                oldjob_name, # restart base analysis
                                subr_advance     # subroutine.for file
                            ]
                            print("Submitting job via Worker .bat file...")
                            # We use .call() because the .bat file is fast
                            # and will exit as soon as the job is submitted.
                            subprocess.call(command, cwd=actual_directory)
                            
                            # POSTPROCESS FOR INDX>=0:
                            damageTen=PMTESCcriTenV2(inpfil_name, actual_directory, setnodeInt, dicc_NeL_T)
                            print(damageTen)
                            eleDamagei,enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control, damageTen, dicc_NeL_E)
                            PI_0 = enerHtotal
                            
                            # Start of the Dn j_ama loop that minimizes the
                            # energy functional PI+deltaR
                            #--------------------------------------------------------------------------------------
                            
                            # Load bisection algorithm for steps where Asigma set is empty:
                            if len(damageTen)==0:
                                print('Stress criterion not fulfilled for the load {}'.format(loadfile_it))
                                PMTESC.energy_fileDCB_CTO(archivo_energias,k+1,m+1,0,0,loadfile_it,damageTen)
                                # incre = abs(newld_iter-load_list[-1][0])
                                loadfile_it = val + float(0.025*loadfile)
                                # nstep += 1
                                with open(archivo_LEBIM, 'r') as src, open(work_dirkm1, 'w') as dst:
                                    dst.write(src.read())
                                break
                            #--------------------------------------------------------------------------------------
                            else:
                                print('{} elements define the A_sigma set'.format(len(damageTen)))
                                #empezamos la miniminizacion
                                #------------------------------------------------------------
                                # LOS POSIBLES INICIOS N del criterio energetico. Esto tendria que cambiar
                                #------------------------------------------------------------
                                Ninicios=2
                                damageN=[]
                                archivo_LEBIM='datos_procesar.txt'
                                # working_directory_Ten = 'criterioTen'
                                # working_directory_Ene = 'criterioEne'
                                
                                for n in range(Ninicios): 
                                    #cambia el archivo de datos_procesar.txt para romper en abaqus
                                    origen=working_directory_Ten+'/damageN'+str(n+1)+'.txt'
                                    destino=archivo_LEBIM
                                    
                                    PMTESC.cambiar_archivos(origen,destino)
                                    #------------------------------------------------------------
                                    # optimizo el criterio energetico con cada inicio n
                                    #------------------------------------------------------------
                                    #inicializando variables
                                    ene_damii=[]
                                    error=0             
                                    for j in range(50): #aqui poner un numero muy alto o un while
                                        # PASO I
                                        # MINIMIZACION DE LA ENERGIA TOTAL POR FEM
                                        inpfil_name = name_files+'_m'+str(indx+1)+'N'+str(n+1)+'j'+str(j+1)
                                        inp_filename = create_crack_restart_inp(inpfil_name, nstep, val)
                                        # add_urdfil_output(inp_filename)
                                        # # --- THIS IS THE COMMAND LIST ---
                                        # Call the .bat file and pass the job_name as an argument
                                        command = [
                                            worker_script,
                                            inpfil_name, # current job name
                                            oldjob_name, # restart base analysis
                                            subr_advance     # subroutine.for file
                                        ]
                                        print("Submitting job via Worker .bat file...")
                                        # We use .call() because the .bat file is fast
                                        # and will exit as soon as the job is submitted.
                                        subprocess.call(command, cwd=actual_directory)
                                        print ("--- Iteration {} complete, base job: {} ---".format(inpfil_name, oldjob_name))

                    		            ############ ENERGY CRITERIA
                                        if j==0:
                                            eleDamagei, enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control,damageTen,dicc_NeL_E)
                                            deltaPI_j = enerHtotal-PI_0
                                            print('Iteration {}, deltaPI_jama = {}\n'.format(j,deltaPI_j))
                                        else:
                                            # inpfil_namejm1 = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)+'N'+str(n+1)+'j'+str(j+1)
                                            eleDamagei, enerHtotal=PMTESCcritEneV2(inpfil_name, actual_directory, setnodeInt, control,damageTen,dicc_NeL_E)
                                            deltaPI_j = enerHtotal-PI_0
                                            print('Iteration {}, deltaPI_jama = {}\n'.format(j,deltaPI_j))
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
                                            ener_disi=ener_disi+disipadaElem
                                        #-----------------------------------------------------------    
                                        ##paso ii. Minimizacion de la funcion dagno       
                                        #-----------------------------------------------------------
                                        #copiamos los PI rotos del los pasos anteriores (k-1) para despues
                                        #seguir anadiendo los de este paso j. En cada paso j este archivo se reescribe.
                                        #cambia el archivo de datos_procesar.txt para romper en abaqus
                                        origen=working_directory_Ten+'/damageKm1.txt'
                                        destino=working_directory_Ene+'/damage_paso_ii.txt'
                                        PMTESC.cambiar_archivos(origen,destino)
                                        file_damageii=open(working_directory_Ene+'/damage_paso_ii.txt','a')
                                        #-----------------------------------------------------------
                                        eleDamage=[] #lista de elementos rotos despues de esta funcion
                                        #estas dos siguientes es solo para el archivo de control:
                                        Gc_eleme=[] #lista de la GcE por elementos posibles a romper por el CT
                                        G_eleme=[] #lista de la Gc por elementos posibles a romper por el CT
                                        #-----------------------------------------------------------
                                        #nos metemos en el blucle de los posibles elementos a romper desde el CT
                                        #para compara elemento por elemento
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
                                                for pi in range(1,5):
                                                    file_damageii.write('%d %d %e\n' % (pi , NeG, 0.0))
                                        file_damageii.close()
                                        #-----------------------------------------------------------
                                        #-----------------------------------------------------------   
                                        #almacenamiento de datos
                                        ene_damii.append([enerHtotal+ener_disi, len(eleDamage), eleDamage,G_eleme,Gc_eleme,enerHtotal,deltaPI_j,deltaPI_j+ener_disi,ener_disi])
                                        # PMTESC.crontol_file(archivo_control,ene_damii[j],n+1,j+1)
                                        # PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,newload,damageTen,ene_damii[j])
                                        print(j,len(eleDamage),enerHtotal,deltaPI_j,deltaPI_j+ener_disi,ener_disi)
                                        
                                        if j!=0:                   
                                            #if abs(ene_damii[j-1][1]-ene_damii[j][1])==error:#deberia cambiarlo por el dano de cada elemento
                                            if(collections.Counter(ene_damii[j-1][2])==collections.Counter(ene_damii[j][2])):
                                                damageN.append([ene_damii[j][0],ene_damii[j][1],ene_damii[j][2],n+1,j+1,enerHtotal,inpfil_name])
                                                print('eleDamage, iter j-1={}, iter j={}'.format(ene_damii[j-1][2], ene_damii[j][2]))
                                                #damageN[0:enerHtotal+ener_disi, 1:suma de elementos dagnado, 2:lista de NeG de elementos dagnados,  
                                                #3:lista de energia por de elemento dagnados, 4:lista de energia critica por de elemento dagnados
                                                #5:enerHtotal]
                                                
                                                # for outp_file in range(1,j):
                                                #     filen = name_files+'_m'+str(indx+1)+'_bisiter_'+str(bisiter)+'N'+str(n+1)+'j'+str(outp_file)
                                                #     filenlst=[filen+'.odb',
                                                #     filen+'.mdl',
                                                #     filen+'.res',
                                                #     filen+'.stt']
                                                #     for file in filenlst:
                                                #         if file.endswith('.odb') and outp_file!=j:
                                                #             os.remove(file)
                                                #         # if file.endswith('.odb') and outp_file<j+1:
                                                #         #     shutil.copy(file,working_directory_FFM)
                                                #         #     os.remove(file)
                                                #         else:
                                                #             os.remove(file)
                                                break
                                        #--------------------------------------------------------------------------------------
                                        #para intentar evitar que se meta en un bucle
                                        contador=ene_damii.count(ene_damii[j])
                                        if contador!=1:
                                            print('peligro bucle j=', j)
                                            exit
                                        #--------------------------------------------------------------------------------------                   
                                        origen=working_directory_Ene+'/damage_paso_ii.txt'
                                        destino=archivo_LEBIM
                                        PMTESC.cambiar_archivos(origen,destino)                                   
                                        #borrando archivos. Poner o quitar odb dependiendo de lo que se quiera
                                        list_delete = ('*.sta', '*.sim', '*.msg', '*.com', '*.jnl',\
                                                       '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc')
                                        PMTESC.borrar_archivos(list_delete)
                                        #------------------------------------------------------------
                                        #comparacion de las N y tomar energia minima
                                        #------------------------------------------------------------
                                        damageN.sort(key=lambda damageN:damageN[0],reverse=False)
                                        origen= working_directory_Ten+ '/damageKm1.txt'
                                        destino=archivo_LEBIM
                                        # PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,0,0,newload,damageTen,damageN[0],factorcoord,GtT,sigma_inf,ener_disi,deltaPI,theta2,gt1,gt2)
                                        enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6])
                                        kstepindx=enerfilenp[:,0]==k
                                        fkstepindx=enerfilenp[:,0]==k+1
                                oldjob_name = damageN[0][-1]
                                with open('elemCE_resumen.txt', 'a') as f:
                                    f.write('%d %d %d %d %d \n' % (k+1, indx+1, damageN[0][3], damageN[0][4], damageN[0][1]))
                        """
                        END OF PRESCRIBED LOAD INCREMENTS
                        """
                        # List of file extensions to delete
                        extensions_to_delete = ['*.sim', '*.com', '*.jnl','*.stt','*.prt','*.mdl','*.res','*.msg'\
                                        '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.for','*.sta']
                        for ext in extensions_to_delete:
                            # glob.glob finds all files matching the pattern
                            files_to_remove = glob.glob(ext)
                            for f in files_to_remove:
                                try:
                                    os.remove(f)
                                    "  - Deleted: {}".format(f)
                                except OSError as e:
                                    "  - Error deleting file {}: {}".format(f, e)
                        sys.exit()
            #------------------------------------------------------------
            #abro el odb con menor energia y saco los datos que quiera graficar
            #este script puede cambiar dependiendo lo que yo quiera sacar
            #------------------------------------------------------------
            # SI EL PASO KMNi DANA ELEMENTOS POR CT Y EL CE:
            if (damageN[0][1])>0 and len(damageTen)>0:
                #name_files para graficar o para el siguiente m
                name_files=name_INP+'_'+'k'+str(k+1)+'m'+str(m+1)+'n'+str(damageN[0][3])+'j'+str(damageN[0][4])
                PMTESCsalDatos.PMTESCsalDatos_CdesplaDCB(name_files, working_directory, salida_datos3, str(k+1), str(m), str(damageN[0][1]), str(damageN[0][0]), str(len(damageTen)))
                PMTESC.energy_fileDCB(archivo_energias,k+1,m+1,n+1,j+1,loadfile,damageTen,ene_damii[j])
                # files we need to export
                inp_file = os.path.join(working_directory_FFM+'\\'+name_files + '.inp')
                mdl_file = os.path.join(actual_directory+'\\'+name_files + '.mdl')
                res_file = os.path.join(actual_directory+'\\'+name_files + '.res')
                odb_file = os.path.join(actual_directory+'\\'+name_files + '.odb')
                stt_file = os.path.join(actual_directory+'\\'+name_files + '.stt')
                export_fil = [mdl_file,eumat,inp_file,res_file,stt_file]
                # export the files into the new directory
                # for f in export_fil:
                #     os.remove(f)
            
            if m>0 and damageM[m][1]==0: #si no hay ningun elemento danano salgo
                newload = loadfile_it + incre
                break
            
            #------------------------------------------------------------
            #evaluo m para seguir dentro del bucle o salir
            #------------------------------------------------------------
            #SI QUIERO CAPTAR UN SNAP-BACK DEBERIA PONER MAXIMO M=1 EN EL ARCHIVO DE ENTRADA
            if (abs(incre)/Fk)<toler and damageN[0][1]>0 and len(kfrac_list)>=2 and m>=0:
                newload = loadfile_it
                print(damageN[0][1], iter_count)
                print(abs(incre)/Fk)
                break
                
            if (abs(incre)/Fk)<toler and m>0 and damageN[0][1]==0 and len(kfrac_list)>=2:
                print(incre, (abs(Fk-Fkm1)/Fk))
                break
            
            if damageN[0][1]==0 and k>=1 and m==0: #si no hay ningun elemento danano salgo
                print(incre, (abs(Fk-Fkm1)/Fk))
                print(damageN[0][1], iter_count)
                newload = loadfile_it
                incre=(Fk-Fkm1)
                eps0=abs(incre)/Fk
                print(eps0)
                incre=incre/1.0
                break
            
            if (abs(incre)/Fk)>toler and damageN[0][1]>0 and m==0:
                print(damageN[0][1], iter_count)
                newload = loadfile_it
                incre=(Fk-Fkm1)
                eps0=abs(incre)/Fk
                print(eps0)
                incre=incre/1.0
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
    
    if k+1 > num_iteraciones and iter_count > numiter:
        print(k+1, abs(Fk-Fkm1)/Fk)
        os._exit(0)  # Exit with a status code (1 indicates an error)
        
    # THE NEXT STEP SHOULD BE PROGRAMMING THE CRACK PROPAGATION SUBSTEPS:
    if k+1 > 1:
        enerfilenp = np.loadtxt(working_directory_FFM+'/archivo_energias.txt', delimiter='\t', dtype=float, usecols=[0,1,2,3,4,5,6,7])
        kstepindx=enerfilenp[:,0]==k
        fkstepindx=enerfilenp[:,0]==k+1
        Fkm1 = enerfilenp[kstepindx,6][0]
        Fk = abs(enerfilenp[fkstepindx,6][0])
        if (abs(incre)/Fk)<toler and damageN[0][1]==0 and m!=0:
            print(incre, (abs(Fk-Fkm1)/newload))
            kfrac_list = [] #Empty list with step value and broken interface elements
            with open('elemCE_resumen.txt', 'r') as f:
                for line in f:
                    line = line.split()
                    if line:
                        line = [i for i in line]
                        kfrac_list.append(line)
                        
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
            
            list_delete = ('*.sta', '*.dat', '*.sim', '*.prt', '*.msg', '*.com', '*.jnl',\
                           '*.mtx','*.pes','*.par','*.pmg','*.ipm','*.pyc','*.log','*.stt','*.mdl','*.res')
            PMTESC.borrar_archivos(list_delete)
            end = time.time()
            timediff=end-start
            print('\n')
            print('El programa ha terminado en %.2f' %(timediff.total_seconds()/60)+' min')
            os._exit(0)  # Exit with a status code (1 indicates an error)
    k+=1;
end = time.time()
print('La simulacion ha terminado satisfactoriamente en %.2f' %((end-start)/60)+' min')