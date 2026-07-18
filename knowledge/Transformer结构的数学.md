# Transformer 结构的数学：词的几何、注意力、归一化、残差与账单

> **适用章节**：《新六艺》· 数_六「神经网络与Transformer」。支撑该章「词的几何」（把词放进空间、高维近正交、方向即语义、BPE 分词）、「注意力：查一张软字典」（除以√d 的方差账、softmax 的正式身份、多头、因果掩码、RoPE 位置编码）、「Transformer 全身」（残差流＝ODE 一步、LayerNorm/RMSNorm/pre-norm、FFN 键值存储、一次前向的账单 FLOPs≈2ND 与 KV cache）。
> **核查日期**：2026-07-16。核查方式：WebSearch 定位 → WebFetch 抓取 arXiv abstract/ar5iv 全文/ACL Anthology/教材 PDF 逐句核对；JL 引理与近正交定理直接从 Blum-Hopcroft-Kannan 教材 PDF 抽取；Vaswani 脚注 4 从 ar5iv 全文核到。
> **政治边界（§6）核查**：本主题为数学与机器学习结构，不涉军政，无需背景参照标注。DeepSeek 等厂商自报数字标「利益相关」。

## 目录

1. 词向量线性类比：Mikolov 2013 及其边界（Linzen 2016）
2. Johnson–Lindenstrauss 引理与高维近正交
3. BPE 分词：Sennrich et al. 2016（源自 Gage 1994 压缩）
4. 缩放点积注意力与多头：Vaswani et al. 2017（除以√d_k 的方差账）
5. softmax 的正式身份：玻尔兹曼分布/最大熵与温度
6. RoPE 旋转位置编码与 YaRN/NTK 外推
7. 归一化：LayerNorm、RMSNorm、pre-norm vs post-norm
8. FFN 作为键值存储：Geva et al. 2021
9. 残差网络与 ODE 离散化视角：He 2015、Neural ODE 2018、E 2017
10. 一次前向的账单：FLOPs≈2N（Kaplan 2020）、KV cache 与内存带宽瓶颈（Pope 2022）
11. 一个 7B Llama 类模型的参数账（可复算）

---

## 一、词向量线性类比：Mikolov 2013 及其边界

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | word2vec 线性类比 king-man+woman≈queen（Mikolov 2013）及争议边界（Linzen 2016 offset 方法批评） | A1 | arXiv/ACL Anthology 全文逐字核实；现象与批评均为已发表结论，无失效条件。

**知识内容：**

- **现象**：词向量上做简单向量算术，能反映语义关系。最著名的例子：**vector("King") − vector("Man") + vector("Woman") 得到的向量最接近 vector("Queen")**。offset（偏移）方法：回答类比 a:b :: c:? ，计算 y = x_b − x_a + x_c，再在向量空间里找与 y 余弦相似度最高的词。
- **边界与争议（正文必须注明）**：该现象被后续工作证明**比宣传的弱**。Linzen 2016 指出，offset 方法依赖余弦相似度，把「偏移一致性」与「无关的邻域结构」混为一谈；关键实证：**若不排除输入词，a*−a+b 的最近邻在 93% 情况下就是 b 本身、5% 是 a***——也就是说很多「成功」其实来自「目标词本就离源词最近」，而非语义空间的几何组织。诚实基线（如 ONLY-B，完全忽略偏移只取 b 的最近邻）在复数类比上就能达到约 0.70 的准确率。
- 结论口径：向量算术的类比现象**真实但脆弱**，标准评测通行做法（排除输入词、余弦相似度）会系统性高估它。本章讲「方向即语义」时，应把它作为「有信号但需警惕评测假象」的例子，语义更准确的图景是「语义在流形上」而非「处处线性」。

**来源列表与原文摘引：**

- Mikolov, T., Yih, W.-T. & Zweig, G. (2013). "Linguistic Regularities in Continuous Space Word Representations." NAACL-HLT 2013, 746–751. ACL Anthology N13-1090.（King−Man+Woman 这句话的原始出处。）
  - 摘要（原文）："the male/female relationship is automatically learned, and with the induced vector representations, 'King - Man + Woman' results in a vector very close to 'Queen.'"
  - offset 方法（§5，原文）："to answer the analogy question a:b c:d where d is unknown, we find the embedding vectors xa, xb, xc (all normalized to unit norm), and compute y = xb − xa + xc."
- Mikolov, T., Chen, K., Corrado, G. & Dean, J. (2013). "Efficient Estimation of Word Representations in Vector Space." arXiv:1301.3781（ICLR 2013 workshop）。
  - 原文（p.2）："Using a word offset technique … vector('King') - vector('Man') + vector('Woman') results in a vector that is closest to the vector representation of the word Queen."
- Linzen, T. (2016). "Issues in evaluating semantic spaces using word analogies." RepEval 2016, 13–18. ACL Anthology W16-2503（arXiv:1606.07736）。
  - 摘要（原文）："We show that the method's reliance on cosine similarity conflates offset consistency with largely irrelevant neighborhood structure, and propose simple baselines that should be used to improve the utility of the method…"
  - §4（原文）："When these words were not excluded, the nearest neighbor of a∗ − a + b was b in 93% of the cases and a∗ in 5% of the cases (it was never a)."

---

## 二、Johnson–Lindenstrauss 引理与高维近正交

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | JL 引理；高维随机向量近正交标准结论（Foundations of Data Science 教材） | A1 | 直接从 Blum-Hopcroft-Kannan 教材 PDF（第 2 章）抽取定理原文；数学定理无失效条件。

**知识内容：**

- **近正交（本章「高维的怪礼物」的正式内核）**：从单位球里随机取两个向量，高概率下它们**几乎正交**——夹角约为 π/2 ± O(1/√d)，归一化点积集中在 ±O(1/√d)。教材 Theorem 2.8：随机取 n 个点，以 1−O(1/n) 的概率，每个点近似单位长、每一对点近似正交（|xᵢ·xⱼ| ≤ √(6 ln n)/√(d−1)）。因为界里对 n 的容忍是 √(ln n)，n 可取到关于维度 d 指数级——这就是「d 维空间能塞下远超 d 个几乎正交方向」的机制。
- **Johnson–Lindenstrauss 引理**：n 个点可被随机投影到 k = O(ln n / ε²) 维，**成对距离在 (1±ε) 内保持**。它与近正交同源，底层都靠高斯环定理（Gaussian Annulus Theorem，Theorem 2.9：d 维单位方差球高斯的概率质量集中在半径 √d 的薄环上）。
- 直觉意义：高维直觉「崩坏」在这里反而帮了大忙——embedding 维度 d 有限，却能容纳数量级远超 d 的「几乎互不干扰」的语义方向。

**来源列表与原文摘引：**

- Blum, A., Hopcroft, J. & Kannan, R. (2020). *Foundations of Data Science*. Cambridge University Press. 第 2 章「High-Dimensional Space」。
  - Theorem 2.11（Johnson-Lindenstrauss Lemma，原文）："For any 0 < ε < 1 and any integer n, let k ≥ (3/cε²) ln n with c as in Theorem 2.9. For any set of n points in R^d, the random projection f : R^d → R^k defined above has the property that for all pairs of points v_i and v_j, with probability at least 1 − 3/2n, (1−ε)√k|v_i − v_j| ≤ |f(v_i) − f(v_j)| ≤ (1+ε)√k|v_i − v_j|."
  - 近正交（§2.4，原文）："the angle between the two vectors will be π/2 ± O(1/√d). In particular … if we draw n points at random in the unit ball, with high probability all points will be close to unit length and each pair of points will be almost orthogonal."
  - Theorem 2.8（原文）："Consider drawing n points x1, x2, …, xn at random from the unit ball. With probability 1 − O(1/n): 1. |xi| ≥ 1 − (2 ln n)/d for all i, and 2. |xi · xj| ≤ √(6 ln n)/√(d−1) for all i≠j."
- 原始出处：Johnson, W. B. & Lindenstrauss, J. (1984). "Extensions of Lipschitz mappings into a Hilbert space." *Contemporary Mathematics*, 26, 189–206.

---

## 三、BPE 分词：Sennrich et al. 2016

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | BPE 子词分词 Sennrich 2016；源自 Gage 1994 压缩算法 | A1 | ACL Anthology 全文逐字核实；方法为通行标准，无失效条件。

**知识内容：**

- BPE（Byte Pair Encoding）本是 Gage 1994 的**数据压缩**算法：反复把序列中最频繁的一对字节替换成一个未用过的新字节。Sennrich et al. 2016 把它**改造为词切分**：不合并字节，而是**迭代地统计所有符号对、把最频繁的一对（'A','B'）合并成新符号 'AB'**，每次合并产生一个代表字符 n-gram 的新符号。
- 意义：BPE＝**频率驱动的压缩**，把开放词表问题（罕见/未登录词）转成子词序列的组合，用固定大小的词表覆盖任意词。这也是本章「预测＝压缩」伏笔的第一块（数_七）。

**来源列表与原文摘引：**

- Sennrich, R., Haddow, B. & Birch, A. (2016). "Neural Machine Translation of Rare Words with Subword Units." ACL 2016, 1715–1725. ACL Anthology P16-1162（arXiv:1508.07909）。
  - §3.2（原文）："Byte Pair Encoding (BPE) (Gage, 1994) is a simple data compression technique that iteratively replaces the most frequent pair of bytes in a sequence with a single, unused byte. We adapt this algorithm for word segmentation. Instead of merging frequent pairs of bytes, we merge characters or character sequences."
  - （原文续）："We iteratively count all symbol pairs and replace each occurrence of the most frequent pair ('A', 'B') with a new symbol 'AB'. Each merge operation produces a new symbol which represents a character n-gram."
  - 原始压缩算法：Gage, P. (1994). "A New Algorithm for Data Compression." *C Users Journal*, 12(2), 23–38.

---

## 四、缩放点积注意力与多头：Vaswani et al. 2017

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | Attention Is All You Need：scaled dot-product 除以√d_k 原文脚注理由（点积方差为 d_k）；多头定义 | A1 | ar5iv 全文核到脚注原文与两式；NeurIPS 2017 已发表，无失效条件。

**知识内容：**

- **缩放点积注意力**：Attention(Q,K,V) = softmax(QKᵀ/√d_k)·V。除以 √d_k 是「一笔方差账」：**假设 q、k 的各分量是独立、零均值、单位方差的随机变量，则点积 q·k = Σᵢ qᵢkᵢ 的均值为 0、方差为 d_k**。维度 d_k 越大，点积的量级越大，softmax 会被推到饱和区、梯度消失；除以 √d_k 把方差拉回 O(1)，抵消这个效应。这正是本章「除以根号 d」样板小节的正式推导。
- **多头注意力**：把 Q、K、V 投影到 h 个低维子空间分别注意再拼接。原论文用 h=8 个头，每个头 d_k=d_v=d_model/h=64。

**来源列表与原文摘引：**

- Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł. & Polosukhin, I. (2017). "Attention Is All You Need." NeurIPS 2017. arXiv:1706.03762.
  - 脚注（√d_k 理由，原文）："To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, q·k = Σ_{i=1}^{d_k} qᵢkᵢ, has mean 0 and variance d_k."
  - 缩放（原文）："Attention(Q,K,V) = softmax(QKᵀ/√d_k)V"；"To counteract this effect, we scale the dot products by 1/√d_k."
  - 多头（原文）："MultiHead(Q,K,V) = Concat(head₁,…,head_h)Wᴼ where headᵢ = Attention(QWᵢᵠ, KWᵢᴷ, VWᵢⱽ)"；"In this work we employ h=8 parallel attention layers, or heads. For each of these we use d_k = d_v = d_model/h = 64."

---

## 五、softmax 的正式身份：玻尔兹曼分布/最大熵与温度

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | softmax = 玻尔兹曼/吉布斯分布；最大熵分布；温度参数标准表述 | B2 | 权威百科 + 同行评审教程逐字核实；点名的 Goodfellow/Bishop 教材页本次未能在线逐字抓取，故用可核验替代源，内容数字定 2。

**知识内容：**

- **玻尔兹曼/吉布斯身份**：softmax 就是统计力学里的玻尔兹曼分布：p_i = exp(z_i/T) / Σⱼ exp(z_j/T)，其中 T 为温度（T = 1/β）。
- **最大熵身份**：在「固定期望得分」这一约束下，softmax 是**最大熵分布**——即在给定期望值约束下最「不偏不倚」的分布。
- **温度**：T 控制分布的尖锐度。T→0（β→∞）时 softmax 收敛到 argmax（一个值独占）；T→∞（α→0）时趋于均匀分布（熵最大、最「随机」）。你每天调的 temperature 参数有精确的物理学出身。

**来源列表与原文摘引：**

- Wikipedia, "Softmax function"（en.wikipedia.org/wiki/Softmax_function）。
  - （原文）："In statistical mechanics, the softargmax function is known as the Boltzmann distribution (or Gibbs distribution)"；"a lower temperature results in a sharper output distribution, with one value dominating"；"as β → ∞, softargmax converges to arg max."
- Franke, M. & Degen, J. "The softmax function: Properties, motivation, and interpretation."（同行评审教程，alpslab.stanford.edu/papers/FrankeDegen_submitted.pdf）。
  - 最大熵（原文）："it is provable that, in general, softmax yields the maximum entropy distribution for a given value of the expected score."
  - 定义与温度（原文）："pᵢ = exp(α sᵢ) / Σⱼ exp(α sⱼ)"，"Some authors use the inverse of α, frequently denoted as τ, and refer to it as 'temperature.'"
- ⚠ 待核（可选升级）：正文若要引 Goodfellow-Bengio-Courville《Deep Learning》(2016) softmax 一节的原话，需线下购书/取全文逐字核对（本次在线抓取被截断）。当前两源已充分支撑三条子命题。

---

## 六、RoPE 旋转位置编码与 YaRN/NTK 外推

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | RoPE（RoFormer, 2104.09864）位置编码为旋转、相对位置出现在内积；YaRN 与 NTK-aware 外推 | B1 | arXiv/期刊全文核实；RoPE 已成主流 LLM 标配（LLaMA 系）。NTK-aware 属论文正文与社区概念，见下注。

**知识内容：**

- **RoPE 机制（本章「欧拉公式第二次出鞘」）**：把绝对位置编码成一个**旋转矩阵**作用在 query/key 上，使**相对位置自动出现在内积里**。设计要求：query q_m 与 key k_n 的内积只能通过词向量与相对位置 m−n 表达，即 ⟨f_q(x_m,m), f_k(x_n,n)⟩ = g(x_m,x_n,m−n)。RoPE 满足 q_mᵀk_n = x_mᵀ W_q R^d_{Θ,n−m} W_k x_n——内积只依赖相对偏移 n−m（通过旋转矩阵）。
- **外推（一笔带过即可）**：用 RoPE 训练的模型无法直接泛化到超过训练长度的序列。**YaRN**（Peng et al. 2023）是计算高效的上下文窗口扩展法，比先前方法少约 10 倍 token、2.5 倍训练步。YaRN 在正文中结合了 **NTK-aware 插值**与注意力温度缩放（"NTK-by-parts"）；NTK-aware 插值最早出自社区博客（作者 bloc97），论文引用之。

**来源列表与原文摘引：**

- Su, J., Lu, Y., Pan, S., Murtadha, A., Wen, B. & Liu, Y. (2021). "RoFormer: Enhanced Transformer with Rotary Position Embedding." arXiv:2104.09864（后见 *Neurocomputing* 568, 2024）。
  - 设计要求（原文）："we require the inner product of query q_m and key k_n to be formulated by a function g, which takes only the word embeddings x_m, x_n, and their relative position m − n as input variables"，即 "⟨f_q(x_m, m), f_k(x_n, n)⟩ = g(x_m, x_n, m − n)."
  - 关键性质（原文）："q_m^⊤ k_n = x_m^⊤ W_q R^d_{Θ,n−m} W_k x_n"（内积只通过旋转矩阵依赖相对偏移 n−m）。
- Peng, B., Quesnelle, J., Fan, H. & Shippole, E. (2023). "YaRN: Efficient Context Window Extension of Large Language Models." arXiv:2309.00071（ICLR 2024）。
  - 摘要（原文）："we present YaRN (Yet another RoPE extensioN method), a compute-efficient method to extend the context window of such models, requiring 10x less tokens and 2.5x less training steps than previous methods."
  - 口径注：「NTK-aware interpolation」在正文而非摘要，引用时归于论文正文。

---

## 七、归一化：LayerNorm、RMSNorm、pre-norm vs post-norm

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | LayerNorm（Ba 2016）、RMSNorm（Zhang-Sennrich 2019）、pre-norm vs post-norm（Xiong 2020） | B1（LayerNorm，纯 arXiv）/ A1（RMSNorm NeurIPS、Xiong ICML） | arXiv/会议全文逐字核实；均为现行主流做法，无失效条件。

**知识内容：**

- **LayerNorm（Ba et al. 2016）**：对单个训练样本、在一层内的全部加和输入上计算均值与方差来做归一化；每个神经元有自适应的 bias 与 gain；训练与测试时计算完全相同（不同于 batchnorm）。
- **RMSNorm（Zhang & Sennrich 2019）**：假设 LayerNorm 的**再中心化（减均值）可有可无**，**只按均方根（RMS）再缩放**，去掉均值统计。给模型再缩放不变性与隐式学习率自适应，且更省——不同模型上运行时间减少 7%~64%。LLaMA 等现代模型采用 RMSNorm。
- **pre-norm vs post-norm（Xiong et al. 2020）**：原始 Post-LN（归一化放在残差块之间）在初始化时靠近输出层的参数期望梯度很大，需精心设计的学习率 warm-up 才稳；把归一化放进残差块内部（Pre-LN）时，初始化时梯度性质良好，**warm-up 阶段可安全去除**，训练更快更稳。这就是本章「pre-norm 为什么训练稳（梯度有恒等通路）」的支撑。

**来源列表与原文摘引：**

- Ba, J. L., Kiros, J. R. & Hinton, G. E. (2016). "Layer Normalization." arXiv:1607.06450.
  - 摘要（原文）："we compute the mean and variance used for normalization from all of the summed inputs to the neurons in a layer on a single training case. … Unlike batch normalization, layer normalization performs exactly the same computation at training and test times."
- Zhang, B. & Sennrich, R. (2019). "Root Mean Square Layer Normalization." NeurIPS 2019. arXiv:1910.07467.
  - 摘要（原文）："RMSNorm regularizes the summed inputs to a neuron in one layer according to root mean square (RMS), giving the model re-scaling invariance property and implicit learning rate adaptation ability."；"reduces the running time by 7%~64% on different models."
- Xiong, R. et al. (2020). "On Layer Normalization in the Transformer Architecture." ICML 2020. arXiv:2002.04745.
  - 摘要（原文）："for the original-designed Post-LN Transformer, which places the layer normalization between the residual blocks, the expected gradients of the parameters near the output layer are large … using a large learning rate on those gradients makes the training unstable. … if the layer normalization is put inside the residual blocks (recently proposed as Pre-LN Transformer), the gradients are well-behaved at initialization. This motivates us to remove the warm-up stage."

---

## 八、FFN 作为键值存储：Geva et al. 2021

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | Transformer FFN 层是键值存储 Geva et al. 2021 | A1 | EMNLP 2021 全文核实；结论无失效条件。

**知识内容：**

- **FFN（前馈层）＝键值记忆**：Transformer 的前馈层约占模型三分之二的参数（本章「三分之二的参数在做键值存储」标题即由此而来）。Geva et al. 证明前馈层作为**键值存储**运作：**每个 key 与训练样本中的文本模式相关，每个 value 在输出词表上诱导一个分布**。低层的 key 捕捉表层语言模式，高层捕捉更抽象的语义关联；最终输出经残差连接对这些记忆的组合逐层精炼而成。

**来源列表与原文摘引：**

- Geva, M., Schuster, R., Berant, J. & Levy, O. (2021). "Transformer Feed-Forward Layers Are Key-Value Memories." EMNLP 2021. arXiv:2012.14913.
  - 摘要（原文）："Feed-forward layers constitute two-thirds of a transformer model's parameters, yet their role in the network remains under-explored. We show that feed-forward layers in transformer-based language models operate as key-value memories, where each key correlates with textual patterns in the training examples, and each value induces a distribution over the output vocabulary."

---

## 九、残差网络与 ODE 离散化视角

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | 残差网络 He 2015；残差连接＝ODE 欧拉离散化（Neural ODE, Chen 2018；E 2017 动力系统视角） | A1（He CVPR、Chen NeurIPS）/ A2（E 2017） | arXiv/会议全文逐字核实；E 2017 venue 经 Springer 核实，未取付费墙逐字引文。

**知识内容：**

- **残差网络（He et al. 2015）**：把层显式地重构为「学习相对于输入的残差函数」，而非无参照的映射；用 shortcut/恒等连接实现 y = F(x) + x。这让极深网络（152 层）也能训练。
- **残差＝ODE 一步（本章「残差流＝欧拉法的一步」的正式内核）**：Neural ODE 指出，残差网络的更新 h_{t+1} = h_t + f(h_t, θ_t) 可看作一个连续变换的**欧拉离散化**；当层数增多、步长变小，极限就是一个由神经网络指定的常微分方程 dh(t)/dt = f(h(t), t, θ)。即**深度网络是一个微分方程的离散化**——数_五欧拉法在此会师。
- **动力系统视角的源头**：把深度学习看作动力系统/最优控制的提法，源自 E Weinan 2017「A Proposal on Machine Learning via Dynamical Systems」。（Neural ODE 为欧拉离散化这一句所引的是 Lu et al. 2017、Haber & Ruthotto 2017 等。）

**来源列表与原文摘引：**

- He, K., Zhang, X., Ren, S. & Sun, J. (2015). "Deep Residual Learning for Image Recognition." arXiv:1512.03385（CVPR 2016）。
  - 摘要（原文）："We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions."
  - 正文 §3.1（原文）："y = F(x, {W_i}) + x"（shortcut 执行恒等映射；F(x)+x 形式在正文，不在摘要）。
- Chen, R. T. Q., Rubanova, Y., Bettencourt, J. & Duvenaud, D. (2018). "Neural Ordinary Differential Equations." NeurIPS 2018（best paper）。arXiv:1806.07366.
  - 引言（原文）："h_{t+1} = h_t + f(h_t, θ_t) … These iterative updates can be seen as an Euler discretization of a continuous transformation."
  - 极限（原文）："In the limit, we parameterize the continuous dynamics of hidden units using an ordinary differential equation (ODE) specified by a neural network: dh(t)/dt = f(h(t), t, θ)."
- E, Weinan (2017). "A Proposal on Machine Learning via Dynamical Systems." *Communications in Mathematics and Statistics*, 5(1), 1–11. DOI 10.1007/s40304-017-0103-z.（动力系统视角原始出处；venue 经核实，未取逐字引文。）

---

## 十、一次前向的账单：FLOPs≈2N 与 KV cache

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | 训练/推理算力账 FLOPs≈2ND（Kaplan 2020 每 token 前向 2N、前向+反向 6N）；KV cache 与推理受内存带宽限制（Pope 2022） | A1（Kaplan）/ A2（Pope，KV 闭式公式属通行式） | arXiv/ar5iv 全文核实；口径为现行通用，无失效条件。

**知识内容：**

- **FLOPs 账（Kaplan et al. 2020）**：每个 token 的**前向**计算量 ≈ **2N**（N 为非嵌入参数量），**前向+反向**（训练）≈ **6N**。因此训练总量 C ≈ 6ND（D 为训练 token 数）。近似式丢掉了一个与上下文长度有关的修正项 2·n_layer·n_ctx·d_model。
- **KV cache 与内存带宽瓶颈（Pope et al. 2022）**：自回归解码时，每层的 key/value 张量（KV cache）必须在整个解码期间存在内存里；解码的瓶颈是**内存带宽**——每生成一个 token，都要把参数与 KV cache 从高带宽内存（HBM）搬进计算核，而计算核基本处于空闲等待状态。这就是本章「推理贵在内存不在计算」的支撑，也是下一节全部新架构的共同动机。
- **KV cache 大小（通行公式）**：2 · n_layers · n_heads · d_head · seq_len · batch · bytes_per_param（因子 2 对应 K 和 V）。此闭式为社区/通行表述，与 Pope 描述一致，但非 Pope 原文逐字方程。

**来源列表与原文摘引：**

- Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., Gray, S., Radford, A., Wu, J. & Amodei, D. (2020). "Scaling Laws for Neural Language Models." arXiv:2001.08361.
  - 前向（原文，Eq. 2.2 附近）："C_forward ≈ 2N + 2·n_layer·n_ctx·d_model"（主导项 ≈ 2N/token）；训练总量 "C ≈ 6N floating point operators per training token"。N 明确定义为非嵌入参数。
- Pope, R., Douglas, S., Chowdhery, A., Devlin, J., Bradbury, J., Levskaya, A., Heek, J., Xiao, K., Agrawal, S. & Dean, J. (2022). "Efficiently Scaling Transformer Inference." arXiv:2211.05102（MLSys 2023）。
  - KV cache（原文）："The attention key and value tensors of each layer, which we refer to as the KV cache, must also be stored in memory for the duration of decoding."
  - 内存带宽瓶颈（原文）："the on-chip memory needs to load this KV cache from off-chip memory once for every token generated during which the computational core of the chip is essentially idle."
  - 规模示例（原文）："for batch size 512 and context length 2048, the KV cache totals 3TB, which is 3 times the size of the model's parameters."

---

## 十一、一个 7B Llama 类模型的参数账（可复算）

搜索时间 | 搜索内容 | 评级 | 时效
--- | --- | --- | ---
2026-07-16 | Llama 类 7B 参数分布（embedding/attention/FFN 占比），从架构超参数复算 | A1 | 超参数经 LLaMA 论文 Table 2 核实，账目可复算至官方 6.7B；FFN=11008、vocab=32000 取自官方发布 config（论文正文未列），见口径注。

**知识内容（本章练习轨「数一个 7B 模型的参数账」，读者可亲手复算）：**

- **超参数（LLaMA-7B，Touvron et al. 2023 论文 Table 2）**：d_model = 4096，n_layers = 32，n_heads = 32；FFN 用 SwiGLU，隐藏维 = 2/3·4d 向上取整到 256 倍数 = 11008（取自官方 config）；vocab = 32000；采用**非绑定**（untied）输入/输出嵌入。
- **逐项复算**：
  - 每层注意力（Q、K、V、O 四个 d×d 矩阵）= 4·4096² = **67,108,864 ≈ 67.1M**；×32 层 = **2.147B**。
  - 每层 FFN（SwiGLU 三个矩阵）= 3·4096·11008 = **135,266,304 ≈ 135.3M**；×32 层 = **4.329B**。
  - 嵌入 = 32000·4096 = **131.07M**（单表）；非绑定输入+输出 = **262.1M**。
  - RMSNorm 参数可忽略（每层 2×d + 末端，共约 0.27M）。
  - 合计（非绑定）= 2.147B + 4.329B + 0.262B ≈ **6.738B**——与官方 6.7B（6.738B）精确吻合。
- **占比（说出每一亿参数在哪）**：FFN ≈ **64.2%**、注意力 ≈ **31.9%**、嵌入 ≈ **3.9%**（在 Transformer 块内部则 FFN ≈ 66.8%、注意力 ≈ 33.2%）。这印证了本章「三分之二的参数在做键值存储（FFN）」的口径。

**来源列表与原文摘引：**

- Touvron, H. et al. (2023). "LLaMA: Open and Efficient Foundation Language Models." arXiv:2302.13971.
  - Table 2（7B 行，原文）："6.7B | 4096 | 32 | 32 | 3.0e−4 | 4M | 1.0T"（params 6.7B，dimension 4096，n heads 32，n layers 32）。
  - FFN（原文）：SwiGLU 隐藏维用 "a dimension of 2/3·4d" 而非 4d。
  - 口径注：FFN 隐藏维 11008 与 vocab 32000 取自官方发布模型 config（论文正文/Table 2 未直接列出）；2/3·4·4096 = 10922.7 向上取整到 256 倍数 = 11008，与论文规则一致。整套账目可独立复算至 6.738B。
- 复算已由本项目 Python 独立核验：attn/layer 67.1M、ffn/layer 135.3M、attn 总 2.147B、ffn 总 4.329B、嵌入（非绑定）262M、合计 6.738B，占比 FFN 64.2%/attn 31.9%/emb 3.9%。
