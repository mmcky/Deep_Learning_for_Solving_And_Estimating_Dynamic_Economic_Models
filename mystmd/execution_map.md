---
title: "Execution Map"
label: execution-map
---

The following table maps each manuscript chapter to its companion slide deck(s) and Jupyter notebooks. All paths are relative to the repository root; the short names are intentionally compact so the table remains readable.

**Execution map: manuscript chapters, slides, and notebooks**

   **Ch.**  **Topic**               **Lecture folder & deck**                **Notebooks (role)**
  --------- ----------------------- ---------------------------------------- ------------------------------------------------------------------------------------
      1     Intro to ML & DL        L02: `01_Intro_to_DL`                    L02 `01`--`09` (c$\times$`<!-- -->`{=html}9)
      2     Deep Equilibrium Nets   L03: `02_DEQNs`; L07: `05b_AutoDiff`     L03 `01`--`02` (c), `03`--`04` (e/s), `05` (c); L07 `01`--`04` (c)
      3     IRBC Model              L04: `03_IRBC`                           L04 `01`--`02` (c)
      4     NAS & Loss Norm.        L05: `04_NAS`, `05_Loss`                 L05 `02`--`04` (c), `05` (e)
      5     OLG Models              L08: `08_OLG`                            L08 `07`--`10` (c), `11` (e)
      6     HA, Young, Seq. Space   L09: `09_HA_Young`; L10: `10_SeqSpace`   L09 `10`--`12` (c); L10 `05`, `05b`, `06` (c), `KrusellSmith_Tutorial_CPU` (x)
      7     PINNs                   L11: `06_PINNs`                          L11 `01`--`05` (c)
      8     CT Het. Agents          L12: `07_CT_Theory`; L13: `08_CT_Num`    L13 `06`--`08` (c), `09` (e)
      9     Surrogates, GPs, DKL    L14: `07_Surrogates_GPs`                 L14 `01`, `02`, `04`--`08` (c), `07`, `09`, `10` (x)
     10     Structural Estimation   L15: `08_Struct_Est`                     L15 `03`, `03b` (c)
     11     Climate & Deep UQ       L16: `08_Climate`; L17: `09_UQ`          L16 `01`--`03` (c); L17 `09_DICE_2P_UQ_Analysis` (c) plus 4 `.py` pipeline drivers
     12     Synthesis & Outlook     L18: `10_Wrap_Up`                        ---

**Path conventions.** The repository organizes lectures by stable block id (`lectures/lecture_`$N$`_B`$YY$`_*/`); the leading `L`$N$ in the table is the student-facing lecture number and the parenthetical `B`$YY$ is the canonical block id (which is stable across renumberings). Slide and notebook names in the table are abbreviated; full paths follow `lectures/lecture_`$N$`_B`$YY$`_*/{slides,code}/`. Notebook role letters: `c` = core, `e` = exercise, `s` = solution (paired with an exercise notebook), `x` = extension/self-study. See the README for complete file names and direct links.

**Workshop material.** The live course includes a hands-on workshop on agentic programming (using AI agents as coding partners), delivered as L06. Because this field is evolving quickly, it is presented through slides, two Python helper scripts, and exercises rather than as a fixed manuscript chapter. The manuscript remains organized chapter by chapter, with the workshop material collected in the L06 slides and exercise prompts.

**Reproducibility.** Random-seed conventions, the `RUN_MODE` budget split, hardware and software pins, and GPU-determinism flags used by every notebook in the table above are documented in Appendix {ref}`app-reproducibility`. Worked solutions and guidance for the end-of-chapter exercises are collected in Appendix {ref}`app-solutions`.
