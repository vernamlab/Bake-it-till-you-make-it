# Bake it till you make it! Heat-induced Power Side-channel Analysis against Masked Neural Networks
This repo contains the code and a link to the dataset of traces used to evaluate the robustness of masked neural networks (NNs) against side-channel attacks. The results of this study are presented in the paper ``Bake It Till You Make It: Heat-induced Power Leakage from Masked Neural Networks'' (https://eprint.iacr.org/2023/076.pdf). [ModuloNET](https://tches.iacr.org/index.php/TCHES/article/view/9306/8872), a masked NN offering first-order security, is implemented on Artix-7 FPGA on Chipwhisperer CW305 target, and the capturing process is controlled by the Chipwhisperer Lite and CW Husky boards. A set of power traces captured for this study is gievn in the dataset folder. 

# Dataset
The dataset is available [here](https://app.box.com/v/BITUMI-traces).

# Python Scripts

In the folder Python, you will find Jupyter python notebooks which can be used to replicate the results using the dataset provided.


# .bib citation
@article{mehta2023bake,
  title={Bake It Till You Make It: Heat-induced Leakage from Masked Neural Networks},
  author={Mehta, Dev M and Hashemi, Mohammad and Koblah, David S and Forte, Domenic and Ganji, Fatemeh},
  journal={Cryptology ePrint Archive},
  year={2023}
}
