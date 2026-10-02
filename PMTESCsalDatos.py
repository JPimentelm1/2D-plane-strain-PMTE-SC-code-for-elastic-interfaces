"""
# ********************************************************************************
# MODULOS DE POSTPROCESADO ODB PARA ESCRIBIR EN FICHEROS Y RETORNAR INFORMACION
# DEL MODELO M.E.F.
# ********************************************************************************
# Modificaciones: Jose Pimentel
"""
#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB   ||||   	   
#-------------------------------------------------------
from os import chdir
from odbAccess import*
from sys import argv
import sys
import math
import numpy as np
# Redirect stdout to the command prompt
sys.stdout = sys.__stdout__

def PMTESCsalDatos_CdesplaDCB(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen):
    #este archivo esta prepardo para sacar los datos del control en desplzamientos con RF (reaccion)
    #antes he tenido que guardar en el modelo el HISTORY OUTPUT para los nodos que quiera sacar:
    #RF1, RF2, U2
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    

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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    
    
    path_HisRegU21 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegU22 = odb.steps[key_step[0]].historyRegions[key_HisReg[2]]
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    U21 = path_HisRegU21.historyOutputs['U1'].data[1][1] #U2 para la DCB
    U22 = path_HisRegU22.historyOutputs['U1'].data[1][1] #U2 para la DCB
    F21 = path_HisRegU21.historyOutputs['RF1'].data[1][1] #RF2 para la DCB
    F22 = path_HisRegU22.historyOutputs['RF1'].data[1][1] #RF2 para la DCB
    
    #---------------------------------------------------
    #escribir el fichero de datos
    #--------------------------------------------------
    #chdir(working_directory_Ene) 
    
    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(U21)+'\t'+str(U22)+'\t'+str(F21)+'\t'+str(F22)
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()

def PMTESCsalDatos_SFLoad(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen, nstep, damage_file, Gcpsi):

    chdir(working_directory)
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
    # fileINPUT = open('inputFFMLEBIM_adaptivef.txt','r')
    # flag = fileINPUT.readline()
    # name_INP = fileINPUT.readline().rstrip()
    # fileINPUT.close()
    # inp_file_path = working_directory+'/'+name_INP+'.inp'
    # with open(inp_file_path, 'r') as inp_file:
    #     inp_lines = inp_file.readlines()
    # first_param, GIc, mu_const, interfh, xi, lambdhs = sigmac_parameter(inp_lines)
    
    odb = openOdb(name_files + '.odb')
    myAssembly = odb.rootAssembly
    working_directory_FFM=working_directory+'/FFM_optimizada01'
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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets['NINTERFACE']
    # path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    # 	getSubset(region=InterElementSet).values
    # path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    #     getSubset(region=InterElementSet).values  #NEL global
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
    	getSubset(region=InterElementSet).values    
    path_SDV6=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV6'].\
    	getSubset(region=InterElementSet).values  
    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
    	getSubset(region=InterElementSet).values  
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values 
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
    	getSubset(region=InterElementSet).values
    path_SDV12=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV12'].\
    	getSubset(region=InterElementSet).values
    path_SDV13=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV13'].\
    	getSubset(region=InterElementSet).values
    path_SDV14=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV14'].\
    	getSubset(region=InterElementSet).values
    path_SDV15=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV15'].\
    	getSubset(region=InterElementSet).values
    path_SDV19=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV19'].\
    	getSubset(region=InterElementSet).values
    intpoint=len(path_SDV4)
    
    theta1v=[]; theta2v=[]; 
    
    Gt1v=[]; Gt2v=[];
    # Access the assembly and instance
    # Access the assembly and instance
    # assembly = odb.rootAssembly
    
    # Access the assembly instances
    instance1 = odb.rootAssembly.instances['INTERFACE1-1']
    instance2 = odb.rootAssembly.instances['INTERFACE2-1']
    
    # Ensure both instances have the same number of elements
    if len(instance1.elements) != len(instance2.elements):
        raise ValueError("Instances must have the same number of elements")
    inst1node_coords=[]
    inst2node_coords=[]
    
    # Access the field output for user-defined state variable SDV1
    field_output1 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance1).values
    field_output2 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance2).values
    
    # integration points and data into a single list for element_output
    data_values1 = np.array([value.data for value in field_output1 if value.integrationPoint==1])
    
    # integration points and data into a single list for element_output
    data_values2 = np.array([value.data for value in field_output2 if value.integrationPoint==1])
    
    # list comprehension of the damaged elements file:
    damage_file = np.array(damage_file)
    # Use np.any() or np.all() to make the comparison explicit
    damage_fileset = [value for value in damage_file if np.any(damage_file[0] == 1)]
    
    if len(damage_fileset)!=0:
                # Loop through elements in both instances and get nodal coordinates
                for indx in damage_fileset:
                    for elem1, elem2 in zip(data_values1, data_values2):
                        if (indx[2]==0.0 and indx[0]==1) and (indx[1]==elem1):
                            # print(elem1.data, elem2.data)
                            locel1=instance1.elements[indx[-1] - 1]
                            # locel2=instance2.elements[indx[-1] - 1]
                            node_labels1 = locel1.connectivity
                            # node_labels2 = locel2.connectivity
                            for node_label1 in node_labels1:
                                node1 = instance1.nodes[node_label1-1] # Adjust for 0-based indexing
                                # node2 = instance2.nodes[node_label2-1]  # Adjust for 0-based indexing
                                coordinates1 = node1.coordinates
                                # coordinates2 = node2.coordinates
                                
                                # instancelist.append([instance1.name, elem1.data, coordinates1[0], coordinates1[1], \
                                #       math.sqrt(math.pow(coordinates1[0],2)+math.pow(coordinates1[1],2))])
                                # instancelist.append([instance2.name, elem2.data, coordinates2[0], coordinates2[1], \
                                #       math.sqrt(math.pow(coordinates2[0],2)+math.pow(coordinates2[1],2))])
                                
                                inst1node_coords.append([instance1.name, elem1, coordinates1[0], coordinates1[1], indx[2]])
                                # inst2node_coords.append([instance2.name, elem2.data, coordinates2[0], coordinates2[1], indx[2]])                    
                        
                        if (indx[2]==0.0 and indx[0]==1) and (indx[1]==elem2):
                            # locel1=instance1.elements[indx[-1] - 1]
                            locel2=instance2.elements[indx[-1] - 1]
                            # node_labels1 = locel1.connectivity
                            node_labels2 = locel2.connectivity
                            for node_label2 in node_labels2:
                                # node1 = instance1.nodes[node_label1-1]  # Adjust for 0-based indexing
                                node2 = instance2.nodes[node_label2-1]  # Adjust for 0-based indexing
                                
                                # coordinates1 = node1.coordinates
                                coordinates2 = node2.coordinates
                                
                                # instancelist.append([instance1.name, elem1.data, coordinates1[0], coordinates1[1], \
                                #       math.sqrt(math.pow(coordinates1[0],2)+math.pow(coordinates1[1],2))])
                                # instancelist.append([instance2.name, elem2.data, coordinates2[0], coordinates2[1], \
                                #       math.sqrt(math.pow(coordinates2[0],2)+math.pow(coordinates2[1],2))])
                                
                                # inst1node_coords.append([instance1.name, elem1.data, coordinates1[0], coordinates1[1], indx[2]])
                                inst2node_coords.append([instance2.name, elem2, coordinates2[0], coordinates2[1], indx[2]])
                if len(inst1node_coords)!=0:
                    inst1node_coords.sort(key=lambda inst1node_coords:inst1node_coords[:][3], reverse=True)
                if len(inst2node_coords)!=0:
                    inst2node_coords.sort(key=lambda inst2node_coords:inst2node_coords[:][3], reverse=True)
    # Computation of debond semiangles:
    if len(inst1node_coords)!=0:
        # and (nstep==0 or nstep==1 or nstep==3 or nstep==4)
        # instancelist.sort(key=lambda instancelist:instancelist[:][2],reverse=True) 
        print(inst1node_coords[0])
            # right fiber pole
        ymax=inst1node_coords[0][3]
        ym1=inst1node_coords[1][3]
        ymax_avg=0.5*(ymax+ym1)
        xmax=inst1node_coords[0][2]
        xm1=inst1node_coords[1][2]
        xmax_avg=0.5*(xmax+xm1)
        theta1_ang=(math.atan(ymax_avg/xmax_avg)*(180/(math.pi)))
        if len(inst2node_coords)!=0 and inst2node_coords[0][-1]==0:
            ymaxl=inst2node_coords[0][3]
            ym1l=inst2node_coords[1][3]
            ymaxl_avg=0.5*(ymaxl+ym1l)
            xmaxl=inst2node_coords[0][2]
            xm1l=inst2node_coords[1][2]
            if xmaxl<0.0 and xm1l<0.0:
                xmaxl=abs(xmaxl); xm1l=abs(xm1l) 
            xmaxl_avg=0.5*(xmaxl+xm1l)
            theta2_ang=(math.atan(ymaxl_avg/xmaxl_avg)*(180/(math.pi)))
        elif len(inst2node_coords)==0: 
            theta2_ang=0.0
    if len(inst2node_coords)!=0:
        # and (nstep==0 or nstep==2 or nstep==3 or nstep==4)
        # left fiber pole
        print(inst2node_coords[0])
        ymaxl=inst2node_coords[0][3]
        ym1l=inst2node_coords[1][3]
        ymaxl_avg=0.5*(ymaxl+ym1l)
        xmaxl=inst2node_coords[0][2]
        xm1l=inst2node_coords[1][2]
        if xmaxl<0.0 and xm1l<0.0:
            xmaxl=abs(xmaxl); xm1l=abs(xm1l) 
        xmaxl_avg=0.5*(xmaxl+xm1l)
        theta2_ang=math.atan(ymaxl_avg/xmaxl_avg)*(180/(math.pi))
        if len(inst1node_coords)!=0 and inst1node_coords[0][-1]==0:
            ymax=inst1node_coords[0][3]
            ym1=inst1node_coords[1][3]
            ymax_avg=0.5*(ymax+ym1)
            xmax=inst1node_coords[0][2]
            xm1=inst1node_coords[1][2]
            xmax_avg=0.5*(xmax+xm1)
            theta1_ang=(math.atan(ymax_avg/xmax_avg)*(180/(math.pi)))
        elif len(inst1node_coords)==0: 
            theta1_ang=0.0
    else:
        if len(inst1node_coords)==0: theta1_ang=0.0
        if len(inst2node_coords)==0: theta2_ang=0.0
    
    # FOR LOOP TO SAVE THE INTERFACE ERRs
    factorcoord=[]; 
    for value in range(intpoint):
        Gtot=path_SDV4[value].data
        # GcT=path_SDV5[value].data
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        GtE=path_SDV12[value].data
        G2E=path_SDV8[value].data
        # GcE=path_SDV6[value].data
        # psi_g=math.atan2(path_SDV14[value].data*(math.sqrt(1/xi)), path_SDV13[value].data); \
        # GcE=float(GIc)*(1+(math.tan(psi_g*(1-lambdhs)))**2)*(mu_const/interfh); psi_gc=(math.pi)/(2*(1-lambdhs)); 
        # if abs(psi_g)>=psi_gc: 
        #     GcE=GIc*1E8
        # sigmarr=path_SDV13[value].data
        # sigmart=path_SDV14[value].data
        
        if x > 0 :
            thetad=(math.atan(y/x)*(180/(math.pi)))
            Gt1v.append(Gtot)
            # GcE=min(GcE, 1E-1)
            factorcoord.append([thetad, G2E, GtE])
        elif x < 0 :
            thetad=180.0 - (math.atan(y/abs(x))*(180/(math.pi)))
            Gt2v.append(Gtot)
            # GcE=min(GcE, 1E-1)
            factorcoord.append([thetad, G2E, GtE])

    # Sort the factorcoord() list in ascending order of thetad:
    factorcoord.sort(key=lambda factorcoord:factorcoord[:][0],reverse=False)
    interfip_vars = np.array(factorcoord)
    GcPsi_np=np.array(Gcpsi)
    interfip_varsn = np.concatenate([interfip_vars, GcPsi_np[:,-1].reshape(len(Gcpsi), 1)], axis=1)
    # Save the array into a text file:
        # Specify the format for each column
    header_fmt = ['%.8e', '%.8e', '%.8e', '%.8e']
    np.savetxt(working_directory_FFM+'\\'+name_files+'_ERRs.txt', interfip_varsn, fmt=header_fmt, delimiter='\t')
    Gt1v.sort(key=lambda Gt1v:Gt1v,reverse=True)
    Gt2v.sort(key=lambda Gt2v:Gt2v,reverse=True)
    
    # thetad=theta1v[0][0]
    # theta2=theta2v[0][0]
    Gt1=Gt1v[0]; Gt2=Gt2v[0];
    
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    hisreglen=len(key_HisReg)
    path_HisRegS11 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    # path_HisRegS12 = odb.steps[key_step[0]].historyRegions[key_HisReg[2]]
    for ikey in range(hisreglen):
        # print(hisreglen, odb.steps[key_step[0]].historyRegions[key_HisReg[ikey]])
        if key_HisReg[ikey].endswith('Node INTERFACE1-1.1'):
            path_HisRegUint0=odb.steps[key_step[0]].historyRegions[key_HisReg[ikey]]
            F21 = path_HisRegUint0.historyOutputs['U1'].data[1][1]
        elif key_HisReg[ikey].endswith('Node INTERFACE1-1.2'):
            path_HisRegUint1=odb.steps[key_step[0]].historyRegions[key_HisReg[ikey]]
            F22 = path_HisRegUint1.historyOutputs['U1'].data[1][1]
    
    instanceobj=[]
    for instanceName in myAssembly.instances.keys():
        instanceobj=myAssembly.instances.keys(instanceName)
    Ldregion = odb.rootAssembly.nodeSets['RFACE']
    Ldfield=lastFrame.fieldOutputs['RT'].getSubset(region=Ldregion).getScalarField(componentLabel='RT1')
    Set_Ufield=lastFrame.fieldOutputs['U'].getScalarField(componentLabel='U1')
    Ldsetval=Ldfield.getSubset(region=Ldregion,position=NODAL);
    # references first item of the nodeset
    SetUfieldval=Set_Ufield.getSubset(region=Ldregion,position=NODAL).values[0].data
    Ufieldval=SetUfieldval
    RFfieldval=Ldsetval.values
    
    Rforce1=0.0
    for node in RFfieldval:
        Rforce1=Rforce1 + node.data
        # print(Rforce1)
            
    # Evaluate the applied average stress over the matrix loaded surface:
    ledge=500; #edge length, micrometer
    sigma_avg=Rforce1/ledge;
    
    interf_int = odb.rootAssembly.nodeSets['INTERF_INTNODES']
    interf_ext = odb.rootAssembly.nodeSets['INTERF_EXTNODES']
    fcenter = odb.rootAssembly.nodeSets['CNODE']
    interfU1 = lastFrame.fieldOutputs['U'].getScalarField(componentLabel='U1',)
    interfU2 = lastFrame.fieldOutputs['U'].getScalarField(componentLabel='U2',)
    interfc1 = lastFrame.fieldOutputs['COORD'].getScalarField(componentLabel='COOR1',)
    interfc2 = lastFrame.fieldOutputs['COORD'].getScalarField(componentLabel='COOR2',)
    
    interfint_u1val = interfU1.getSubset(region=interf_int, position=NODAL);
    interfext_u1val = interfU1.getSubset(region=interf_ext, position=NODAL);
    interfint_u2val = interfU2.getSubset(region=interf_int, position=NODAL);
    interfext_u2val = interfU2.getSubset(region=interf_ext, position=NODAL);
    interfint_coor1 = interfc1.getSubset(region=interf_int, position=NODAL);
    interfint_coor2 = interfc2.getSubset(region=interf_int, position=NODAL);
    interfext_coor1 = interfc1.getSubset(region=interf_ext, position=NODAL);
    interfext_coor2 = interfc2.getSubset(region=interf_ext, position=NODAL);
    FU1 = interfU1.getSubset(region=fcenter, position=NODAL).values[0].data;
    # fn_u1vals = fiber_u1val.values; FU1 = fn_u1vals[0]
    
    interf_arr = []
    for u1_int, u1_ext, u2_int, u2_ext, coor1int, coor1ext, coor2int, coor2ext \
        in zip(interfint_u1val.values, interfext_u1val.values, interfint_u2val.values, interfext_u2val.values, \
               interfint_coor1.values, interfext_coor1.values, interfint_coor2.values, interfext_coor2.values):
            # x, y, z = nodei1.coordinates  # Get the coordinates of the node1
            # xe, ye, ze = nodei2.coordinates
            interfext_defc1 = coor1ext.data + u1_ext.data
            interfext_defc2 = abs(coor2ext.data + u2_ext.data)
            interfint_defc1 = coor1int.data + u1_int.data
            interfint_defc2 = abs(coor2int.data + u2_int.data)
            deltacoor1_ext = abs(interfext_defc1-FU1)
            deltacoor1_int = abs(interfint_defc1-FU1)
            umag_int = math.sqrt(math.pow(u1_int.data,2)+math.pow(u2_int.data,2))
            umag_ext = math.sqrt(math.pow(u1_ext.data,2)+math.pow(u2_ext.data,2))
            alphaext = math.atan(u2_ext.data/u1_ext.data)*(180/(math.pi))
            alphaint = math.atan(u2_int.data/u1_int.data)*(180/(math.pi))
            
            URext = math.sqrt(math.pow(float(deltacoor1_ext),2) + math.pow(interfext_defc2,2))
            URint = math.sqrt(math.pow(float(deltacoor1_int),2) + math.pow(interfint_defc2,2))
            deltaUR = URext-URint
            # CODisp = math.sqrt(math.pow(interfext_defc1-interfint_defc1,2) + math.pow(interfext_defc2-interfint_defc2,2))
            if interfext_defc1 > 0:
                theta_def = math.atan(interfext_defc2/deltacoor1_ext)*(180/(math.pi))
                utheta_ext = umag_ext*math.cos(theta_def+90.0-alphaext)
                utheta_int = umag_int*math.cos(theta_def+90.0-alphaint)
                deltaUt = abs(utheta_ext) - abs(utheta_int)
            else:
                theta_def = 180.0 - (math.atan(interfext_defc2/(deltacoor1_ext))*(180/(math.pi)))
                utheta_ext = umag_ext*math.cos(theta_def+90.0-alphaext)
                utheta_int = umag_int*math.cos(theta_def+90.0-alphaint)
                deltaUt = abs(utheta_ext) - abs(utheta_int)
            
            interf_arr.append([theta_def, deltaUR, deltaUt])
    interf_arr.sort(key=lambda interf_arr:interf_arr[:][0], reverse=False)
    interfnodes_np = np.array(interf_arr)
    # Save the array into a text file:
        # Specify the format for each column
    fmt = ['%.8e', '%.8e', '%.8e']
    np.savetxt(working_directory_FFM+'\\'+name_files+'_CODisp.txt', interfnodes_np, fmt=fmt, delimiter='\t')       

    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] 
    # Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] 
     #RF2 para la DCB
     #RF2 para la DCB
    DeltaU = F22 - F21
    #---------------------------------------------------
    #escribir el fichero de datos
    #---------------------------------------------------
    # in case the reaction force output returns "0.0":
    if sigma_avg == 0.0:
        sigma_avg=Sel1 #stress output of matrix element close to y=0
    
    # fich_salida= open(salida_datos3,'a')
    # datos_escri=stepk+'\t'+stepm+'\t'+str(nnodosdamagTen)+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(DeltaU)+'\t'+str(theta1_ang)+'\t'+str(factorcoord[0][0])
    # fich_salida.write('\n')
    # fich_salida.write(datos_escri)
    # fich_salida.close()
    
    odb.close()
    return str(theta1_ang), str(factorcoord[0][1]), sigma_avg, str(theta2_ang), Gt1, Gt2, Ufieldval
    
def PMTESCsalDatos_SFUload(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen, nstep):
    
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    myAssembly = odb.rootAssembly

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
    	  # statev(6)=factor
    Eset='NINTERFACE'
    key_step = odb.steps.keys()
    lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets[Eset]
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
    intpoint=len(path_SDV4)
    
    factorcoord=[]; 
    theta1v=[]; theta2v=[];
    
    Gt1v=[]; Gt2v=[];
    # LOOP ITERATION TO SAVE THE INTERFACE DEBOND ANGLES & (Sigma_rr, Tau)
    for value in range(intpoint):
        Gtot=path_SDV4[value].data
        GcT=path_SDV5[value].data
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        sigmarr=path_SDV13[value].data
        sigmart=path_SDV14[value].data
        if x > 0 and Gtot != 0:
            thetad1=(math.atan(y/x)*(180/(math.pi)))
            theta1v.append([thetad1, sigmarr, sigmart])
            Gt1v.append(Gtot)
            factorcoord.append([Gtot, GcT])
        elif x < 0 and Gtot != 0:
            thetad2=(math.atan(y/-x)*(180/(math.pi)))
            theta2v.append([thetad2, sigmarr, sigmart])
            Gt2v.append(Gtot)
            factorcoord.append([Gtot, GcT])
    # Sort the thetav() lists in ascending order of the debond angle:
    theta1v.sort(key=lambda theta1v:theta1v[:][0],reverse=False)
    theta2v.sort(key=lambda theta2v:theta2v[:][0],reverse=False)
    # Sort the factorcoord() list in descending order of GtotT:
    factorcoord.sort(key=lambda factorcoord:factorcoord[:][0],reverse=True)
    Gt1v.sort(key=lambda Gt1v:Gt1v,reverse=True)
    Gt2v.sort(key=lambda Gt2v:Gt2v,reverse=True)
    
    thetad=theta1v[0][0]
    theta2=theta2v[0][0]
    Gt1=Gt1v[0]; Gt2=Gt2v[0];
    
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    # RFset=key_HisReg[7:]
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    path_HisRegS11 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegS12 = odb.steps[key_step[0]].historyRegions[key_HisReg[3]]
    path_HisRegUint1 = odb.steps[key_step[0]].historyRegions[key_HisReg[10]]
    path_HisRegUint0 = odb.steps[key_step[0]].historyRegions[key_HisReg[9]]
    # Nforce=0.0;
    
    instanceobj=[]
    for instanceName in myAssembly.instances.keys():
        instanceobj=myAssembly.instances.keys(instanceName)
    Ldregion = odb.rootAssembly.instances[instanceobj[-1]].nodeSets['LOADNSET']
    Ldfield=lastFrame.fieldOutputs['RF'].getScalarField(componentLabel='RF1',)
    Ldsetval=Ldfield.getSubset(region=Ldregion,position=NODAL);
    RFfieldval=Ldsetval.values
    Rforce1=0.0
    for node in RFfieldval:
        Rforce1=Rforce1 + node.data
    # Evaluate the applied average stress over the matrix loaded surface:
    ledge=500; #edge length, micrometer
    sigma_avg=Rforce1/ledge;

    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] #U2 para la DCB
    Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] #U2 para la DCB
    F21 = path_HisRegUint1.historyOutputs['U1'].data[1][1] #RF2 para la DCB
    F22 = path_HisRegUint0.historyOutputs['U1'].data[1][1] #RF2 para la DCB
    DeltaU = F21 - F22
    
    # in case the reaction force output returns "0.0":
    if sigma_avg == 0.0:
        sigma_avg=Sel1 #stress output of matrix element close to y=0
    #---------------------------------------------------
    #escribir el fichero de datos
    #---------------------------------------------------

    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(DeltaU)+'\t'+str(thetad)+'\t'+str(factorcoord[0][0])
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()
    return str(thetad), str(factorcoord[0][1]), sigma_avg, str(theta2), Gt1, Gt2

def PMTESCsalDatos_2SFLoad(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen, nstep, xcf2, ycf2):
    
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    myAssembly = odb.rootAssembly
    
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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets['NINTERFACE']
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    	getSubset(region=InterElementSet).values
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
    path_SDV17=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV17'].\
    	getSubset(region=InterElementSet).values
    path_SDV18=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV18'].\
    	getSubset(region=InterElementSet).values
    path_SDV15=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV15'].\
    	getSubset(region=InterElementSet).values
    path_SDV19=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV19'].\
    	getSubset(region=InterElementSet).values
    intpoint=len(path_SDV1)
    
    factorcoord=[]; 
    theta1v=[]; theta2v=[];
    theta2d1v=[]; theta2d2v=[];
    Gt1v=[]; Gt2v=[];  
    # Access the assembly instances
    instance1 = odb.rootAssembly.instances['INTERFACE-1']
    instance2 = odb.rootAssembly.instances['INTERFACE-2']
    
    # Ensure both instances have the same number of elements
    if len(instance1.elements) != len(instance2.elements):
        raise ValueError("Instances must have the same number of elements")
        # os.exit(0)
    # instancelist=[]
    inst1node_coords=[]
    inst2node_coords=[]
    # Access the field output for user-defined state variable SDV1
    field_output1 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance1).values
    field_output2 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance2).values
    # locelem1 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV19'].\
    #     	getSubset(region=instance1).values
    # locelem2 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV19'].\
    #     	getSubset(region=instance2).values
    # Gtfield_output = path_SDV4
    
    element_output1 = field_output1
    element_output2 = field_output2
    # elem1_Gtoutput = Gtfield_output
    # elem2_Gtoutput = Gtfield_output
    
    # if len(damage_file)!=0:
    #             # Loop through elements in both instances and get nodal coordinates
    #             for indx in damage_file:
    #                 for elem1, elem2 in zip(element_output1, element_output2):
    #                     if (indx[2]==0.0 and indx[0]==1) and (indx[1]==int(elem1.data)) \
    #                     and (elem1.integrationPoint==1 or elem2.integrationPoint==1):
    #                         # print(elem1.data, elem2.data)
    #                         locel1=instance1.elements[indx[-1] - 1]
    #                         # locel2=instance2.elements[indx[-1] - 1]
    #                         node_labels1 = locel1.connectivity
    #                         # node_labels2 = locel2.connectivity
    #                         for node_label1 in node_labels1:
    #                             node1 = instance1.nodes[node_label1-1] # Adjust for 0-based indexing
    #                             # node2 = instance2.nodes[node_label2-1]  # Adjust for 0-based indexing
    #                             coordinates1 = node1.coordinates
    #                             # coordinates2 = node2.coordinates
                                
    #                             # instancelist.append([instance1.name, elem1.data, coordinates1[0], coordinates1[1], \
    #                             #       math.sqrt(math.pow(coordinates1[0],2)+math.pow(coordinates1[1],2))])
    #                             inst1node_coords.append([instance1.name, elem1.data, coordinates1[0], coordinates1[1], indx[2]])
                        
    #                     if (indx[2]==0.0 and indx[0]==1) and (indx[1]==int(elem2.data)) \
    #                     and (elem1.integrationPoint==1 or elem2.integrationPoint==1):
    #                         # locel1=instance1.elements[indx[-1] - 1]
    #                         locel2=instance2.elements[indx[-1] - 1]
    #                         # node_labels1 = locel1.connectivity
    #                         node_labels2 = locel2.connectivity
    #                         for node_label2 in node_labels2:
    #                             # node1 = instance1.nodes[node_label1-1]  # Adjust for 0-based indexing
    #                             node2 = instance2.nodes[node_label2-1]  # Adjust for 0-based indexing
                                
    #                             coordinates2 = node2.coordinates
                                
    #                             # instancelist.append([instance2.name, elem2.data, coordinates2[0], coordinates2[1], \
    #                             #       math.sqrt(math.pow(coordinates2[0],2)+math.pow(coordinates2[1],2))])
    #                             inst2node_coords.append([instance2.name, elem2.data, coordinates2[0], coordinates2[1], indx[2]])
    #             if len(inst1node_coords)!=0:
    #                 inst1node_coords.sort(key=lambda inst1node_coords:inst1node_coords[:][3], reverse=True)
    #             if len(inst2node_coords)!=0:
    #                 inst2node_coords.sort(key=lambda inst2node_coords:inst2node_coords[:][3], reverse=True)
    # # Computation of debond semiangles:
    # if len(inst1node_coords)!=0:
    #     # and (nstep==0 or nstep==1 or nstep==3 or nstep==4)
    #     # instancelist.sort(key=lambda instancelist:instancelist[:][2],reverse=True) 
    #     print(inst1node_coords[0])
    #         # right fiber pole
    #     ymax=inst1node_coords[0][3]
    #     ym1=inst1node_coords[1][3]
    #     ymax_avg=0.5*(ymax+ym1)
    #     xmax=inst1node_coords[0][2]
    #     xm1=inst1node_coords[1][2]
    #     xmax_avg=0.5*(xmax+xm1)
    #     theta1_ang=(math.atan(ymax_avg/xmax_avg)*(180/(math.pi)))
    #     if len(inst2node_coords)!=0 and inst2node_coords[0][-1]==0:
    #         ymaxl=inst2node_coords[0][3]
    #         ym1l=inst2node_coords[1][3]
    #         ymaxl_avg=0.5*(ymaxl+ym1l)
    #         xmaxl=inst2node_coords[0][2]
    #         xm1l=inst2node_coords[1][2]
    #         if xmaxl<0.0 and xm1l<0.0:
    #             xmaxl=abs(xmaxl); xm1l=abs(xm1l) 
    #         xmaxl_avg=0.5*(xmaxl+xm1l)
    #         theta2_ang=(math.atan(ymaxl_avg/xmaxl_avg)*(180/(math.pi)))
    #     elif len(inst2node_coords)==0: 
    #         theta2_ang=0.0
    # if len(inst2node_coords)!=0:
    #     # and (nstep==0 or nstep==2 or nstep==3 or nstep==4)
    #     # left fiber pole
    #     print(inst2node_coords[0])
    #     ymaxl=inst2node_coords[0][3]
    #     ym1l=inst2node_coords[1][3]
    #     ymaxl_avg=0.5*(ymaxl+ym1l)
    #     xmaxl=inst2node_coords[0][2]
    #     xm1l=inst2node_coords[1][2]
    #     if xmaxl<0.0 and xm1l<0.0:
    #         xmaxl=abs(xmaxl); xm1l=abs(xm1l) 
    #     xmaxl_avg=0.5*(xmaxl+xm1l)
    #     theta2_ang=math.atan(ymaxl_avg/xmaxl_avg)*(180/(math.pi))
    #     if len(inst1node_coords)!=0 and inst1node_coords[0][-1]==0:
    #         ymax=inst1node_coords[0][3]
    #         ym1=inst1node_coords[1][3]
    #         ymax_avg=0.5*(ymax+ym1)
    #         xmax=inst1node_coords[0][2]
    #         xm1=inst1node_coords[1][2]
    #         xmax_avg=0.5*(xmax+xm1)
    #         theta1_ang=(math.atan(ymax_avg/xmax_avg)*(180/(math.pi)))
    #     elif len(inst1node_coords)==0: 
    #         theta1_ang=0.0
    # else:
    #     if len(inst1node_coords)==0: theta1_ang=0.0
    #     if len(inst2node_coords)==0: theta2_ang=0.0
    
    # 2 FIBERS: LOOP ITERATION TO SAVE THE INTERFACE DEBOND ANGLES andS (Sigma_rr, Tau)
    # OUTDATED METHODOLOGY
    for value in range(intpoint):
        # dama=path_SDV1[value].data
        Gtot=path_SDV4[value].data
        GcT=path_SDV5[value].data
        # Gi=path_SDV17[value].data
        # Gii=path_SDV18[value].data
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        sigmarr=path_SDV13[value].data
        sigmart=path_SDV14[value].data
        
        NeL2=str(path_SDV2[value].elementLabel)+'_'+str(path_SDV2[value].instance.name)
        if NeL2.endswith('_INTERFACE-1'):
            if x > 0 and Gtot != 0.0:
                thetad1=(math.atan(abs(y)/x)*(180/(math.pi)))
                theta1v.append([Gtot, thetad1, sigmarr, sigmart])
                Gt1v.append(Gtot)
                factorcoord.append([Gtot, GcT])
            elif x < 0 and Gtot != 0.0:
                thetad2=(math.atan(abs(y)/-x)*(180/(math.pi)))
                theta2v.append([Gtot, thetad2, sigmarr, sigmart])
                Gt2v.append(Gtot)
                factorcoord.append([Gtot, GcT])
        if NeL2.endswith('_INTERFACE-2') and xcf2>0:
            if (x-xcf2) > 0 and Gtot != 0.0:
                theta2d1=math.atan(abs(y-ycf2)/(x-xcf2))*(180/(math.pi))
                theta2d1v.append([Gtot, theta2d1, sigmarr, sigmart])
                Gt1v.append(Gtot)
                factorcoord.append([Gtot, GcT])
            elif (x-xcf2) < 0 and Gtot != 0.0:
                theta2d2=math.atan(abs(y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                theta2d2v.append([Gtot, theta2d2, sigmarr, sigmart])
                Gt2v.append(Gtot)
                factorcoord.append([Gtot, GcT])
        if NeL2.endswith('_INTERFACE-2') and xcf2<0:
            if (x-abs(xcf2)) > 0 and Gtot != 0.0:
                theta2d1=math.atan(abs(y-ycf2)/(x-abs(xcf2)))*(180/(math.pi))
                theta2d1v.append([Gtot, theta2d1, sigmarr, sigmart])
                Gt1v.append(Gtot)
                factorcoord.append([Gtot, GcT])
            elif (x-abs(xcf2)) < 0 and Gtot != 0.0:
                theta2d2=math.atan(abs(y-ycf2)/-(x-abs(xcf2)))*(180/(math.pi))
                theta2d2v.append([Gtot, theta2d2, sigmarr, sigmart])
                Gt2v.append(Gtot)
                factorcoord.append([Gtot, GcT])
    # Sort the thetav() lists in descending order of sigmarr:
    theta1v.sort(key=lambda theta1v:theta1v[:][2],reverse=True) 
    theta2v.sort(key=lambda theta2v:theta2v[:][2],reverse=True)
    theta2d1v.sort(key=lambda theta2d1v:theta2d1v[:][2],reverse=True)
    theta2d2v.sort(key=lambda theta2d2v:theta2d2v[:][2],reverse=True)
    # Sort the factorcoord() list in descending order of GtotT:
    factorcoord.sort(key=lambda factorcoord:factorcoord[:][0],reverse=True)
    Gt1v.sort(key=lambda Gt1v:Gt1v,reverse=True)
    Gt2v.sort(key=lambda Gt2v:Gt2v,reverse=True)
    # fiber no. 1:
    thetad=(theta1v[0][1])
    theta2=(theta2v[0][1])
    # fiber no. 2:
    thetrfib2=(theta2d1v[0][1])
    thetlfib2=(theta2d2v[0][1])
    
    theta1tot=thetad+theta2
    theta2tot=thetrfib2+thetlfib2
    Gt1=Gt1v[0]; Gt2=Gt2v[0];
    
    key_HisReg = odb.steps[key_step[-1]].historyRegions.keys()
    hisreglen=len(key_HisReg)
    path_HisRegS11 = odb.steps[key_step[-1]].historyRegions[key_HisReg[1]]
    path_HisRegS12 = odb.steps[key_step[-1]].historyRegions[key_HisReg[5]]
    F21=0.0; F22=0.0;
    for ikey in range(hisreglen):
        if key_HisReg[ikey].endswith('Node INTERFACE-1.1'):
            path_HisRegUint0=odb.steps[key_step[-1]].historyRegions[key_HisReg[ikey]]
            F21 = path_HisRegUint0.historyOutputs['U1'].data[1][1]
        if key_HisReg[ikey].endswith('Node INTERFACE-1.2'):
            path_HisRegUint1=odb.steps[key_step[-1]].historyRegions[key_HisReg[ikey]]
            F22 = path_HisRegUint1.historyOutputs['U1'].data[1][1]
    
    instanceobj=[]
    for instanceName in myAssembly.instances.keys():
        instanceobj=myAssembly.instances.keys(instanceName)
    Ldregion = odb.rootAssembly.instances[instanceobj[-1]].nodeSets['LOADNSET']
    Ldfield=lastFrame.fieldOutputs['RF'].getScalarField(componentLabel='RF1',)
    Ldsetval=Ldfield.getSubset(region=Ldregion,position=NODAL);
    RFfieldval=Ldsetval.values
    Rforce1=0.0
    for node in RFfieldval:
        Rforce1=Rforce1 + node.data
    # Evaluate the applied average stress over the matrix loaded surface:
    ledge=500; #edge length, micrometer
    sigma_avg=Rforce1/ledge;
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] #U2 para la DCB
    Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] #U2 para la DCB
     #RF2 para la DCB
     #RF2 para la DCB
    DeltaU = F22 - F21
    #---------------------------------------------------
    #escribir el fichero de datos
    #---------------------------------------------------
    # in case the reaction force output returns "0.0":
    if sigma_avg == 0.0:
        sigma_avg=Sel1 #stress output of matrix element close to y=0
    
    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(DeltaU)+'\t'+str(theta1tot+theta2tot)+'\t'+str(factorcoord[0][0])
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()
    return str(theta1tot), str(factorcoord[0][1]), sigma_avg, str(theta2tot), Gt1, Gt2

def PMTESCsalDatos_2SFLoadV2(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen, nstep, xcf2, ycf2, damage_file):
    with open(name_files + '.inp', 'r') as inp_file:
        inp_lines = inp_file.readlines()
        inp_file.close()
        
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

    first_param, GIc, mu_const, interfh, xi, lambdhs = sigmac_parameter(inp_lines)
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    myAssembly = odb.rootAssembly
    working_directory_FFM=working_directory+'/FFM_optimizada01'
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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    lastFrame = odb.steps[key_step[0]].frames[-1]
    InterElementSet = odb.rootAssembly.elementSets['NINTERFACE']
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    	getSubset(region=InterElementSet).values
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
    	getSubset(region=InterElementSet).values
    path_SDV6=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV6'].\
    	getSubset(region=InterElementSet).values   
    path_SDV8=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV8'].\
    	getSubset(region=InterElementSet).values  
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values 
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
    	getSubset(region=InterElementSet).values
    path_SDV12=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV12'].\
    	getSubset(region=InterElementSet).values
    path_SDV13=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV13'].\
     	getSubset(region=InterElementSet).values
    path_SDV14=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV14'].\
     	getSubset(region=InterElementSet).values
    # path_SDV17=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV17'].\
    # 	getSubset(region=InterElementSet).values
    # path_SDV18=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV18'].\
    # 	getSubset(region=InterElementSet).values
    intpoint=len(path_SDV1)
    
    # Access the assembly instances
    instance1 = odb.rootAssembly.instances['INTERFACE-1']
    instance2 = odb.rootAssembly.instances['INTERFACE-2']
    
    # Ensure both instances have the same number of elements
    if len(instance1.elements) != len(instance2.elements):
        raise ValueError("Instances must have the same number of elements")
    inst1node_coords=[]
    inst2node_coords=[]
    # Access the field output for user-defined state variable SDV2: 
    field_output1 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance1).values
    field_output2 = odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
        	getSubset(region=instance2).values
    
    # integration points and data into a single list for element_output
    data_values1 = np.array([value.data for value in field_output1 if value.integrationPoint==1])
    
    # integration points and data into a single list for element_output
    data_values2 = np.array([value.data for value in field_output2 if value.integrationPoint==1])
    
    # list comprehension of the damaged elements file:
    damage_file = np.array(damage_file)
    # Use np.any() or np.all() to make the comparison explicit
    damage_fileset = [value for value in damage_file if np.any(damage_file[0] == 1)]
    if len(damage_fileset)!=0:
        # print(np.array(damage_file))
        # **PERHAPS, ONLY A SINGLE LOOP WILL BE ENOUGH TO DETERMINE ELEMENT NODAL COORDINATES
        # Loop through elements in both interface instances and get nodal coordinates
        for indx in damage_fileset:
            # print(indx)
            # indx[-1]: local element number associated to its part instance
            # indx[1] : global element number, used by the abaqus code
            # indx[0] : integration point label of the element
            for elem1, elem2 in zip(data_values1, data_values2):
                if (indx[2]==0.0 and indx[0]==1) and (indx[1]==elem1):
                    # print(elem1.data, elem1.elementLabel, instance1.elements[indx[-1] - 1].connectivity)
                    locel1=instance1.elements[indx[-1] - 1]
                    node_labels1 = locel1.connectivity
                    for node_label1 in node_labels1:
                        node1 = instance1.nodes[node_label1-1] # Adjust for 0-based indexing
                        coordinates1 = node1.coordinates
                        inst1node_coords.append([instance1.name, locel1, coordinates1[0], coordinates1[1], indx[2]])
                    # print(elem1.data)
                if (indx[2]==0.0 and indx[0]==1) and (indx[1]==elem2):
                    locel2=instance2.elements[indx[-1] - 1]
                    node_labels2 = locel2.connectivity
                    for node_label2 in node_labels2:
                        node2 = instance2.nodes[node_label2-1]  # Adjust for 0-based indexing
                        coordinates2 = node2.coordinates
                        inst2node_coords.append([instance2.name, locel2, coordinates2[0]-xcf2, coordinates2[1]-ycf2, indx[2]])
        if len(inst1node_coords)!=0:
            inst1node_coords.sort(key=lambda inst1node_coords:inst1node_coords[:][3], reverse=False)
            # print(inst1node_coords)
        if len(inst2node_coords)!=0:
            inst2node_coords.sort(key=lambda inst2node_coords:inst2node_coords[:][3], reverse=False)
            # print(inst2node_coords)
    
    # Computation of fiber debond angles:
    f1thetal = []; f1thetar = [];
    f2thetal = []; f2thetar = [];
    if len(inst1node_coords)!=0:
        for node1 in inst1node_coords:
            if node1[2] < 0 and abs(node1[3])!=0:
                # left pole of fiber-1
                ymaxl1=node1[3]
                # ym1=inst1node_coords[1][3]
                # ymax_avg=0.5*(ymax+ym1)
                xmaxl1=abs(node1[2])
                # xm1=inst1node_coords[1][2]
                # xmax_avg=0.5*(xmax+xm1)
                thetaf1l_ang=(math.atan(ymaxl1/xmaxl1)*(180/(math.pi)))
                f1thetal.append(thetaf1l_ang)
            if node1[2] > 0:
                # right pole of fiber-1
                ymaxr1=node1[3]
                xmaxr1=node1[2]
                thetaf1r_ang=math.atan(ymaxr1/xmaxr1)*(180/(math.pi))
                f1thetar.append(thetaf1r_ang)
        f1thetal.sort(key=lambda f1thetal:f1thetal, reverse=True)
        f1thetar.sort(key=lambda f1thetar:f1thetar, reverse=True)
        if len(f1thetal)==0:
            thetaf1l = 0.0
        if len(f1thetar)==0:
            thetaf1r = 0.0
        if len(f1thetal)!=0:
            thetaf1l = f1thetal[0] + abs(f1thetal[-1])
        if len(f1thetar)!=0:
            thetaf1r = f1thetar[0] + abs(f1thetar[-1])
    else:
        thetaf1l=0.0; thetaf1r=0.0;
        
    if len(inst2node_coords)!=0:
        for node2 in inst2node_coords:
            if node2[2] < 0 and abs(node2[3])!=0:
                # left pole of fiber-2
                ymaxl2=node2[3]
                xmaxl2=abs(node2[2])
                thetaf2l_ang=math.atan(ymaxl2/xmaxl2)*(180/(math.pi))
                f2thetal.append(thetaf2l_ang)
            if node2[2] > 0:
                # right pole of fiber-2
                ymaxr2=node2[3]
                xmaxr2=node2[2]
                thetaf2r_ang=math.atan(ymaxr2/xmaxr2)*(180/math.pi)
                f2thetar.append(thetaf2r_ang)
        f2thetal.sort(key=lambda f2thetal:f2thetal, reverse=True)
        f2thetar.sort(key=lambda f2thetar:f2thetar, reverse=True)
        if len(f2thetal)==0:
            thetaf2l = 0.0
        if len(f2thetar)==0:
            thetaf2r = 0.0
        if len(f2thetal)!=0:
            thetaf2l = f2thetal[0] + abs(f2thetal[-1])
        if len(f2thetar)!=0:
            thetaf2r = f2thetar[0] + abs(f2thetar[-1])
    else:
        thetaf2l=0.0; thetaf2r=0.0
    print([thetaf1l, thetaf1r, thetaf2l, thetaf2r])
    fiberinter_angles = [thetaf1l, thetaf1r, thetaf2l, thetaf2r]
    
    
    # 2 FIBERS: LOOP ITERATION TO SAVE THE INTERFACE DEBOND ANGLES and (Sigma_rr, Tau)
    ERRf1_array=[]
    ERRf2_array=[]
    for value in range(intpoint):
        # Gtot=path_SDV4[value].data
        # GcT=path_SDV5[value].data
        # x=path_SDV10[value].data
        # y=path_SDV11[value].data
        # GtE=path_SDV12[value].data
        # G2E=path_SDV8[value].data
        # GcE=path_SDV6[value].data
        psi_g=math.atan2(path_SDV14[value].data*(math.sqrt(1/xi)), path_SDV13[value].data)
        GcE=float(GIc)*(1+(math.tan(psi_g*(1-lambdhs)))**2)*(mu_const/interfh); psi_gc=(math.pi)/(2*(1-lambdhs));
        x=path_SDV10[value].data
        y=path_SDV11[value].data
        GtE=path_SDV12[value].data
        G2E=path_SDV8[value].data
        if abs(psi_g)>=psi_gc: GcE=GIc*1E8
        # sigmarr=path_SDV13[value].data
        # sigmart=path_SDV14[value].data
        
        NeL2=str(path_SDV2[value].elementLabel)+'_'+str(path_SDV2[value].instance.name)
        if NeL2.endswith('_INTERFACE-1'):
            if y >= 0 and x >= 0:
                thetad1=(math.atan(y/x)*(180/(math.pi)))
                ERRf1_array.append([thetad1, G2E, GtE, GcE])
                # Gt1v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif y >= 0  and x < 0:
                thetad1=float(180) - (math.atan(y/abs(x))*(180/(math.pi)))
                ERRf1_array.append([thetad1, G2E, GtE, GcE])
                # Gt2v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            if y < 0 and x >= 0:
                thetad1=float(-1)*math.atan(abs(y)/x)*(180/(math.pi))
                ERRf1_array.append([thetad1, G2E, GtE, GcE])
            elif y < 0  and x < 0:
                thetad1=float(-180) + (math.atan(abs(y)/abs(x))*(180/(math.pi)))
                ERRf1_array.append([thetad1, G2E, GtE, GcE])
        if NeL2.endswith('_INTERFACE-2') and (x-xcf2)>0:
            if (y-ycf2) >= 0 :
                thetad2=math.atan((y-ycf2)/(x-xcf2))*(180/(math.pi))
                ERRf2_array.append([thetad2, G2E, GtE, GcE])
                # Gt1v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
            elif (y-ycf2) < 0:
                thetad2=float(-1)*math.atan(abs(y-ycf2)/(x-xcf2))*(180/(math.pi))
                ERRf2_array.append([thetad2, G2E, GtE, GcE])
                # Gt2v.append(Gtot)
                # factorcoord.append([Gtot, GcT])
        if NeL2.endswith('_INTERFACE-2') and (x-xcf2)<0:
            if (y-ycf2) >= 0 :
                thetad2=float(180) - math.atan((y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                ERRf2_array.append([thetad2, G2E, GtE, GcE])

            elif (y-ycf2) < 0:
                thetad2=float(-180) + math.atan(abs(y-ycf2)/abs(x-xcf2))*(180/(math.pi))
                ERRf2_array.append([thetad2, G2E, GtE, GcE])

    # Sort the ERR lists in ascending order of thetad:
    ERRf1_array.sort(key=lambda ERRf1_array:ERRf1_array[:][0], reverse=False)
    ERRf2_array.sort(key=lambda ERRf2_array:ERRf2_array[:][0], reverse=False)
    ERRf1np = np.array(ERRf1_array); ERRf2np = np.array(ERRf2_array);
    # Save the arrays as text files:
        # Specify the format for each column
    header_fmt = ['%.8e', '%.8e', '%.8e', '%.8e']
    np.savetxt(working_directory_FFM+'\\'+name_files+'_ERRf1.txt', ERRf1np, fmt=header_fmt, delimiter='\t')
    np.savetxt(working_directory_FFM+'\\'+name_files+'_ERRf2.txt', ERRf2np, fmt=header_fmt, delimiter='\t')
    
    # Define the radius R, and the search tolerance, toler:
    R_o = 7.51
    R_i = 7.5
    toler = 1E-6
    
    interfU1 = lastFrame.fieldOutputs['U'].getScalarField(componentLabel='U1',)
    interfU2 = lastFrame.fieldOutputs['U'].getScalarField(componentLabel='U2',)
    # interfc1 = lastFrame.fieldOutputs['COORD'].getScalarField(componentLabel='COOR1',)
    # interfc2 = lastFrame.fieldOutputs['COORD'].getScalarField(componentLabel='COOR2',)

    # Initialize a list to store node labels that satisfy the condition
    node_labelsi1int = []; node_labelsi1ext = []
    node_labelsi2int = []; node_labelsi2ext = []
    # Loop through all nodes in the instance
    for nodei1, nodei2 in zip(instance1.nodes, instance2.nodes):
        x, y, z = nodei1.coordinates  # Get the coordinates of the node1
        x2, y2, z2 = nodei2.coordinates
        if x==0: x=x+toler
        elif abs(x2-xcf2)==0: x2=abs(xcf2)+toler
        
        if instance1.name=='INTERFACE-1' :
            # Extract the displacement values for the target node
            u1_values = interfU1.getSubset(region=nodei1).values
            u2_values = interfU2.getSubset(region=nodei1).values
            # Check if x^2 + y^2 equals R^2 (with a small tolerance)
            if abs(math.sqrt(x**2 + y**2) - R_o) < toler :  
                
                interf1C1 = x
                interf1C2 = y
                # umag = math.sqrt(u1_values[0].data**2 + u2_values[0].data**2)
                interfext_defc1 = interf1C1 + u1_values[0].data
                interfext_defc2 = abs(interf1C2 + u2_values[0].data)
                deltacoor1_ext = abs(interfext_defc1)
                URext = math.sqrt(math.pow(float(deltacoor1_ext),2) + math.pow(interfext_defc2,2))
                if x>=0 and y>=0:
                    node_labelsi1ext.append([math.atan(interfext_defc2/interfext_defc1)*(180.0/math.pi), interf1C1, interf1C2, URext])  
                    # print([math.atan(y/x)*(180.0/math.pi), interf1C1[0].data, interf1C2[0].data, URext])
                elif x>=0 and y<0: node_labelsi1ext.append([float(-1)*math.atan((interfext_defc2)/interfext_defc1)*(180.0/math.pi), interf1C1, interf1C2, URext])
                if x<0 and y>=0: node_labelsi1ext.append([float(180) - math.atan(interfext_defc2/abs(interfext_defc1))*(180.0/math.pi), interf1C1, interf1C2, URext])
                elif x<0 and y<0: node_labelsi1ext.append([float(-180) + math.atan((interfext_defc2)/abs(interfext_defc1))*(180.0/math.pi), interf1C1, interf1C2, URext])
            # Check if x^2 + y^2 equals R^2 (with a small tolerance)
            if abs(math.sqrt(x**2 + y**2) - R_i) < toler :
                
                interf1C1 = x
                interf1C2 = y
                # umag = math.sqrt(u1_values[0].data**2 + u2_values[0].data**2)
                interfint_defc1 = interf1C1 + u1_values[0].data
                interfint_defc2 = abs(interf1C2 + u2_values[0].data)
                deltacoor1_int = abs(interfint_defc1)
                URint = math.sqrt(float(deltacoor1_int**2) + interfint_defc2**2)
                if x>=0 and y>=0:
                    node_labelsi1int.append([math.atan(interfint_defc2/interfint_defc1)*(180.0/math.pi), interf1C1, interf1C2, URint])  
                    # print([math.atan(y/x)*(180.0/math.pi), interf1C1[0].data, interf1C2[0].data, URext])
                elif x>=0 and y<0: node_labelsi1int.append([float(-1)*math.atan((interfint_defc2)/interfint_defc1)*(180.0/math.pi), interf1C1, interf1C2, URint])
                if x<0 and y>=0: node_labelsi1int.append([float(180) - math.atan(interfint_defc2/abs(interfint_defc1))*(180.0/math.pi), interf1C1, interf1C2, URint])
                elif x<0 and y<0: node_labelsi1int.append([float(-180) + math.atan((interfint_defc2)/abs(interfint_defc1))*(180.0/math.pi), interf1C1, interf1C2, URint])
                
                
        if instance2.name=='INTERFACE-2' :
            # Extract the displacement values for the target node
            u1_values = interfU1.getSubset(region=nodei2).values
            u2_values = interfU2.getSubset(region=nodei2).values
            # umag = math.sqrt(u1_values[0].data**2 + u2_values[0].data**2)
            if abs(math.sqrt((x2-xcf2)**2 + (y2-ycf2)**2) - R_o) < toler : 
                interf2C1 = (x2-xcf2)
                interf2C2 = (y2-ycf2)
                interfext_defc1 = interf2C1 + u1_values[0].data
                interfext_defc2 = abs(interf2C2 + u2_values[0].data)
                deltacoor1_ext = (interfext_defc1)
                URext = math.sqrt((deltacoor1_ext**2) + (interfext_defc2**2))
                if (x2-xcf2)>=0 and (y2-ycf2)>=0:
                    node_labelsi2ext.append([math.atan((interfext_defc2)/(interfext_defc1))*(180.0/math.pi), interf2C1, interf2C2, URext])  
                    # print([math.atan(y/x)*(180.0/math.pi), interf1C1[0].data, interf1C2[0].data, URext])
                elif (x2-xcf2)>=0 and (y2-ycf2)<0: node_labelsi2ext.append([float(-1)*math.atan(abs(interfext_defc2)/(interfext_defc1))*(180.0/math.pi), interf2C1, interf2C2, URext])
                if (x2-xcf2)<0 and (y2-ycf2)>=0: node_labelsi2ext.append([float(180) - math.atan((interfext_defc2)/abs(interfext_defc1))*(180.0/math.pi), interf2C1, interf2C2, URext])
                elif (x2-xcf2)<0 and (y2-ycf2)<0: node_labelsi2ext.append([float(-180) + math.atan(abs(interfext_defc2)/abs(interfext_defc1))*(180.0/math.pi), interf2C1, interf2C2, URext])

                # node_labelsi2ext.append([180.0 - math.atan(y2/abs(x2))*(180.0/math.pi), interf2C1[0].data, interf2C2[0].data, URext])  # Add the node label to the list
                # print(nodei2.coordinates)
            if abs(math.sqrt((x2-xcf2)**2 + (y2-ycf2)**2) - R_i) < toler :
                interf2C1 = (x2-xcf2)
                interf2C2 = (y2-ycf2)
                interfint_defc1 = (interf2C1) + u1_values[0].data
                interfint_defc2 = abs((interf2C2) + u2_values[0].data)
                deltacoor1_int = abs(interfint_defc1)
                URint = math.sqrt((deltacoor1_int**2) + (interfint_defc2**2))
                if (x2-xcf2)>=0 and (y2-ycf2)>=0:
                    node_labelsi2int.append([math.atan((y2-ycf2)/(interfint_defc1))*(180.0/math.pi), interf2C1, interf2C2, URint])  
                    # print([math.atan(y/x)*(180.0/math.pi), interf1C1[0].data, interf1C2[0].data, URext])
                elif (x2-xcf2)>=0 and (y2-ycf2)<0: node_labelsi2int.append([float(-1)*math.atan(interfint_defc2/(interfint_defc1))*(180.0/math.pi), interf2C1, interf2C2, URint])
                if (x2-xcf2)<0 and (y2-ycf2)>=0: node_labelsi2int.append([float(180) - math.atan((interfint_defc2)/abs(interfint_defc1))*(180.0/math.pi), interf2C1, interf2C2, URint])
                elif (x2-xcf2)<0 and (y2-ycf2)<0: node_labelsi2int.append([float(-180) + math.atan((interfint_defc2)/abs(interfint_defc1))*(180.0/math.pi), interf2C1, interf2C2, URint])

                # node_labelsi2int.append([180.0 - math.atan(y2/abs(x2))*(180.0/math.pi), interf2C1[0].data, interf2C2[0].data, URint]) # Add the node label to the list
                # print(nodei2.coordinates)
    node_labelsi1int.sort(key=lambda node_labelsi1int:node_labelsi1int[0], reverse=False)        
    node_labelsi1ext.sort(key=lambda node_labelsi1ext:node_labelsi1ext[0], reverse=False)      
    node_labelsi2ext.sort(key=lambda node_labelsi2ext:node_labelsi2ext[0], reverse=False)
    node_labelsi2int.sort(key=lambda node_labelsi2int:node_labelsi2int[0], reverse=False)
    
    thetaUR_arr = []; thetaUR_f2arr = [];
    for nodes_int, nodes_ext, nodes2int, nodes2ext in zip(node_labelsi1int, node_labelsi1ext, node_labelsi2int, node_labelsi2ext):
        DeltaUR = nodes_ext[-1] - nodes_int[-1]
        DeltaURi2 = nodes2ext[-1] - nodes2int[-1]
        thetaUR_arr.append([nodes_ext[0], DeltaUR])
        thetaUR_f2arr.append([nodes2ext[0], DeltaURi2])
    thetaUR_arr.sort(key=lambda thetaUR_arr:thetaUR_arr[0], reverse=False)
    thetaUR_f2arr.sort(key=lambda thetaUR_f2arr:thetaUR_f2arr[0], reverse=False)
    thetaURnp = np.array(thetaUR_arr); thetaURf2np = np.array(thetaUR_f2arr)
    # Save the array into a text file:
        # Specify the format for each column
    fmt = ['%.8e', '%.8e']
    np.savetxt(working_directory_FFM+'\\'+name_files+'_thetaURdeltaf1.txt', thetaURnp, fmt=fmt, delimiter='\t')
    np.savetxt(working_directory_FFM+'\\'+name_files+'_thetaURdeltaf2.txt', thetaURf2np, fmt=fmt, delimiter='\t')
    
    key_HisReg = odb.steps[key_step[-1]].historyRegions.keys()
    hisreglen=len(key_HisReg)
    path_HisRegS11 = odb.steps[key_step[-1]].historyRegions[key_HisReg[1]]
    # path_HisRegS12 = odb.steps[key_step[-1]].historyRegions[key_HisReg[5]]
    F21=0.0; F22=0.0;
    for ikey in range(hisreglen):
        if key_HisReg[ikey].endswith('Node INTERFACE-1.1'):
            path_HisRegUint0=odb.steps[key_step[-1]].historyRegions[key_HisReg[ikey]]
            F21 = path_HisRegUint0.historyOutputs['U1'].data[1][1]
        if key_HisReg[ikey].endswith('Node INTERFACE-1.2'):
            path_HisRegUint1=odb.steps[key_step[-1]].historyRegions[key_HisReg[ikey]]
            F22 = path_HisRegUint1.historyOutputs['U1'].data[1][1]
    
    instanceobj=[]
    # mtrxinstance = odb.rootAssembly.instances['MATRIX-1']
    for instanceName in myAssembly.instances.keys():
        instanceobj=myAssembly.instances.keys(instanceName)
    Ldregion = odb.rootAssembly.instances['MATRIX-1'].nodeSets['LOADNSET']
    Ldfield=lastFrame.fieldOutputs['RF'].getScalarField(componentLabel='RF1',)
    Ldsetval=Ldfield.getSubset(region=Ldregion,position=NODAL);
    RFfieldval=Ldsetval.values
    Rforce1=0.0
    for node in RFfieldval:
        Rforce1=Rforce1 + node.data
    # Evaluate the applied average stress over the matrix loaded surface:
    ledge=500; #edge length, micrometer
    sigma_avg=Rforce1/ledge;
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] #U2 para la DCB
    # Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] #U2 para la DCB
     #RF2 para la DCB
     #RF2 para la DCB
    # DeltaU = F22 - F21
    #---------------------------------------------------
    #escribir el fichero de datos
    #---------------------------------------------------
    # in case the reaction force output returns "0.0":
    if sigma_avg == 0.0:
        sigma_avg=Sel1 #stress output of matrix element close to y=0
    
    # fich_salida= open(salida_datos3,'a')
    # datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(DeltaU)+'\t'+str(sum(fiberinter_angles))+'\t'+str(factorcoord[0][0])
    # fich_salida.write('\n')
    # fich_salida.write(datos_escri)
    # fich_salida.close()
    
    odb.close()
    return str(thetaf1l), str(0.0), sigma_avg, str(thetaf1r), fiberinter_angles

def PMTESCsalDatos_MFUload(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen):

    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    
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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    
    
    path_HisRegS11 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegS12 = odb.steps[key_step[0]].historyRegions[key_HisReg[3]]
    path_HisRegU1 = odb.steps[key_step[0]].historyRegions[key_HisReg[-1]]
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] #
    Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] #
    F21 = path_HisRegU1.historyOutputs['U1'].data[1][1] #
    F22 = path_HisRegU1.historyOutputs['U1'].data[1][1] #
    
    #---------------------------------------------------
    #escribir el fichero de datos
    #--------------------------------------------------
    #chdir(working_directory_Ene) 
    
    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(F22)
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()
    
def PMTESCsalDatos_MFm2Uload(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen):

    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    
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
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    
    path_HisRegS11 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegS12 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegU1 = odb.steps[key_step[0]].historyRegions[key_HisReg[-1]]
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    Sel1 = path_HisRegS11.historyOutputs['S11'].data[1][1] #
    Sel2 = path_HisRegS12.historyOutputs['S11'].data[1][1] #
    F21 = path_HisRegU1.historyOutputs['U1'].data[1][1] #
    F22 = path_HisRegU1.historyOutputs['U1'].data[1][1] #
    
    #---------------------------------------------------
    #escribir el fichero de datos
    #--------------------------------------------------
    #chdir(working_directory_Ene) 
    
    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(Sel1)+'\t'+str(Sel2)+'\t'+str(F21)+'\t'+str(F22)
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()