
<img src="images/romsoclogo-logo.png" alt="EU Flag"  width="150"/>

## Benchmarks for MIP rail scheduling
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5171817.svg)](https://doi.org/10.5281/zenodo.5171817) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ROMSOC/benchmarks-mip-rail-scheduling/HEAD?labpath=Benchmark.ipynb)

This benchmark provides ten test cases for integrated locomotive scheduling and driver rostering problem in rail freight. They are developed in colaboration with DB Cargo Polska S.A.

## Description
The aim of this benchmark is to provide the basis for comparison of various solution algorithms and approaches against a realistic dataset, reflecting the trains to be performed in February 2020, the available locomotives and drivers, as well as information about the compatibilit. 
All the benchmark cases are included in the ``instances`` directory. 
A step-by-step guide on how to use these benchmarks can be found in ``documentation`` directory.

## Benchmark execution
The benchmark case can be run using the script files ``main.py`` at each instance subfolder. 

## Run Jupyter notebooks 
The entire benchmark repository can be executed in a provided Docker container where a full installation of Gurobi is available. Once you have clone or downloaded this repository, to build the container just type
```bash
docker build -t benchmarks-mip-rail-scheduling . 
```
and for running it locally:
```bash
docker run -it --rm -p 8888:8888 benchmarks-mip-rail-scheduling jupyter-lab --ip=0.0.0.0 --port=8888 --allow-root
```
Alternatively, please use the following link to run a user-friendly Jupyter Notebook (``Benchmark.ipynb``) with different instances. For instance, Benchmark ``1W_4`` is available at:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ROMSOC/benchmarks-mip-rail-scheduling/HEAD?labpath=Benchmark.ipynb). Please, notice that mybinder cloud computations are limited to 2GB of RAM memory.

## Disclaimer
In downloading this SOFTWARE you are deemed to have read and agreed to the following terms:
This SOFTWARE has been designed with an exclusive focus on civil applications. It is not to be used
for any illegal, deceptive, misleading or unethical purpose or in any military applications. This includes ANY APPLICATION WHERE THE USE OF THE SOFTWARE MAY RESULT IN DEATH,
PERSONAL INJURY OR SEVERE PHYSICAL OR ENVIRONMENTAL DAMAGE. Any redistribution of the software must retain this disclaimer. BY INSTALLING, COPYING, OR OTHERWISE
USING THE SOFTWARE, YOU AGREE TO THE TERMS ABOVE. IF YOU DO NOT AGREE TO
THESE TERMS, DO NOT INSTALL OR USE THE SOFTWARE

## Acknowledgments
<img src="images/EU_Flag.png" alt="EU Flag"  width="150" height="100" />

The ROMSOC project has received funding from the European Union???s Horizon 2020 research and innovation programme under the Marie Sk??odowska-Curie Grant Agreement No. 765374.
This repository reflects the views of the author(s) and does not necessarily reflect the views or policy of the European Commission. The REA cannot be held responsible for any use that may be made of the information this repository contains.
