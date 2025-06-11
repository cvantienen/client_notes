# 📝 Client Notes Manager

A lightweight documentation system for managing and updating notes on GSA clients.  
Built using [MkDocs](https://www.mkdocs.org/) with custom Python scripts for automation and structure enforcement.

---
## 📁 Project Structure

- `Dockerfile` — *Docker build file*
- `mkdocs.yml` — *MkDocs configuration*
- `noteTaker.py` — *Script to add/update client notes*
- `updateList.py` — *Automation for indexing or task lists*
- `note_structure_fix.sh` — *Utility to normalize note structure*
- `requirements.txt` — *Python dependencies*
- `styles/` — *MkDocs theme overrides*
- `docs/` — *Documentation files*
  - `index.md` — *Landing page*
  - `daily.md` — *Daily notes/tasks*
  - `mods.md` — *Change logs or module notes*
  - `clients/` — *Individual client files (e.g., `ACME_INC.md`)*
- `venv/` — *(Optional) Python virtual environment*



## 🚀 Run with Docker

To launch the documentation server using Docker:

```bash
docker run --rm -p 8000:8000 \
    -v /mnt/g/clients/client_notes:/app \
    clientnotes
````

This will:

* Serve MkDocs at [http://localhost:8000](http://localhost:8000)
* Mount your local project folder into the container
* Automatically reflect local file changes live

---

## 📚 Usage Overview

* Add or update client notes with `noteTaker.py`
* Automatically rebuild task/client indexes with `updateList.py`
* Run `note_structure_fix.sh` to normalize folder and file formatting
* Customize theme or styles via `styles/custom.css`

---

## 🛠️ Local Development (Optional)

If working outside Docker:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

---

## 🧾 Notes

* Client notes live under `docs/clients/`
* All documentation updates are reflected immediately in the live server
