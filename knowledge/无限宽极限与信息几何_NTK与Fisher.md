# 无限宽极限与信息几何：NTK、lazy training、Fisher 信息、Kolmogorov 压缩与窄网络逼近

> **适用章节**：《新六艺》· 数_七「训练的数学」的数学加深。本文件为 `优化算法进化史_SGD到Muon.md`、`深度学习泛化之谜.md`、`损失函数与信息论_交叉熵与压缩.md` 的补充条目：无限宽网络的训练动力学=固定核的核回归（NTK）、lazy training 与特征学习之争、Fisher 信息几何与自然梯度、语言模型压缩率与 Kolmogorov 复杂度、通用逼近的窄网络加强版。
> **核查日期**：2026-07-17。核查方式：WebSearch 定位 → WebFetch 抓取 arXiv abstract 与论文 HTML（ar5iv）逐字核对；Delétang 正文的 Kolmogorov/Solomonoff 段落经 ar5iv 全文核到。
> **政治边界（§6）核查**：本主题为数学与机器学习理论，不涉军政，无需背景参照标注。

## 目录

1. 神经正切核（NTK）：无限宽网络的训练=固定核核回归（Jacot, Gabriel & Hongler 2018）
2. lazy training 与特征学习之争（Chizat, Oyallon & Bach 2019）；μP 与特征学习极限一句话
3. Fisher 信息与自然梯度：定义、Fisher 度量下最速下降、KL 二阶展开≈Fisher
4. Kolmogorov 复杂度与 LLM 压缩：压缩长度是 K 复杂度的上界（Delétang 2023 正文直接讨论）
5. 通用逼近的窄网络加强版：宽度 (n+4) 的 ReLU 网络（Lu et al. 2017）

---

## 一、神经正切核（NTK）：无限宽网络的训练=固定核核回归

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-17 | Neural Tangent Kernel（1806.07572）；无限宽极限 NTK 收敛到确定核并训练中保持不变；训练=函数空间的核梯度下降；最小二乘下网络函数服从线性微分方程 | A1 | NeurIPS 2018 论文；arXiv abstract 逐字核对。

**知识内容：**

- **初始化即高斯过程**：在无限宽极限下，网络在初始化时等价于高斯过程，从而把神经网络接到核方法上。
- **训练也由一个核描述**：梯度下降训练参数时，网络函数 f_θ（输入→输出的映射）沿一个新核——**神经正切核（NTK）**——的核梯度下降，最小化的是（关于函数的、凸的）泛函代价。
- **无限宽 ⇒ NTK 冻结**：NTK 在有限宽时随机、且训练中变化；但在**无限宽极限下收敛到一个确定的极限核，并在训练全程保持不变**。这使得可在**函数空间**（而非参数空间）研究训练：最小二乘回归下，网络函数 f_θ 训练中服从一个**线性微分方程**，沿 NTK 最大的核主成分收敛最快（为 early stopping 提供理论动机）；收敛性与极限 NTK 的正定性挂钩。
- **正文口径**：这是「无限宽的神经网络其实在做固定核的核回归」的严格出处——训练动力学被一个不动的核完全刻画，网络退化为线性模型（关于参数的线性化）。它把「为什么超宽网络能训、且行为可预测」这件事，还原成经典核方法。

**来源列表与原文摘引：**

- Jacot, A., Gabriel, F. & Hongler, C. (2018). "Neural Tangent Kernel: Convergence and Generalization in Neural Networks." NeurIPS 2018；arXiv:1806.07572。（abstract 逐字核对。）
  - 原文："during gradient descent on the parameters of an ANN, the network function f_θ … follows the kernel gradient of the functional cost … w.r.t. a new kernel: the Neural Tangent Kernel (NTK). … While the NTK is random at initialization and varies during training, in the infinite-width limit it converges to an explicit limiting kernel and it stays constant during training. This makes it possible to study the training of ANNs in function space instead of parameter space. … in the infinite-width limit, the network function f_θ follows a linear differential equation during training."

---

## 二、lazy training 与特征学习之争；μP 与特征学习极限

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-17 | lazy training（Chizat, Oyallon & Bach 2019, 1812.07956）；过参数网络训练时参数几乎不动、等价于线性化/正定核学习；lazy 未必是深度学习成功之因 | A1 | NeurIPS 2019 论文；arXiv abstract 逐字核对。

**知识内容：**

- **lazy training 现象**：强过参数网络用梯度法可指数快收敛到零训练损失，而**参数几乎不变**。Chizat 等指出，这一「lazy training」**不是过参数网络独有**，而源于一个（常被隐含采用的）**缩放选择**，使模型表现得像它在初始化处的**线性化**——于是等价于用一个正定核在学习（即 NTK 那一套）。
- **与特征学习的张力（正文须注明的「之争」）**：作者用实验给出**批判性一笔**——常用的非线性深度卷积网络在 lazy 区训练时**性能下降**；故 lazy training **不太可能**是神经网络在困难高维任务上诸多成功的根源。换言之：把网络当固定核（lazy/NTK 区）是可分析的，但**真正带来性能的是「特征学习」区**（参数显著移动、表示随训练改变），二者是两种不同的训练体制。
- **与 μP 的关系（一句话，接已有条目）**：`优化算法进化史_SGD到Muon.md` 条目 11 已收 μP/muTransfer（超参随宽度零样本迁移）。补一句其理论定位：μP（最大更新参数化）正是为在**无限宽极限下保持「特征学习」**而设计的参数化——与 NTK/lazy 那种「无限宽即冻结为固定核」的极限相对立。即同为无限宽，NTK 极限是「懒惰、核回归、不学特征」，μP 极限是「仍在学特征」，二者由缩放/参数化选择区分。（Yang & Hu 特征学习极限，见 `优化算法进化史` 已有条目，此处不重复溯源。）

**来源列表与原文摘引：**

- Chizat, L., Oyallon, E. & Bach, F. (2019). "On Lazy Training in Differentiable Programming." NeurIPS 2019；arXiv:1812.07956。（abstract 逐字核对。）
  - 原文："this 'lazy training' phenomenon is not specific to over-parameterized neural networks, and is due to a choice of scaling, often implicit, that makes the model behave as its linearization around the initialization, thus yielding a model equivalent to learning with positive-definite kernels. … we observe that the performance of commonly used non-linear deep convolutional neural networks in computer vision degrades when trained in the lazy regime. This makes it unlikely that 'lazy training' is behind the many successes of neural networks in difficult high dimensional tasks."
  - 口径注（纠正易错引用）：任务简称「Chizat & Bach 2019」，本文**第二作者为 Édouard Oyallon**，完整作者为 Chizat, Oyallon & Bach，引用时勿漏。

---

## 三、Fisher 信息与自然梯度：定义、Fisher 度量下最速下降、KL 二阶展开≈Fisher

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-17 | Fisher 信息矩阵定义；自然梯度=Fisher 度量下最速下降；KL 二阶泰勒展开≈½δᵀFδ（Amari 1998；Martens 2020） | A2 | 经典结果，无失效条件。Martens abstract 核到 Fisher=广义高斯牛顿；KL≈Fisher 的逐字原始教材页未抓取，见 ⚠。

**知识内容（补充 `优化算法进化史` 的 Amari 1998 条目）：**

- **Fisher 信息矩阵定义**：对参数化概率模型 p(x; θ)，Fisher 信息矩阵
  F(θ) = E_{x∼p(·;θ)}[ ∇_θ log p(x;θ) · ∇_θ log p(x;θ)ᵀ ] = −E[ ∇²_θ log p(x;θ) ]（两式在正则条件下相等）。它度量「对数似然对参数的敏感度」，是**参数空间上概率分布之间的自然黎曼度量**（信息几何的度量张量）。
- **自然梯度=Fisher 度量下的最速下降**：普通梯度是欧氏度量下的最速下降方向；把参数空间赋予 Fisher 度量后，最速下降方向是**自然梯度** F(θ)⁻¹ ∇_θ L(θ)。更新为 θ ← θ − γ F(θ)⁻¹ ∇L。其含义：不在「参数改变量」而在「模型输出分布改变量（KL）」意义下做最速下降，故对参数化的选择不敏感。
- **KL 二阶展开 ≈ Fisher**：模型分布之间的 KL 散度在局部由 Fisher 矩阵二次型逼近：
  **KL( p_θ ‖ p_{θ+δ} ) = ½ δᵀ F(θ) δ + O(‖δ‖³)**（一阶项为零，因 KL 在 δ=0 取最小值 0）。这正是「Fisher 是 KL 诱导的局部度量」的来源，也把「自然梯度在 KL 约束下最速下降」讲严格：在 KL(θ,θ+δ)≤常数 的信赖域里最速降 L，一阶最优解即自然梯度方向。
- **正文口径**：本书讲「训练不只在参数空间里走直线，而在分布空间里走直线」时，Fisher 是那把尺子；自然梯度是「按分布距离而非参数距离」的最速下降。Amari 1998 已证在线自然梯度学习是 Fisher efficient（见已有条目）。

**来源列表与原文摘引：**

- Amari, S. (1998). "Natural Gradient Works Efficiently in Learning." *Neural Computation*, 10(2), 251–276.（自然梯度=信息几何下最速方向、Fisher efficient；详见 `优化算法进化史_SGD到Muon.md` 已有条目的原文摘引。）
- Martens, J. (2020). "New insights and perspectives on the natural gradient method." *JMLR* 21(146)；arXiv:1412.1193。（abstract 核到。）
  - 原文（abstract）："the Fisher information matrix is shown to be equivalent to the Generalized Gauss-Newton matrix"（Fisher=广义高斯牛顿，为自然梯度作为二阶法的桥梁）。
- Amari, S. & Nagaoka, H. (2000). *Methods of Information Geometry*. AMS/Oxford.（Fisher 为参数流形黎曼度量、KL 局部二阶展开等于 Fisher 二次型的标准教材出处。）
- ⚠ 待核（仅限逐字原文）：本条「KL 二阶展开 = ½δᵀFδ」与「自然梯度=Fisher 度量最速下降」为信息几何经典结论（Amari 1998/Amari–Nagaoka 2000、Martens 2020 均含），但本次仅从二手讲义（多份大学课程 note）与 Martens abstract 交叉印证，**未抓到 Amari–Nagaoka 教材相应页的逐字原文**。该结论属初等可推导（KL 在最小点的 Hessian 即 Fisher），内容判定 2；正文引用时按 A2 处理，如需页码级引用需线下取教材。

---

## 四、Kolmogorov 复杂度与 LLM 压缩：压缩长度是 K 复杂度的上界

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-17 | 语言模型压缩率与 Kolmogorov 复杂度/Solomonoff 的关系；Delétang 2023 正文是否直接讨论 K 复杂度 | A1 | Delétang 2023（ICLR 2024）正文 ar5iv 逐字核到，直接讨论 Kolmogorov/Solomonoff；理论关系为经典 AIT 结论。

**知识内容（补充 `损失函数与信息论` 的 Delétang 条目）：**

- **精确表述**：Kolmogorov 复杂度 K(x) 是 x 的**最短程序长度**，是「x 可被压到多短」的**理论下界**（任何无损压缩器都压不过 K，至多差一个与 x 无关的常数）。等价地，**任何实际压缩器（含语言模型+算术编码）对 x 的输出长度都是 K(x) 的一个上界**：K(x) ≤ L_LM(x) + c。所以「语言模型压缩率是数据 Kolmogorov 复杂度的上界」这一表述**成立且方向正确**——LM 越会压，其码长越逼近（但不可能低于）K(x)。
- **Delétang 2023 正文直接讨论 K 复杂度与 Solomonoff（本次核实的关键点）**：论文正文明确把「最优通用信源编码」与 Kolmogorov 复杂度挂钩，并引入 Solomonoff 预测器（所有可编程预测器的贝叶斯混合）作为理论上的最优预测/压缩。故本书要谈「压缩即智能」的信息论根基时，**可直接引 Delétang 2023 正文**（A 级、ICLR 2024），无需仅靠名人发言旁证。
- **香农层的桥**：更弱但更可操作的一层是香农信源编码定理——期望码长下界为熵 H(ρ)，而最优熵编码的期望码长等于模型的负对数似然（log loss）。故「最小化 log loss = 最小化（该模型作算术编码器时的）压缩率」。K 复杂度层是「与模型无关的终极下界」，香农/log-loss 层是「给定模型的可达码长」。
- **名人论述（C 级旁证，不作正文论据）**：Ilya Sutskever 在 Simons Institute 讲座（"An Observation on Generalization"）用 Kolmogorov 复杂度界定无监督学习、称 LLM 是其近似；Marcus Hutter 公开转述认可该讲法。此为背景参照，正文论据以 Delétang 2023 与经典 AIT 教材（Li & Vitányi）为准。

**来源列表与原文摘引：**

- Delétang, G., Ruoss, A., Duquenne, P.-A., Catt, E., Genewein, T., Mattern, C., Grau-Moya, J., Wenliang, L. K., Aitchison, M., Orseau, L., Hutter, M. & Veness, J. (2023). "Language Modeling Is Compression." arXiv:2309.10668（ICLR 2024）。（正文经 ar5iv `ar5iv.labs.arxiv.org/abs/2309.10668` 逐字核对。）
  - Kolmogorov（正文原文）：最优通用信源编码 "can, in theory, be achieved by choosing ℓ_c(x_{1:n}) as the Kolmogorov complexity"（选码长为 x 的 Kolmogorov 复杂度）。
  - Solomonoff（正文原文）：Solomonoff 预测器为 "a Bayesian mixture of all predictors that can be programmed in a chosen Turing-complete programming language."
  - 香农/算术编码（正文原文）："Shannon's source coding theorem establishes the limit on possible data compression as L ≥ H(ρ) for any possible code, where H(ρ) := E_{x∼ρ}[−log₂ ρ(x)]"；"minimizing the log-loss is equivalent to minimizing the compression rate of that model used as a lossless compressor with arithmetic coding."
- 教材出处（K 复杂度=最短程序、压缩长度为其上界）：Li, M. & Vitányi, P. *An Introduction to Kolmogorov Complexity and Its Applications*（Springer）。
- 旁证（C）：Sutskever, I. "An Observation on Generalization"（Simons Institute 讲座，2023）；Marcus Hutter 转述（X/Twitter）。仅作背景参照，不进正文论据。

---

## 五、通用逼近的窄网络加强版：宽度 (n+4) 的 ReLU 网络（Lu et al. 2017）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-17 | 宽度受限 ReLU 网络的通用逼近；宽度 (n+4)（n 为输入维）足以逼近任意 Lebesgue 可积函数；宽度 n 相变（Lu et al. 2017, 1709.02540） | A2 | NeurIPS 2017 论文；arXiv abstract 逐字核对。

**知识内容（补充 `神经网络的数学基础_逼近与反向传播` 的深度视角）：**

- **窄而深也能通用逼近**：经典通用逼近定理是「宽度换表达力」（浅而宽，Cybenko/Hornik）。Lu et al. 从**宽度**视角给出对偶结论：**宽度为 (n+4) 的 ReLU 网络（n 为输入维），在任意深度下是通用逼近器**（对 Lebesgue 可积函数）。
- **相变（宽度下界）**：除一个测度零集外，**所有函数都无法被宽度为 n 的 ReLU 网络逼近**——存在一个宽度阈值处的相变（n 不够、n+4 就够）。这与已有条目里「深度赢过宽度」（Telgarsky 2016、Eldan–Shamir 2016）互补：不仅深度能省参数，**窄到接近输入维、只要够深，就仍是万能逼近器**。
- **正文口径**：讲「万能的三明治」时可加这一句现代加强——通用逼近不必靠「无限加宽」，一个宽度仅比输入维多 4 的网络，只要够深就够用；表达力的天平在深度一侧。

**来源列表与原文摘引：**

- Lu, Z., Pu, H., Wang, F., Hu, Z. & Wang, L. (2017). "The Expressive Power of Neural Networks: A View from the Width." NeurIPS 2017；arXiv:1709.02540。（abstract 逐字核对。）
  - 原文："We show a universal approximation theorem for width-bounded ReLU networks: width-(n+4) ReLU networks, where n is the input dimension, are universal approximators. Moreover, except for a measure zero set, all functions cannot be approximated by width-n ReLU networks, which exhibits a phase transition."
- 评级说明：NeurIPS 2017 同行评审（A），该宽度界为其原创结果、单一上游，内容记 2 → A2。
