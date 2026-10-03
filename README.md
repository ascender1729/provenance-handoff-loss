# The Chain Is Signed, the Handoff Is Prose: Measuring Provenance Loss at the Model Layer

Code and data for the paper by Pavan Kumar Dubasi (VibeTensor, https://vibetensor.com).

Accepted as a poster at the NeurIPS 2026 Workshop "Agents in the Wild: Safety, Security, and Beyond" (AIWILD, third edition). The workshop is non-archival.

OpenReview: https://openreview.net/forum?id=jo8LG8LlaI

## Summary

Capability-based delegation (UCAN, RFC 8693 token exchange, ZCAP-LD) already records who a delegated task is being done for, but that signed chain lives in a token envelope the language model never reads; the handoff the model actually writes to the next agent is prose. This repository measures what that prose carries. Across 480 delegation chains and 1,440 generation hops on four model families (Claude Haiku 4.5, Llama 3.3 70B, Nova Pro, Pixtral Large, all via AWS Bedrock), the originating principal's name and identifier survive to the end of an unprompted chain in 35.8% of cases, and one explicit instruction raises this to 99.6%. Loss happens mostly at the first handoff, model family matters far more than depth, and the instruction arm is the only one that fabricates identities (2 of 240 clause chains).

## Repository layout

    code/run_provenance.py   harness: chain generation (run), scoring + LLM judge (score)
    code/paper_numbers.py    prints every number quoted in the paper (offline)
    code/make_figures.py     builds figures/p1_arch, p2_perhop, p3_armdepth (offline)
    code/make_report.py      renders RESULTS.md from results.json + data/scored.jsonl (offline)
    code/probe_models.py     checks which Bedrock model ids your account can invoke (paid, tiny)
    data/chains.jsonl        every chain, every hop, raw model output (486 lines: 480 ok + 6 throttled attempts later refilled)
    data/judgements.jsonl    LLM-judge verdict for all 480 chains
    data/scored.jsonl        one merged record per chain: both scorings + terminal handoff
    results.json             cell tables (family x arm x depth) with Wilson 95% intervals, per-hop curves
    RESULTS.md               long-form write-up of the same numbers
    figures/                 the three paper figures (PDF + PNG)
    paper/                   submitted (anonymous, review) version: PDF + LaTeX source

## Install

Python 3.11+ (tested on 3.13).

    python -m venv .venv
    . .venv/bin/activate            # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

## Reproduce the paper (offline, no API calls, no cost)

Run from the repository root.

| Paper element | Command | Output |
|---|---|---|
| Abstract, Sec. 2-3 numbers, Table 1, fabrication counts, regex-screen precision/recall | `python code/paper_numbers.py` | stdout |
| Figure 1 (two-layer diagram) | `python code/make_figures.py` | `figures/p1_arch.pdf` |
| Figure 2 (per-hop retention, depth-5 control) | `python code/make_figures.py` | `figures/p2_perhop.pdf` |
| Figure 3 (arm x depth with Wilson bands) | `python code/make_figures.py` | `figures/p3_armdepth.pdf` |
| results.json and data/scored.jsonl from raw chains + cached judge verdicts | `python code/run_provenance.py score` | `results.json`, `data/scored.jsonl` |
| RESULTS.md | `python code/make_report.py` | `RESULTS.md` |

`run_provenance.py score` makes no API call when `data/judgements.jsonl` already covers every chain (it does: 480 of 480). It still imports `boto3`, so that package must be installed. The only field that changes on re-scoring is `meta.generated` (a timestamp). The regenerated figures are pixel-identical to the ones in the paper.

## Re-running generation (paid)

Regenerating chains needs AWS Bedrock access in us-east-1 to the four models listed in `code/run_provenance.py` (`FAMILIES`) plus the judge (Claude Sonnet 4.5). The reported run cost USD 2.32 at list prices. Use your own AWS credentials through the standard boto3 credential chain; none are included here.

    python code/probe_models.py          # optional: check model access
    mv data data_paper                   # keep the paper's data; the harness resumes from data/
    python code/run_provenance.py all --workers 10

Sampling is at temperature 0.7, so a fresh run will not reproduce the paper's chains token for token; the shipped `data/` is the frozen corpus behind every reported number.

## Data

- Principals, employee IDs and tasks are synthetic (20 invented principals, 5 task templates, see `PRINCIPALS` and `TASKS` in `code/run_provenance.py`). No real personal data is involved.
- Model outputs were generated through AWS Bedrock in August 2026. Each record carries the model id that produced it.
- `prog_*` fields are the strict programmatic scoring; `judge_*` fields are the LLM judge. The paper reports the programmatic column as primary and the judge for fabrication.

## Citation

    @inproceedings{dubasi2026chainsigned,
      title     = {The Chain Is Signed, the Handoff Is Prose: Measuring Provenance Loss at the Model Layer},
      author    = {Dubasi, Pavan Kumar},
      booktitle = {NeurIPS 2026 Workshop on Agents in the Wild: Safety, Security, and Beyond (AIWILD), non-archival},
      year      = {2026},
      url       = {https://openreview.net/forum?id=jo8LG8LlaI}
    }

## Licence

- Code (`code/`): Apache License 2.0, see `LICENSE`.
- Data (`data/`, `results.json`, `RESULTS.md`, `figures/`): Creative Commons Attribution 4.0 (CC BY 4.0). Model outputs remain subject to the terms of the respective model providers.
- Paper text (`paper/prov_paper.tex`, `paper/prov_paper.pdf`): CC BY 4.0, matching the OpenReview licence. `paper/neurips_2026.sty` is the NeurIPS style file and is distributed under its own terms.
