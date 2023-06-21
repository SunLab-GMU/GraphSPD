# GraphSPD

* [Description](#description)
* [Disclaimer & License](#disclaimer--license)
* [Installation](#installation)
  * [Install OS](#1-install-os)
  * [Clone Source Code](#2-clone-source-code)
  * [Install Dependencies](#3-install-dependencies)
* [How-to-Run](#how-to-run)
  * [Pre-processing](#1-pre-processing)
    * [Use Test Patch Samples](#11-use-test-patch-samples)
    * [Use Your Own Patches](#12-use-your-own-patches)
  * [Generate PatchCPGs](#2-generate-patchcpgs)
  * [Run PatchGNN](#3-run-patchgnn)
* [Other Resources](#other-resources)
* [Team](#team)

## Description

This is a package of **[GraphSPD](https://sunlab-gmu.github.io/GraphSPD/)**, a graph-based model to detect security patches with their code property graphs. More information can be found in our paper *"[GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics]()"*, which will appear in the 44th IEEE Symposium on Security and Privacy (IEEE S&P 2023), San Francisco, CA, May 22-26, 2023. 

If you are using GraphSPD for work that will result in a publication (thesis, dissertation, paper, article), please use the following citation.

```bibtex
@inproceedings{wang2022graphspd,
  title={GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics},
  author={Wang, Shu and Wang, Xinda and Sun, Kun and Jajodia, Sushil and Wang, Haining and Li, Qi},
  booktitle={2023 IEEE Symposium on Security and Privacy (SP)},
  pages={604--621},
  year={2022},
  organization={IEEE Computer Society}
}
```

or

*Shu Wang, Xinda Wang, Kun Sun, Sushil Jajodia, Haining Wang, and Qi Li, "GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics," 2023 44th IEEE Symposium on Security and Privacy (S&P 2023), 2023.*

## Disclaimer & License

We developed GraphSPD and released the source code, aiming to help admins and developers identify silent security patches and prioritize their development.
We hold no liability for any undesirable consequences of using the software package. 

GraphSPD is released under the Apache License 2.0 (refer to the [LICENSE](LICENSE) file for details)
The `./joern/` library is based on [Jeorn](https://github.com/joernio/joern), which is also under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Installation

### 1. Install OS

Download [Ubuntu 20.04.4 LTS](https://releases.ubuntu.com/20.04/) (Focal Fossa) desktop version `.iso` file and install the OS. 

>Note: To avoid potential version conflicts of Python and Java on existing OS, we suggest installing a new Ubuntu virtual machine on VMM (e.g., [VirtualBox 5.2.24](https://www.virtualbox.org/wiki/Download_Old_Builds_5_2), VMware, etc.).

**Suggested system configurations:**\
(Our package can run on pure CPU environments)\
RAM: >2GB\
Disk: >30GB\
CPU: >1 core

### 2. Clone Source Code

Install `git` tool if you have not intalled it.

```shell
sudo apt install git
```

Download the project folder into the user's `HOME` directory.

```shell
cd ~
git clone https://github.com/SunLab-GMU/GraphSPD.git
```


### 3. Install Dependencies

```shell 
cd ~/GraphSPD/
chmod +x install_dep.sh
./install_dep.sh
```

## How-to-Run

>Note: All commands are executed under the main project folder: `~/GraphSPD/`.

### 1. Pre-processing

#### 1.1 Use Test Patch Samples

We provide 10 patch as test examples in `~/GraphSPD/raw_patch/`.

To retrive their pre- and post-patch files, run the following commands under `~/GraphSPD/`:

```shell
python3 get_ab_file.py nginx nginx 02cca547
python3 get_ab_file.py nginx nginx 661e4086
python3 get_ab_file.py nginx nginx 9a3ec202
python3 get_ab_file.py nginx nginx dac90a4b
python3 get_ab_file.py nginx nginx fc785b12
python3 get_ab_file.py nginx nginx 60a8ed26
python3 get_ab_file.py nginx nginx bd7dad5b
python3 get_ab_file.py nginx nginx 4c5a49ce
python3 get_ab_file.py nginx nginx 71eb19da
python3 get_ab_file.py nginx nginx 56f53316
```

In the above, the third column refers to the owner (i.e., `nginx`), the fourth column refers to the repository (i.e., `nginx`), and the last column refers to the commit ID (e.g., `02cca547`).

As the result, the pre-patch and post-patch files will be stored in `~/GraphSPD/ab_file/`.

#### 1.2 Use Your Own Patches

You can pre-process your own patches by running:
```shell 
python3 get_ab_file.py [owner] [repository] [commitID]
```
where `[owner]`, `[repository]`, and `[commitID]` are the owner name, repository name, and commit ID of the patch hosted on GitHub.

### 2. Generate PatchCPGs

To generate PatchCPGs for all the patches processed by the last step, please run the following commands under `~/GraphSPD/`:

```shell 
chmod -R +x ./joern
sudo python3 gen_cpg.py
python3 merge_cpg.py
```

Here, `gen_cpg.py` will generate two CPGs for pre- and post-patch files, respectively.\
`merge_cpg.py` will generate a merged PatchCPG from the two CPGs.\
The output PatchCPGs will be saved in `~/GraphSPD/testdata/`.

### 3. Run PatchGNN

In `~/GraphSPD/`, run the command:

```shell 
python3 test.py
```

The prediction results are saved in file `~/GraphSPD/logs/test_results.txt`. 

See the results by running:

```shell 
cat logs/test_results.txt
```

The prediction results contains the PatchCPG file path and the predictions, where 1 represents security patch and 0 represents non-security patch.

```text
filename,prediction
./testdata/fc785b12/out_slim_ninf_noast_n1_w.log,0
./testdata/dac90a4b/out_slim_ninf_noast_n1_w.log,1
./testdata/60a8ed26/out_slim_ninf_noast_n1_w.log,1
./testdata/71eb19da/out_slim_ninf_noast_n1_w.log,0
./testdata/9a3ec202/out_slim_ninf_noast_n1_w.log,1
./testdata/bd7dad5b/out_slim_ninf_noast_n1_w.log,1
./testdata/661e4086/out_slim_ninf_noast_n1_w.log,1
./testdata/02cca547/out_slim_ninf_noast_n1_w.log,0
./testdata/4c5a49ce/out_slim_ninf_noast_n1_w.log,0
./testdata/56f53316/out_slim_ninf_noast_n1_w.log,0
```

## Other Resources

[1] [PatchDB: A Large-Scale Security Patch Dataset](https://sunlab-gmu.github.io/PatchDB/)\
[2] [PatchRNN: A Deep Learning-Based System for Security Patch Identification](https://shuwang127.github.io/PatchRNN-demo/)\
[3] [Detecting "0-Day" Vulnerability: An Empirical Study of Secret Security Patch in OSS](https://par.nsf.gov/servlets/purl/10109780)

## Team

The GraphSPD package is built by [Sun Security Laboratory](https://sunlab-gmu.github.io/) (SunLab) at [George Mason University](https://www2.gmu.edu/), Fairfax, VA. 

<div align="left" display="flex">    
    <img src="./docs/imgs/sunlab_logo_full.png" height = "125" alt="sunlab" align="center" />
    &emsp;&emsp;&emsp;&emsp;
    <img src="./docs/imgs/csis_logo.png" height = "135" alt="csis" align="center" />
</div>

---
Last Updated Date: Aug, 2022
