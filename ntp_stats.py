#!/usr/bin/env python3
"""
Parse output of ntpq to produce stats


Copyright (C) 2023  Glen Pitt-Pladdy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


See: https://github.com/glenpp/cacti-ntp

Version 20230730

"""

import sys
import subprocess
import io


# CSV header for output
HEADER = [
    'remote',
    'refid',
    'st',
    't',
    'when',
    'poll',
    'reach',
    'delay',
    'offset',
    'jitter',
]


def ntpq_sources():
    """
    Run and parse ntpq output into list of dicts
    """
    proc = subprocess.run(
        ['ntpq', '-np'],
        capture_output=True,
        universal_newlines=True,
        check=True,
    )
    header = None
    header_complete = False
    results = []
    for line in proc.stdout.splitlines():
        if not header and not header_complete:
            header = line.strip().lower().split()
            if header != HEADER:
                raise ValueError(f"Got different header to expected: {header}")
            continue
        if not header_complete:
            if not line.startswith('=================='):
                raise ValueError(f"Got different header delimiter expected: {line}")
            header_complete = True
            continue
        # peer line
        tally_code = line[0]
        parts = line[1:].strip().lower().split()
        data = {h: v for h, v in zip(header, parts)}
        data['tally_code'] = tally_code
        data['tally_code_description'] = {
            ' ': "discarded as not valid",
            'x': "discarded by intersection algorithm",
            '.': "discarded by table overflow (not used)",
            '-': "discarded by the cluster algorithm",
            '+': "included by the combine algorithm",
            '#': "backup (more than tos maxclock sources)",
            '*': "system peer",
            'o': "PPS peer (when the prefer peer is valid)",
        }[tally_code]
        if data['t'].isdigit():
            data['t_description'] = f"NTS unicast with {data['t']} of cookies stored"
        else:
            data['t_description'] = {
                'u': "unicast or manycast client",
                'l': "local (reference clock)",
                'p': "pool",
                's': "symmetric (peer), server",
                'B': "broadcast server",
            }[data['t']]
        for key in ('st', 'when', 'poll'):
            if data[key] == '-':
                data[key] = None
            elif key in ('when'):   # in sec/min/hour/day/year
                if data[key].endswith('m'):
                    data[key] = int(data[key][:-1]) * 60
                elif data[key].endswith('h'):
                    data[key] = int(data[key][:-1]) * 3600
                elif data[key].endswith('d'):
                    data[key] = int(data[key][:-1]) * 86400
                elif data[key].endswith('y'):
                    data[key] = int(data[key][:-1]) * 86400 * 365
                else:
                    data[key] = int(data[key])
            else:
                data[key] = int(data[key])
        for key in ('delay', 'offset', 'jitter'):
            data[key] = float(data[key]) / 1000
        # reach - octal with LSB most recent status
        data['reach'] = int(data['reach'], 8)
        results.append(data)
    return results


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in HEADER:
        print("Usage: {} <key>".format(sys.argv[0]))
        sys.exit(1)
    key = sys.argv[1]
    # grab results and transform
    results = ntpq_sources()
    by_tally = {}
    for result in results:
        if result['tally_code'] not in by_tally:
            by_tally[result['tally_code']] = []
        by_tally[result['tally_code']].append(result)
    # prepare outputs
    min_value = None
    max_value = None
    servers = []
    for tally in ('o', '*', '+', '#'):
        for result in by_tally.get(tally, []):
            if min_value is None or result[key] < min_value:
                min_value = result[key]
            if max_value is None or result[key] > max_value:
                max_value = result[key]
            servers.append(str(result[key]))
    # output
    print(min_value)
    print(max_value)
    print('\n'.join(servers))


if __name__ == '__main__':
    main()
