# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 16:53:20 2019

@author: MAR
"""
#-------------------------------------------------------
#funcion para hacer un diccionario con las referencia de los nodos
#de local a global
#-------------------------------------------------------

from os import remove
from glob import glob
from shutil import copyfileobj, copy
import numpy as np

def get_dicc_nodes(file_name,instance):
    
    #print(instance)
    NnG_NnL={}
    lineas=[]
    part_file = open(file_name, 'r') # abrimos el fichero en modo lectura
    ter='0'
    
    for line in enumerate(part_file):
        lineas.append(line)
        
    p=0
    
    
    for i in range(len(lineas)): 
        line=lineas[i][1].split("\n")
    
        if line[0]==instance:
            p=p+1
    
        if p==2:
            ter=lineas[i+1][1].split(" ") 
    
            break
    
    Nnodos=int(ter[0])
    
    for j in range(i+2,i+2+Nnodos):
        ter=lineas[j][1].split(" ")
        NnG_NnL.update({int(ter[0]):int(ter[1])})  
    
    part_file.close()
    #print(NnG_NnL)
    #print(p)
    
    return NnG_NnL
#-------------------------------------------------------
#funcion para obtener las matrices de rigidez
###NO UTILIZADA NI EN V13 NI EN V14
#-------------------------------------------------------
def get_stiffness_matrix(file_name):
    
    stiffness_matrix = open(file_name, 'r') # abrimos el fichero en modo lectura
    m_stiffness={}
    stiffness=[]
    lineas=[]
    
    for line in enumerate(stiffness_matrix):
        lineas.append(line)
        
    for i in range(len(lineas)): 
        line=lineas[i][1]
        ter = line.split() 
    
        if len(ter)> 2 and ter[1]=='ELEMENT' and ter[2]=='NUMBER':
            enteros=[int(s) for s in line.split() if s.isdigit()]
            stiffness.append(enteros[0])    
    
        if len(ter)> 2 and ter[1]=='ELEMENT' and ter[2]=='NODES':
            line=lineas[i+1][1]
            enteros=line.split()
            enteros2=[]
            for j in range(1,len(enteros)):
                cadena=enteros[j]
                enteros2.append([int(s) for s in cadena.split(',') if s.isdigit()])
            stiffness.append(enteros2)
    
        if ter[0]=='*MATRIX,TYPE=STIFFNESS':
            ksalta=[1, 2, 3, 4, 5, 7, 9, 11]
            ksalta2=[1, 2, 3, 4, 6, 8, 10,12]
            matrix=[]
            for k in range(1,13):
                line=lineas[i+k][1]
                ter = line.split()            
                for m in ksalta:
                    if k==m:
                        vector=[]
                for j in range(len(ter)):
                    prueba=(ter[j].split(','))[0]
                    try:
                        vector.append(float(prueba))
                    except:
                        continue
                
                for m in ksalta2:
                    if k==m:
                        matrix.append(vector)
            for j in range(len(matrix)):
                for p in range(j+1,len(matrix)):
                    matrix[j].append(matrix[p][j])
            stiffness.append(matrix)
            
        if len(stiffness)==3:
            m_stiffness.update({int(stiffness[0]):[stiffness[1],stiffness[2]]})
            stiffness=[]
            
    stiffness_matrix.close()            
    return m_stiffness

#-------------------------------------------------------
#funcion para obtener las matrices de rigidez
#-------------------------------------------------------
            
def get_dicc_file(file_name):

    disp_file = open(file_name, 'r') # abrimos el fichero en modo lectura
    lineas=[]    
    diccionario={}
    for line in enumerate(disp_file):
        lineas.append(line)
        
    for i in range(len(lineas)):
        ternum2=[]
        line=lineas[i][1]
        ter = line.split(" ")
        keyd=int(ter[0])
        for j in range(1,len(ter)):
            try:
                ternum=float(ter[j])
                ternum2.append(ternum)
            except ValueError:
                continue

        diccionario.update({keyd:ternum2})
    
    disp_file.close()    
    return diccionario

#-------------------------------------------------------
#funcion para obtener una lista desde un archivo
#-------------------------------------------------------

def get_list_file(file_name):

    disp_file = open(file_name, 'r') # abrimos el fichero en modo lectura
    lineas=[]    
    lista=[]
    for line in enumerate(disp_file):
        lineas.append(line)
        
    for i in range(len(lineas)):
        ternum2=[]
        line=lineas[i][1]
        ter = line.split(" ")
        for j in range(len(ter)):
            try:
                ternum=float(ter[j])
                ternum2.append(ternum)
            except ValueError:
                continue

        lista.append(ternum2)
    
    disp_file.close()    
    return lista

def get_list_file2(file_name):

    disp_file = open(file_name, 'r') # abrimos el fichero en modo lectura
    lineas=[]    
    lista=[]
    for line in enumerate(disp_file):
        lineas.append(line)
        
    for i in range(len(lineas)):
        ternum2=[]
        line=lineas[i][1]
        ter = line.split(" ")
        for j in range(len(ter)):
            try:
                ternum=float(ter[j])
                ternum2.append(ternum)
            except ValueError:
                ternum=str(ter[j])
                ternum2.append(ternum)
                continue

        lista.append(ternum2)
    
    disp_file.close()    
    return lista

#-------------------------------------------------------
#escribir el nuevo archivo de dano para que lo lea la UMAT
###NO UTILIZADA EN V14
#-------------------------------------------------------
def write_file_damage(file_name,damageKm1,damageNew):
    damage_file=open(file_name,'w')      
    for m in range(len(damageKm1)):
        damage_file.write('%d %d \n'
    		% (damageKm1[m][0],damageKm1[m][1]))
        
    for nE in range(int(len(damageNew))):
        damage_file.write('%d %d \n'
         % (1 , int(damageNew[nE])))
        damage_file.write('%d %d \n'
         % (2 , int(damageNew[nE])))
        damage_file.write('%d %d \n'
         % (3 , int(damageNew[nE])))
        damage_file.write('%d %d \n'
         % (4 , int(damageNew[nE])))
    damage_file.close()

#-------------------------------------------------------
#escribir el archivo de control para inicio de paso
#-------------------------------------------------------
#escribo la lista de NeG que se dagnan con el criterio tensional damageTen[j][0]
#si quiero sacar el NeG deberia escribir damageTen[j][1]
def crontol_file_paso(file_name,damageTen,pasok,pasom):
    control_file=open(file_name,'a')
    control_file.write('\n')
    control_file.write('Paso k= %d \t Paso m= %d \n' %(pasok,pasom))
    control_file.write('%d Elementos dagnados por el criterio tensional:\t' %(len(damageTen)))	
    for j in range(len(damageTen)):
        b=str(int(damageTen[j][0]))+' '
        control_file.write(b+' ')
    control_file.write('\n')        
    control_file.close()    

#-------------------------------------------------------
#escribir el archivo de control para inicio de paso
#-------------------------------------------------------
#escribo la lista de NeG que se dagnan con el criterio tensional damageTen[j][0]
#si quiero sacar el NeG deberia escribir damageTen[j][1]
def crontol_file_pasoMF(file_name,damageTen,pasok,pasom,nfibers):
    control_file=open(file_name,'a')
    control_file.write('\n')
    control_file.write('Paso k= %d \t Paso m= %d \n' %(pasok,pasom))
    control_file.write('No. total de fibras con grietas de interfase: %d \n' %(nfibers))
    control_file.write('%d Elementos dagnados por el criterio tensional:\t' %(len(damageTen)))	
    for j in range(len(damageTen)):
        b=str(int(damageTen[j][0]))+' '
        control_file.write(b+' ')
    control_file.write('\n') 
    control_file.close()
#-------------------------------------------------------
#escribir el archivo de control
#-------------------------------------------------------
    
#def crontol_file(file_name,lista,s,t):
#    control_file=open(file_name,'a')
#    control_file.write('N=%d\t j=%d \n' % (s,t))	
#    for j in range(len(lista)):
#        b=str(lista[j])+' '
#        control_file.write(b)     
#    control_file.write('\n')        
#    control_file.close()

def crontol_file(file_name,lista,s,t):
    control_file=open(file_name,'a')
    control_file.write('n=%d\t j=%d \n' % (s,t))
    ener=str(lista[5])
    control_file.write('(i)Energía_h del paso='+ener+'\n')
    
    enerTotal=str(lista[0])
    NelemtsD=str(lista[1])   
    elemtsD=str(lista[2])
    Elemets=str(lista[3])
    Eclemets=str(lista[4])
    
    control_file.write('(i)Energía total del paso='+enerTotal+'\n')
    control_file.write('(ii)Elementos a dañados por CE='+NelemtsD+'\t')
    control_file.write('Etiquetas de elementos dañados='+elemtsD+'\t')
    control_file.write('Energía por elementos='+Elemets+'\t')
    control_file.write('Energía crítica por elementos='+Eclemets+'\t')
    
    control_file.write('\n')        
    control_file.close()
    #se debe tener en cuenta que los elementos dagnados segun el CE despues del 
    #paso ii del paso j, es lo que propone la minimizacion de la energia segun el dagno
    #pero al final de ese paso j la energia calculada es con los elementos
    #dagnados del paso j anterior
    #el dagno se actualiza en el siguiente paso 
#-------------------------------------------------------
#escribir el archivo de control final
#-------------------------------------------------------

def crontol_file_final(file_name,lista,pasok,pasom):
    control_file=open(file_name,'a')
    control_file.write('\n')
    control_file.write('Final del Paso k= %d y Paso m= %d\n' %(pasok,pasom))

    ener=str(lista[0])
    NelemtsD=str(lista[1])
    elemtsD=str(lista[2])
    tipoN=str(lista[3])
    tipoj=str(lista[4])
    
    control_file.write('Energía total='+ener+'\t')
    control_file.write('Elementos dañados='+NelemtsD+'\t')
    control_file.write('Etiquetas de elementos dañados='+elemtsD+'\n')
    control_file.write('Daño total de la n='+tipoN+'\t')
    control_file.write('obtenida en la j='+tipoj+'\t')

    control_file.write('\n')        
    control_file.close()
    
#-------------------------------------------------------
#escribir fichero de energia para poder graficarlas crontol_file:
#Esta funcion es para escribir cuando el criterio tensional no rompe nada
#-------------------------------------------------------
#escribo la lista de NeG que se dagnan con el criterio tensional damageTen[j][0]
#si quiero sacar el NeG deberia escribir damageTen[j][1]
def energy_file_CTO(file_name,pasok,pasom,pason,pasoj,newload,damageTen,thetad,gtotalt,sigmaxinf):
    control_file=open(file_name,'a')
    #escribimos k m n j
    control_file.write('%d\t %d\t %d\t %d\t'%(pasok,pasom,pason,pasoj))
    #escribimos el numero de elementos que se rompen por criterio tensional
    numeleten=len(damageTen)
    control_file.write('%d\t'%(numeleten))
    #escribimos el numero de elementos que se rompen por criterio energetico=0
    NelemtsD=0
    control_file.write('%d\t'%(NelemtsD))
    #escribimos la carga o el desplazamiento impuesto
    control_file.write(str(newload)+'\t')
    # remote applied x-stress
    control_file.write(str(sigmaxinf)+'\t')
    #escribimos la energia interna y la energia interna mas disipada (total)
    #como todavia no ha roto nada no se calcula
    enerinterna=str(0.00)
    enerTotal=str(0.00)
    control_file.write(enerinterna+'\t')
    control_file.write(enerTotal+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\t')
    control_file.write(str(0.0)+'\n')
    control_file.close()
#-------------------------------------------------------
#escribir fichero de energia para poder graficarlas crontol_file(file_name,lista,s,t): 
#-------------------------------------------------------
def energy_file(file_name,pasok,pasom,pason,pasoj,newload,damageTen,listaene,thetad,gtotalt,sigmaxinf,deltaR,deltaPI,thetad2,gtr,gtl):
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
    control_file.write(str(gtl)+'\n')
    control_file.close()
    #se debe tener en cuenta que los elementos dagnados segun el CE despues del 
    #paso ii del paso j, es lo que propone la minimizacion de la energia segun el dagno
    #pero al final de ese paso j la energia calculada es con los elementos
    #dagnados del paso j anterior
    #el dagno se actualiza en el siguiente paso     

def energy_fileMF_CTO(file_name,pasok,pasom,pason,pasoj,newload,damageTen):
    control_file=open(file_name,'a')
    #escribimos k m n j
    control_file.write('%d\t %d\t %d\t %d\t'%(pasok,pasom,pason,pasoj))
    #escribimos el numero de elementos que se rompen por criterio tensional
    numeleten=len(damageTen)
    control_file.write('%d\t'%(numeleten))
    #escribimos el numero de elementos que se rompen por criterio energetico=0
    NelemtsD=0
    control_file.write('%d\t'%(NelemtsD))
    #escribimos la carga o el desplazamiento impuesto
    control_file.write(str(newload)+'\t')
    #
    #escribimos la energia interna y la energia interna mas disipada (total)
    #como todavia no ha roto nada no se calcula
    enerinterna=str(0.00)
    enerTotal=str(0.00)
    control_file.write(enerinterna+'\t')
    control_file.write(enerTotal+'\n')
    # control_file.write(gct+'\n')
    control_file.close()    
#-------------------------------------------------------
#escribir fichero de energia para poder graficarlas crontol_file(file_name,lista,s,t): 
#-------------------------------------------------------
def energy_fileMF(file_name,pasok,pasom,pason,pasoj,newload,damageTen,listaene,delPI,delR):
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
    #escribimos la energia interna y la energia interna mas disipada (total)
    enerinterna=str(listaene[5])
    enerTotal=str(listaene[0])
    control_file.write(enerinterna+'\t') #PI
    control_file.write(enerTotal+'\t') #PI+deltaR
    # evaluacion de deltaPI + deltaR:
    delPIdelR=delPI+delR
    # se escribe a deltaPI, deltaR, y deltaPI+deltaR
    control_file.write(str(delPI)+'\t')
    control_file.write(str(delR)+'\t')
    control_file.write(str(delPIdelR)+'\n')
    control_file.close()
    #se debe tener en cuenta que los elementos dagnados segun el CE despues del 
    #paso ii del paso j, es lo que propone la minimizacion de la energia segun el dagno
    #pero al final de ese paso j la energia calculada es con los elementos
    #dagnados del paso j anterior
    #el dagno se actualiza en el siguiente paso       
#---------------------------------------------------
#escribir el fichero de datos
#--------------------------------------------------
def write_load_file(load_file,floatnumber):
    fich_carga= open(load_file,'w')
    fich_carga.write(str(floatnumber))
    fich_carga.write('\n')
    fich_carga.close()
    
#---------------------------------------------------
#escribir un archivo de una lista, anadiendo
#--------------------------------------------------
def write_file_add(file_name,lista):
    control_file=open(file_name,'a')
	
    for j in range(len(lista)):
        b=str(lista[j])+' '
        control_file.write(b)     
    control_file.write('\n')        
    control_file.close()
    
#---------------------------------------------------
#borrando archivos
#--------------------------------------------------    
def borrar_archivos(list_delete):
    for files in list_delete:
        files_delete = glob(files)
        for k in range(len(files_delete)):
            remove(files_delete[k])
            
#---------------------------------------------------
#sustituye un archivo por otro
#--------------------------------------------------             
def cambiar_archivos(origen,destino):
    with open(origen, 'rb') as forigen:
        with open(destino, 'wb') as fdestino:
            copyfileobj(forigen, fdestino)
    forigen.close()
    fdestino.close()
            
#---------------------------------------------------
#escribir nuevo fichero INP con parametro de carga
#---------------------------------------------------
def cambiar_cadena(originalfile,copyfile,old_cadena,new_cadena):
    f1 = open(originalfile,   'r')
    f2 = open(copyfile, 'w')
    for line in f1:
        f2.write(line.replace(old_cadena, new_cadena))
    f1.close()
    f2.close()


#---------------------------------------------------
#sacar la energia disipada en el paso i despues de cada FEM
###NO UTILIZADA EN V14
#--------------------------------------------------
#esto dependera de con cuantos elementos rotos comencemos cada N
#ahora mismo con 0 o con todos los del CT             
def optimi_damagei(damageEG_L,eleDamage):
    elem_posib=len(damageEG_L)
    elem_dana=len(eleDamage)
    Ecri_inter=0
    for nEd in range(elem_dana):
        for nEp in range(elem_posib):
            if eleDamage[nEd]==damageEG_L[nEp][0]:
                Ecri_inter=damageEG_L[nEp][2]+Ecri_inter
                break
    return Ecri_inter

#---------------------------------------------------
#sacar la energia disipada en el paso i despues de cada FEM new
###NO UTILIZADA EN V14
#--------------------------------------------------
#con esta funcion se calcula la energia disipada en el paso i
#ahora mismo con 0 o con todos los del CT 
#la minimizazion del dagno es: zG+(z-1)GcE
#suponiendo z=0 dagnado y z=1 no dagnado            
def optimi_damageinew(eleDamagei):
    Enerdisi=0.0
    for nEd in eleDamagei:
        disipadaElem=nEd[5]*(1.0-nEd[6])
        Enerdisi=Enerdisi+disipadaElem
    return Enerdisi

#---------------------------------------------------
#hacer la optimizacion del paso ii con PIntegracion. Es solo comparar en cada elemento Gc y la G
###NO UTILIZADA EN V14
#--------------------------------------------------  
def optimi_damageii(working_directory_Ene,damageKm1,damageEG_L):            
    #------------------------------------------------------------
    #los datos del criterio Tensional:
    #------------------------------------------------------------
    #damageKm1: los necesitos para formar el archivos siguiente de datos a procesar
    #son los elementos nuevos a romper mas los que llevo de los anteriores pasos k-1
    
    #damageEG_L: es la lista de elementos posibles desde el CT
    #------------------------------------------------------------
    #sacamos los datos criterio Energetico
    #------------------------------------------------------------
    #energiaNL=FFM.get_dicc_file(working_directory_Ene+'/archivoEneElements_paso_i.txt')	
    energiaNL=get_dicc_file(working_directory_Ene+'/archivoEneElements_paso_i.txt')
    #-----------------------------------------------------------
    elementos=len(damageEG_L) #numero de posibles elementos a romper por el CT
    eleDamage=[] #lista de elementos rotos despues de esta funcion
    #estas dos siguientes es solo para el archivo de control:
    Gc_eleme=[] #lista de la GcE por elementos posibles a romper por el CT
    G_eleme=[] #lista de la Gc por elementos posibles a romper por el CT
    #-----------------------------------------------------------
    #copiamos los PI rotos del los pasos anteriores (k-1) para despues
    #seguir anadiendo los de este paso j. En cada paso j este archivo se reescribe.    
    file_damageii=open(working_directory_Ene+'/damage_paso_ii.txt','w')      
    for m in range(len(damageKm1)):
        file_damageii.write('%d %d \n'
    		% (damageKm1[m][0],damageKm1[m][1]))   
    #-----------------------------------------------------------
    #nos metemos en el blucle de los posibles elementos a romper desde el CT
    #para compara elemento por elemento
    for nE in range(elementos):
        #energia critica por elemento
        NeG=int(damageEG_L[nE][0])
        enerCrElem=damageEG_L[nE][2]   
        enerEUndamage=energiaNL.get(NeG)[2]
        enerEDamage=energiaNL.get(NeG)[3]
        #para control:
        Gc_eleme.append(enerCrElem+enerEDamage)
        G_eleme.append(enerEUndamage)
        #comparacion:
        if enerEUndamage>=enerCrElem+enerEDamage:
            eleDamage.append(damageEG_L[nE][0])
            file_damageii.write('%d %d \n'
             % (1 , int(damageEG_L[nE][0])))
            file_damageii.write('%d %d \n'
             % (2 , int(damageEG_L[nE][0])))
            file_damageii.write('%d %d \n'
             % (3 , int(damageEG_L[nE][0])))
            file_damageii.write('%d %d \n'
             % (4 , int(damageEG_L[nE][0])))
    file_damageii.close()            
    return eleDamage,G_eleme,Gc_eleme

