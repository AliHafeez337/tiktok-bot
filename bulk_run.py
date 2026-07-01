"""Run multiple Chrome profiles in series with different targets."""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_bulk_input(text):
    """
    Parse bulk input like:
      profile1; brandymelvilleusa, lift_the_label. profile2; freeflyapparel, citychicpl
    """
    entries = []
    for chunk in re.split(r"\.\s*", text.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ";" not in chunk:
            raise ValueError(f"Invalid entry (expected 'profile; targets'): {chunk!r}")
        profile, targets = chunk.split(";", 1)
        profile = profile.strip()
        targets = targets.strip()
        if not profile or not targets:
            raise ValueError(f"Invalid entry (profile and targets required): {chunk!r}")
        entries.append((profile, targets))
    if not entries:
        raise ValueError("No profile entries found in input.")
    return entries


def list_profiles():
    sessions_dir = Path("sessions")
    if not sessions_dir.is_dir():
        return []
    return sorted(
        p.name for p in sessions_dir.iterdir() if p.is_dir()
    )


def run_profile(profile, targets, log_file):
    """Run main.py for one profile and stream output to console + log file."""
    started = datetime.now()
    header = (
        f"Bulk run log\n"
        f"Profile: {profile}\n"
        f"Targets: {targets}\n"
        f"Started: {started.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'=' * 60}\n\n"
    )

    with open(log_file, "w", encoding="utf-8") as log:
        log.write(header)
        log.flush()
        print(header, end="")

        proc = subprocess.Popen(
            [sys.executable, "main.py", "-p", profile, "--targets", targets],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            log.write(line)
            log.flush()

        exit_code = proc.wait()
        finished = datetime.now()
        footer = (
            f"\n{'=' * 60}\n"
            f"Exit code: {exit_code}\n"
            f"Finished: {finished.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {finished - started}\n"
        )
        log.write(footer)
        print(footer, end="")

    return exit_code


def main():
    parser = argparse.ArgumentParser(
        description="Run multiple Chrome profiles in series with different targets."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help='Bulk input, e.g. "profile1; user1, user2. profile2; user3, user4"',
    )
    args = parser.parse_args()

    bulk_input = args.input
    if not bulk_input:
        print("Bulk input format:")
        print("  profile1; target1, target2. profile2; target3, target4")
        print()
        print("Example:")
        print(
            "  profile1; brandymelvilleusa, lift_the_label. "
            "profile2; freeflyapparel, citychicpl"
        )
        print()
        bulk_input = input("Enter bulk input: ").strip()

    if not bulk_input:
        print("ERROR: No input provided.", file=sys.stderr)
        sys.exit(1)

    try:
        entries = parse_bulk_input(bulk_input)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    available = set(list_profiles())
    if available:
        print("Available profiles:", ", ".join(available))
    else:
        print("WARNING: No profiles found under sessions/.")

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nRunning {len(entries)} profile(s) in series.")
    print(f"Logs will be saved under: {log_dir}\n")

    failed = []
    for index, (profile, targets) in enumerate(entries, start=1):
        if available and profile not in available:
            print(
                f"WARNING: Profile '{profile}' was not found in sessions/. "
                "It will still be attempted."
            )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_dir / f"bulk_{timestamp}_{profile}.log"

        print(f"\n{'=' * 60}")
        print(f"[{index}/{len(entries)}] Profile: {profile}")
        print(f"Targets: {targets}")
        print(f"Log file: {log_file}")
        print(f"{'=' * 60}\n")

        exit_code = run_profile(profile, targets, log_file)
        if exit_code != 0:
            failed.append((profile, exit_code))

    print(f"\n{'=' * 60}")
    print("BULK RUN COMPLETE")
    print(f"{'=' * 60}")
    print(f"Profiles run: {len(entries)}")
    print(f"Log directory: {log_dir.resolve()}")

    if failed:
        print("\nProfiles with non-zero exit codes:")
        for profile, code in failed:
            print(f"  - {profile}: exit {code}")
        sys.exit(1)


if __name__ == "__main__":
    main()
