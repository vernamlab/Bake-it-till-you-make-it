# Heat-induced Side-channel Analysis against Masked Neural Networks
This repo contains the code and a link to the dataset of traces used to evaluate the robustness of masked neural networks (NNs) against side-channel attacks. The results of this study are presented in the paper ``Bake It Till You Make It: Heat-induced Leakage from Masked Neural Networks'' (https://eprint.iacr.org/2023/076.pdf). In this study, power traces have been collected using a LeCroy wavePro 725Zi oscilloscope in the Riscure setup. [ModuloNET](https://tches.iacr.org/index.php/TCHES/article/view/9306/8872), a masked NN offering first-order security, is implemented on Artix-7 FPGA on Chipwhisperer CW305 target, and the capturing process is controlled by the Chipwhisperer Lite board. 

# Dataset
The dataset is available upon request. Please contact fganji (at) wpi (dot) edu

# TVLA test

In the folder TVLA, you will find Jupyter python notebooks which can be used to replicate the results using the dataset provided. 

# Results

In the results folder, you will find PNGs that were generated using the t-test codes provided in the repo.

# .bib citation
@article{mehta2023bake,
  title={Bake It Till You Make It: Heat-induced Leakage from Masked Neural Networks},
  author={Mehta, Dev M and Hashemi, Mohammad and Koblah, David S and Forte, Domenic and Ganji, Fatemeh},
  journal={Cryptology ePrint Archive},
  year={2023}
}
