      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,   
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,CMNAME,
     3 NDI,NSHR,NTENS,NSTATV,PROPS,NPROPS,COORDS,DROT,PNEWDT,
     4 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
     
      IMPLICIT NONE
C     Include the definition of the common block
C      INCLUDE 'my_common.inc'
      LOGICAL lee, exist, endflag
  
      DATA lee /.true./
      
C     Como no cargamos el archivo 'ABA_PARAM.INC' debemos de inicializar las variables
      CHARACTER*80 CMNAME
      REAL*8 STRESS(NTENS),
     1 DDSDDE(NTENS,NTENS),
     2 DDSDDT(NTENS),DRPLDE(NTENS),STATEV(nstatv),
     3 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     4 PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
      REAL*8 ZERO, HALF, ONE, TWO, THREE
      PARAMETER (ZERO=0.0d0, ONE=1.0d0, TWO=2.0d0, HALF=ONE/TWO,
     &           THREE=3.0d0)
c     Cargamos esta cabecera para controlar paralelizacion (Mutex)
c     #include <SMAAspUserSubroutines.hdr>
      
      integer ndi,nshr,ntens,nprops,noel,npt
	integer layer,kspt,kstep,kinc,nstatv
	real*8 sse,spd,scd,rpl,drpldt,dtime,temp,dtemp,celent,pnewdt

c	variables nuestras	
      INTEGER PT,ELEM,NMAX_PT,NMAX_EL
      REAL*8 dam,damage
      INTEGER error_ap,error_lec
      PARAMETER (NMAX_PT=4, NMAX_EL=300000) 
      REAL*8 DAMA(NMAX_PT,NMAX_EL) 
      
      real*8 DSTRESS(4),DDS(4,4),psig,lambdaHS,GIct
      real*8 sigmact,Pi,Gi,Gii,Gtot,h,ktkn,Gct,psiGcrit, mu,GcE
      REAL*8 t,tc,sigmac,tauc
      real*8 Knn,Ktt,Kss,K33
      real*8 GiE,GiiE,KnnInter,KttInter,signoN,funN,funT
	integer k,j,i

      CHARACTER*256 fullname,testpath,salidaA,salidaB,program_path
      CHARACTER*256 OFILE, OUTDIR, LENOUTDIR
      CHARACTER(LEN=1) :: dletter 
	COMMON /uext_var/ endflag
	COMMON /directory/ program_path
c$$$  Variables para testear paralelizacion
c$$$      logical exist 
c$$$      integer numThreads, myThreadID
c$$$      numThreads = GETNUMTHREADS()
c$$$      myThreadID = get_thread_id()

c     Inicializacion Mutex
c     call MutexInit(1)

      IF (((KINC*KSTEP).EQ.ZERO) .AND. (endflag)) THEN
        damage=1.0d0 
        dds=0.d0
        psig=0.d0
      ENDIF
      Pi=ACOS(-1d0)
      Gi=0.d0
      Gii=0.d0

c     Explicacion de time(1):
c     TIME(1): Current value of step time.
c     TIME(2): Current value of total time. 

c     READ THE MATERIAL PROPERTIES FROM THE INPUT FILE
      sigmact=PROPS(1)
      GIct=PROPS(2)
      lambdaHS=PROPS(3)
      ktkn=PROPS(4)
      h=PROPS(5)
	mu=PROPS(6)
c     definicion de parametros mecanicos de la interfase para el CCFFM
      KnnInter=h*(sigmact**2)/(2*GIct)
      KttInter=KnnInter*ktkn     

cccccccccccccccccccccccccc NEW CCCCCCCCCCCCCCCCCCCCCCCCCCCCC
c Added by Alfonso Gijon on February 2022
        
c     Leer fichero archivos_procesar.txt la primera vez para
c     construir el array dama()
c      call MutexLock(1) ! Abrimos Mutex
C     Obtain the output directory name of the current job file
      CALL GETOUTDIR(OUTDIR, LENOUTDIR)
      ! Extract the drive letter (Windows-specific)
      program_path = OUTDIR
      dletter = program_path(1:1)        
      if (lee .AND. (KINC.LE.ONE)) then

         dama(:,:) = 1.0d0
		 dam=1.0d0
      
         fullname=dletter//':\Users\Jose M Pimentel\'//
     *'Desktop\2DPMTE-SC UMAT2F\datos_procesar.txt' 
         OPEN (7,FILE=fullname,ACTION='READ',SHARE='DENYNONE',
     +        STATUS='OLD',IOSTAT=error_ap)
         error_lec=0
         DO WHILE ((error_ap.eq.0).and.(error_lec.eq.0))
            READ (7,*,IOSTAT=error_lec) PT, ELEM, dam
            IF(error_lec.eq.0) THEN              
               dama(pt,elem)=dam
   
            ENDIF
         ENDDO
         CLOSE(7)

         lee = .false.

      end if

c     Definir damage     
      damage = dama(npt,noel)
c      call MutexUnLock(1) ! Cerramos Mutex      
      
cccccccccccccccccccccccccc END NEW CCCCCCCCCCCCCCCCCCCCCCCCCCCCC
cccccccccccccccccccccccccc NEW MARCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
c Added by Mar on April 2022
c funcion dagno para normales dependiendo del signo del strain
c     signoN es el signo de la deformacion normal. 
c     -1.0 para strain de compresion, 1.0 para straib traccion o cero
      signoN=SIGN(1.0,(STRAN(1)+DSTRAN(1)))
      funN=(1.d0-((1.d0-damage)/2)*(1+signoN))
      funT=damage
c     Rigideces del resorte
      Knn=KnnInter*funN
      Kss=(Knn/1d18)*funT
      K33=(Knn/1d18)*funT
      Ktt=KttInter*funT
      
c	Actualizacion de la matriz de elasticidad
      DDS(1,1)=Knn
      DDS(2,2)=Kss
      DDS(3,3)=K33
      DDS(4,4)=Ktt
      
c     Incremento del tensor de tension.
c     es una variable nuestra

c     sigma_nn:
      DSTRESS(1)=DDS(1,1)*DSTRAN(1)
c     sigma_ss:
      DSTRESS(2)=DDS(2,2)*DSTRAN(2)
c     sigma_33:
      DSTRESS(3)=DDS(3,3)*DSTRAN(3)
c     sigma_tt:
      DSTRESS(4)=DDS(4,4)*DSTRAN(4)
      
c	Implementacion del tensor de tension
c     STRESS y DSTRAN son variables de ABAQUS
	DO k=1,4
      STRESS(k)=STRESS(k)+DSTRESS(k)
c	STRESS(k)=DSTRESS(k)               
	ENDDO	

c	Determinacion de la matriz TANGENTE
c     DDS es nuestra variable y DDSDDE de ABAQUS
	DO i=1,4
		DO j=1,4
			DDSDDE(i,j)=DDS(i,j)
		ENDDO
      ENDDO

c     calculo de energia del criterio tensional
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
      
c     calculo de energia del criterio energetico
c	energia aportada por cada PI a la energia interna. 
c     Se calcula con el elmento roto o no roto
c     porque despues, en python, lo multiplicaremos por
c     la funcion dano en el AMA. Por eso se llaman GiE
c     la energia no va multiplicada por h porque 
C     como hacemos el calculo energetico por elemento
c     multiplicamos por el area y lo dividimos entre 4 (jacobiano)
 	GcE=Gct*mu/h
      GiE=KnnInter*(STRAN(1)+DSTRAN(1))**2.d0/(2.d0)
      GiiE=KttInter*(STRAN(4)+DSTRAN(4))**2.d0/(2.d0)
	
cccccccccccccccccccccccccc END NEW MARCCCCCCCCCCCCCCCCCCCCCCCCCCCCC     
c    ***********************************************************************************************************
c    ***********************************************************************************************************  
c	salida de datos. Todos los datos han de ser utilizado con anterioridad
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
	statev(13)=STRESS(1)
	statev(14)=tc
	RETURN
	END
	
C     |||||||START OF UEXTERNALDB SUBROUTINE|||||||
C     _____________________________________________
!      SUBROUTINE UEXTERNALDB(LOP, LRESTART, TIME, DTIME, KSTEP, KINC)
!      INCLUDE 'ABA_PARAM.INC'
!      DIMENSION TIME(2)
!
!      LOGICAL endflag
!      COMMON /uext_var/ endflag
!      CHARACTER*256 OUTDIR, program_path
!      COMMON /directory/ program_path
!      
!      IF (LOP.EQ.0) THEN
!        ! Start of the analysis job
!        endflag = .TRUE.
!        CALL GETOUTDIR(OUTDIR, LENOUTDIR)
!!        WRITE(*,*) 'Subroutine working directory: ', OUTDIR
!        program_path=OUTDIR
!        
!      ENDIF
!            
!      ! End of the analysis increment, endflag=TRUE 
!      IF ((LOP .EQ. 1).OR.(LOP .EQ. 2)) THEN 
!        CALL GETOUTDIR(OUTDIR, LENOUTDIR)
!        program_path=OUTDIR
!      ENDIF
!      
!      RETURN
!      END
C     ___________________________________________
C     |||||||END OF UEXTERNALDB SUBROUTINE|||||||