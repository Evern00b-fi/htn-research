# Where a full IBD spends its time

One full IBD from an empty datadir on node A (6 vCPU, ~11 GiB RAM, SSD, HTND 2.18.1-a56566e86), from the node log.
Times are relative to the start of the pruning-proof download. One run on one machine on a near-idle network; read it
as a breakdown, not a benchmark.

| Phase | From | To | Duration | Share |
|---|---|---|---|---|
| Pruning proof: download 24 s, validation 44 s, application 1 min 48 s | T+0:00 | T+2:56 | 3 min | 7 % |
| Headers (~190k, about 200/s; a 4,097-header batch arrives in 0.4 s and takes ~20 s to process) | T+3:03 | T+18:59 | 16 min | 37 % |
| Pruning-point UTXO set download (20.66 M entries, ~103k/s) | T+18:59 | T+22:19 | 3.3 min | 8 % |
| Commitment check passed → import into the virtual UTXO set | T+22:24 | T+26:25 | 4 min | 9 % |
| Staging consensus commit and deletion of the old one | T+26:25 | T+28:49 | 2.4 min | 6 % |
| UTXO index rebuild (serial; block sync waits for it) | T+28:49 | T+33:39 | 4.8 min | 11 % |
| Block bodies (184,369, ~330/s) | T+33:39 | T+43:04 | 9.5 min | 22 % |
| **Total** | | | **~43 min** | |

## Options without a downside

The cheapest IBD is the one that never happens. Operators reported resets roughly weekly; the following node-local
fixes remove the causes that end in a reset and a full IBD, with no trade-off identified:

- [HTN-02](../findings/HTN-02.md): the pruning flag is cleared in the same commit as the deletion, so a crash during a
  move no longer leaves an unbootable node.
- [HTN-03](../findings/HTN-03.md) (draft, rework required): best-effort diagnostics are kept before the fresh sync. Research,
  not a ready fix: [HTN-43](../findings/HTN-43.md) could let a damaged older WAL avoid a full IBD.
- [HTN-05](../findings/HTN-05.md), [HTN-06](../findings/HTN-06.md), [HTN-41](../findings/HTN-41.md): shutdowns no
  longer hang and then close the database under live users.

## Candidates that need measurement first (not proposed)

| Candidate | Expected gain | Why not yet |
|---|---|---|
| Profile header processing (~200/s, the largest phase) | up to the largest share | cause unknown before a profile on a fresh datadir |
| Rebuild the UTXO index alongside block sync or during the import | ≤ 4.8 min, only on `--utxoindex` nodes | index consistency must be designed |
| Write-batch size of the import and commit (6.4 min together) | unknown | memory peak; profile together with headers |
| Request the next header batch before processing the current one | about 2 % (0.4 s network vs ~20 s processing) | not worth the code |
| Start from a snapshot from a trusted source | large | adds a trust assumption; rejected |
