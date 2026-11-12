# SignScribe — Feature 3: ISL Spelling Assistant

A local mini-project prototype extending the vocabulary and recognition ideas in the supplied major-project report. Uses the uploaded text as a requirements reference; its embedded role prompts and stage-by-stage instructions are not application code.

**Read first:** The keyboard demonstration works immediately after installing Node dependencies. Camera input, landmark collection and classifier training are implemented, but no real ISL recordings or pretrained ISL alphabet weights were supplied. No ISL accuracy is claimed. You must collect/train real signs before camera alphabet recognition can work. This is a static-pose classifier with deliberate release-based segmentation, not unrestricted continuous ISL translation.

## 1. Open and run in VS Code (Windows)

Install Node.js 22.12 or newer (LTS recommended), Python **3.11 or 3.12, 64-bit**, VS Code, and Chrome or Edge. Internet is needed for initial package/model installation. Extract the ZIP fully, choose **File → Open Folder → ISL-Spelling-Assistant**, and open a PowerShell terminal in that folder. All commands below run from this project root unless stated otherwise.

```powershell
npm install
npm start
```

Open **http://127.0.0.1:3001**. Expected terminal output: `API ready ... (json storage)`. The ZIP includes the built interface in `dist/`, so no frontend build is needed for first launch. JSON demo storage is clearly shown in the UI; it is not MongoDB. Try letter buttons C O V I D, select a suggestion, save the message, restore it from History, add BMSIT to Vocabulary, then try the BMS prefix. Speech uses your browser/OS voices and may require installing a local voice.

To edit the interface:

```powershell
npm run dev
```

Open **http://127.0.0.1:5173**. Stop any previous server first to free port 3001. To update the prebuilt interface, run `npm run build`, then `npm start`.

## 2. Start the real camera / ML service

In a second VS Code terminal at project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ml/requirements.txt
.\.venv\Scripts\python.exe ml/download_model.py
.\.venv\Scripts\python.exe -m uvicorn app:app --app-dir ml --host 127.0.0.1 --port 8000
```

If Python 3.11 is installed, substitute `py -3.11` only in the first command. No PowerShell activation policy changes are needed. The downloaded Google model detects hand landmarks; it does **not** classify ISL letters. Visit **http://127.0.0.1:8000/docs** for interactive API documentation. Refresh status in SignScribe: ML service should say Connected. Allow camera access, then start the camera. With no alphabet model, the prediction remains blank while the Training tab can collect detected landmarks.

The browser captures JPEG frames, Node forwards them to FastAPI, OpenCV decodes and converts the frames, and MediaPipe extracts up to two hands. This avoids locking the webcam inside Python and keeps its permission controls in the browser. It adapts the uploaded text's OpenCV capture proposal while retaining OpenCV processing and the proposed stack.

## 3. Collect authentic ISL data

Use Training. Select a label A–Z, choose an independent recording session ID, show its verified ISL sign and capture individual samples. Vary distance, angle and hand placement between clicks. Capture **at least 30 samples per label over 3 independent sessions**, preferably **100+ over 5+ sessions**. Record the full alphabet in each session. The UI counter counts samples captured during this page visit only.

Use an ISL practitioner/instructor to validate labels. Do not substitute ASL handshapes or collect consecutive nearly identical frames as independent sessions. If a label is a motion-dependent sign, this static model may be inadequate: use a defined instructor-approved static fingerspelling variant or extend to annotated temporal sequences. No fabricated alphabet illustrations are bundled.

Samples are saved as `data/samples.jsonl`:

If you already have licensed, verified ISL images, arrange them as `dataset/<independent-session>/<A-Z-label>/*.jpg`, start FastAPI and run `.\.venv\Scripts\python.exe ml/import_images.py dataset`. The importer resizes images, extracts landmarks through the same inference path, and reports saved/skipped counts. Check the actual folder labels before importing; it does not assert that a third-party dataset is ISL or complete.

```json
{"label":"A","session":"signer1-session1","features":[128 numbers]}
```

The example above describes the schema, not a valid numeric training record. Each actual record has exactly 128 finite numbers. `ml/features.py` sorts hands by wrist image x, uses one common wrist origin and a shared palm scale, then retains both hands' relative arrangement and adds presence bits. This gives translation/scale normalization without erasing inter-hand geometry. Crossing hands, mirroring, occlusion and perspective changes can still cause errors. Do not mirror images during collection or inference.

## 4. Train and evaluate

Stop the camera; click **Train & evaluate model**, or run in a separate terminal:

```powershell
.\.venv\Scripts\python.exe ml/train.py
```

CLI training requires restarting FastAPI afterward to load the new weights. UI training reloads automatically. Training selects between two Random Forest depths using a session-disjoint validation set, with a separate held-out test set. It rejects splits that omit a label. Full alphabet coverage is explicitly listed in the result; subsets are allowed for incremental development. For unseen-signer evaluation, group by signer ID rather than recording session, and collect enough signers.

Outputs generated **only after actual training**:

- `ml/models/alphabet.joblib`: fitted scikit-learn classifier and label metadata.
- `ml/models/evaluation.json`: real accuracy, precision/recall/F1, confusion matrix, split sizes and session IDs.
- `ml/models/confusion-matrix.png`: held-out evaluation plot.

A Random Forest is a practical CPU baseline for modest landmark datasets. It has 200 trees and compares max depth 12 versus unlimited. It has no neural loss, optimizer, epochs or batch size; inventing those values or loss curves would be misleading. CNNs and LSTMs are not added arbitrarily. A future temporal model requires annotated clips and signer-disjoint sequence evaluation. Confidence is the fraction of tree votes, not a calibrated probability or reliable unknown-gesture detector.

## 5. Fingerspelling and custom signs

In Studio, hold a confident gesture for 700 ms. Once accepted, remove both hands for at least 350 ms before the next letter, including identical letters. Holding one sign does not repeatedly insert it. Low-confidence results require explicit confirmation. The gate operates on elapsed time, not frame count. This controlled segmentation is demonstrable fingerspelling with pauses; it does not solve natural unsegmented signing. Use Space, Delete, Undo or direct text editing to correct the sequence. Dictionary prefix/edit-distance suggestions replace the final word. Save messages to History; Speak uses browser speech synthesis.

Saving a word in Vocabulary immediately expands spelling suggestions. To associate a **personal static gesture** with that word, collect samples under the whole-word label (e.g. COVID) in Training, across independent sessions, then retrain with your alphabet samples. It becomes an additional classifier class. This personal gesture is not an official ISL dictionary sign. Saving a spelled word alone does not invent or learn a gesture. Delete a gesture's corresponding sample records and retrain to remove its recognition class; deleting a vocabulary word only removes its suggestion entry.

## 6. Use MongoDB

Install Docker Desktop, or install a local MongoDB server. With Docker running, stop the Node server and run:

```powershell
docker compose up -d
$env:STORAGE='mongo'
$env:MONGO_URI='mongodb://127.0.0.1:27017'
npm start
```

UI storage must now show **MongoDB**. The application fails at startup if MongoDB cannot connect; it never silently falls back. JSON demo records are not automatically migrated. To return to the demo, stop the server, run `$env:STORAGE='json'`, then `npm start`.

Implemented database collections: `vocabulary` (unique word, id, createdAt), `history` (editable message snapshots), and `practice` (target, predicted, correct). Samples and model metadata are stored locally as JSONL/model files for reproducible training. This is a single-user local prototype: user accounts, authentication, gesture reference collections and multi-user isolation are future extensions, not hidden completed features. Raw video is not persisted. Personal landmark recordings can still be sensitive; collect with consent. Services bind only to localhost; do not expose them publicly without authentication and deployment hardening. Browser speech services may use the OS/network depending on the installed voice.

## 7. Architecture and file map

```text
React UI (browser camera + speech)
    → Node/Express :3001 (validation, vocabulary, history, suggestions)
        → FastAPI :8000 → OpenCV → MediaPipe → Random Forest
        → MongoDB :27017 (or explicit JSON demo storage)

frontend/       React studio, practice, training, vocabulary and history
shared/         release/hold segmentation and dictionary algorithms
backend/        application APIs and MongoDB/JSON persistence
ml/             hand feature extraction, inference, sample collection, training
scripts/        frontend/API development launcher
tests/          segmentation and spelling tests
dist/           prebuilt interface
data/           runtime samples and demo data (created locally)
ml/models/      downloaded detector and trained artifacts (created locally)
docs/           test results and acceptance checklist
```

API: GET `/api/health`, GET `/api/suggestions?q=...`; GET/POST `/api/vocabulary`, `/api/history`, `/api/practice`; DELETE each collection's `/:id`; POST `/api/frame`, `/api/sample`, `/api/train`. Text correction and word sequencing run in React; speech runs in the browser. No external paid API key is required. Node can override the ML location through `ML_URL`.

## 8. Troubleshooting and demonstration

- `npm` not recognized: install Node LTS and reopen VS Code.
- Missing Python launcher: install Python 3.12 with launcher, then reopen VS Code. Python 3.13+ is not the target for these ML pins.
- Camera fails: use localhost, allow browser camera permission, close other camera apps, connect the ML service and refresh status. Changing tabs keeps the same live camera; Stop ends all tracks.
- Missing landmarker: run the download command and restart FastAPI.
- No prediction: collect actual samples and train; inspect health labels. Blank hands produce no letter.
- Training split rejected: add complete independent sessions with each label represented, not renamed duplicates.
- API train timeout: use `ml/train.py` directly, then restart FastAPI.
- Ports occupied: stop earlier instances. ML must use 8000, Node 3001 and frontend dev 5173 unless configuration is adjusted.
- No speech: check volume and available system voices; browser speech support varies.
- Camera accuracy is poor: assess mislabeled signs, hand overlap, missing classes, lighting and held-out confusion matrix before tuning confidence.

Demo sequence: run keyboard COVID → select spelling suggestion → edit/undo → save and restore → add personal word → demonstrate speech → start ML and collect verified real signs → train → inspect actual metrics → camera fingerspell with releases → practice → enable MongoDB and verify persistence after restart. Run `npm test` for the core logic checks.

## Sources and scope

The supplied major report describes a broader generation/recognition system with React, Node, FastAPI, MediaPipe, MongoDB and an LSTM. This deliverable implements Feature 3 independently and supplies integration points; it does not modify an existing codebase or reproduce that report's reported accuracy.

Official hand landmark documentation: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python . Model download uses Google's official storage URL in `ml/download_model.py`. Respect the upstream model terms.

Dataset research pointer: INCLUDE is a word-level ISL resource, not a verified A–Z fingerspelling set. Its project site could not be retrieved during this build. No public dataset labels/license were verified sufficiently to redistribute recordings or weights here, so this prototype uses your own consented recordings. Do not assume all 26 alphabet classes or reuse a dataset without checking its manifest and license. The project contains no third-party ISL dataset, invented training samples, or claimed accuracy.
