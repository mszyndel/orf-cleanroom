#!/usr/bin/env python3
"""Restricted single-pass interpolation compatibility for lead #79.

Known public exception values motivated this model: this is not a blind test.
Mark nonzero-low4 sites only; diagonal-1 at equal coordinate parity, axial-2
otherwise. Test marked-neighbour components of size 1/2, excluding components
with any member within two pixels of the boundary. Report larger components
as unsupported. Test increasing/decreasing raster order, one floor-mean
four-neighbour overwrite per marked site, initial marked words uint16 and
low4 zero, all unmarked words fixed. For a pair invert the earlier equation,
then replay all admissible later-site originals. Aggregate output only.
Compatibility does not establish actual camera order or original sensor
values. Zero-low4 sites may themselves be mapped; this model cannot find
those. Edges and larger components stay untested. Builds on #79/#146/#190.
Stdlib, read-only, no image/preview access or output.
"""
import argparse
import collections
import hashlib
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, first


def offsets(y, x):
    if y % 2 == x % 2:
        return ((-1, -1), (-1, 1), (1, -1), (1, 1))
    return ((-2, 0), (2, 0), (0, -2), (0, 2))


def initial_candidates(value, other_sum):
    """All uint16 multiples16 making floor((other_sum+candidate)/4)=value."""
    lo = max(0, 4 * value - other_sum)
    hi = min(65535, 4 * value + 3 - other_sum)
    return list(range(((lo + 15) // 16) * 16, hi + 1, 16))


def score_pair(early, late, early_other_sum, late_other_sum):
    """Both sites are neighbours; other sums exclude the other marked site."""
    latest_holds = (late_other_sum + early) // 4 == late
    candidates = initial_candidates(early, early_other_sum)
    # The early site's initial value is unused by these two overwrites; zero
    # is one admissible witness. Only aggregate replay counts are returned.
    replay_matches = 0
    for initial_late in candidates:
        replay_early = (early_other_sum + initial_late) // 4
        replay_late = (late_other_sum + replay_early) // 4
        replay_matches += replay_early == early and replay_late == late
    return {'latest_equation_holds': latest_holds,
            'initial_candidate_count': len(candidates),
            'replay_matching_candidates': replay_matches,
            'compatible': latest_holds and replay_matches > 0}


def summarize(words, width, height):
    if width < 5 or height < 5 or len(words) != width * height:
        raise ValueError('requires exact packed16 words and dimensions >=5')
    if any(not isinstance(v, int) or not 0 <= v <= 65535 for v in words):
        raise ValueError('requires uint16 words')
    marked = {i for i, v in enumerate(words) if v & 15}
    def neighbours(pos):
        y, x = divmod(pos, width)
        return [(y + dy) * width + x + dx for dy, dx in offsets(y, x)
                if 0 <= y + dy < height and 0 <= x + dx < width]
    adjacency = {i: set(neighbours(i)) & marked for i in marked}
    unseen = set(marked)
    components = []
    while unseen:
        pending = [min(unseen)]
        unseen.remove(pending[0])
        comp = []
        while pending:
            i = pending.pop()
            comp.append(i)
            for j in sorted(adjacency[i] & unseen):
                unseen.remove(j)
                pending.append(j)
        components.append(sorted(comp))
    result = {'marked_words': len(marked), 'components': len(components),
              'component_size_histogram': dict(collections.Counter(map(len, components))),
              'excluded_boundary_components': 0, 'excluded_boundary_words': 0,
              'unsupported_large_components': 0, 'unsupported_large_words': 0,
              'tested_singletons': 0, 'singleton_matches': 0, 'tested_pairs': 0,
              'orders': {name: {'pair_latest_equation_matches': 0,
                               'pair_initial_candidate_histogram': {},
                               'pair_replay_match_histogram': {},
                               'compatible_pairs': 0}
                         for name in ('increasing_raster', 'decreasing_raster')}}
    for comp in components:
        if any(not (2 <= i // width < height - 2 and 2 <= i % width < width - 2)
               for i in comp):
            result['excluded_boundary_components'] += 1
            result['excluded_boundary_words'] += len(comp)
            continue
        if len(comp) > 2:
            result['unsupported_large_components'] += 1
            result['unsupported_large_words'] += len(comp)
            continue
        if len(comp) == 1:
            result['tested_singletons'] += 1
            i = comp[0]
            result['singleton_matches'] += sum(words[j] for j in neighbours(i)) // 4 == words[i]
            continue
        result['tested_pairs'] += 1
        a, b = comp
        for name, early, late in [('increasing_raster', a, b), ('decreasing_raster', b, a)]:
            scored = score_pair(words[early], words[late],
                                sum(words[j] for j in neighbours(early) if j != late),
                                sum(words[j] for j in neighbours(late) if j != early))
            group = result['orders'][name]
            group['pair_latest_equation_matches'] += scored['latest_equation_holds']
            group['compatible_pairs'] += scored['compatible']
            for report_key, score_key in [('pair_initial_candidate_histogram', 'initial_candidate_count'),
                                          ('pair_replay_match_histogram', 'replay_matching_candidates')]:
                hist = group[report_key]
                key = str(scored[score_key])
                hist[key] = hist.get(key, 0) + 1
    tested_words = result['tested_singletons'] + 2 * result['tested_pairs']
    assert tested_words + result['excluded_boundary_words'] + result['unsupported_large_words'] == len(marked)
    for group in result['orders'].values():
        group['compatible_tested_components'] = result['singleton_matches'] + group['compatible_pairs']
        group['all_tested_components_compatible'] = (group['compatible_tested_components'] == result['tested_singletons'] + result['tested_pairs']) if result['tested_singletons'] + result['tested_pairs'] else None
        group['tested_components'] = result['tested_singletons'] + result['tested_pairs']
    return result


def measure(path):
    with open(path, 'rb') as source:
        data = source.read()
    tiff = Tiff(data)
    best = max(tiff.all_ifds(), key=lambda tags: sum(tags.get(0x117) or [0]))
    width, height = first(best, 0x100), first(best, 0x101)
    strips, counts = best.get(0x111) or [], best.get(0x117) or []
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError('invalid dimensions')
    if not strips or len(strips) != len(counts) or sum(counts) != 2 * width * height:
        raise ValueError('requires exact packed16 strip total')
    ranges = sorted(zip(strips, counts))
    for i, (offset, count) in enumerate(ranges):
        if offset < 0 or count <= 0 or offset + count > len(data):
            raise ValueError('invalid strip bounds')
        if i and ranges[i - 1][0] + ranges[i - 1][1] > offset:
            raise ValueError('overlapping strips')
    payload = b''.join(data[o:o + c] for o, c in zip(strips, counts))
    words = [v[0] for v in struct.iter_unpack(tiff.e + 'H', payload)]
    result = summarize(words, width, height)
    result.update(lead=79, input_sha256=hashlib.sha256(data).hexdigest(),
                  width=width, height=height, size_class='packed-16',
                  byte_order='little' if tiff.e == '<' else 'big')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    args = parser.parse_args()
    try:
        result = measure(args.file)
    except (OSError, ValueError, TypeError, struct.error):
        print('measurement failed: unsupported or unreadable packed16 input', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
