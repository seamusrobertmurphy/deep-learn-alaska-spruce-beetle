# Crown network

The fine-tuned four-band dead-crown network built by the `crown-finetune` chunk of
`01.manuscript/manuscript.qmd`, and the triage queue it feeds.

2026-08-14: `crown-finetune` crashes whenever the label-pair tile count is odd, because the
loop steps `range(0, len(order), 2)` and DeepLabV3's ASPP pooling branch reduces the final
one-tile batch to 1x1, which BatchNorm rejects in training mode; fixed with a
`drop_last`-equivalent skip. Matters because the chunk ran or failed on the parity of an
input count, which is invisible until it fires.

2026-08-14: `02.inputs/label-pairs/` has changed since the committed run, 72 train and 20
validation tiles in `git show HEAD:03.outputs/crown_net_metrics.csv` against 79 and 21 on
disk over the same 29 and 8 areas. Matters because the committed `tbl-crownnet` figures
describe a label set that no longer exists and cannot be reproduced from it.

2026-08-14: the committed `03.outputs/crown_net_metrics.csv` holds four rows where `EPOCHS`
is 8, so the recorded run was truncated, and the recall 0.55 at precision 0.18 and IoU
0.154 quoted in CLAUDE.md is its epoch 2, the checkpointed best. Matters because those
figures are a truncated run's interim best, not a completed training result.

2026-08-14: `crown-finetune` sets `torch.manual_seed(20260812)` but `load(augment=True)`
draws flips, rotations and jitter from unseeded `np.random`, so the chunk is not
reproducible as CLAUDE.md claims. Unresolved, because reseeding changes the result again.

2026-08-14: `triage-queue` skips blocks whose GeoPackage already exists but writes
`03.outputs/triage_queue.csv` from only the newly written rows, so an interrupted and
resumed run undercounts silently. Matters because that count is what the annotation-scope
decision is meant to rest on.
