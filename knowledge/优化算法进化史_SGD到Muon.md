# 优化算法进化史：从 SGD 到 Muon 知识库

> 《新六艺》项目 · 知识库文件
> 服务章节：数_七「训练的数学」——「下山」「优化器的进化」两节（鞍点、动量、Adam/AdamW、学习率调度、二阶方法、Muon、μP、低精度）
> 搜索时间：2026-07-16
> 溯源方式：逐条联网核验，优先 arXiv 原文 abstract/正文（部分下载 PDF 提取正文）与作者原始博文/技术报告；每条给出原文精确摘引。企业自研优化器/训练框架标注「利益相关」并从严交叉证实。

---

## 元数据

| 项目 | 内容 |
|------|------|
| 覆盖主题 | 高维鞍点、SGD、动量、Adam、AdamW、warmup/余弦/WSD/梯度裁剪、自然梯度/K-FAC/Shampoo/SOAP、Muon（Newton–Schulz 正交化＋谱视角＋规模化证据＋MuonClip）、μP、混合精度/FP8 |
| 评级双轴 | 信源字母（A–F）＋内容数字（1–5），按 AGENTS.md §3 |
| 使用门槛 | 1–2 可进正文；3–4 进正文须注明局限；⚠ 待核项不得作正文论据 |

---

## 条目 4：高维临界点几乎都是鞍点（Dauphin et al. 2014）

搜索时间 2026-07-16 | 搜索内容：高维非凸优化中鞍点而非局部极小是主要障碍 | 评级 A/1 | 时效：结论稳定，被后续随机矩阵理论/实证工作反复印证

---

在高维非凸损失面上，优化的主要障碍不是「比全局最优高很多的坏局部极小」，而是鞍点的大量繁殖。直觉支持：维度越高，一个临界点在所有方向上都恰好是极小（Hessian 全部特征值同号）的概率越低，绝大多数临界点会在某些方向上升、某些方向下降，即鞍点。因此「往哪走总能找到一条下山的方向」——这是本章「荒野里为什么也能走」的核心：高维这次翻向好的一面。

---

**来源与原文摘引**

Yann Dauphin, Razvan Pascanu, Caglar Gulcehre, Kyunghyun Cho, Surya Ganguli, Yoshua Bengio, "Identifying and attacking the saddle point problem in high-dimensional non-convex optimization," NeurIPS 2014, arXiv:1406.2572。https://arxiv.org/abs/1406.2572 （已 fetch）。信源 A（NeurIPS 2014；作者含 Bengio、Ganguli）。

> "Here we argue, based on results from statistical physics, random matrix theory, neural network theory, and empirical evidence, that a deeper and more profound difficulty originates from the proliferation of saddle points, not local minima, especially in high dimensional problems of practical interest."

内容 1：结论由统计物理/随机矩阵理论多路独立支撑，并被 Choromanska et al. 2015 等后续工作交叉印证。

---

## 条目 5：SGD（Robbins–Monro 1951）与动量法（Polyak 1964 heavy ball）

搜索时间 2026-07-16 | 搜索内容：随机梯度下降与重球动量的原始出处 | 评级：Robbins–Monro A/1；Polyak 书目 A/2，原文逐字⚠ | 时效：奠基文献，无失效

---

**SGD 的祖先——随机逼近**：Robbins & Monro 1951 提出「随机逼近方法」：目标 M(x) 只能带噪声地观测，用逐步实验 x₁, x₂, … 使 xₙ 依概率收敛到方程 M(x)=α 的解 θ。这是随机梯度下降（用小批量噪声梯度替代真实梯度）的数学源头。

**动量——重球法**：Polyak 1964「加速迭代收敛的一些方法」提出 heavy ball（重球）动量：更新时加入上一步位移的惯性项，在狭长峡谷地形里沿谷底方向累积速度、抑制垂直方向的来回震荡，从而加快收敛。这是深度学习动量法（指数滑动平均梯度）的原型。

---

**来源与原文摘引**

Herbert Robbins, Sutton Monro, "A Stochastic Approximation Method," *The Annals of Mathematical Statistics*, 22(3):400–407, 1951, DOI: 10.1214/aoms/1177729586。https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-22/issue-3/A-Stochastic-Approximation-Method/10.1214/aoms/1177729586.full 。信源 A（顶级统计期刊奠基论文）。

> "We give a method for making successive experiments at levels x1, x2, ⋯ in such a way that xn will tend to θ in probability."

B. T. Polyak, "Some methods of speeding up the convergence of iteration methods," 俄文原刊 *Zh. Vychisl. Mat. Mat. Fiz.* 4(5):791–803, 1964；英译 *USSR Computational Mathematics and Mathematical Physics* 4(5):1–17, DOI: 10.1016/0041-5553(64)90137-5。信源 A（书目已核实）。

> ⚠ 待核（仅限逐字原文）：英译本正文遭 ScienceDirect 付费墙（HTTP 403），未使用盗版渠道，未能取得 heavy ball 论点的逐字原文。书目信息（期刊、卷 4、期 5、年 1964、页码、收稿 1962-11-26）已核实；「重球动量加速收敛」的内容由大量后续文献一致转述，内容判定为 2（有确凿出处、逻辑自洽，缺原文逐字独立证实）。

---

## 条目 6：Adam（Kingma & Ba 2015）

搜索时间 2026-07-16 | 搜索内容：Adam 一阶/二阶矩估计、偏差修正、默认超参 | 评级 A/1 | 时效：结论稳定；已被 AdamW 等改进但机制不变

---

Adam＝对每个参数维护梯度的一阶矩（均值 mₜ）与二阶矩（未中心化方差 vₜ）的指数滑动平均，更新量为 mₜ 除以 √vₜ（加 ε）——本质是把更新归一化到与梯度尺度无关，给每个参数各自的自适应步长。因两个滑动平均初始化为 0，早期估计偏向 0，故用偏差修正（bias correction）项 m̂=mₜ/(1−β₁ᵗ)、v̂=vₜ/(1−β₂ᵗ) 抵消。默认超参（原文逐字）：α=0.001, β₁=0.9, β₂=0.999, ε=10⁻⁸。

---

**来源与原文摘引**

Diederik P. Kingma, Jimmy Ba, "Adam: A Method for Stochastic Optimization," ICLR 2015, arXiv:1412.6980。https://arxiv.org/abs/1412.6980 （已 fetch，并由子代理下载 PDF 提取正文逐字核对）。信源 A（ICLR 2015，被引数十万）。

> "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments."（Abstract）

> "Good default settings for the tested machine learning problems are α = 0.001, β1 = 0.9, β2 = 0.999 and ε = 10−8."（Algorithm 1 图注，第 2 页，逐字确认）

> "Adam utilizes initialization bias correction terms ... this initialization bias can be easily counteracted, resulting in bias-corrected estimates."（§3 Initialization Bias Correction）

内容 1：机制与默认值均逐字核实，被无数实现交叉印证。

---

## 条目 7：AdamW（Loshchilov & Hutter，解耦权重衰减）

搜索时间 2026-07-16 | 搜索内容：L2 正则 ≠ 权重衰减（对自适应优化器）、解耦权重衰减 | 评级 A/1 | 时效：结论稳定，AdamW 已成 LLM 训练默认之一

---

对标准 SGD，L2 正则化与权重衰减（按学习率缩放后）等价；但对 Adam 这类自适应优化器**不等价**——因为 L2 正则项会被并入梯度、再经 √v 的自适应缩放，导致大梯度参数被衰减得更少，破坏了「所有权重按同一比例收缩」的本意。AdamW 的修正：把权重衰减从损失梯度里拆出去，直接对权重乘一个衰减因子（解耦权重衰减），恢复权重衰减的原始形式。这就是正文「权重衰减为什么必须从梯度里拆出去」的那笔账。

---

**来源与原文摘引**

Ilya Loshchilov, Frank Hutter, "Decoupled Weight Decay Regularization," ICLR 2019, arXiv:1711.05101。https://arxiv.org/abs/1711.05101 （已 fetch）。信源 A（ICLR 2019）。

> "L2 regularization and weight decay regularization are equivalent for standard stochastic gradient descent (when rescaled by the learning rate), but as we demonstrate this is not the case for adaptive gradient algorithms, such as Adam. ... we propose a simple modification to recover the original formulation of weight decay regularization by decoupling the weight decay from the optimization steps taken w.r.t. the loss function."

内容 1：论证清晰、被广泛复现（PyTorch/JAX 均内置 AdamW）。

---

## 条目 8：学习率的账——warmup、余弦、WSD、梯度裁剪

搜索时间 2026-07-16 | 搜索内容：warmup 依据、余弦退火 SGDR、WSD 调度、梯度范数裁剪 | 评级：SGDR A/1；梯度裁剪 A/1；warmup（Goyal 经验 A/2、RAdam 解释 B/2）；WSD B/2（利益相关，方法性） | 时效：调度经验规律，随实践演进

---

**warmup（学习率预热）**：训练初期先把学习率从很小逐步升到目标值，避免开局大步长破坏尚未稳定的参数。Goyal et al. 2017（大批量 ImageNet 一小时）提出 gradual warmup 的经验做法；RAdam（Liu et al. 2019）给出一种理论解释：自适应学习率在早期方差过大，warmup 起到方差缩减作用（此解释是其中一种说法，非唯一定论）。

**余弦调度**：Loshchilov & Hutter 2016（SGDR）提出带热重启的 SGD，重启周期内学习率按余弦形状从高退火到低——「余弦退火」由此成为主流调度（注：余弦函数形式是论文正文机制，abstract 未出现 "cosine" 字样）。

**WSD（Warmup-Stable-Decay）**：MiniCPM（Hu et al. 2024）提出的三段式调度——预热、长时间恒定学习率、末段快速衰减，便于持续训练与领域适应，也便于研究数据-模型缩放律。

**梯度裁剪**：Pascanu et al. 2013 针对 RNN 梯度爆炸提出梯度范数裁剪（gradient norm clipping）：当梯度范数超阈值时按比例缩回，防止一步跳飞。

---

**来源与原文摘引**

Priya Goyal 等, "Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour," 2017, arXiv:1706.02677。信源 A（FAIR）。
> "Gradual warmup. We present an alternative warmup that gradually ramps up the learning rate from a small to a large value. This ramp avoids a sudden increase of the learning rate, allowing healthy convergence at the start of training."（§2.2，PDF 正文）

Liyuan Liu 等, "On the Variance of the Adaptive Learning Rate and Beyond"（RAdam）, ICLR 2020, arXiv:1908.03265。信源 A。内容 2（warmup 的方差解释是一家之说）。
> "we identify a problem of the adaptive learning rate (i.e., it has problematically large variance in the early stage), suggest warmup works as a variance reduction technique..."（Abstract）

Ilya Loshchilov, Frank Hutter, "SGDR: Stochastic Gradient Descent with Warm Restarts," ICLR 2017, arXiv:1608.03983。信源 A。
> "we propose a simple warm restart technique for stochastic gradient descent to improve its anytime performance when training deep neural networks."（Abstract）

Shengding Hu 等, "MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training Strategies," 2024, arXiv:2404.06395。信源 B（模型团队技术报告，利益相关；方法性内容，交叉可查）。
> "we introduce a Warmup-Stable-Decay (WSD) learning rate scheduler (LRS), conducive to continuous training and domain adaptation."（Abstract）

Razvan Pascanu, Tomas Mikolov, Yoshua Bengio, "On the difficulty of training Recurrent Neural Networks," ICML 2013, arXiv:1211.5063（arXiv 提交 2012，会议发表 2013）。信源 A。
> "We propose a gradient norm clipping strategy to deal with exploding gradients and a soft constraint for the vanishing gradients problem."（Abstract）

---

## 条目 9：二阶的诱惑——自然梯度、K-FAC、Shampoo、SOAP

搜索时间 2026-07-16 | 搜索内容：自然梯度、Kronecker 近似二阶、张量预条件 Shampoo、SOAP | 评级：Amari A/1（出版页付费墙，逐字⚠）；K-FAC A/1；Shampoo A/1；SOAP B/2 | 时效：Shampoo/SOAP 属活跃研究，实践仍在演进

---

牛顿法用 Hessian 逆预条件梯度，但 Hessian 是参数量的平方，大模型不可行。一系列方法用矩阵结构近似二阶信息：

- **自然梯度（Amari 1998）**：在概率模型的参数空间里，最速下降方向不是普通梯度，而是用 Fisher 信息矩阵度量的「自然梯度」；在线自然梯度学习被证明是 Fisher efficient（渐近达到最优批估计的效率）。
- **K-FAC（Martens & Grosse 2015）**：把每层对应的 Fisher 大块近似为两个小矩阵的 Kronecker 积，从而高效近似自然梯度下降。
- **Shampoo（Gupta, Koren, Singer 2018）**：结构感知的张量预条件，为每个维度各维护一个预条件矩阵、在其余维度上收缩，避免存储完整巨型预条件矩阵。
- **SOAP（Vyas et al. 2024）**：先证明「Shampoo（用 1/2 次幂）等价于在其预条件子特征基下运行 Adafactor（Adam 的省内存近似）」，据此让优化器在该（缓慢变化的）特征基坐标系里，像 Adam 那样持续更新二阶矩滑动平均，从而稳定并加速 Shampoo，仅比 Adam 多一个超参。

---

**来源与原文摘引**

Shun-ichi Amari, "Natural Gradient Works Efficiently in Learning," *Neural Computation* 10(2):251–276, 1998, DOI: 10.1162/089976698300017746。信源 A（Neural Computation，奠基论文，dblp 书目核实）。
> ⚠ 待核（仅限逐字原文）：MIT Press 原文页返回 403（付费墙），摘要文字取自检索聚合，未逐字复核出版社原页。核心内容（自然梯度＝信息几何下最速方向、Fisher efficient）与书目均一致，内容判定 1。
> 转引摘要："the ordinary gradient of a function does not represent its steepest direction, but the natural gradient does ... natural gradient online learning ... is proved to be Fisher efficient."

James Martens, Roger Grosse, "Optimizing Neural Networks with Kronecker-factored Approximate Curvature," ICML 2015, arXiv:1503.05671。信源 A。
> "an efficient method for approximating natural gradient descent in neural networks which we call Kronecker-Factored Approximate Curvature (K-FAC) ... approximates various large blocks of the Fisher (corresponding to entire layers) as being the Kronecker product of two much smaller matrices."

Vineet Gupta, Tomer Koren, Yoram Singer, "Shampoo: Preconditioned Stochastic Tensor Optimization," ICML 2018, arXiv:1802.09568。信源 A。
> "Shampoo maintains a set of preconditioning matrices, each of which operates on a single dimension, contracting over the remaining dimensions."

Nikhil Vyas, Depen Morwani, Rosie Zhao, Mujin Kwun, Itai Shapira, David Brandfonbrener, Lucas Janson, Sham Kakade, "SOAP: Improving and Stabilizing Shampoo using Adam," 2024, arXiv:2409.11321。信源 B（预印本，尚新；Harvard Kempner 团队）。内容 2。
> "Shampoo is equivalent to running Adafactor in the eigenbasis of Shampoo's preconditioner ... SOAP mitigates this degradation by continually updating the running average of the second moment, just as Adam does, but in the current (slowly changing) coordinate basis."

---

## 条目 10：Muon——把梯度正交化（重点）

搜索时间 2026-07-16 | 搜索内容：Muon 原始定义（Newton–Schulz 正交化）、谱范数视角、规模化证据、Kimi K2 MuonClip | 评级：机制描述 B/2（一手博文＋规模化论文交叉证实）；企业规模化证据 B/2（利益相关） | 时效：2024–2025 新方法，仍在快速演进，实验结论每季度可能被修订

---

**机制（原始定义）**：Muon（MomentUm Orthogonalized by Newton-Schulz）只作用于神经网络的二维隐藏层参数。它先取 SGD-动量产生的更新矩阵，再对其做 Newton–Schulz（NS）迭代作为后处理，把更新矩阵近似正交化——即用「离它最短（Frobenius 距离）的半正交矩阵」替换它。等价地，若更新矩阵 SVD 为 USVᵀ，正交化就是把它替换为 UVᵀ（丢掉奇异值大小、只保留方向）。输入层、输出层（嵌入与分类头）仍用 AdamW，不用 Muon。

**为什么这样做——谱视角**：优化真正该控制的，不是每个分量各自的大小，而是「更新矩阵」作为一个整体的谱范数（最大奇异值）。正交化让更新矩阵所有奇异值都等于 1，等于对更新做了谱意义上的规范化。相关理论谱系：Bernstein & Newhouse 2024「Old Optimizer, New Norm」把 Adam/Shampoo/Prodigy 统一理解为「关掉指数滑动平均后，各自是某个算子范数下的最速下降」，并主张不同张量应按其在网络中的角色分配不同范数——这是 Muon 谱范数解释的理论近亲。

**⚠ 归因更正（重要）**：常见口径「Muon = 谱范数下的最速下降」这一具体命题，**并不出自** arXiv:2409.20325 论文正文——该论文（v1/v2）通篇未出现 "Muon" 或 "spectral norm" 字样，只讨论 Adam/Shampoo/Prodigy。「Muon 对应谱范数最速下降」的具体论述应归于 Bernstein 等人的后续/相关博文（如「Deriving Muon」系列、modular norm 材料），引用时须注明信源是博文而非该 arXiv 论文，避免张冠李戴。

**规模化证据**：Moonshot AI「Muon is Scalable for LLM Training」（2025）报告，加两处改进即可让 Muon 在大规模训练中开箱即用：(1) 加权重衰减；(2) 谨慎调节每参数更新尺度（consistent update RMS / per-parameter update scale）。据其口径，Muon 相比 AdamW 在计算最优训练下达到约 2× 计算效率，并以 Moonlight（3B/16B MoE，5.7T tokens）验证。Kimi K2 技术报告（2025）进一步提出 MuonClip＝Muon＋QK-Clip：QK-Clip 在更新后对注意力 Q/K 投影权重做钳制，抑制大规模下 Muon 更易出现的「注意力 logit 爆炸」不稳定；据报告，Kimi K2 用 MuonClip 预训练 15.5T tokens 且零 loss spike。这些企业自研证据均标「利益相关」，从严对待。

正文可用口径：2025 年起，若干新的大模型训练开始用 Muon 系方法替换沿用十年的 Adam——这是「近两年优化算法的代表作」，但其规模化优势主要由发起团队与厂商报告，属仍在检验中的实验规律。

---

**来源与原文摘引**

Keller Jordan, "Muon: An optimizer for hidden layers in neural networks," 个人技术博文，2024-12-08。https://kellerjordan.github.io/posts/muon/ （已 fetch，两次交叉核对贡献者名单）。列名贡献者：Keller Jordan（作者）＋ Jeremy Bernstein, Laker Newhouse, Vlado Boza, Yuchen Jin, Jiacheng You, Franz Cesista, Braden Koszarsky。信源 F→B（自出版个人技术报告，无正式同行评审；但为 Muon 的权威一手定义，且被 arXiv:2502.16982 独立复述，故按 B 处理并标注性质）。

> "Muon ... optimizes 2D neural network parameters by taking the updates generated by SGD-momentum, and then applying a Newton-Schulz (NS) iteration as a post-processing step to each of them before applying them to the parameters."
> "The function of the NS iteration is to approximately orthogonalize the update matrix ... This is equivalent to replacing the update by UV^T, where USV^T is its singular value decomposition (SVD)."
> "When training transformers, AdamW should be used for the embedding and final classifier head layers in order to attain the best performance."

Jeremy Bernstein, Laker Newhouse, "Old Optimizer, New Norm: An Anthology," 2024, arXiv:2409.20325。信源 A。
> "after switching off exponential moving averages, each method is equivalent to steepest descent under a particular norm ... Different operator norms should be assigned to different tensors based on the role that the tensor plays within the network."
> ⚠ 该论文未提 Muon/谱范数；见上「归因更正」。

Jingyuan Liu 等（Moonshot AI）, "Muon is Scalable for LLM Training," 2025, arXiv:2502.16982。信源 B（厂商，利益相关）。
> "Muon achieves ~2× computational efficiency compared to AdamW with compute optimal training."；两处改进："(1) adding weight decay and (2) carefully adjusting the per-parameter update scale."

Kimi Team（Moonshot AI）, "Kimi K2: Open Agentic Intelligence," 2025, arXiv:2507.20534。信源 B（厂商，利益相关）。
> "We propose the MuonClip optimizer, which improves upon Muon with a novel QK-clip technique to address training instability while enjoying the advanced token efficiency of Muon ... K2 was pre-trained on 15.5 trillion tokens with zero loss spike."

内容 2：机制定义有一手权威出处且被独立论文复述；规模化数字为利益相关方单方报告，须交叉与从严。

---

## 条目 11：μP / muTransfer（超参随宽度零样本迁移）

搜索时间 2026-07-16 | 搜索内容：Maximal Update Parametrization、muTransfer、小模型调参迁移到大模型 | 评级 A/2 | 时效：2022 论文，方法被业界采用；迁移精度依赖参数化实现

---

在「最大更新参数化」（μP）下，许多最优超参（尤其学习率）在模型宽度改变时保持稳定，于是可以在小模型上调好超参、零样本迁移到大模型，无需在大模型上重新搜参（muTransfer）。论文实例：从 40M 参数模型迁移超参去训 6.7B 的 GPT-3，超越已发表基线，而调参成本仅为总预训练成本的 7%。这把「调参」从大模型上的玄学炼丹，变成小模型上一次性的、可迁移的数学工作。

---

**来源与原文摘引**

Greg Yang, Edward J. Hu, Igor Babuschkin, Szymon Sidor, Xiaodong Liu, David Farhi, Nick Ryder, Jakub Pachocki, Weizhu Chen, Jianfeng Gao, "Tensor Programs V: Tuning Large Neural Networks via Zero-Shot Hyperparameter Transfer," 2022, arXiv:2203.03466。https://arxiv.org/abs/2203.03466 （已 fetch）。信源 A（Microsoft/OpenAI，NeurIPS 2021 相关系列）。

> "in the recently discovered Maximal Update Parametrization (muP), many optimal HPs remain stable even as model size changes. This leads to a new HP tuning paradigm we call muTransfer ... by transferring from 40M parameters, we outperform published numbers of the 6.7B GPT-3 model, with tuning cost only 7% of total pretraining cost."

内容 2：结论有确凿出处、逻辑自洽、被业界（含 Cerebras、多家 LLM 团队）采用；迁移的严格性依赖参数化正确实现，故从严记 2。

---

## 条目 12：低精度训练——混合精度与 FP8（DeepSeek-V3）

搜索时间 2026-07-16 | 搜索内容：混合精度训练（loss scaling、FP32 主权重）、FP8 大规模训练实例 | 评级：混合精度 A/1；DeepSeek-V3 FP8 B/2（利益相关，FP8 细节在正文非摘要） | 时效：FP8 训练为 2024–2025 前沿，实践快速演进

---

**混合精度训练（Micikevicius et al. 2017）**：用 FP16 半精度做前向/反向以省显存和加速，但需两项技术兜住数值范围：(1) 保留一份 FP32 主权重副本累积梯度、每步再舍入到半精度；(2) 损失缩放（loss scaling）——把 loss 乘一个大因子，防止很小的梯度在 FP16 下下溢为 0。这就是数_五「浮点税」一线在训练场的收账：哪些量必须留在高精度是有讲究的。

**FP8 大规模实例（DeepSeek-V3）**：DeepSeek-V3（671B 总参、37B 激活的 MoE，14.8T tokens 预训练）采用细粒度 FP8 混合精度框架，核心 GEMM 矩阵乘用 FP8，而嵌入模块、输出头、MoE 门控、归一化算子、注意力算子，以及主权重/权重梯度/优化器状态保留高精度（BF16/FP32）。它是「FP8 可用于超大规模训练」的公开工程验证之一。

---

**来源与原文摘引**

Paulius Micikevicius 等, "Mixed Precision Training," ICLR 2018, arXiv:1710.03740。信源 A（NVIDIA/Baidu）。
> "we recommend maintaining a single-precision copy of the weights that accumulates the gradients after each optimizer step. This single-precision copy is rounded to half-precision format during training. Secondly, we propose scaling the loss appropriately to handle the loss of information with half-precision gradients."

DeepSeek-AI, "DeepSeek-V3 Technical Report," 2024（arXiv:2412.19437，2025-02 修订）。https://arxiv.org/abs/2412.19437 。信源 B（厂商技术报告，利益相关）。
> ⚠ 注意：**abstract 不含 "FP8" 字样**，FP8 表述在正文训练基础设施章节（arXiv HTML 全文）："we propose a fine-grained mixed precision framework utilizing the FP8 data format for training DeepSeek-V3"；保留高精度的组件："the embedding module, the output head, MoE gating modules, normalization operators, and attention operators."（引用须指向正文段落，勿误引摘要。）

内容：混合精度记 1（多来源、多框架内置复现）；DeepSeek-V3 FP8 记 2（单一厂商报告，利益相关，须交叉）。
