#!/usr/bin/env python3
"""
Parse output of chronyc to produce stats


Copyright (C) 2021  Glen Pitt-Pladdy

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

Version 20210114

"""

import sys
import subprocess
import io
import csv

# CSV header for output
HEADER = [
    'Mode',
    'State',
    'Address',
    'Stratum',
    'Poll',
    'Reach',
    'LastRx',
    'Offset',
    'AdjustedOffset',
    'Error',
]

def chronyc_sources():
    """
    Run and parse chronyc output into list of dicts
    """
    proc = subprocess.run(
        ['chronyc', '-c', 'sources'],
        capture_output=True,
        check=True,
    )
    csvr = csv.reader(io.StringIO(proc.stdout.decode()))
    results = []
    for row in csvr:
        data = {
            key: value
            for key, value in zip(HEADER, row)
        }
        data['Mode'] = {
            '^': "Server",
            '=': "Peer",
            '#': "LocalClock",
        }[data['Mode']]
        data['State'] = {
            '*': "CurrentSynced",
            '+': "Combined",
            '-': "NotCombined",
            '?': "Unreachable",
            'x': "MaybeError",
            '~': "TooVariable",
        }[data['State']]
        results.append(data)
    return results


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in HEADER:
        print("Usage: {} <key>".format(sys.argv[0]))
        sys.exit(1)
    key = sys.argv[1]
    # grab results and transform
    results = chronyc_sources()
    by_state = {}
    for result in results:
        if result['State'] not in by_state:
            by_state[result['State']] = []
        by_state[result['State']].append(result)
    # prepare outputs
    min_value = None
    max_value = None
    servers = []
    for state in ('CurrentSynced', 'Combined', 'NotCombined'):
        for result in by_state.get(state, []):
            if min_value is None or result[key] < min_value:
                min_value = result[key]
            if max_value is None or result[key] > max_value:
                max_value = result[key]
            servers.append(result[key])
    # output
    print(min_value)
    print(max_value)
    print('\n'.join(servers))


if __name__ == '__main__':
    main()
