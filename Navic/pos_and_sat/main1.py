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


    vel.append(x_kdot)
    vel.append(y_kdot)
    vel.append(z_kdot)

    return vel


def acceleration(time,sv,SVlockBias,SVclockDrift,SVclockDriftRate,IODE,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,CodesL2,GPSWeek, L2Pflag, SVacc, health, TGD, IODC,TransTime):
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

    acce.append(x_a)
    acce.append(y_a)
    acce.append(z_a)

    return acce

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

output3 = input_data.apply(lambda row: acceleration(*row), axis=1)

df1 = pd.DataFrame(output1)

df2 = pd.DataFrame(output2)

df3 = pd.DataFrame(output3)

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

df4 = pd.read_csv('final.csv')
df5 = pd.read_csv('final1.csv')
df6 = pd.read_csv('final2.csv')

merged_df = pd.concat([df4,df5,df6],axis=1)
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
df = df.drop([df.columns[2],df.columns[4]], axis=1)

# Rename the column
df = df.rename(columns={'0.2':'satellite acceleration'})
df = df.rename(columns={'0.1':'satellite velocity'})
df = df.rename(columns={'0': 'satellite position'})
df = df.rename(columns={'Unnamed: 0': 'index'})

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_file.csv', index=False)

