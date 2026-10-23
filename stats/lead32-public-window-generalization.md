# Lead #32: public window generalization

Tool: `tools/value_map_window_probe.py` at `f750607171d79781273f9c93bee6e98aec8e7743`, unchanged; source hashes are emitted by the tool. Aggregate cells and every public input SHA-256 are in `lead32-public-window-generalization.csv`. Measured by @radialmonster, 2026-10-21. Builds on #11, #32, @mtakemoto's bridge-energy design/tool (#64), and the window tool (#151).

This is an unfinished public generalization study, not a verified finding or a reproduction of the historical private growth experiment. The [design/claim](https://github.com/radialmonster/orf-cleanroom/issues/32#issuecomment-6308448930) fixed all samples, starts and cells before this study's target measurements. The two hires prefix results and earlier #151 smoke windows were already known. No target-outcome-based selection or tuning was performed.

## Method

Six available CC0 public files cover four further ordinary bodies and two E-M1 Mark II High Res reference samples. Starts are absolute candidate-token indices 0 and 8388608; length is 262144 for every window. Report all three suffix-only mappings and both lane counts: 72 pooled cells, with separate even/odd pools for two lanes. Each window has 2048 complete 128-token blocks. The candidate parser scans from payload bit zero; q>=17 is parsed with no extra skip. Omit whole escape-containing blocks without joining surviving neighbors. No incomplete tails or zero-variance lanes occurred. All files have measured `size_class=variable`, compression tag 1, and remain unassigned variants.

For each lane of n increments, A=sum((n*S_k-k*T)^2), V=n*sum(x^2)-T^2. Bridge energy is E=A/n^3; the exact uniformly permuted multiset mean is N=(n+1)*V/(6*n^2). Pool with sum(E)/sum(N), not the mean of ratios. The CSV preserves exact pool numerator/denominator and sums A/V. `at_most_half` uses exact fractions. Decimals and parity ratios are rounded to nine places. `defined_blocks` and `blocks_at_most_half` are within-cell counts, not sample-level test outcomes. Unary q is not assembled into mapped values.

Controls are the exact permutation mean and the existing synthetic exhaustive-permutation, independent rational-bridge and opposite-order tests. At n=128, alternating +/-1 has R=3/129; grouped halves have R=16386/258. These validate the machinery's sensitivity to order, not any camera interpretation. No random-shuffle p-values are claimed.

## Results

None of the 48 ordinary-body pooled cells is at or below 0.5. Across those cells the ratios span 0.854274082 to 1.619835656. This supports only this bounded negative under the declared bridge-energy metric; it neither reproduces the private historical growth figures nor rules out other maps.

Four of the 24 hires-reference cells are at or below 0.5: signed_digit, one lane, both starts on each file. ID 1994 gives 0.450267435 at zero and 0.439970235 at 8388608; ID 1996 gives 0.431336369 and 0.437041737. The prefix values match the earlier exploratory public report. Every other hires mapping/lane cell is above 0.5. Persistence is descriptive and does not separate code from scene content or prove a pixel-value reading.

Escape omission is material. Retained blocks at starts zero / 8388608 are: 241, 2045 / 2033; 1079, 1999 / 1905; 4126, 2047 / 2030; 6946, 1071 / 1992; 1994, 2023 / 2022; 1996, 2022 / 2020. TG-7's first window omits 977 of 2048 blocks (2235 parsed escapes), so its reported pool covers a selectively retained subset.

## Public inputs and reproduction

All six input hashes match existing manifest rows; no rows were replaced or relabeled. Check each named file with `python -I -B tools/pixls_samples.py check FILE` first. The CSV's `id`, `public_name` and `sha256` identify exact files; local basenames are not identifiers. Sources are public CC0, with no private inputs.

After reading complete sources and imports, run the following at the tool commit above. Each command prints aggregate JSON only. Repeat each measurement command with `--start-token 8388608`; keep both outputs. `FILE241` etc. denote the exact hash-matched local inputs.

```text
python -I -B tools/test_value_map_window_probe.py
python -I -B tools/value_map_probe.py --self-test
python -I -B tools/value_map_window_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --measured-by radialmonster --start-token 0 --max-tokens 262144
python -I -B tools/value_map_window_probe.py --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --measured-by radialmonster --start-token 0 --max-tokens 262144
python -I -B tools/value_map_window_probe.py --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --measured-by radialmonster --start-token 0 --max-tokens 262144
python -I -B tools/value_map_window_probe.py --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946 --measured-by radialmonster --start-token 0 --max-tokens 262144
python -I -B tools/value_map_window_probe.py --sample 1994 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1994 --measured-by radialmonster --start-token 0 --max-tokens 262144
python -I -B tools/value_map_window_probe.py --sample 1996 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1996 --measured-by radialmonster --start-token 0 --max-tokens 262144
```

CSV rows directly format `sample.cells`: `pool.sum_A`, `pool.sum_V`, `pool.R_pool` and `parity_pools`; omission fields come from `sample.omissions`; signature fields from `sample.measured_signature`. No additional sample measurement or fitted analysis is used in formatting. Count a pooled ratio <=0.5 by testing twice its numerator <= its denominator. Preserve samples and windows separately; do not pool differently sized scenes or treat the 72 dependent cells as independent trials.

## Limits and remaining work

Absolute token starts are not established image coordinates. The later start samples a different fraction of a large hires frame than of an ordinary frame. Four ordinary bodies with one file each and two hires files of one body cannot separate body, mode, scene or escape-framing effects. Escape omission does not repair unknown earlier misalignment. The tool's schema labels windows exploratory even though these settings were fixed before this study's runs. Detrending removes mean drift; no undetrended bounded path, reconstruction or decoder is established.

The historical private estimator and files, other #32 mappings, q assembly, physical rows and causal content-versus-code question remain untested. A public controlled cohort with comparable scenes/modes and independently justified framing would address generalization more directly. The lead stays open. Both helper and supervisor represent @radialmonster; no independent human verification is claimed. CPU only; no images/previews or other decoder material used. This work follows RULES.md.

## One-off formatting of existing aggregate output

Keep each command's aggregate JSON as `study32-ID-START.json` in a scratch directory, using its numeric ID and start. The following one-off reducer reads only those existing aggregate outputs and prints the CSV above. Save this visible code in scratch and run `python -I -B REDUCER AGGREGATE_DIRECTORY`; it does not read raw samples or write files.

```python
"""One-off formatting/counting of existing aggregate JSON; no raw inputs."""
import csv
import json
import pathlib
import sys
from fractions import Fraction
scratch = pathlib.Path(sys.argv[1])
fields = ['tool','source_commit','measured_by','id','public_name','sha256','width','height','bpp','start_token','returned_tokens','start_bit','end_bit','retained_blocks','omitted_blocks','escapes','mapping','lanes','sum_A','sum_V','R_numerator','R_denominator','R_decimal','at_most_half','even_R','odd_R','defined_blocks','blocks_at_most_half','zero_variance_lanes']
out = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator='\n')
out.writeheader()
for sid in (241,1079,4126,6946,1994,1996):
    for start in (0,8388608):
        with (scratch / ('study32-%s-%s.json' % (sid,start))).open(encoding='utf-8-sig') as stream:
            doc = json.load(stream)
        s = doc['sample']
        assert s['raw_pixls_us_id']==sid and s['window_start_token']==start
        assert s['returned_tokens']==262144 and s['requested_tokens']==262144
        assert s['omissions']['complete_blocks']==2048 and s['omissions']['incomplete_tail_tokens']==0
        assert s['measured_signature']['size_class']=='variable'
        for c in s['cells']:
            p = c['pool']
            r = Fraction(p['R_pool']['numerator'],p['R_pool']['denominator'])
            n = c['increments_per_lane']
            assert r==Fraction(6*p['sum_A'],n*(n+1)*p['sum_V'])
            assert p['sum_A']==sum(b['sum_A'] for b in c['blocks'])
            assert p['sum_V']==sum(b['sum_V'] for b in c['blocks'])
            parity = [format(v['R_pool']['approx'],'.9f') for v in c['parity_pools']]
            values = ['tools/value_map_window_probe.py','f750607171d79781273f9c93bee6e98aec8e7743','@radialmonster',sid,s['raw_pixls_us_name'],s['sha256'],s['measured_signature']['payload_w'],s['measured_signature']['payload_h'],s['measured_signature']['bpp'],start,s['returned_tokens'],s['window_start_bit'],s['window_end_bit_exclusive'],s['omissions']['retained_blocks'],s['omissions']['escape_omitted_blocks'],s['omissions']['parsed_escapes'],c['mapping'],c['lane_count'],p['sum_A'],p['sum_V'],r.numerator,r.denominator,format(float(r),'.9f'),int(r<=Fraction(1,2)),parity[0] if parity else '',parity[1] if parity else '',c['block_ratios']['defined_blocks'],c['block_ratios']['at_most_half_count'],p['zero_variance_lanes']]
            out.writerow(dict(zip(fields,values)))

```
