#!/usr/bin/env python3
"""Project Timing Tool CLI - v1"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Project Timing Tool: Track time on projects',
        prog='task_timer'
    )
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'status', 'report'],
        help='Command to execute'
    )
    parser.add_argument(
        'project_id',
        nargs='?',
        help='Project ID for start command'
    )

    args = parser.parse_args()

    # Stub implementations - to be replaced with actual logic
    if args.command == 'start':
        if not args.project_id:
            print("Error: project_id required for start", file=sys.stderr)
            sys.exit(1)
        print(f"Starting timer for project: {args.project_id}")
    elif args.command == 'stop':
        print("Stopping current timer")
    elif args.command == 'status':
        print("Current status: No active timer")
    elif args.command == 'report':
        print("Generating report... (stub)")

if __name__ == '__main__':
    main()