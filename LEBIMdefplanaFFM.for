      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,   
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,CMNAME,
     3 NDI,NSHR,NTENS,NSTATV,PROPS,NPROPS,COORDS,DROT,PNEWDT,
     4 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C     SUBROUTINE VARIABLES NEED TO BE DECLARED BY THE USER
      IMPLICIT NONE
C     JSTEP: this variable represents the current step number,
C     similar to what KSTEP does.

C &&&&&&&&&&&&&&&&&&&&&&&&&&--START OF VARIABLE DECLARATION BLOCK--&&&&&&&&&&&&&&&&&&&&&&&&&&
c     dama() matrix could be defined as a 1D array
c$$$      logical lee
c$$$      integer ip,nmax
c$$$      parameter (nmax=1000000) ! maximum number of integr. pts
c$$$      integer dama(nmax)      
c$$$      data lee /.true./,
c$$$     +(dama(ip), ip=1,nmax)/nmax*0/

C     MAXIMUM NUMBER OF INTEGRATION POINTS AND ELEMENTS
      LOGICAL LEE, EXIST, FLAGS(4)
      INTEGER NMAX_PT, NMAX_EL
      PARAMETER (NMAX_PT=4, NMAX_EL=300000) 
      REAL*8 DAMA(NMAX_PT,NMAX_EL)      
      DATA LEE /.TRUE./
C	COMMON /damagefile/ LEE, DAMA
C     it is NOT necessary to share the LEE, DAMA variables
      CHARACTER*80 CMNAME, CPNAME
      CHARACTER*256 OFILE, OUTDIR
      CHARACTER(LEN=256) :: program_path
      CHARACTER(LEN=1) :: dletter 
C     INTEGER, PARAMETER :: dp = SELECTED_REAL_KIND(15, 307)
      REAL*8 STRESS(NTENS),
     1 DDSDDE(NTENS,NTENS),
     2 DDSDDT(NTENS),DRPLDE(NTENS),STATEV(nstatv),
     3 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     4 PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3),
     5 JSTEP(4)
      SAVE program_path
C     SHARE THE VARIABLE BETWEEN DIFFERENT SUBROUTINE CALLS      
C     COMMON /TRACK/ program_path

C	UMAT VARS
      INTEGER NDI,NSHR,NTENS,NPROPS,NOEL,NPT,LENOUTDIR,LOCNUM,JRCD
      INTEGER LAYER,KSPT,KSTEP,KINC,NSTATV
	REAL*8 SSE,SPD,SCD,RPL,DRPLDT,DTIME,TEMP,DTEMP,CELENT,PNEWDT
C	DAMA VARS DECLARATION	
      INTEGER PT,ELEM
      REAL*8 DAM,DAMAGE
      INTEGER ERROR_AP,ERROR_LEC
      
      REAL*8 DSTRESS(4),DDS(4,4),PSIG,LAMBDAHS,GICT,sigmac,tauc,t,tc
      REAL*8 SIGMACT,PI,GI,GII,GTOT,H,KTKN,GCT,PSIGCRIT,MU,GCE
      REAL*8 KNN,KTT,KSS,K33
      REAL*8 GIE,GIIE,KNNINTER,KTTINTER,SIGNON,FUNN,FUNT
	INTEGER K,J,I,INDX
      CHARACTER*200 FULLNAME
C &&&&&&&&&&&&&&&&&&&&&&&&&&--END OF VARIABLE DECLARATION BLOCK--&&&&&&&&&&&&&&&&&&&&&&&&&&
C
      IF ((KINC*KSTEP).EQ.1) THEN
        DAMAGE=1.0D0 
        DDS=0.D0
        PSIG=0.D0
      ENDIF
      Pi=ACOS(-1.0d0)
      Gi=0.d0
      Gii=0.d0   
C     TIME( ) DEFINITION:
C     TIME(1): CURRENT VALUE OF STEP TIME.
C     TIME(2): CURRENT VALUE OF TOTAL TIME. 

C     MATERIAL PROPERTIES FROM THE INPUT FILE
      SIGMACT=PROPS(1)
      GICT=PROPS(2)
      LAMBDAHS=PROPS(3)
      KTKN=PROPS(4)
      H=PROPS(5)
      MU=PROPS(6)
C     DEFINICION DE PARAMETROS MECANICOS DE LA INTERFASE PARA EL CCFFM
      KnnInter=h*(SIGMACT**2)/(2*GICT)
      KttInter=KnnInter*ktkn
C     CCCCCCCCCCCCCCCCCCCCCCCCCC NEW CCCCCCCCCCCCCCCCCCCCCCCCCCCCC        
C     Obtain the output directory name of the current job file
      CALL GETOUTDIR(OUTDIR, LENOUTDIR)
      ! Extract the drive letter (Windows-specific)
      program_path = OUTDIR
      dletter = program_path(1:1)
      
      IF (LEE) THEN
         dama(:,:) = 1.0d0
		 dam=1.0d0
		 
C     FULLNAME MUST INCLUDE THE PC FULL DIRECTORY PATH OF THE
C     DATOS_PROCESAR.TXT FILE:
	     fullname=dletter//':\Users\Jose M Pimentel\'//
     *'Desktop\2DFiberMatrix_PMTE-SC\datos_procesar.txt'    
         OPEN (7,FILE=fullname,ACTION='READ',SHARE='DENYNONE',
     +        STATUS='OLD',IOSTAT=error_ap)
         error_lec=0
         DO WHILE ((error_ap.eq.0).and.(error_lec.eq.0))
            READ (7,*,IOSTAT=error_lec) PT, ELEM, dam
            IF(error_lec.eq.0) THEN
c               ip = 4*(elem-1) + pt               
c               dama(ip) = 1               
               dama(pt,elem)=dam
   
            ENDIF
         ENDDO
         CLOSE(7)

         lee = .false.

      END IF
c     Damage definition    
      DAMAGE = DAMA(NPT,NOEL)
cccccccccccccccccccccccccc END NEW CCCCCCCCCCCCCCCCCCCCCCCCCCCC

cccccccccccccccccccccccccc NEW MAR CCCCCCCCCCCCCCCCCCCCCCCCCCCC
c Added by Mar on April 2022
c funcion dagno para normales dependiendo del signo del strain
c     signoN es el signo de la deformacion normal. 
c     -1.0 para strain de compresion, 1.0 para strain traccion o cero
      signoN=SIGN(1.0,(STRAN(1)+DSTRAN(1)))
      funN=(1.d0-((1.d0-damage)/2)*(1+signoN))
      funT=damage
C     RIGIDECES DEL RESORTE
      Knn=KnnInter*funN
      Kss=(Knn/1d18)*funT
      K33=(Knn/1d18)*funT
      Ktt=KttInter*funT
      
C	ACTUALIZACION DE LA MATRIZ DE ELASTICIDAD
      DDS(1,1)=Knn
      DDS(2,2)=Kss
      DDS(3,3)=K33
      DDS(4,4)=Ktt
      
C******LEYENDA DE LAS TENSIONES *****
C     SIGMA_NN:
C      DSTRESS(1)=DDS(1,1)*DSTRAN(1)
C     SIGMA_SS:
C      DSTRESS(2)=DDS(2,2)*DSTRAN(2)
C     SIGMA_33:
C      DSTRESS(3)=DDS(3,3)*DSTRAN(3)
C     SIGMA_TT:
C      DSTRESS(4)=DDS(4,4)*DSTRAN(4)
C**************************************
      
C	IMPLEMENTACION DEL TENSOR DE TENSION
C     STRESS Y DSTRAN SON VARIABLES DE ABAQUS
	DO k=1,4
	     DSTRESS(k)=DDS(k,k)*DSTRAN(k)
           STRESS(k)=STRESS(k)+DSTRESS(k)             
	ENDDO	

C	DETERMINACION DE LA MATRIZ TANGENTE
C     DDS ES NUESTRA VARIABLE Y DDSDDE DE ABAQUS
	DO i=1,4
		DO j=1,4
			DDSDDE(i,j)=DDS(i,j)
		ENDDO
      ENDDO
      
      IF ((KSTEP*KINC.GT.0.d0).AND.(signoN.LE.-1.d0)) THEN
        IF (damage>=0.d0) THEN
C       spring stiffness
C         Knn stiffness linear variation in compression
          Knn=KnnInter*(1.d0 + ABS(STRESS(1)/sigmact))
          Kss=(Knn/1d18)*funT
          K33=(Knn/1d18)*funT
          Ktt=KttInter*funT
        ENDIF
      ENDIF
      
C     CALCULO DE ENERGIA DEL CRITERIO TENSIONAL
      Gi=h*(STRESS(1))**2.d0/(2.d0*KnnInter)
      Gii=h*(STRESS(4))**2.d0/(2.d0*KttInter)
	Gtot=Gi+Gii
      psig=datan2(STRESS(4)*dsqrt(1/ktkn),STRESS(1))
      Gct=GIct*(1.d0+(dtan(psig*(1.d0-lambdaHS)))**2.d0)
	psiGcrit=pi/(2.d0*(1.d0-lambdaHS))
	IF(abs(psig).ge.psiGcrit) Gct=GIct*1.d8
	
C     I.P. traction vector norm:
      t = DSQRT(STRESS(1)**2.d0 + STRESS(4)**2.d0)
C     I.P. normal critical strength:     
      sigmac=sigmact*DSQRT((1.d0+(dtan(psig*(1.d0-lambdaHS)))**2.d0))*
     @DCOS(psig)
C     I.P. shear critical strength:
      tauc=dsqrt(ktkn)*sigmact*
     @DSQRT((1.d0+(dtan(psig*(1.d0-lambdaHS)))**2.d0))*DSIN(psig)
C     norm of the critical strengths:   
      tc = DSQRT(sigmac**2.d0 + tauc**2.d0)
      
C     CALCULO DE ENERGIA DEL CRITERIO ENERGETICO
C	ENERGIA APORTADA POR CADA PI A LA ENERGIA INTERNA. 
C     SE CALCULA CON EL ELMENTO ROTO O NO ROTO
C     PORQUE DESPUES, EN PYTHON, LO MULTIPLICAREMOS POR
C     LA FUNCION DANO EN EL AMA. POR ESO SE LLAMAN GIE
C     LA ENERGIA NO VA MULTIPLICADA POR H PORQUE 
C     COMO HACEMOS EL CALCULO ENERGETICO POR ELEMENTO
C     MULTIPLICAMOS POR EL AREA Y LO DIVIDIMOS ENTRE 4 (JACOBIANO)

 	GcE=Gct*mu/h
      GiE=KnnInter*(STRAN(1)+DSTRAN(1))**2.d0/(2.d0) 
      GiiE=KttInter*(STRAN(4)+DSTRAN(4))**2.d0/(2.d0)
	
cccccccccccccccccccccccccc END NEW MARCCCCCCCCCCCCCCCCCCCCCCCCCCCCC     
c    ***********************************************************************************************************
c    ***********************************************************************************************************  
C	SALIDA DE DATOS. TODOS LOS DATOS HAN DE SER UTILIZADO CON ANTERIORIDAD
      statev(1)=damage
      statev(2)=noel
      statev(3)=psig
      statev(4)=Gtot
      statev(5)=Gct
      statev(6)=GcE
      statev(7)=GiE
      statev(8)=GiiE
      statev(9)=signoN
	statev(10)=COORDS(1)
	statev(11)=COORDS(2)
	statev(12)=GiE+GiiE
C     (SET DEPVAR=19 IN THE .INP FILE!)
C     INTERFACE NORMAL STRESS AT I.P. LOCATION
	statev(13)=STRESS(1)
C     INTERFACE SHEAR STRESS AT I.P. LOCATION
	statev(14)=STRESS(4)
C	
	statev(15)=t
	statev(16)=tc
	statev(17)=Gi
	statev(18)=Gii
C     LAST INCREMENT OF THE STEP:
C     FLAGS(4): indicates whether the current increment is the last increment of the analysis
      IF (KSTEP*KINC.EQ.1.d0) THEN
	  IF (statev(1).EQ.0.d0) THEN
	      CALL GETPARTINFO(NOEL, 1, CPNAME, LOCNUM, JRCD)
C	      WRITE INSTANCE NAME, LOCAL ELEMENT NUMBER
C	      WRITE(*,*) CMNAME, CPNAME, LOCNUM
	      statev(19)=LOCNUM
	  ELSE 
	  statev(19)=0.d0
	  ENDIF
	ELSE 
	statev(19)=0.d0
      ENDIF

      RETURN
	END