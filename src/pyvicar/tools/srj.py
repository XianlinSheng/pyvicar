import shutil
import re
import h5py
import numpy as np
from dataclasses import dataclass
from functools import partial
import pyvicar.tools.log as log


@dataclass
class SRJParams:
    nomega: int
    omegas: np.ndarray


def preset36():
    return SRJParams(
        nomega=36,
        omegas=np.array(
            [
                [297.7724258],
                [0.5002377712],
                [0.9571478258],
                [2.152616084],
                [0.5966655686],
                [6.296132447],
                [0.722842847],
                [0.5299004681],
                [1.426818452],
                [12.74917157],
                [0.5118302742],
                [3.06347303],
                [0.8214342569],
                [0.6502556805],
                [38.33900958],
                [1.148323483],
                [0.5575372581],
                [1.851813902],
                [0.5021453759],
                [4.789145161],
                [0.7683161051],
                [0.575508563],
                [20.56133703],
                [1.273845174],
                [0.5197583086],
                [2.543395235],
                [0.8837256681],
                [91.30355166],
                [0.6214142807],
                [0.5059897697],
                [3.776234975],
                [1.044237077],
                [0.6838090436],
                [8.675977693],
                [0.5424229022],
                [1.615558299],
            ]
        ),
    )


# rearrange srj omega list to stablize
# N is grid number nx or ny
def rearrange_omegas(omegas, Ms, N):
    kappamin = 2 * np.sin(np.pi / 2 / N) ** 2
    kappa = np.arange(kappamin, 2, kappamin)
    G = np.ones_like(kappa)

    # first omega is omega_0
    omegalist = [omegas[0]]
    G *= np.abs(1 - omegas[0] * kappa)  # current G(kappa) curve after applying omega

    # omega[0] used up, delete it
    omegas = omegas[1:]
    Ms = Ms[1:]

    # find the next best omega to apply
    while np.sum(Ms) > 0:
        # the best new omega theoretically, which reduces the maxima of current G curve to 0. (1 - kappa[i] * newomegabest = 0)
        newomegabest = 1 / kappa[np.argmax(G)]

        # the omega (index in the array) we have closest to above best theoretical omega
        bestomegai = np.argmin(np.abs(omegas - newomegabest))

        # set this as the next omega
        omegalist += [omegas[bestomegai]]
        G *= np.abs(1 - omegas[bestomegai] * kappa)

        # remove it if used up, otherwise decrease usable count by 1
        if Ms[bestomegai] == 1:
            omegas = omegas.tolist()
            Ms = Ms.tolist()
            del omegas[bestomegai], Ms[bestomegai]
            omegas = np.array(omegas)
            Ms = np.array(Ms)
        else:
            Ms[bestomegai] -= 1

    return np.array(omegalist)


# key example: P3N256
def read_omegas(key, gridN=None, file="./srj_database.h5"):
    key = key.upper()
    splitted_keys = re.findall(r"[A-Z][0-9]+", key)
    path = "/".join(splitted_keys)

    P = int(re.search(r"[A-Za-z](\d+)", splitted_keys[0]).group(1))
    N = int(re.search(r"[A-Za-z](\d+)", splitted_keys[1]).group(1))
    if gridN is None:
        gridN = N

    with h5py.File(file) as f:
        omegas = f[f"{path}/omegas"]
        Ms = f[f"{path}/Ms"]

        omegalist = rearrange_omegas(omegas, Ms, gridN)

    arr = np.array(omegalist)[:, np.newaxis]
    return SRJParams(
        nomega=arr.shape[0],
        omegas=arr,
    )


# key example: P3N256
def read_rearranged_omegas(key, file="./srj_rearranged_database.h5"):
    key = key.upper()
    splitted_keys = re.findall(r"[A-Z][0-9]+", key)
    path = "/".join(splitted_keys)

    P = int(re.search(r"[A-Za-z](\d+)", splitted_keys[0]).group(1))
    N = int(re.search(r"[A-Za-z](\d+)", splitted_keys[1]).group(1))

    with h5py.File(file) as f:
        omegalist = f[f"{path}/omegalist"]

        # omegalist is a reference of h5 dataset, so this must be done within f scope
        arr = np.array(omegalist)[:, np.newaxis]

    return SRJParams(
        nomega=arr.shape[0],
        omegas=arr,
    )


# predefine database
def generate_database(name="./srj_database.h5"):
    with h5py.File(f"{name}", "w") as f:
        # total 2 omegas
        P2 = f.create_group("P2")

        P2N16 = P2.create_group("N16")
        P2N16.attrs["rho"] = 3.31
        P2N16.create_dataset("omegas", data=np.array([32.60, 0.8630], dtype=float))
        P2N16.create_dataset("Ms", data=np.array([1, 15], dtype=int))

        P2N32 = P2.create_group("N32")
        P2N16.attrs["rho"] = 3.81
        P2N32.create_dataset("omegas", data=np.array([81.22, 0.9178], dtype=float))
        P2N32.create_dataset("Ms", data=np.array([1, 30], dtype=int))

        P2N64 = P2.create_group("N64")
        P2N16.attrs["rho"] = 4.14
        P2N64.create_dataset("omegas", data=np.array([190.2, 0.9532], dtype=float))
        P2N64.create_dataset("Ms", data=np.array([1, 63], dtype=int))

        P2N128 = P2.create_group("N128")
        P2N16.attrs["rho"] = 4.34
        P2N128.create_dataset("omegas", data=np.array([425.8, 0.9742], dtype=float))
        P2N128.create_dataset("Ms", data=np.array([1, 130], dtype=int))

        P2N256 = P2.create_group("N256")
        P2N16.attrs["rho"] = 4.45
        P2N256.create_dataset("omegas", data=np.array([877.8, 0.98555], dtype=float))
        P2N256.create_dataset("Ms", data=np.array([1, 257], dtype=int))

        P2N512 = P2.create_group("N512")
        P2N16.attrs["rho"] = 4.52
        P2N512.create_dataset("omegas", data=np.array([1972, 0.99267], dtype=float))
        P2N512.create_dataset("Ms", data=np.array([1, 564], dtype=int))

        P2N1024 = P2.create_group("N1024")
        P2N16.attrs["rho"] = 4.55
        P2N1024.create_dataset("omegas", data=np.array([4153, 0.99615], dtype=float))
        P2N1024.create_dataset("Ms", data=np.array([1, 1172], dtype=int))

        # total 3 omegas
        P3 = f.create_group("P3")

        P3N16 = P3.create_group("N16")
        P3N16.attrs["rho"] = 5.71
        P3N16.create_dataset(
            "omegas", data=np.array([64.66, 6.215, 0.7042], dtype=float)
        )
        P3N16.create_dataset("Ms", data=np.array([1, 5, 21], dtype=int))

        P3N32 = P3.create_group("N32")
        P3N16.attrs["rho"] = 7.90
        P3N32.create_dataset(
            "omegas", data=np.array([213.8, 11.45, 0.7616], dtype=float)
        )
        P3N32.create_dataset("Ms", data=np.array([1, 7, 45], dtype=int))

        P3N64 = P3.create_group("N64")
        P3N16.attrs["rho"] = 10.2
        P3N64.create_dataset(
            "omegas", data=np.array([684.3, 20.73, 0.8149], dtype=float)
        )
        P3N64.create_dataset("Ms", data=np.array([1, 11, 106], dtype=int))

        P3N128 = P3.create_group("N128")
        P3N16.attrs["rho"] = 12.5
        P3N128.create_dataset(
            "omegas", data=np.array([2114, 36.78, 0.8611], dtype=float)
        )
        P3N128.create_dataset("Ms", data=np.array([1, 17, 252], dtype=int))

        P3N256 = P3.create_group("N256")
        P3N16.attrs["rho"] = 14.6
        P3N256.create_dataset(
            "omegas", data=np.array([6319, 63.99, 0.8989], dtype=float)
        )
        P3N256.create_dataset("Ms", data=np.array([1, 27, 625], dtype=int))

        P3N512 = P3.create_group("N512")
        P3N16.attrs["rho"] = 16.4
        P3N512.create_dataset(
            "omegas", data=np.array([18278, 109.2, 0.9282], dtype=float)
        )
        P3N512.create_dataset("Ms", data=np.array([1, 43, 1571], dtype=int))

        P3N1024 = P3.create_group("N1024")
        P3N16.attrs["rho"] = 17.8
        P3N1024.create_dataset(
            "omegas", data=np.array([51769.1, 184.31, 0.95025], dtype=float)
        )
        P3N1024.create_dataset("Ms", data=np.array([1, 68, 3955], dtype=int))

        # total 4 omegas
        P4 = f.create_group("P4")

        P4N16 = P4.create_group("N16")
        P4N16.attrs["rho"] = 7.40
        P4N16.create_dataset(
            "omegas", data=np.array([80.154, 17.217, 2.6201, 0.62230], dtype=float)
        )
        P4N16.create_dataset("Ms", data=np.array([1, 2, 8, 20], dtype=int))

        P4N32 = P4.create_group("N32")
        P4N16.attrs["rho"] = 11.3
        P4N32.create_dataset(
            "omegas", data=np.array([289.46, 40.791, 4.0877, 0.66277], dtype=float)
        )
        P4N32.create_dataset("Ms", data=np.array([1, 3, 14, 46], dtype=int))

        P4N64 = P4.create_group("N64")
        P4N16.attrs["rho"] = 16.6
        P4N64.create_dataset(
            "omegas", data=np.array([1029.4, 95.007, 6.3913, 0.70513], dtype=float)
        )
        P4N64.create_dataset("Ms", data=np.array([1, 5, 26, 114], dtype=int))

        P4N128 = P4.create_group("N128")
        P4N16.attrs["rho"] = 23.1
        P4N128.create_dataset(
            "omegas", data=np.array([3596.4, 217.80, 9.9666, 0.74755], dtype=float)
        )
        P4N128.create_dataset("Ms", data=np.array([1, 7, 50, 285], dtype=int))

        P4N256 = P4.create_group("N256")
        P4N16.attrs["rho"] = 30.8
        P4N256.create_dataset(
            "omegas", data=np.array([12329, 492.05, 15.444, 0.78831], dtype=float)
        )
        P4N256.create_dataset("Ms", data=np.array([1, 9, 86, 664], dtype=int))

        P4N512 = P4.create_group("N512")
        P4N16.attrs["rho"] = 39.0
        P4N512.create_dataset(
            "omegas", data=np.array([41459, 1096.3, 23.730, 0.82597], dtype=float)
        )
        P4N512.create_dataset("Ms", data=np.array([1, 12, 155, 1650], dtype=int))

        # total 5 omegas
        P5 = f.create_group("P5")

        P5N16 = P5.create_group("N16")
        P5N16.attrs["rho"] = 8.5
        P5N16.create_dataset(
            "omegas",
            data=np.array([88.190, 30.122, 6.8843, 1.6008, 0.58003], dtype=float),
        )
        P5N16.create_dataset("Ms", data=np.array([1, 2, 5, 12, 23], dtype=int))

        P5N32 = P5.create_group("N32")
        P5N16.attrs["rho"] = 14.0
        P5N32.create_dataset(
            "omegas",
            data=np.array([330.57, 82.172, 13.441, 2.2402, 0.60810], dtype=float),
        )
        P5N32.create_dataset("Ms", data=np.array([1, 2, 7, 20, 46], dtype=int))

        P5N64 = P5.create_group("N64")
        P5N16.attrs["rho"] = 22.0
        P5N64.create_dataset(
            "omegas",
            data=np.array([1228.8, 220.14, 26.168, 3.1668, 0.63890], dtype=float),
        )
        P5N64.create_dataset("Ms", data=np.array([1, 3, 10, 38, 106], dtype=int))

        P5N128 = P5.create_group("N128")
        P5N16.attrs["rho"] = 33.2
        P5N128.create_dataset(
            "omegas",
            data=np.array([4522.0, 580.86, 50.729, 4.5018, 0.67161], dtype=float),
        )
        P5N128.create_dataset("Ms", data=np.array([1, 3, 16, 73, 250], dtype=int))

        P5N256 = P5.create_group("N256")
        P5N16.attrs["rho"] = 48.3
        P5N256.create_dataset(
            "omegas",
            data=np.array([16459, 1513.4, 97.832, 6.4111, 0.70531], dtype=float),
        )
        P5N256.create_dataset("Ms", data=np.array([1, 4, 26, 142, 605], dtype=int))

        P5N512 = P5.create_group("N512")
        P5N16.attrs["rho"] = 67.7
        P5N512.create_dataset(
            "omegas",
            data=np.array([59226, 3900.56, 187.53, 9.1194, 0.73905], dtype=float),
        )
        P5N512.create_dataset("Ms", data=np.array([1, 6, 40, 277, 1500], dtype=int))


def node_omega_rearrange(path, obj, gridN):
    # a struct
    splitted_keys = path.split("/")
    name = splitted_keys[-1]
    if re.match("N[0-9]+", name):
        N = int(re.search(r"[A-Za-z](\d+)", name).group(1))

        if gridN is None:
            gridN = N

        omegas = obj["omegas"]
        Ms = obj["Ms"]
        log.log_host(f"Rearranging {path} datasets, using gridN = {gridN}")

        obj.create_dataset("omegalist", data=rearrange_omegas(omegas, Ms, gridN))
        # del obj['omegas']
        # del obj['Ms']


# rearrange database
def generate_rearranged_database(
    origdb="./srj_database.h5",
    rearrangeddb="./srj_rearranged_database.h5",
    gridN=None,
):

    shutil.copy(origdb, rearrangeddb)
    with h5py.File(f"{rearrangeddb}", "a") as f:
        f.visititems(partial(node_omega_rearrange, gridN=gridN))
