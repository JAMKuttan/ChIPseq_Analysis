## Create new env in specific folder
```shell
conda create -p /project/shared/bicf_workflow_ref/chipseq_bchen4/ -c r r-essentials
#Add channels
conda config --add channels conda-forge
conda config --add channels r
conda config --add channels bioconda
pip install --user twobitreader
conda install -c r r-xml
```

Install bioconductor in R console:
```R
source("http://bioconductor.org/biocLite.R")
biocLite()
biocLite(c("DiffBind","ChIPseeker"))
```