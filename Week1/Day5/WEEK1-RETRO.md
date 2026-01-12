# Day 1 — File Handling & Performance

## Lessons Learned
1. Learned the difference between buffer-based file reading and stream-based file reading.
2. Understood why loading large files entirely into memory is risky.
3. Learned how to measure execution time and memory usage in Node.js.
4. Gained clarity on when to prefer streams over buffers for scalability.

## What Broke
1. Initial confusion about memory usage metrics.
2. Output timing was misleading when async code was not handled properly.

### Day 2 — CLI Tools, Large Data & Concurrency

## Lessons Learned
1. Learned how to build executable CLI tools using Node.js.
2. Understood how command-line arguments are parsed and used.
3. Learned difference between parallelism and concurrency .
4. Gained exposure to concurrency using chunks and worker threads.
5. Learned that higher concurrency does not always guarantee better performance.

## What Broke
1. Incorrect chunk division caused incomplete file processing initially.
2. Worker thread communication bugs resulted in missing statistics (Used Promise all Function for that).

### Day 3 — Git Recovery & Discipline

## Lessons Learned
1. Learned how to recover from mistakes without rewriting Git history using.
```bash 
git revert
```
2. Understood the real difference between git reset (Deleting commit history) and git revert (Adding new commit).
3. Learned how to use git bisect to identify faulty commits efficiently.
```bash
git bisect
```
4. Gained confidence in resolving merge conflicts manually and learned why they occur in first place.
5. Learned how git stash helps maintain clean workflows during interruptions.

## What Broke

1. Reverting an old commit caused merge conflicts that required manual resolution.
2. Main branch was ahead of the repo branch , therefore had to use git pull to copy the content from main branch and then resolve conflict.
3. Merge conflicts were confusing until conflict markers were clearly understood.

### Day 4 — HTTP & API Forensics

## Lessons Learned
1. Learned the fundamentals of the HTTP request–response cycle.
2. Understood how headers influence server behavior.
3. Learned how pagination works in APIs.
4. Gained hands-on experience with caching using ETag and 304 responses.
5. Learned how to inspect raw HTTP traffic using curl and Postman.

## What Broke

1. Header modifications initially appeared ineffective, causing confusion.
3. Needed careful inspection to avoid assuming differences where none existed.

### Day 5 — Automation & Safeguards

## Lessons Learned
1. Learned how automation prevents bad commits early in the workflow.
2. Understood the importance of validation scripts in CI-like setups.
3. Learned how ESLint and Prettier enforce code quality.
4. Gained experience configuring Husky pre-commit hooks.
5. Learned how build artifacts and checksums improve reliability and traceability.

## What Broke
1. ESLint configuration issues caused commits to be blocked unexpectedly.
2. Invalid config.json repeatedly failed validation until fixed correctly.
3. Husky command deprecations caused setup confusion (newer version of husky introduced new commands).

## Overall Week Reflection
1. Learned to debug systems instead of guessing.
2. Understood the value of discipline, automation, and observability.
3. Gained confidence in handling real-world development workflows.
