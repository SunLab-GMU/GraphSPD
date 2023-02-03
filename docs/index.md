---
layout: default
---

<!-- We have uploaded the source code to GitHub and will provide instructions and more information after the paper camera-ready. -->

* [Description](#description)
* [Download](#download)
  * [Disclaimer](#disclaimer)
  * [License](#license)
* [Other Resources](#other-resources)
* [Team](#team)


## Description

With the increasing popularity of open-source software, embedded vulnerabilities have been widely propagating to downstream software. Due to different maintenance policies, software vendors may silently release security patches without providing sufficient advisories (e.g., CVE). This leaves users unaware of security patches and provides attackers good chances to exploit unpatched vulnerabilities. Thus, detecting those silent security patches becomes imperative for secure software maintenance. 

We design a graph neural network based security patch detection system named **GraphSPD**, which represents patches as graphs with richer semantics and utilizes a patch-tailored graph model for detection. 

More details about GraphSPD can be found in the paper "[GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics](https://csis.gmu.edu/ksun/publications/SP23_GraphSPD.pdf)", to appear in the 44th IEEE Symposium on Security and Privacy (IEEE S&P 2023), San Francisco, CA, May 22-26, 2023. 

## Download

You can download the source code of GraphSPD via GitHub: [https://github.com/SunLab-GMU/GraphSPD](https://github.com/SunLab-GMU/GraphSPD).

If you are using GraphSPD for work that will result in a publication (thesis, dissertation, paper, article), please use the following citation.

```bibtex
@INPROCEEDINGS{GraphSPD23Wang,
  author={Wang, Shu and Wang, Xinda and Sun, Kun and Jajodia, Sushil and Wang, Haining and Li, Qi},
  booktitle={2023 IEEE Symposium on Security and Privacy (SP)}, 
  title={GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics}, 
  year={2023},
  pages={604-621},
  doi={10.1109/SP46215.2023.00035}
}
```

or

*Shu Wang, Xinda Wang, Kun Sun, Sushil Jajodia, Haining Wang, and Qi Li, "GraphSPD: Graph-Based Security Patch Detection with Enriched Code Semantics," 2023 44th IEEE Symposium on Security and Privacy (S&P 2023), San Francisco, CA, US, 2023, pp. 604-621. doi: 10.1109/SP46215.2023.00035*

### Disclaimer

We developed GraphSPD and released the source code, aiming to help admins and developers identify silent security patches and prioritize their development.
We hold no liability for any undesirable consequences of using the software package.

### License

Copyright 2022 SunLab-GMU

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The `joern` library is based on [Jeorn](https://github.com/joernio/joern), which is also under the Apache License 2.0 (see `./jeorn/LICENSE` for more information).

## Other Resources

[1] [PatchDB: A Large-Scale Security Patch Dataset](https://sunlab-gmu.github.io/PatchDB/)\
[2] [PatchRNN: A Deep Learning-Based System for Security Patch Identification](https://shuwang127.github.io/PatchRNN-demo/)\
[3] [Detecting "0-Day" Vulnerability: An Empirical Study of Secret Security Patch in OSS](https://par.nsf.gov/servlets/purl/10109780)

## Team

The GraphSPD repo is built by [Sun Security Laboratory](https://sunlab-gmu.github.io/) (SunLab) at [George Mason University](https://www2.gmu.edu/), Fairfax, VA. 

<div align="center" display="flex">    
    <img src="./imgs/sunlab_logo_full.png" height = "125" alt="sunlab" align="center" />
    &emsp;&emsp;&emsp;&emsp;
    <img src="./imgs/csis_logo.png" height = "135" alt="csis" align="center" />
</div>
<br/>

---
Last Updated Date: Oct, 2022
