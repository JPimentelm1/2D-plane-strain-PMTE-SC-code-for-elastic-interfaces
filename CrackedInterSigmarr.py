# -*- coding: utf-8 -*-
"""
CrackedInterSigmarr:
Created on Thu May 16 13:45:27 2024
This function opens the .ODB file in the load step of the first crack onset,
proceeds to read the interface state variables, and finally writes the cracked
interface I.P. polar angle with its corresponding normal and shear stress in a .txt file.

**Interface angle is measured counterclockwise in relation to the positive X-axis
  along the symmetry plane.
@author: José Miguel Pimentel. ETSI, Universidad de Sevilla.
"""
# ********MODULE IMPORT*********
from os import chdir
from odbAccess import*
from sys import argv
import math
import numpy as np
from abaqus import *
from abaqusConstants import *
import __main__
import numpy as np
# ******************************

def CrackedInterSigmarr(name_INP, k1frac, workdir, sigmadir, working_directory_odbs, sigmac):
    
    chdir(workdir)
    name_files = name_INP + '_' + 'k' + str(k1frac[1])+ 'm' + str(k1frac[2])+ 'n' +str(k1frac[3])+ 'j' + str(k1frac[4])
    odb = openOdb(working_directory_odbs+'/'+name_files+ '.odb')
    myAssembly = odb.rootAssembly
    key_step = odb.steps.keys()
    
    lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets['NINTERFACE']
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    # path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
    # 	getSubset(region=InterElementSet).values
    path_SDV6=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV6'].\
    	getSubset(region=InterElementSet).values
    path_SDV7=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV7'].\
    	getSubset(region=InterElementSet).values
    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
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
    path_SDV17=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV17'].\
    	getSubset(region=InterElementSet).values
    path_SDV18=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV18'].\
    	getSubset(region=InterElementSet).values
    intpoint=len(path_SDV4)
    
    # factorcoord=[]; 
    theta1v=[]; theta2v=[];
    
    Gt1v=[]; Gt2v=[];
    # LOOP ITERATION TO SAVE THE INTERFACE DEBOND ANGLES & (Sigma_rr, Tau)
    for value in range(intpoint):
        Gtot=path_SDV4[value].data
        GcE=path_SDV6[value].data
        Gi=path_SDV7[value].data
        Gii=path_SDV8[value].data
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        sigmarr=path_SDV13[value].data
        sigmart=path_SDV14[value].data
        tmod=path_SDV15[value].data
        tcmod=path_SDV16[value].data
        if x > 0 : #and Gtot != 0
            thetad1=(math.atan(y/x)*(180/(math.pi)))
            theta1v.append([thetad1, sigmarr, sigmart, GcE, Gi, Gii])
            Gt1v.append(Gtot)
            # factorcoord.append([Gtot, GcT])
        elif x < 0 : #and Gtot != 0
            thetad2=180.0 - (math.atan(y/abs(x))*(180/(math.pi)))
            theta2v.append([thetad2, sigmarr, sigmart, GcE, Gi, Gii])
            Gt2v.append(Gtot)
            # factorcoord.append([Gtot, GcT])
    # Sort the theta1v() list in ascending order of the debond angle:
    theta1v.sort(key=lambda theta1v:theta1v[:][0],reverse=False)
    # Sort theta2v in ascending order:
    theta2v.sort(key=lambda theta2v:theta2v[:][0],reverse=False)
    # Append the left interface values to the right-end interface array:
    theta1vnp=np.array(theta1v); theta2vnp=np.array(theta2v)
    # thetafnp=np.concatenate((theta1vnp, theta2vnp), axis=0)
    
    # Sort the factorcoord() list in descending order of GtotT:
    # factorcoord.sort(key=lambda factorcoord:factorcoord[:][0],reverse=True)
    Gt1v.sort(key=lambda Gt1v:Gt1v,reverse=True)
    Gt2v.sort(key=lambda Gt2v:Gt2v,reverse=True)
        
    num_rows=len(theta1v)
    num_rows2=len(theta2v)
    filename=sigmadir+'/'+name_files+'_S'+str(round(sigmac*10e5))+'.txt'
    fileout1=open(filename,'w+')
    # x=[]; y=[];
    
    #DONE:
    for k in range(num_rows):
        fileout1.write('\n%.6f\t%e\t%e\t%e\t%e\t%e' \
                      % (theta1v[k][0], theta1v[k][1], theta1v[k][2], theta1v[k][3], theta1v[k][4], theta1v[k][5]))
    for j in range(num_rows2):
        fileout1.write('\n%.6f\t%e\t%e\t%e\t%e\t%e' \
                      % (theta2v[j][0], theta2v[j][1], theta2v[j][2], theta2v[j][3], theta2v[j][4], theta2v[j][5]))
    
    fileout1.close()
    thetafnp=np.loadtxt(filename, delimiter='\t', dtype=float)        
    return thetafnp
    odb.close()

def CrackedInterSigmarr2F(name_INP, k1frac, workdir, sigmadir, working_directory_odbs, sigmac, xcf2, ycf2):
    """

    Parameters
    ----------
    name_INP : TYPE
        DESCRIPTION.
    k1frac : TYPE
        DESCRIPTION.
    workdir : TYPE
        DESCRIPTION.
    sigmadir : TYPE
        DESCRIPTION.
    working_directory_odbs : TYPE
        DESCRIPTION.
    sigmac : TYPE
        DESCRIPTION.
    xcf2 : TYPE
        DESCRIPTION.
    ycf2 : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    chdir(workdir)
    name_files = name_INP + '_' + 'k' + str(k1frac[1])+ 'm' + str(k1frac[2])+ 'n' +str(k1frac[3])+ 'j' + str(k1frac[4])
    odb = openOdb(working_directory_odbs+'/'+name_files+ '.odb')
    key_step = odb.steps.keys()
    
    # lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets['NINTERFACE']
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
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
    path_SDV17=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV17'].\
    	getSubset(region=InterElementSet).values
    path_SDV18=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV18'].\
    	getSubset(region=InterElementSet).values
    intpoint=len(path_SDV4)
    
    # factorcoord=[]; 
    theta1v=[]; 
    thetaf2v=[]; 
    # thetaf2v2=[];
    Gt1v=[]; Gt2v=[];
    # LOOP ITERATION TO SAVE THE INTERFACE DEBOND ANGLES & (Sigma_rr, Tau)
    for value in range(intpoint):
        # ip=path_SDV2[k].integrationPoint #integration point data
        # NeG=path_SDV2[k].data #global element number
        NeInstance=str(path_SDV2[value].elementLabel)+'_'+str(path_SDV2[value].instance.name)
        Gtot=path_SDV4[value].data
        # GcT=path_SDV5[value].data
        Gi=path_SDV17[value].data
        Gii=path_SDV18[value].data
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        sigmarr=path_SDV13[value].data
        sigmart=path_SDV14[value].data
        t=path_SDV15[value].data
        tc=path_SDV16[value].data
        if NeInstance.endswith('_INTERFACE-1'):
            if x > 0 and y > 0: #quadrant I
                thetad1=(math.atan(abs(y)/x)*(180/(math.pi)))
                theta1v.append([thetad1, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                Gt1v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif x > 0 and y < 0: #quadrant 4
                thetad1=360.00 - (math.atan(abs(y)/x)*(180/(math.pi)))
                theta1v.append([thetad1, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                Gt1v.append(Gtot)
            elif x < 0 and y > 0: #quadrant 2
                thetad2=180.00 - (math.atan(abs(y)/-x)*(180/(math.pi)))
                theta1v.append([thetad2, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                Gt2v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif x < 0 and y < 0: #quadrant 3
                thetad2=180 + (math.atan(abs(y)/-x)*(180/(math.pi)))
                theta1v.append([thetad2, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                Gt2v.append(Gtot)
        elif NeInstance.endswith('_INTERFACE-2'):
            if (x-xcf2) > 0 and (y-ycf2) > 0: #quadrant 1
                thetaf2d=math.atan(abs(y-ycf2)/(x-xcf2))*(180/(math.pi))
                thetaf2v.append([thetaf2d, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                # Gtf2v1.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif (x-xcf2) < 0 and (y-ycf2) > 0: #quadrant 2
                thetaf2d=180.00 - math.atan(abs(y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                thetaf2v.append([thetaf2d, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                # Gtf2v2.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif (x-xcf2) < 0 and (y-ycf2) < 0: #quadrant 3
                thetaf2d=180.00 + math.atan(abs(y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                thetaf2v.append([thetaf2d, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                # Gtf2v2.append(Gtot)
            elif (x-xcf2) > 0 and (y-ycf2) < 0: #quadrant 4
                thetaf2d=360.00 - math.atan(abs(y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                thetaf2v.append([thetaf2d, sigmarr, sigmart, t, tc, Gtot, Gi, Gii])
                # Gtf2v2.append(Gtot)
    # Sort the theta1v() list in ascending order of the debond angle:
    theta1v.sort(key=lambda theta1v:theta1v[:][0],reverse=False)
    thetaf2v.sort(key=lambda thetaf2v1:thetaf2v1[:][0],reverse=False)
    theta1vnp=np.array(theta1v)
    thetaf2vnp=np.array(thetaf2v)
    # Gt1v.sort(key=lambda Gt1v:Gt1v,reverse=True)
    # Gt2v.sort(key=lambda Gt2v:Gt2v,reverse=True)
    
    num_rows=len(theta1v)
    num_rows2=len(thetaf2v)
    filename=sigmadir+'/interf1_'+name_files+'_S'+str(round(sigmac*10e5))+'.txt'
    fileout1=open(filename,'w+')
    filename2=sigmadir+'/interf2_'+name_files+'_S'+str(round(sigmac*10e5))+'.txt'
    fileout2=open(filename2,'w+')
    # Write the list rows into a text .txt file:
    #DONE:
    for k in range(num_rows):
        fileout1.write('\n%.6f\t%e\t%e\t%e\t%e\t%e' \
                      % (theta1v[k][0], theta1v[k][1], theta1v[k][2], theta1v[k][3], theta1v[k][4], theta1v[k][5]))
    for j in range(num_rows2):
        fileout2.write('\n%.6f\t%e\t%e\t%e\t%e\t%e' \
                      % (thetaf2v[j][0], thetaf2v[j][1], thetaf2v[j][2], thetaf2v[j][3], thetaf2v[j][4], thetaf2v[j][5]))
            
    fileout1.close()
    fileout2.close()
    return theta1vnp, thetaf2vnp
    odb.close()