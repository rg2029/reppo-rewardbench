"""Read-only arithmetic audit for exported Judging Judges HTML reports.

Uses Python stdlib. This proves displayed aggregation arithmetic only, not
on-chain execution, voting authenticity, judge independence or reward accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def cls(self, c):
        return c in self.attrs.get('class', '').split()

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

    def find(self, tag=None, cls=None):
        return next((n for n in self.walk() if n is not self and
                     (tag is None or n.tag == tag) and (cls is None or n.cls(cls))), None)

    def findall(self, tag=None, cls=None):
        return [n for n in self.walk() if n is not self and
                (tag is None or n.tag == tag) and (cls is None or n.cls(cls))]

    def text(self):
        return ''.join(ch.text() if isinstance(ch, Node) else ch for ch in self.children).strip()


class Parser(HTMLParser):
    VOIDS = {'meta', 'br', 'hr', 'link', 'input', 'img', 'source', 'area'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOIDS:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def required(parent, tag=None, cls=None):
    node = parent.find(tag=tag, cls=cls)
    if node is None:
        raise ValueError(f'Missing expected element: {tag}/{cls}')
    return node


def audit(path: Path):
    buf = path.read_bytes()
    parser = Parser()
    parser.feed(buf.decode('utf-8'))
    root = parser.root
    prompt = required(root,'p','eval').text()
    primary = []
    for card in required(root,cls='grid').findall('div','card'):
        primary.append({'id':required(card,cls='name').text(), 'model_claim':required(card,cls='badge').text()})
    allowed = {item['id'] for item in primary}
    if not primary or len(allowed) != len(primary):
        raise ValueError('Invalid primary set')
    voters = []
    totals = {name:0 for name in allowed}
    for card in required(root,cls='stack').findall('div','card'):
        name = required(card,cls='name').text()
        model = required(card,cls='badge').text()
        stake_text = required(card,cls='stake').text()
        stake_match = re.fullmatch(r'([0-9,]+) veReppo',stake_text)
        if not stake_match:
            raise ValueError('Invalid veReppo balance')
        stake=int(stake_match.group(1).replace(',',''))
        entries=[]
        seen=set()
        for tr in card.findall('tr'):
            who=required(tr,cls='who').text()
            amt=int(required(tr,cls='amt').text().replace(',',''))
            if who in seen or who not in allowed:
                raise ValueError('Unknown or duplicate candidate')
            seen.add(who)
            entries.append({'evaluator_id':who,'signed_allocation':amt})
            totals[who] += amt
        if seen != allowed: raise ValueError(f'Incomplete allocation from {name}')
        if sum(abs(x['signed_allocation']) for x in entries) != stake:
            raise ValueError(f'Absolute allocations do not match stake for {name}')
        voters.append({'voter':name,'model_claim':model,'ve_reppo':stake,
                       'signed_sum':sum(x['signed_allocation'] for x in entries),
                       'absolute_sum':sum(abs(x['signed_allocation']) for x in entries),
                       'allocations':entries})
    if not voters: raise ValueError('No voting records')
    claimed = {}
    for el in required(root,cls='nets').findall('div','net'):
        who=required(el,cls='name').text()
        claimed[who]=int(required(el,cls='net-amt').text().replace(',',''))
    if set(claimed) != allowed: raise ValueError('Reported net list does not match primary set')
    winner_text=required(root,cls='verdict').find(cls='stake').text()
    m=re.search(r'Winning evaluator:\s*(evaluator-[0-9]+)',winner_text)
    if not m: raise ValueError('No winner specified')
    winner=m.group(1)
    actual_winners=[k for k,v in totals.items() if v==max(totals.values())]
    uniform={name:sum(next(x['signed_allocation'] for x in v['allocations'] if x['evaluator_id']==name)/v['ve_reppo'] for v in voters) for name in allowed}
    uniform_winners=sorted(k for k,v in uniform.items() if abs(v-max(uniform.values()))<1e-9)
    stake_total=sum(v['ve_reppo'] for v in voters)
    signed_total=sum(totals.values())
    out={
        'audit_kind':'REPORT-ARITHMETIC-ONLY, not independent validation',
        'source_file':path.name,
        'source_sha256':hashlib.sha256(buf).hexdigest(),
        'question':prompt,
        'primary_evaluators':primary,
        'num_primary':len(primary),
        'num_voters':len(voters),
        'num_allocations':sum(len(v['allocations']) for v in voters),
        'reported_winner':winner,
        'winner_matches_reported_net_argmax':winner in actual_winners,
        'reported_net':dict(sorted(claimed.items())),
        'recomputed_net':dict(sorted(totals.items())),
        'net_replay_exact_match':claimed==totals,
        'total_ve_reppo':stake_total,
        'total_abs_allocations':sum(v['absolute_sum'] for v in voters),
        'total_signed_allocations':signed_total,
        'negative_vote_count':sum(x['signed_allocation']<0 for v in voters for x in v['allocations']),
        'uniform_per_voter_normalized_scores':dict(sorted((k,round(val,6)) for k,val in uniform.items())),
        'uniform_per_voter_winners':uniform_winners,
        'uniform_per_voter_matches_reported_winner':winner in uniform_winners,
        'per_voter_allocation_audit':voters,
        'limits':[
            'This demonstrates consistency of the supplied HTML report totals, not truth of onchain records or real independent votes.',
            'One-voter-one-vote normalization is a hypothetical arithmetic comparison, not validated production Eval API aggregation.',
            'No independently verified correctness labels, coding-agent patch tests, timestamps for vote events, or confirmed causal identification.',
            'The final judge may involve separate scoring beyond choosing the maximum displayed net votes.',
            'Original data licensing, authenticity, and permission for public release have not been confirmed.',
        ],
    }
    return out


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('reports',nargs='+',type=Path)
    cli.add_argument('--output',type=Path)
    args=cli.parse_args()
    audits=[audit(p) for p in args.reports]
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({'cases':audits},indent=2,ensure_ascii=False)+'\n')
    for item in audits:
        print(f"{item['source_file']}: {item['num_primary']} primaries, {item['num_voters']} voters, "
              f"{item['num_allocations']} allocations, signed_net={item['total_signed_allocations']}, "
              f"stake={item['total_ve_reppo']}, replay_match={item['net_replay_exact_match']}, "
              f"winner={item['reported_winner']}, equal_voter={','.join(item['uniform_per_voter_winners'])}")


if __name__=='__main__':main()