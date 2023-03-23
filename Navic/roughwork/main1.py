import numpy as np
import math
import pandas as pd
import sys
import csv

#find the position 

def position_x(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    pos=[]
    w=83.410441763725728
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
       # argument of perigree for circular orbits is 0 
    phy_k=v_k+omega
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    #pos.append(x_k)
    #pos.append(y_k)
    #pos.append(z_k)
    
    return x_k
    
def position_y(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    pos=[]
    w=83.41104
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    phy_k=v_k+omega
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    #pos.append(x_k)
    #pos.append(y_k)
    #pos.append(z_k)
    
    return y_k


def position_z(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    pos=[]
    w=83.410441763725728
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    phy_k=v_k+omega
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    #pos.append(x_k)
    #pos.append(y_k)
    #pos.append(z_k)
    
    return z_k






# find the velocity

def velocity_x(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    #vel=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)


    #vel.append(x_kdot)
    #vel.append(y_kdot)
    #vel.append(z_kdot)

    return x_kdot
def velocity_y(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    #vel=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)


    #vel.append(x_kdot)
    #vel.append(y_kdot)
    #vel.append(z_kdot)

    return y_kdot
def velocity_z(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    #vel=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)


    #vel.append(x_kdot)
    #vel.append(y_kdot)
    #vel.append(z_kdot)

    return z_kdot


def acceleration_x(time,sv,SVlockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    acce=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)

    F=-1.5*j_2*(mu/(r_k*r_k))*((R_E*R_E)/(r_k*r_k))
    x_a=-mu*(x_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(x_k/r_k))+2*y_kdot*omega_e_dot+x_k*omega_e_dot*omega_e_dot

    y_a=-mu*(y_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(y_k/r_k))-2*x_kdot*omega_e_dot+y_k*omega_e_dot*omega_e_dot


    z_a=-mu*(z_k/(r_k*r_k*r_k))+F*((3-5*((z_k*z_k)/(r_k*r_k)))*(z_k/r_k))

    #acce.append(x_a)
    #acce.append(y_a)
    #acce.append(z_a)

    return x_a

def acceleration_y(time,sv,SVlockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    acce=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)

    F=-1.5*j_2*(mu/(r_k*r_k))*((R_E*R_E)/(r_k*r_k))
    x_a=-mu*(x_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(x_k/r_k))+2*y_kdot*omega_e_dot+x_k*omega_e_dot*omega_e_dot

    y_a=-mu*(y_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(y_k/r_k))-2*x_kdot*omega_e_dot+y_k*omega_e_dot*omega_e_dot


    z_a=-mu*(z_k/(r_k*r_k*r_k))+F*((3-5*((z_k*z_k)/(r_k*r_k)))*(z_k/r_k))

    #acce.append(x_a)
    #acce.append(y_a)
    #acce.append(z_a)

    return y_a
def acceleration_z(time,sv,SVlockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    acce=[]
    R_E =  6378137.0 #meters
    j_2 = 0.0010826262
    A = sqrtA*sqrtA
    mu=3.986005E+14# × 1014
    omega_e_dot=7.2921151467E-5
    n_o=np.sqrt(mu/(A*A*A))
    t_k=TransTime-Toe
    
    if(t_k>302400):
        t_k=t_k-604800
    elif(t_k<-302400):
        t_k=t_k+604800
    else:
        t_k=t_k;
        
    n=n_o+DeltaN
    M_k=M0+n*t_k
    E_k=M_k
    
    for i in range(0,3):
        E_k=E_k+ (M_k - E_k + Eccentricity*np.sin(E_k))/(1-Eccentricity*np.cos(E_k))
    v_k=2*np.arctan(np.sqrt((1+Eccentricity)/(1-Eccentricity))*np.tan(E_k/2))
    w=np.pi  # argument of perigree for circular orbits is 0 
    phy_k=v_k+w
    del_u_k = Cus*np.sin(2*phy_k) + Cuc*np.cos(2*phy_k)
    del_r_k = Crs*np.sin(2*phy_k) + Crc*np.cos(2*phy_k)
    del_i_k = Cis*np.sin(2*phy_k) + Cic*np.cos(2*phy_k)
    u_k=phy_k + del_u_k
    r_k=A*(1-Eccentricity*np.cos(E_k))+del_r_k
    i_k=Io+del_i_k + IDOT*t_k
    x_kd=r_k*np.cos(u_k)
    y_kd=r_k*np.sin(u_k)
    omega_k=Omega0 + (OmegaDot - omega_e_dot)*t_k - omega_e_dot*Toe
    x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
    y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
    z_k=y_kd*np.sin(i_k)
    E_kdot = n/(1-Eccentricity*np.cos(E_k))
    v_kdot = (E_kdot*(np.sqrt(1-Eccentricity*Eccentricity)))/(1-Eccentricity*np.cos(E_k))
    d_ik_dt = IDOT + 2*v_kdot*(Cis*np.cos(2*phy_k)-Cic*np.sin(2*phy_k))
    u_kdot = v_kdot+2*v_kdot*(Cus*np.cos(2*phy_k) - Cus*np.sin(2*phy_k))
    r_kdot =Eccentricity*A*E_kdot*np.sin(E_k) + 2*v_kdot*(Crs*np.cos(2*phy_k) -Crc*np.sin(2*phy_k))
    omega_kdot = OmegaDot - omega_e_dot
    x_kdd = r_kdot*np.cos(u_k) - r_k*u_kdot*np.sin(u_k)
    y_kdd = r_kdot*np.sin(u_k) + r_k*u_kdot*np.cos(u_k)

    x_kdot = -x_kd*omega_kdot*np.sin(omega_k) + x_kdd*np.cos(omega_k) - y_kdd*np.sin(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.cos(omega_k)*np.cos(i_k) -(d_ik_dt)*np.sin(omega_k)*np.sin(i_k))


    y_kdot = -x_kd*omega_kdot*np.cos(omega_k) + x_kdd*np.sin(omega_k) + y_kdd*np.cos(omega_k)*np.cos(i_k) - y_kd*(omega_kdot*np.sin(omega_k)*np.cos(i_k) +(d_ik_dt)*np.cos(omega_k)*np.sin(i_k))


    z_kdot =  y_kd*(d_ik_dt)*np.cos(i_k)+y_kdd*np.sin(i_k)

    F=-1.5*j_2*(mu/(r_k*r_k))*((R_E*R_E)/(r_k*r_k))
    x_a=-mu*(x_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(x_k/r_k))+2*y_kdot*omega_e_dot+x_k*omega_e_dot*omega_e_dot

    y_a=-mu*(y_k/(r_k*r_k*r_k))+F*((1-5*((z_k*z_k)/(r_k*r_k)))*(y_k/r_k))-2*x_kdot*omega_e_dot+y_k*omega_e_dot*omega_e_dot


    z_a=-mu*(z_k/(r_k*r_k*r_k))+F*((3-5*((z_k*z_k)/(r_k*r_k)))*(z_k/r_k))

    #acce.append(x_a)
    #acce.append(y_a)
    #acce.append(z_a)

    return z_a

#function for finding sperical coordinates
def spherical(arr):
    # Earth's semi-major axis (m)
    a = 6378137.0
    # Earth's flattening factor
    f = 1/298.257223563
    # Earth's semi-minor axis (m)
    b = a * (1 - f)
    # Eccentricity squared
    e_sq = (a**2 - b**2) / a**2
    # Distance from the origin
    r = math.sqrt(arr[0]**2 + arr[1]**2 + arr[2]**2)
    # Longitude (radians)
    theta = math.atan2(arr[1], arr[0])
    # Latitude (radians)
    phi = math.atan2(arr[2], math.sqrt(arr[0]**2 + arr[1]**2))
    speri=[]
    speri.append(r)
    speri.append(theta)
    speri.append(phi)
    return speri


# Load the CSV file into a pandas DataFrame
df = pd.read_csv('float.csv')

# Specify the columns to use as input for the function
columns_to_use = ['time', 'sv', 'SVclockBias', 'SVclockDrift', 'SVclockDriftRate', 'IODE','Crs', 'DeltaN', 'M0', 'Cuc', 'Eccentricity', 'Cus', 'sqrtA', 'Toe','Cic', 'Omega0', 'Cis', 'Io', 'Crc', 'omega', 'OmegaDot', 'IDOT','CodesL2', 'GPSWeek', 'L2Pflag', 'SVacc', 'health', 'TGD', 'IODC','TransTime']


# Specify the number of rows to read
num_rows_to_read = 340

# Read the specified columns for the specified number of rows
input_data = df.loc[:num_rows_to_read - 1, columns_to_use]

# Apply the custom function to the input data
output1 = input_data.apply(lambda row: position_x(*row), axis=1)
output2 = input_data.apply(lambda row: position_y(*row), axis=1)
output3 = input_data.apply(lambda row: position_z(*row), axis=1)
output4 = input_data.apply(lambda row: velocity_x(*row), axis=1)
output5 = input_data.apply(lambda row: velocity_y(*row), axis=1)
output6 = input_data.apply(lambda row: velocity_z(*row), axis=1)
output7 = input_data.apply(lambda row: acceleration_x(*row), axis=1)
output8 = input_data.apply(lambda row: acceleration_y(*row), axis=1)
output9 = input_data.apply(lambda row: acceleration_z(*row), axis=1)


df1 = pd.DataFrame(output1)
df2 = pd.DataFrame(output2)
df3 = pd.DataFrame(output3)
df4 = pd.DataFrame(output4)
df5 = pd.DataFrame(output5)
df6 = pd.DataFrame(output6)
df7 = pd.DataFrame(output7)
df8 = pd.DataFrame(output8)
df9 = pd.DataFrame(output9)


pd.set_option("display.max_rows", None, "display.max_columns", None,)


# Print the output data
#print('position')
#print(df1)
#print('velocity')
#print(df2)
#print('acceleration')
#print(df3)

df1.to_csv('final.csv')
df2.to_csv('final1.csv')    
df3.to_csv('final2.csv')
df4.to_csv('final3.csv')
df5.to_csv('final4.csv')
df6.to_csv('final5.csv')
df7.to_csv('final6.csv')
df8.to_csv('final7.csv')
df9.to_csv('final8.csv')

df10 = pd.read_csv('final.csv')
df11= pd.read_csv('final1.csv')
df12 = pd.read_csv('final2.csv')
df13 = pd.read_csv('final3.csv')
df14 = pd.read_csv('final4.csv')
df15 = pd.read_csv('final5.csv')
df16 = pd.read_csv('final6.csv')
df17 = pd.read_csv('final7.csv')
df18 = pd.read_csv('final8.csv')

merged_df = pd.concat([df10,df11,df12,df13,df14,df15,df16,df17,df18],axis=1)
#print('merged_file')
#print(merged_df)
merged_df.to_csv('merged_file.csv',index=False)


# Load the source CSV file containing the columns to be added
source_file = pd.read_csv('float.csv')

# Load the target CSV file
target_file = pd.read_csv('merged_file.csv')

# Select the columns to be added (e.g., columns named 'new_column1' and 'new_column2')
new_column1 = source_file['time']
new_column2 = source_file['sv']

# Concatenate the two DataFrames (e.g., target_file and new_column1, new_column2)
new_file = pd.concat([target_file, new_column1, new_column2], axis=1)

# Save the merged DataFrame to a new CSV file (e.g., new_file.csv)
new_file.to_csv('new_file.csv', index=False)
df = pd.read_csv('new_file.csv')
# Drop the third column (which has index 2)
df = df.drop([df.columns[4],df.columns[6],df.columns[8],df.columns[10],df.columns[12],df.columns[14]], axis=1)

# Rename the column
df = df.rename(columns={'0.2':'satellite acceleration'})
df = df.rename(columns={'0.1':'satellite velocity'})
df = df.rename(columns={'0': 'satellite position'})
df = df.rename(columns={'Unnamed: 0': 'index'})

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_file.csv', index=False)

df1 = pd.read_csv('updated_file.csv')
# Drop the third column (which has index 2)
df1 = df.drop([df.columns[2],df.columns[10]], axis=1)
# Rename the column
df1 = df1.rename(columns={'satellite position':'satellite_position_x'})
df1 = df1.rename(columns={'satellite velocity':'satellite_position_y'})
df1 = df1.rename(columns={'satellite acceleration': 'satellite_position_z'})
df1 = df1.rename(columns={'0.3': 'satellite_velocity_x'})
df1 = df1.rename(columns={'0.4': 'satellite_velocity_y'})
df1 = df1.rename(columns={'0.5': 'satellite_velocity_z'})
df1 = df1.rename(columns={'0.6': 'satellite_acceleration_x'})
df1 = df1.rename(columns={'0.7': 'satellite_acceleration_y'})
df1 = df1.rename(columns={'0.8': 'satellite_acceleration_z'})

df1.to_csv('file_u.csv', index=False)

