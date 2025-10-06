import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
plt.style.use('tableau-colorblind10')
cmap = plt.get_cmap('viridis')
slicedCM = cmap(np.linspace(0, 1, 4)) 


def plot_rms_history(df):
    plt.figure()
    # Check if its DIRECT or ADJOINT
    fields = df.keys()
    if '   "rms[A_P][0]"  ' in fields: 
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_P][0]"  '].values, label='RMS AD Pressure')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_U][0]"  '].values, label='RMS AD Vel-U')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_V][0]"  '].values, label='RMS AD Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.savefig('adjoint_history_zone_0.png')
        plt.close()
        
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_P][1]"  '].values, label='RMS AD Pressure')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_U][1]"  '].values, label='RMS AD Vel-U')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_V][1]"  '].values, label='RMS AD Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.savefig('adjoint_history_zone_1.png')
        plt.close()
        
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_P][2]"  '].values, label='RMS AD Pressure')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_U][2]"  '].values, label='RMS AD Vel-U')
        plt.plot(df['Outer_Iter'].values, df['   "rms[A_V][2]"  '].values, label='RMS AD Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.savefig('adjoint_history_zone_2.png')
        plt.close()
    else:
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['    "rms[P][0]"   '].values, label='RMS Pressure')
        plt.plot(df['Outer_Iter'].values, df['    "rms[U][0]"   '].values, label='RMS Vel-U')
        plt.plot(df['Outer_Iter'].values, df['    "rms[V][0]"   '].values, label='RMS Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.xlabel('Iteration Number')
        plt.savefig('direct_history_zone_0.png')
        plt.close()
        
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['    "rms[P][1]"   '].values, label='RMS Pressure')
        plt.plot(df['Outer_Iter'].values, df['    "rms[U][1]"   '].values, label='RMS Vel-U')
        plt.plot(df['Outer_Iter'].values, df['    "rms[V][1]"   '].values, label='RMS Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.xlabel('Iteration Number')
        plt.savefig('direct_history_zone_1.png')
        plt.close()
        
        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['    "rms[P][2]"   '].values, label='RMS Pressure')
        plt.plot(df['Outer_Iter'].values, df['    "rms[U][2]"   '].values, label='RMS Vel-U')
        plt.plot(df['Outer_Iter'].values, df['    "rms[V][2]"   '].values, label='RMS Vel-V')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.xlabel('Iteration Number')
        plt.savefig('direct_history_zone_2.png')
        plt.close()

        plt.figure()
        plt.plot(df['Outer_Iter'].values, df['    "ComboObj"    '].values)
        plt.xlabel('Iteration Number')
        plt.ylabel('Pressure Drop [Pa]')
        plt.grid()
        plt.savefig('OF_hist.png')
        plt.close()

    
    return True


if __name__== '__main__':
    df = pd.read_csv('main.csv')
    plot_rms_history(df)