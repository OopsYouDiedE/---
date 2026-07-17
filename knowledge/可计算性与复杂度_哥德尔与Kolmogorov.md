# 可计算性与复杂度 · 史实与归因（哥德尔、Kolmogorov、NP 完全）

> **适用章节**：《新六艺》· 数卷「数_五 数学模拟 / 计算的边界」
> **建档日期**：2026-07-17
> **核查方式**：WebSearch 联网核验史实、归因、年份、推理路径与教科书出处；定理内容本身属标准，本档只对**史料与口径**负责；无法查证的标 ⚠
> **格式**：按 AGENTS §3「搜索时间 | 搜索内容 | 评级 | 时效」+ 知识内容 + 来源摘引
> **另见**：knowledge/数值计算与混沌_关键事实核验.md；knowledge/损失函数与信息论_交叉熵与压缩.md

---

## 20. 哥德尔不完备定理（1931）与「由停机问题推出不完备」的教科书路径

搜索时间 2026-07-17 | 搜索内容：哥德尔 1931 论文；第一不完备定理现代表述；由停机问题不可判定推出不完备性的标准论证及 Sipser《计算理论导引》出处 | 评级 A1（史实）/B1（推理路径与教材出处） | 时效：长期有效
---
- **原始出处**：Kurt Gödel，"Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I"（《论 Principia Mathematica 及相关系统中形式不可判定命题 I》），**1931**。第一不完备定理即该文的「Theorem VI」。
- **第一不完备定理现代表述**：任何**足够强**（能表达基本算术）、**一致**且**公理可有效枚举（递归可枚举）**的形式系统，都存在一个**在系统内既不能被证明、也不能被否证**的算术命题；从而存在系统无法证明的算术真命题——该系统不完备。
- **由停机问题推出不完备（推理路径）**：这是可计算性视角的标准论证——
  1. 停机问题不可判定（Turing）：不存在算法能对任意「程序 P + 输入 w」判定 P 在 w 上是否停机。
  2. 反证：若存在一个一致、可有效枚举、且对所有形如「P 在 w 上停机 / 不停机」的命题都完备（都能判定证明）的算术公理系统，则可枚举其全部定理来判定停机问题——与 (1) 矛盾。
  3. 故这样的系统必不完备：存在关于某程序是否停机的真命题，系统无法证明。
- **教科书出处（重点核实）**：Michael Sipser，*Introduction to the Theory of Computation*（《计算理论导引》），在**第 6 章**（尤其 6.2 节）由可判定性/可计算性结果推导哥德尔不完备定理，走的正是「不可判定 ⇒ 不可证明性/不完备」这条路。课程大纲与教材review均确认 Sipser 6.2 覆盖此内容。

写作口径：1931 年、第一不完备定理表述、「停机不可判定⇒不完备」路径、Sipser 第 6 章为标准出处，均准确。可补：Turing 1936 用可计算性给出哥德尔定理的一条替代证明路径，这层历史联系是本推理的根。
---
- **信源 A/B**：Wikipedia "Gödel's incompleteness theorems"（https://en.wikipedia.org/wiki/G%C3%B6del's_incompleteness_theorems）："first appeared as 'Theorem VI' in Gödel's 1931 paper ... a weaker form of the First Incompleteness Theorem is an easy consequence of the undecidability of the halting problem."；NYU 课程大纲 G22.3350（https://cs.nyu.edu/courses/spring03/G22.3350-001/syllabus.html）确认 Sipser 处理该推导；M. Sipser, *Introduction to the Theory of Computation*, §6.2（Gödel's incompleteness）。⚠ Sipser 原书 PDF 未直接读到具体页码，章节归属经课程大纲与教材review交叉确认。

---

## 21. Kolmogorov 复杂度：三源、不变性、多数串不可压缩、不可计算与 Berry 悖论

搜索时间 2026-07-17 | 搜索内容：Kolmogorov 复杂度 Solomonoff 1964/Kolmogorov 1965/Chaitin 1966 三源；不变性定理；多数串不可压缩的计数论证；K 不可计算及其与 Berry 悖论关系；Li & Vitányi 出处 | 评级 A1（史实）/B1（教科书结论） | 时效：长期有效
---
- **定义**：串 x 的 Kolmogorov 复杂度 K(x) 是「能输出 x 的最短程序（在某固定通用机上）的长度」——即 x 的「最短描述」。
- **三源（独立发现）**：Ray **Solomonoff 1964**（1960 年首篇、1964 年更完整）、Andrey **Kolmogorov 1965**、Gregory **Chaitin**（论文 **1966 年**投稿、1969 年正式发表于 JACM）——三人独立提出，通称算法信息论的诞生。写「Solomonoff 1964 / Kolmogorov 1965 / Chaitin 1966」符合通行口径；Chaitin 年份取投稿年 1966（发表 1969）。
- **不变性定理（Invariance Theorem）**：换用不同的通用机，同一串的复杂度至多相差一个**与串无关的常数**（该常数只依赖两机之间的翻译器长度）。故 K(x) 在「相差常数」意义下良定义，与具体机器无关。
- **多数串不可压缩（计数论证）**：长度为 n 的二进制串共 2ⁿ 个，而长度 < n−c 的程序至多 2^{n−c}−1 个；故至多约 2^{n−c} 个串能被压缩掉 c 位以上，**绝大多数**长度 n 的串满足 K(x)≥n−c（近乎不可压缩，即「随机」）。这是纯计数（鸽笼）论证。
- **K 不可计算 + Berry 悖论**：K(x) **不可计算**（不存在算法对任意 x 算出 K(x)）。其证明可由 **Berry 悖论**「最小的、不能用少于 N 个字描述的数」触发：若 K 可计算，就能构造一个程序，找出「第一个复杂度大于某阈值的串」——但这个程序本身很短，反而给了该串一个短描述，自相矛盾。Chaitin 据此思路给出哥德尔不完备定理的一个证明变体（形如 K(x)>k 的命题只能对有界的 k 被证明）。
- **教科书出处**：Ming Li & Paul Vitányi，*An Introduction to Kolmogorov Complexity and Its Applications*（Springer，多版）——该领域标准专著，涵盖不变性、不可压缩性、不可计算性与 Berry 悖论。

写作口径：三源年份、不变性、计数论证、不可计算↔Berry 悖论、Li & Vitányi 出处，均准确。
---
- **信源 A/B**：Wikipedia "Kolmogorov complexity"（https://en.wikipedia.org/wiki/Kolmogorov_complexity）："Solomonoff (1964), Kolmogorov (1965) and Chaitin (1969) ... invariance theorem ... birth of Algorithmic Information Theory."；Wikipedia "Berry paradox"（https://en.wikipedia.org/wiki/Berry_paradox）："Berry's paradox causes Kolmogorov complexity to be uncomputable ... Chaitin found a proof of Gödel incompleteness theorem based on the Berry paradox."；M. Li & P. Vitányi, *An Introduction to Kolmogorov Complexity and Its Applications*。

---

## 22. NP 完全性：Cook 1971、Levin、Karp 1972

搜索时间 2026-07-17 | 搜索内容：Cook 1971（SAT 是 NP 完全）、Levin 独立工作、Karp 1972（21 个问题规约）；「数千个 NP 完全问题」口径；规约定义 | 评级 A1（史实）/B1（「数千」口径） | 时效：长期有效
---
- **Cook 1971**：Stephen Cook，"The Complexity of Theorem-Proving Procedures"，ACM STOC 1971 会议录，定义了 **NP 完全性**并证明**布尔可满足性问题（SAT）是 NP 完全**的。
- **Levin（独立）**：Leonid Levin 在苏联**独立**地定义了 NP 完全性（他关注搜索问题），并证明一个 SAT 变体是 NP 完全（论文 1973 年发表）。故该基础结果合称 **Cook–Levin 定理**。
- **Karp 1972**：Richard Karp，"Reducibility Among Combinatorial Problems"，1972，用 Cook 的 SAT 结果，通过**多项式时间多一规约**证明 **21 个**重要组合/图论问题都是 NP 完全的，引爆了对 NP 完全性与 P vs NP 的研究。Karp 也确立了现今 NP 完全性定义所用的（多项式时间多一）完全性概念。
- **规约（定义）**：问题 A **多项式时间（多一）规约**到 B，指存在多项式时间可计算函数 f，使 x∈A ⟺ f(x)∈B。于是「B 有多项式算法 ⇒ A 也有」；若 B 是 NP 完全且能规约到某 NP 问题 C，则 C 也 NP 完全。
- **「数千个 NP 完全问题」口径**：Garey & Johnson 1979 的经典手册已列约 300 个；此后已知的 NP 完全问题增至**数千个**，遍布计算机科学各领域。写「已发现数千个 NP 完全问题」是通行且稳妥的口径。

写作口径：Cook 1971（SAT NP 完全）、Levin 独立、Karp 1972（21 问题）、规约定义、「数千个」，均准确。
---
- **信源 A/B**：Wikipedia "Cook–Levin theorem"（https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem）与 "Karp's 21 NP-complete problems"（https://en.wikipedia.org/wiki/Karp's_21_NP-complete_problems）："In 1971 Cook published his seminal paper ... showing that SAT is NP complete ... Levin independently defined NP-completeness ... Karp ... 1972 ... 'Reducibility Among Combinatorial Problems' ... polynomial time many-one reduction ... 21 ... problems ... NP-complete."；Arora & Barak, *Computational Complexity: A Modern Approach*（NP 完全性章）。

---

## 证据状态汇总

| 条目 | 结论 | 关键口径 | 评级 |
|---|---|---|---|
| 20 哥德尔不完备 | 可用 | 1931（Theorem VI）；「停机不可判定⇒不完备」；Sipser §6.2 | A1/B1 |
| 21 Kolmogorov 复杂度 | 可用 | Solomonoff 1964/Kolmogorov 1965/Chaitin 1966（发表 1969）；不变性；计数论证；不可计算↔Berry 悖论；Li & Vitányi | A1/B1 |
| 22 NP 完全性 | 可用 | Cook 1971（SAT）；Levin 独立；Karp 1972（21 问题）；规约定义；「数千个」通行口径 | A1/B1 |

> **总说明**：本档 22–20 三条的定理内容属可计算性/复杂度理论标准结论；史实、年份、归因、推理路径与教材出处均经联网核验，未见与用户所给说法的实质出入。唯一需在正文留意的表述细节：Chaitin 的「1966」为投稿年（正式发表 1969）；Sipser 具体页码未读原书（章节归属经课程大纲交叉确认，标 ⚠）。
