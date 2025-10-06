from FADO import *

# Design variables ----------------------------------------------------- #
nDV = 12
ffd = InputVariable(0.0,PreStringHandler("DV_VALUE="),nDV)
ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -8e-2, 8e-2)

# Parameters ----------------------------------------------------------- #
# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))
enable_def = Parameter([""], LabelReplacer("%__DEF__"))

# Switch Objective Functions
OF_Dp = Parameter([""], LabelReplacer("%__OF_DP__"))

# Evaluations ---------------------------------------------------------- #

nproc= "12"
configMaster="main.cfg"
config1 = "config_inlet.cfg"
config2 = "config_core.cfg"
config3 = "config_outlet.cfg"
meshName="combi_mesh.su2"

def_command = "mpirun -n " + nproc + " SU2_DEF " + configMaster
cfd_command = "mpirun -n " + nproc + " SU2_CFD " + configMaster + " &&" + " python3 plot_history.py"

cfd_ad_command = "mpirun -n " + nproc + " SU2_CFD_AD " + configMaster + " &&" + " python3 plot_history.py"
dot_ad_command = "mpirun -n " + nproc + " SU2_DOT_AD " + configMaster

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addConfig(config1)
deform.addConfig(config2)
deform.addConfig(config3)
deform.addData(meshName)
deform.addExpected("mesh_out.su2")
deform.addParameter(enable_def)
deform.addParameter(OF_Dp)

# direct run
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addConfig(config1)
direct.addConfig(config2)
direct.addConfig(config3)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addData("plot_history.py")
direct.addExpected("restart_0.dat")
direct.addExpected("restart_1.dat")
direct.addExpected("restart_2.dat")
direct.addExpected("main.csv")
direct.addParameter(enable_direct)
direct.addParameter(OF_Dp)

# adjoint run
adjoint = ExternalRun("ADJOINT",cfd_ad_command,True)
adjoint.setMaxTries(max_tries)
adjoint.addConfig(configMaster)
adjoint.addConfig(config1)
adjoint.addConfig(config2)
adjoint.addConfig(config3)
adjoint.addData("DEFORM/mesh_out.su2", destination=meshName)
adjoint.addData("plot_history.py")
# add all primal restart files
adjoint.addData("DIRECT/restart_0.dat", destination="restart_0.dat")
adjoint.addData("DIRECT/restart_1.dat", destination="restart_1.dat")
adjoint.addData("DIRECT/restart_2.dat", destination="restart_2.dat")
adjoint.addExpected("restart_adj_custom_0.dat")
adjoint.addParameter(enable_adjoint)
adjoint.addParameter(OF_Dp)

# gradient projection
dot = ExternalRun("DOT_AD",dot_ad_command,True)
dot.setMaxTries(max_tries)
dot.addConfig(configMaster)
dot.addConfig(config1)
dot.addConfig(config2)
dot.addConfig(config3)
dot.addData("DEFORM/mesh_out.su2", destination=meshName)
dot.addData("ADJOINT/restart_adj_custom_0.dat", destination="restart_adj_custom_0.dat")
dot.addData("ADJOINT/restart_adj_custom_1.dat", destination="restart_adj_custom_1.dat")
dot.addData("ADJOINT/restart_adj_custom_2.dat", destination="restart_adj_custom_2.dat")
dot.addExpected("of_grad.dat")
dot.addParameter(enable_def)
dot.addParameter(OF_Dp) 

# Functions ------------------------------------------------------------ #

CombObj = Function("Pressure_Drop", "DIRECT/main.csv",LabeledTableReader("\"ComboObj\""))
CombObj.addInputVariable(ffd,"DOT_AD/of_grad.dat",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
CombObj.addValueEvalStep(deform)
CombObj.addValueEvalStep(direct)
CombObj.addGradientEvalStep(adjoint)
CombObj.addGradientEvalStep(dot)
CombObj.setDefaultValue(1e3)

# Driver --------------------------------------------------------------- #

driver = ScipyDriver()
driver.addObjective("min", CombObj, 1)
driver.setWorkingDirectory("OPTIM")
driver.setEvaluationMode(False, 2.0)
driver.setStorageMode(True,"DSN_")
driver.setFailureMode("HARD")
driver.preprocess()
his = open("optim.dat","w",1)
his.write('idx,ComboObj\n')
driver.setHistorian(his)

# Undeformed/initial primal first in order to have the correct solution in
# the WorkindDirectory for the following adjoint
print("Computing baseline primal")
x = driver.getInitial()
driver.fun(x) # baseline evaluation

# Compute discrete adjoint gradient
print("Computing discrete adjoint gradient")
driver.grad(x)

# Primal simulation for each FD step-size and each DV
chosenDV= range(0, nDV, 1)
FDstep= [1e-3]
for iDV in chosenDV:
  for stepsize in FDstep:
    print("Computing primal of DV ", iDV, "/", nDV-1, " with stepsize ", stepsize)
    x = driver.getInitial()
    x[iDV] = stepsize # DV_VALUE, FD-step
    driver.fun(x)

his.close()

