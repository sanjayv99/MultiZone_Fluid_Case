import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def loadData(DV, FDstep, DApath, DAstring, FDpath, FDstring):
    """
    Load DA-grad and primal values to compute FD-grad. Also compute abs/rel-diff.
    Returns a Pandas DataFrame with columns:
    DV | DAgrad | FDgrad(step1) | FDgrad(step2) | ... | relDiff(step1) | ...
    """
    data = pd.DataFrame()
    data["DV"] = DV

    # Load DA-grad
    DAdata = pd.read_csv(DApath)
    data["DAgrad"] = DAdata.iloc[DV].values

    # Load FD data and compute FD gradients
    FDdata = pd.read_csv(FDpath, usecols=[1])
    FDbase_idx = 0
    FDbase = FDdata.iloc[FDbase_idx].values
    FDdata.drop([FDbase_idx], inplace=True)

    # Build FDstep array
    FDstep_array = []
    for i in range(len(DV)):
        for step in FDstep:
            FDstep_array.append(step)

    FDdata["FDstep"] = FDstep_array

    FDgrad = (FDdata[FDstring] - FDbase).div(FDdata["FDstep"]).values
    FDgrad = FDgrad.reshape(len(DV), len(FDstep)).T

    for i, step in enumerate(FDstep):
        data[f"FDgrad_{step}"] = FDgrad[i]
        data[f"relDiff_{step}"] = abs(data["DAgrad"] - data[f"FDgrad_{step}"]) / abs(data["DAgrad"])

    return data


def plot_grad_comparison(data, FDstep, save_path=None):
    """
    Plot DA vs FD gradients and their relative differences.
    """
    plt.figure(figsize=(10, 5))
    
    # Plot DA and FD gradients
    plt.subplot(1, 2, 1)
    plt.plot(data["DV"], data["DAgrad"], 'o-', label="DA grad")
    for step in FDstep:
        plt.plot(data["DV"], data[f"FDgrad_{step}"], 'x--', label=f"FD grad (step={step:g})")
    plt.xlabel("Design Variable (DV #)")
    plt.ylabel("Gradient Value")
    plt.legend()
    plt.grid(True)

    # Plot relative difference
    plt.subplot(1, 2, 2)
    for step in FDstep:
        plt.plot(data["DV"], data[f"relDiff_{step}"], 'o--', label=f"Rel. Diff (step={step:g})")
    plt.xlabel("Design Variable (DV #)")
    plt.ylabel("Relative Difference |DA−FD| / |DA|")
    plt.yscale("log")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'GV_comparison.png'), dpi=600)


if __name__ == "__main__":
  nDV = 12
  chosenDV = list(np.arange(nDV))
  FDstep = [1e-3]

  data = loadData(chosenDV, FDstep,
                  "DSN_001/DOT_AD/of_grad.dat", "CUSTOM_OBJFUNC",
                  "optim.dat", "ComboObj")
  data.to_csv("gradient_data_combo.csv", sep=',', index=False)
  print(data.to_string(index=False))
  dir_path = os.path.dirname(os.path.realpath(__file__))
  plot_grad_comparison(data, FDstep, dir_path)
