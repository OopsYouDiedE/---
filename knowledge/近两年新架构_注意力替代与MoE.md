# 近两年新架构：省着看/挑着看/压缩着看——注意力替代与 MoE

> **适用章节**：《新六艺》· 数_六「神经网络与Transformer」·「这两年：对一张账单的五种回答」（全章重心之一）。注意力对序列长度的二次账单 O(n²) 是近两年结构创新的共同起点。本文件支撑：「省着看」（GQA/MLA/LoRA）、「挑着看」（滑窗/attention sink/NSA）、「压缩着看」（线性注意力/SSM/Mamba）、「同一件事的两种写法」（Mamba-2 对偶）、「无损与有损的两难」（混合架构）、「稀疏激活：MoE」。
> **核查日期**：2026-07-16。核查方式：WebSearch 定位 → WebFetch 抓取 arXiv abstract/ar5iv 全文/官方技术报告逐句核对；作者名与关键数字（KV 减 93.3%、671B/37B、10000×）逐一核实并纠正若干易错引用。
> **政治边界（§6）核查**：本主题为机器学习架构，不涉军政，无需背景参照标注。厂商自报数字（DeepSeek MLA/V3、AI21 Jamba）标「利益相关」，与自家基线对比，从严看待。

## 目录

1. 省着看（一）：MQA（Shazeer 2019）与 GQA（Ainslie et al. 2023）
2. 省着看（二）：MLA——DeepSeek-V2 低秩 KV 联合压缩（利益相关）
3. 挑着看（一）：attention sink / StreamingLLM（Xiao et al. 2023）
4. 挑着看（二）：NSA——原生可训练稀疏注意力（DeepSeek 2025，利益相关）
5. 压缩着看：线性注意力（Katharopoulos 2020）、Mamba（Gu-Dao 2023）、Mamba-2/SSD（Dao-Gu 2024）
6. DeltaNet、RWKV-7 与「线性注意力＝测试时回归」统一视角
7. 无损与有损的两难：混合架构 Jamba（AI21 2024，利益相关）
8. 稀疏激活 MoE：Shazeer 2017、Switch（Fedus 2021）、DeepSeek-V3（2024，利益相关）
9. 省着看（三）：LoRA 低秩适配（Hu et al. 2021）

---

## 一、MQA 与 GQA

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | MQA（Shazeer 2019）单写头共享 KV；GQA（Ainslie 2023）分组共享 KV，MHA 与 MQA 之间插值 | A1 | arXiv/EMNLP 全文逐字核实；均为现行主流做法（Llama-2/3 用 GQA），无失效条件。

**知识内容：**

- **动机**：KV cache 是解码期的内存/带宽大头（见 `Transformer结构的数学` §十）。省 KV 的第一招是**共享 KV 头**。
- **MQA（Multi-Query Attention，Shazeer 2019）**：所有 query 头**共享同一组 key/value**，只保留一个 KV 头，大幅加速解码；代价是可能有质量损失。
- **GQA（Grouped-Query Attention，Ainslie et al. 2023）**：MHA 与 MQA 之间的**插值**——用「多于 1、少于 query 头数」的中间数量 KV 头，把 query 头分成 G 组，每组共享一个 key 头和 value 头（G=1 即 MQA，G=n_heads 即 MHA）。还给出「用 5% 原预训练算力把已有 MHA checkpoint 升级为 MQA/GQA」的配方。

**来源列表与原文摘引：**

- Shazeer, N. (2019). "Fast Transformer Decoding: One Write-Head is All You Need." arXiv:1911.02150.
  - 摘要（原文）："the keys and values are shared across all of the different attention 'heads'."
  - §3（原文）："Multi-query attention is identical except that the different heads share a single set of keys and values."
- Ainslie, J., Lee-Thorp, J., de Jong, M., Zemlyanskiy, Y., Lebrón, F. & Sanghai, S. (2023). "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints." EMNLP 2023. arXiv:2305.13245.
  - 摘要（原文）："We propose grouped-query attention (GQA), a generalization of multi-query attention which uses an intermediate (more than one, less than number of query heads) number of key-value heads."
  - 正文（原文）："Grouped-query attention divides query heads into G groups, each of which shares a single key head and value head."

---

## 二、MLA：DeepSeek-V2 低秩 KV 联合压缩（利益相关）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | MLA（DeepSeek-V2, 2405.04434）低秩 KV 联合压缩机制与 KV 减 93.3% 口径 | A2（利益相关） | arXiv 技术报告核实；93.3%/5.76×/42.5% 均为 DeepSeek 自报、以自家 DeepSeek 67B 为基线，从严看待。

**知识内容（本章「SVD/低秩一线在此兑现」）：**

- **MLA（Multi-head Latent Attention）机制**：把 key 和 value **联合做低秩压缩**成一个低维**潜向量** c_t^{KV}，推理时**只缓存这个潜向量**（外加一个解耦的 RoPE key），再在用时展开——用「压进低秩潜空间再展开」替代缓存完整的逐头 K/V。这正是 SVD/低秩思想在架构上的兑现。
- **压缩数字（DeepSeek 自报，利益相关）**：相较 DeepSeek 67B，DeepSeek-V2 通过 MLA **把 KV cache 减少 93.3%**、**把最大生成吞吐提升到 5.76 倍**、并**节省 42.5% 训练成本**。DeepSeek-V2 共 236B 总参、每 token 激活 21B，支持 128K 上下文。
- 口径提示：以上数字均为厂商自报、与自家基线对比，进正文须注明「DeepSeek 官方口径、自家基线」。

**来源列表与原文摘引：**

- DeepSeek-AI (2024). "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model." arXiv:2405.04434.
  - 摘要（原文）：MLA "guarantees efficient inference through significantly compressing the Key-Value (KV) cache into a latent vector"；相较 DeepSeek 67B，DeepSeek-V2 "reduces the KV cache by 93.3%", "saves 42.5% of training costs", and "boosts the maximum generation throughput to 5.76 times."

---

## 三、attention sink / StreamingLLM（Xiao et al. 2023）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | attention sink / StreamingLLM（Xiao 2023）滑窗失效、保留初始 sink token | A1 | ICLR 2024 全文逐字核实；现象与方法均已被广泛复现，无失效条件。

**知识内容（本章「挑着看：稀疏注意力」）：**

- **现象（attention sink）**：模型会把**异常大量的注意力分数分配给序列最初的几个 token，无论它们与当前任务是否相关**——这些初始 token 充当「注意力汇（sink）」，即使语义上不重要也持续吸走注意力。
- **后果与解法**：纯滑窗注意力（只缓存最近的 KV）在文本长度超过缓存大小时会失效；但**保留初始 sink token 的 KV（约 4 个即可）＋一个滑动窗口**，就能大幅恢复性能，让有限注意力窗口训练的 LLM **无需微调**处理近乎无限长的文本。这解释了滑窗为何要配 sink，是「挑着看」策略的关键一环。

**来源列表与原文摘引：**

- Xiao, G., Tian, Y., Chen, B., Han, S. & Lewis, M. (2023). "Efficient Streaming Language Models with Attention Sinks." ICLR 2024. arXiv:2309.17453.
  - 观察（原文）："a surprisingly large amount of attention score is allocated to the initial tokens, irrespective of their relevance to the language modeling task."
  - 解法（摘要，原文）："keeping the KV of initial tokens will largely recover the performance of window attention"；方法使 "LLMs trained with a finite attention window to work on text of infinite length without fine-tuning."

---

## 四、NSA：原生可训练稀疏注意力（DeepSeek 2025，利益相关）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | NSA（DeepSeek, Native Sparse Attention, 2502.11089）三分支（压缩/选择/滑窗）端到端可训练 | A1（利益相关） | arXiv 全文核实，ACL 2025 最佳论文；提速数字为 DeepSeek 自报，从严看待。

**知识内容（本章「稀疏模式本身变成可学习的对象」）：**

- **NSA（Native Sparse Attention）** 的关键是**稀疏模式端到端可训练（natively trainable）**，而非只在推理时施加稀疏——它把算法创新与硬件对齐优化结合，减少预训练计算而不牺牲性能。
- **三分支结构**：
  1. **token 压缩（compression）**：把 token 压成粗粒度的压缩 token；
  2. **token 选择（selection）**：选出细粒度的重要 token；
  3. **滑动窗口（sliding window）**：专门处理局部上下文，让压缩与选择两支不被局部模式「抄近路」，各自专注学习自己的特征。
- 荣誉：获 **ACL 2025 最佳论文奖**（多源核实）。提速数字（如 64k 上下文解码约 11.6× 等）为 DeepSeek 自报，利益相关。

**来源列表与原文摘引：**

- Yuan, J., Gao, H., Dai, D., Luo, J., Zhao, L., Zhang, Z., Xie, Z., Wei, Y. X., Wang, L., Xiao, Z., Wang, Y., Ruan, C., Zhang, M., Liang, W. & Zeng, W. (2025). "Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention." arXiv:2502.11089（ACL 2025，aclanthology.org/2025.acl-long.1126）。
  - 可训练（原文）："We present NSA, a Natively trainable Sparse Attention mechanism that integrates algorithmic innovations with hardware-aligned optimizations… We enable end-to-end training, reducing pretraining computation without sacrificing model performance."
  - 摘要点名两支 "coarse-grained token compression with fine-grained token selection"；第三支滑窗（正文，原文）："we introduce a dedicated sliding window branch that explicitly handles local context, allowing other branches (compression and selection) to focus on learning their respective features without being shortcutted by local patterns."

---

## 五、压缩着看：线性注意力、Mamba、Mamba-2/SSD

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | 线性注意力（Katharopoulos 2020）；Mamba 选择性 SSM（Gu-Dao 2023）；Mamba-2/SSD 状态空间对偶（Dao-Gu 2024） | A1 | arXiv/ICML 全文逐字核实；均为现行活跃架构方向，无失效条件。

**知识内容（本章「把全部历史压成固定大小的状态：RNN 的复活」与「同一件事的两种写法」）：**

- **线性注意力（Katharopoulos et al. 2020）**：用**核特征映射**替换 softmax，借矩阵乘法结合律把复杂度从 O(N²) 降到 **O(N)**；这一形式允许迭代实现，**揭示了 Transformer 与 RNN 的关系**（"Transformers are RNNs"）。
- **Mamba（Gu & Dao 2023）——选择性 SSM**：让状态空间模型（SSM）的参数**依赖输入（选择性）**，从而能沿序列维**有选择地传播或遗忘信息**；配硬件感知的并行扫描（parallel scan）算法，线性扩展。这就是「状态方程＋输入依赖的选择性门」。
- **Mamba-2 / SSD（Dao & Gu 2024）——状态空间对偶**：证明 SSM 与（一类）注意力**其实是紧密相关的同一对象**，通过一类被充分研究的**结构化半可分矩阵（structured semiseparable matrices）**的不同分解相连——这就是**状态空间对偶（Structured State Space Duality, SSD）**框架，也据此设计出 Mamba-2。这正是本章「线性注意力与状态空间模型是同一个数学对象的两种展开」「原来是同一件事」美学线第三处的正式内核。

**来源列表与原文摘引：**

- Katharopoulos, A., Vyas, A., Pappas, N. & Fleuret, F. (2020). "Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention." ICML 2020. arXiv:2006.16236.
  - 原文："we express the self-attention as a linear dot-product of kernel feature maps and make use of the associativity property of matrix products to reduce the complexity from O(N²) to O(N)… this formulation permits an iterative implementation that dramatically accelerates autoregressive transformers and reveals their relationship to recurrent neural networks."
- Gu, A. & Dao, T. (2023). "Mamba: Linear-Time Sequence Modeling with Selective State Spaces." arXiv:2312.00752.
  - 原文："simply letting the SSM parameters be functions of the input addresses their weakness with discrete modalities, allowing the model to selectively propagate or forget information along the sequence length dimension depending on the current token… we design a hardware-aware parallel algorithm in recurrent mode."
- Dao, T. & Gu, A. (2024). "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality." ICML 2024. arXiv:2405.21060.
  - 原文："We show that these families of models are actually quite closely related, and develop a rich framework of theoretical connections between SSMs and variants of attention, connected through various decompositions of a well-studied class of structured semiseparable matrices. Our state space duality (SSD) framework allows us to design a new architecture (Mamba-2)…"

---

## 六、DeltaNet、RWKV-7 与「线性注意力＝测试时回归」统一视角

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | DeltaNet（Yang et al. 2024 delta 规则并行化）；RWKV-7（2025）；线性注意力＝测试时回归/在线学习统一视角 | A2 | arXiv/NeurIPS 核实；DeltaNet 与 test-time regression 作者名已纠正（见口径注）。此方向 2024–2025 活跃，后续综述可能更新表述。

**知识内容（本章「状态更新规则本身是一步在线梯度下降——模型在推理时内部也在学习」，数_七预告）：**

- **DeltaNet（Yang et al. 2024）**：用 **delta 规则**（一种误差修正的状态更新）改进线性 Transformer；关键贡献是给出**沿序列长度并行化** delta 规则的硬件高效算法（利用 Householder 矩阵乘积的省内存表示），解决了此前这类模型不能沿序列并行、训练低效的问题。
- **RWKV-7「Goose」（2025）**：引入**广义化的 delta 规则**，带**向量值门控**与**在上下文中的学习率（in-context learning rates）**；可做状态跟踪、识别所有正则语言，在标准复杂度猜想下超出 Transformer（其被限制在 TC⁰）的能力，同时保持并行性。
- **统一视角（线性注意力＝测试时回归/在线学习）**：把关联记忆的读取看作「**先记忆、再检索**」两步，其中**记忆被表述为一个回归问题**；线性注意力、状态空间模型、快权重编程器（fast-weight programmers）、在线学习器、乃至 softmax 注意力，都作为**特例**，由三个设计选择（回归权重、回归器函数类、测试时优化算法）区分。即：这些序列模型的状态更新，本质是在**测试时**解一个回归/做一步在线学习——「模型在推理时内部也在学习」。

**来源列表与原文摘引：**

- Yang, S., Wang, B., Zhang, Y., Shen, Y. & Kim, Y. (2024). "Parallelizing Linear Transformers with the Delta Rule over Sequence Length." NeurIPS 2024. arXiv:2406.06484.
  - 原文："existing algorithms for training such models do not parallelize over sequence length and are thus inefficient to train on modern hardware... This work describes a hardware-efficient algorithm for training linear transformers with the delta rule, which exploits a memory-efficient representation for computing products of Householder matrices."
  - 口径注（纠正易错引用）：作者共 5 人 Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, Yoon Kim——无「Panda」，勿误列。
- Peng, B., Zhang, R., Goldstein, D., Alcaide, E. 等 (2025). "RWKV-7 'Goose' with Expressive Dynamic State Evolution." arXiv:2503.14456.
  - 原文："RWKV-7 introduces a newly generalized formulation of the delta rule with vector-valued gating and in-context learning rates"；"RWKV-7 can perform state tracking and recognize all regular languages, while retaining parallelizability… This exceeds the capabilities of Transformers under standard complexity conjectures, which are limited to TC⁰."
- Wang, K. A., Shi, J. & Fox, E. B. (2025). "Test-time regression: a unifying framework for designing sequence models with associative memory." arXiv:2501.12352.
  - 口径注（纠正易错引用）：作者为 Ke Alexander Wang, Jiaxin Shi, Emily B. Fox——Songlin Yang **不是**本文作者，勿误列。统一视角：关联记忆＝记忆（回归）+检索两步，线性注意力/SSM/fast-weight/在线学习/softmax 注意力均为特例。

---

## 七、无损与有损的两难：混合架构 Jamba（AI21 2024，利益相关）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | 混合架构 Jamba（AI21 2024）注意力层与 Mamba(SSM) 层混搭 + MoE | A3（利益相关） | arXiv 核实标题与混合口径；具体 1:7 层比来自论文配置（非摘要逐字），厂商自报，从严看待。

**知识内容（本章「混合架构（层间混搭）是当前的工程答案」）：**

- **两难**：全量注意力＝精确检索但二次账单（无损但贵）；固定状态（SSM/线性注意力）＝线性但对历史有损压缩。信息论权衡没有免费午餐。
- **Jamba（AI21 Labs 2024）** 是当前工程折中的代表：**交替堆叠 Transformer（注意力）块与 Mamba（SSM）块**，兼取两族之长，并在部分层加入 **MoE** 以在控制激活参数的同时扩容量。具体配置为每 8 层一个块、注意力:Mamba = 1:7、每隔一层加 MoE（此比例来自论文正文配置，非摘要逐字）。

**来源列表与原文摘引：**

- Lieber, O., Lenz, B. 等（AI21 Labs）(2024). "Jamba: A Hybrid Transformer-Mamba Language Model." arXiv:2403.19887.
  - 摘要（原文）："Jamba interleaves blocks of Transformer and Mamba layers, enjoying the benefits of both model families. MoE is added in some of these layers to increase model capacity while keeping active parameter usage manageable."
  - 口径注：1:7 层比与「每 8 层一块、每隔一层 MoE」为论文配置，未在摘要逐字出现；引用具体比例时归于论文正文/配置。

---

## 八、稀疏激活 MoE：Shazeer 2017、Switch 2021、DeepSeek-V3 2024

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | MoE 稀疏门控（Shazeer 2017）；Switch Transformer（Fedus 2021）top-1；DeepSeek-V3 无辅助损失负载均衡、671B/37B | A1（DeepSeek-V3 利益相关） | arXiv/JMLR 全文核实；671B 总参/37B 激活、bias 项负载均衡逐字核实。DeepSeek 数字为自报。

**知识内容（本章「稀疏激活：MoE」「参数量与计算量解耦」）：**

- **稀疏门控 MoE（Shazeer et al. 2017）**：一个 MoE 层含成千上万个前馈子网络（专家）；一个可训练的**门控网络**为每个样本选出**稀疏**的专家组合来用——这就是「条件计算」的原型，把参数量与每样本计算量**解耦**。
- **Switch Transformer（Fedus et al. 2021）**：把路由简化到极致——**每个 token 只路由给单个专家（top-1）**，以简单高效的稀疏性把模型扩到万亿参数。
- **DeepSeek-V3（2024）——无辅助损失负载均衡**：**671B 总参数、每 token 激活 37B**（数字逐字核实）。其负载均衡不靠传统的辅助损失，而是**给每个专家一个偏置项 b_i**加到亲和度分数上决定 top-K 路由，并在专家过载时调低、欠载时调高该偏置——即「**无辅助损失**」策略，避免辅助损失损害主任务、又防路由塌缩。「万亿参数、百亿激活」这句营销话术背后就是这笔数学账（总参 ≫ 激活参）。

**来源列表与原文摘引：**

- Shazeer, N., Mirhoseini, A., Maziarz, K., Davis, A., Le, Q., Hinton, G. & Dean, J. (2017). "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer." ICLR 2017. arXiv:1701.06538.
  - 原文："a Sparsely-Gated Mixture-of-Experts layer (MoE), consisting of up to thousands of feed-forward sub-networks. A trainable gating network determines a sparse combination of these experts to use for each example."
- Fedus, W., Zoph, B. & Shazeer, N. (2021). "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity." JMLR (2022). arXiv:2101.03961.
  - 原文（§2.1）："we instead use a simplified strategy where we route to only a single expert."
- DeepSeek-AI (2024). "DeepSeek-V3 Technical Report." arXiv:2412.19437.
  - 原文："a strong Mixture-of-Experts (MoE) language model with 671B total parameters with 37B activated for each token."
  - 无辅助损失负载均衡（原文）："we introduce a bias term b_i for each expert and add it to the corresponding affinity scores s_{i,t} to determine the top-K routing"；"we will decrease the bias term by γ if its corresponding expert is overloaded, and increase it by γ if its corresponding expert is underloaded."
  - 口径提示：671B/37B 等为 DeepSeek 自报，利益相关。

---

## 九、LoRA 低秩适配（Hu et al. 2021）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | LoRA（Hu et al. 2021）低秩适配、冻结预训练权重注入低秩矩阵、10000× 减少可训练参数 | A1 | arXiv/ICLR 全文逐字核实；为现行主流微调法，无失效条件。

**知识内容（本章「LoRA 微调同款低秩思想顺带三行讲完」）：**

- **LoRA（Low-Rank Adaptation）**：**冻结预训练权重**，在每层注入**可训练的低秩分解矩阵** ΔW = BA（秩 r ≪ d），只训练这两个小矩阵。与用 Adam 全参微调 GPT-3 175B 相比，LoRA 把**可训练参数量减少 10000 倍、GPU 显存需求减少 3 倍**。这与 MLA 的低秩 KV 压缩同属「低秩/SVD」一线思想。

**来源列表与原文摘引：**

- Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L. & Chen, W. (2021). "LoRA: Low-Rank Adaptation of Large Language Models." ICLR 2022. arXiv:2106.09685.
  - 摘要（原文）："We propose Low-Rank Adaptation, or LoRA, which freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks. Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times."
