# Working on Symphonic-Joules

1. Create venv and install:
   - `python -m venv .venv`
   - `source .venv/bin/activate`  # or .venv\Scripts\activate on Windows
   - `pip install -e .`

2. Run tests:
   - `pytest`

3. Run lint/format:
   - `ruff check .`
   - `ruff format .`

4. Add new features:
   - Put audio-related functions in `audio.py`.
   - Put energy/physics functions in `energy.py`.
   - Shared helpers go in `utils.py`.
   - Export public functions in `__init__.py`.

5. Commit & push:
   - `git status`
   - `git commit -am "Describe change"`
   - `git push`
6. Current ideas / backlog

- [ ] Add spectrogram + energy overlay helper.
- [ ] Write one end-to-end example in docs/.
- [ ] Improve utils.py with shared helpers.
