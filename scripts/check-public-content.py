"""Offline public-content check. Reports locations/rules only, never secret values."""
import argparse
import re
import subprocess
import sys

RULES = {
    'credential': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-(?:proj-)?[A-Za-z0-9_-]{25,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)'),
    'personal-path': re.compile(rb'(?i)(?<![A-Za-z])(?:[A-Z]:[/\\]+(?:Users|ChatGPT)[/\\]+|/home/[a-z0-9_]+/)'),
}

def git(*args):
    return subprocess.check_output(['git', *args])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    rows = git('rev-list', '--objects', 'HEAD').splitlines() if args.history else git('ls-tree', '-r', 'HEAD').splitlines()
    requests = []
    for row in rows:
        if args.history:
            oid, _, path = row.partition(b' ')
        else:
            meta, path = row.split(b'\t', 1)
            oid = meta.split()[2]
        requests.append((oid, path))
    batch = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    failures = []
    checked = 0
    for oid, path in requests:
        batch.stdin.write(oid + b'\n')
        batch.stdin.flush()
        header = batch.stdout.readline().split()
        data = batch.stdout.read(int(header[2]))
        batch.stdout.read(1)
        kind = header[1]
        if kind not in (b'blob', b'commit') or b'\0' in data[:8000]:
            continue
        checked += 1
        for rule, pattern in RULES.items():
            if pattern.search(data):
                failures.append((oid[:12], path or b'[commit]', rule))
        if kind == b'commit':
            for email in re.findall(rb'(?m)^(?:author|committer) .* <([^>]+)>', data):
                if not email.endswith((b'users.noreply.github.com', b'noreply.github.com', b'example.com')) and email != b'noreply@github.com':
                    failures.append((oid[:12], b'[commit metadata]', 'non-private-email-required'))
    batch.stdin.close()
    batch.wait()
    for oid, path, rule in failures:
        print(f'{rule}: {oid.decode()} {path.decode("utf-8", errors="replace")}')
    print(f'Checked {checked} text/commit objects; findings={len(failures)}. LFS payloads and unknown secret formats require separate review.')
    return bool(failures)

if __name__ == '__main__':
    sys.exit(main())
