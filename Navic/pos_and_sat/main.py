import numpy as np
import math
import pandas as pd
import sys

#find the position 

def position(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    pos=[]
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
    pos.append(x_k)
    pos.append(y_k)
    pos.append(z_k)
    
    return pos
    



# find the velocity

def velocity(time,sv,SVclockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
    vel=[]
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


    vel.append(x_kdot)
    vel.append(y_kdot)
    vel.append(z_kdot)

    return vel



# Load the CSV file into a pandas DataFrame
df = pd.read_csv('float.csv')

# Specify the columns to use as input for the function
columns_to_use = ['time', 'sv', 'SVclockBias', 'SVclockDrift', 'SVclockDriftRate', 'IODE','Crs', 'DeltaN', 'M0', 'Cuc', 'Eccentricity', 'Cus', 'sqrtA', 'Toe','Cic', 'Omega0', 'Cis', 'Io', 'Crc', 'omega', 'OmegaDot', 'IDOT','CodesL2', 'GPSWeek', 'L2Pflag', 'SVacc', 'health', 'TGD', 'IODC','TransTime']


# Specify the number of rows to read
num_rows_to_read = 340

# Read the specified columns for the specified number of rows
input_data = df.loc[:num_rows_to_read - 1, columns_to_use]

# Apply the custom function to the input data
output1 = input_data.apply(lambda row: position(*row), axis=1)

output2 = input_data.apply(lambda row: velocity(*row), axis=1)

df1 = pd.DataFrame(output1)

df2 = pd.DataFrame(output2)

pd.set_option("display.max_rows", None, "display.max_columns", None,)


# Print the output data

df1.to_csv('position.csv')
df2.to_csv('velocity.csv')    
    
with open('output.txt', 'w') as f:
    # Redirect standard output to the file
    sys.stdout = f
    
    # Print the output to the file
    print(output1)
    print(output2)
    
    # Restore standard output
    sys.stdout = sys.__stdout__
