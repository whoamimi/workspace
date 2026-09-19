import sys
import pickle
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Tuple

import h5py
import numpy as np
import torch
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from torch.utils.data import Dataset
from tqdm.auto import tqdm  # works on Kaggle

# ------------------------ CONFIG ----------------------------

from pathlib import Path

INPUT_DIR = Path("/kaggle/input/brain-to-text-25")
OUTPUT_DIR = Path("/kaggle/working/")
# Input Comp Dataset
NEURAL_DATA_DIR = INPUT_DIR / "t15_copyTask_neuralData" / "hdf5_data_final"
PRETRAINED_DIR = INPUT_DIR / "t15_pretrained_rnn_baseline" / "t15_pretrained_rnn_baseline"
CKPT_DIR = PRETRAINED_DIR / "checkpoint"
ARGS_PATH = CKPT_DIR / "args.yaml"
CKPT_PATH = CKPT_DIR / "best_checkpoint"
# Mounted Github Baseline Model
BASELINE_MODEL_PATH = Path("/kaggle/input/baseline-model/pytorch/default/1")
KB_PATH = OUTPUT_DIR / "knowledgeBase.pkl"
OUTPUT_PATH = OUTPUT_DIR / 'submission.csv'

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_LOAD: Optional[int] = None
NEURAL_HIDDEN_DIM = 512

# competition uses WER over lowercase, no punctuation [web:23]
BOS_TOKEN = BOS = "<s>"
EOS_TOKEN = EOS = "</s>"
PAD_TOKEN = UNK = "<unk>"

CONTEXT_SIZE = 2
TOP_K = 5
N_FEATURES = 2**20
BATCH_SIZE = 256

# ------------------------ TOKENIZER (LM) ---------------------

TOKEN_PATTERN = re.compile(
    r"(</s>|<s>)"              # BOS/EOS tags
    r"|[A-Za-z']+"             # words + contractions
    r"|[0-9]+"                 # numbers
    r"|[^\sA-Za-z0-9]"         # punctuation/symbols
)

def tokenize(text: str) -> List[str]:
    return TOKEN_PATTERN.findall(text)

def make_training_pairs(texts: Iterable[str], n_context: int = CONTEXT_SIZE):
    """
    Yields (context_string, next_word) pairs from readable sentences.
    """
    for t in texts:
        toks = tokenize(t)
        toks = [BOS_TOKEN] * n_context + toks
        for i in range(n_context, len(toks)):
            ctx = " ".join(toks[i - n_context:i])
            nxt = toks[i]
            yield ctx, nxt

# ------------------------ Online N-gram LM -------------------

class OnlineNGramClassifier:
    """
    Language model over READABLE tokens: P(next_word | context_words).
    """

    def __init__(self, n_context: int = CONTEXT_SIZE, n_features: int = N_FEATURES):
        self.n_context = n_context
        self.n_features = n_features

        self.vocab = {BOS_TOKEN, UNK}
        self.vec = HashingVectorizer(
            n_features=self.n_features,
            alternate_sign=False,
            norm="l2",
        )
        self.clf = SGDClassifier(
            loss="log_loss",
            alpha=1e-5,
            learning_rate="optimal",
        )
        self._is_fitted = False

    @property
    def classes(self) -> np.ndarray:
        return np.array(sorted(self.vocab))

    def partial_fit(self, texts: List[str], batch_size: int = BATCH_SIZE) -> None:
        X_batch, y_batch = [], []

        for ctx, nxt in make_training_pairs(texts, n_context=self.n_context):
            X_batch.append(ctx)
            y_batch.append(nxt)
            self.vocab.add(nxt)

            if len(X_batch) >= batch_size:
                X = self.vec.transform(X_batch)
                y = np.array(y_batch)
                self.clf.partial_fit(X, y, classes=self.classes)
                X_batch, y_batch = [], []
                if not self._is_fitted:
                    self._is_fitted = True

        if X_batch:
            X = self.vec.transform(X_batch)
            y = np.array(y_batch)
            if not self._is_fitted:
                self.clf.partial_fit(X, y, classes=self.classes)
                self._is_fitted = True
            else:
                self.clf.partial_fit(X, y)

    def predict_next(self, last_words: List[str], topk: int = TOP_K) -> List[Tuple[str, float]]:
        if not self._is_fitted:
            raise RuntimeError("Model not fitted yet. Call partial_fit first.")

        toks = [w if w in self.vocab else UNK for w in last_words][-self.n_context:]
        ctx = " ".join(([BOS_TOKEN] * (self.n_context - len(toks))) + toks)
        X = self.vec.transform([ctx])
        proba = self.clf.predict_proba(X)[0]
        idx = np.argsort(proba)[::-1][:topk]
        return [(self.classes[i], float(proba[i])) for i in idx]

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "n_context": self.n_context,
            "n_features": self.n_features,
            "vocab": list(self.vocab),
            "clf": self.clf,
        }
        with open(path, "wb") as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: str | Path) -> "OnlineNGramClassifier":
        path = Path(path)
        with open(path, "rb") as f:
            state = pickle.load(f)

        obj = cls(n_context=state["n_context"], n_features=state["n_features"])
        obj.vocab = set(state["vocab"])
        obj.clf = state["clf"]
        obj._is_fitted = True
        obj.vec = HashingVectorizer(
            n_features=state["n_features"],
            alternate_sign=False,
            norm="l2",
        )
        return obj

# ------------------------ KnowledgeBase ----------------------

class KnowledgeBase:
    """
    - phonetic2token: P(readable_word | phonetic_token) for decoding.
    - token2phonetic: P(phonetic_token | readable_word) (optional reverse).
    - ngram_model: LM over readable sentences for proof-reading.
    """

    def __init__(self, smoothing: float = 1.0):
        self.smoothing = smoothing
        self.phonetic2token: Dict[str, Counter] = defaultdict(Counter)
        self.phoneticCounts: Counter = Counter()
        self.token2phonetic: Dict[str, Counter] = defaultdict(Counter)
        self.tokenCounts: Counter = Counter()
        self.ngram_model: Optional[OnlineNGramClassifier] = None

    def update(self, true_seq: List[str], pred_seq: List[str]) -> None:
        true_tokens = [tok for sent in true_seq for tok in sent.split()]
        pred_tokens = [tok for sent in pred_seq for tok in sent.split()]

        for t_word, r_tok in zip(true_tokens, pred_tokens):
            self.phonetic2token[r_tok][t_word] += 1
            self.phoneticCounts[r_tok] += 1
            self.token2phonetic[t_word][r_tok] += 1
            self.tokenCounts[t_word] += 1

        if self.ngram_model is None:
            self.ngram_model = OnlineNGramClassifier()
        self.ngram_model.partial_fit(true_seq)

    def translate(
        self,
        raw_tok: str,
        cand_true: Optional[Iterable[str]] = None,
    ) -> Dict[str, float]:
        if raw_tok not in self.phoneticCounts:
            return {}

        true_counts = self.phonetic2token.get(raw_tok)
        total_for_raw = self.phoneticCounts.get(raw_tok)

        if not true_counts or not total_for_raw:
            return {}

        if cand_true is None:
            candidates = list(true_counts.keys())
        else:
            cand_true = list(cand_true)
            candidates = [t for t in cand_true if t in true_counts]

        if not candidates:
            return {}

        vocab_size = max(len(true_counts), 1)
        probs: Dict[str, float] = {}
        for t in candidates:
            c_xy = true_counts[t]
            p = (c_xy + self.smoothing) / (total_for_raw + self.smoothing * vocab_size)
            probs[t] = p

        Z = sum(probs.values())
        if Z > 0:
            for k in probs:
                probs[k] /= Z

        return probs

    def proof_reader(self, translated_sequence: List[str] | np.ndarray) -> List[str]:
        assert self.ngram_model is not None, \
            "ngram_model missing; call `update` on some true text first."

        print(translated_sequence[:1])

        cleaned: List[str] = []
        for seq in translated_sequence:
            try:
                seq_token = seq.split()

                if all(tok == PAD_TOKEN for tok in seq_token):
                    cleaned.append(seq)
                    continue

                tokens: List[str] = []
                for idx, token in enumerate(seq_token):
                    if token == PAD_TOKEN:
                        ctx_tokens = seq_token[:idx]
                        preds = self.ngram_model.predict_next(ctx_tokens)
                        replace_word = preds[0][0] if preds else token
                    else:
                        replace_word = token
                    tokens.append(replace_word)

                cleaned.append(" ".join(tokens))
            except Exception as e:
                print("Inserted:", translated_sequence[0], "-> Tried splitting:", seq)
                raise e
        return cleaned

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "smoothing": self.smoothing,
            "phonetic2token": self.phonetic2token,
            "phoneticCounts": self.phoneticCounts,
            "token2phonetic": self.token2phonetic,
            "tokenCounts": self.tokenCounts,
        }

        if self.ngram_model is not None:
            ngram_path = path.with_suffix(".ngram.pkl")
            self.ngram_model.save(ngram_path)
            state["ngram_path"] = str(ngram_path)
        else:
            state["ngram_path"] = None

        with open(path, "wb") as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path: Path) -> "KnowledgeBase":
        path = Path(path)
        with open(path, "rb") as f:
            state = pickle.load(f)

        kb = KnowledgeBase(smoothing=state["smoothing"])
        kb.phonetic2token = state["phonetic2token"]
        kb.phoneticCounts = state["phoneticCounts"]
        kb.token2phonetic = state["token2phonetic"]
        kb.tokenCounts = state["tokenCounts"]

        ngram_path = state.get("ngram_path")
        if ngram_path:
            kb.ngram_model = OnlineNGramClassifier.load(ngram_path)

        return kb

# ------------------------ Data loading -----------------------

COLS = [
    "neural_features",
    "n_time_steps",
    "seq_class_ids",
    "seq_len",
    "transcriptions",
    "sentence_label",
    "session",
    "block_num",
    "trial_num",
]

def load_h5py_file(file_path: str) -> Dict[str, List]:
    data = {c: [] for c in COLS}
    with h5py.File(file_path, "r") as f:
        for key in f.keys():
            g = f[key]
            neural_features = g["input_features"][:]
            n_time_steps = g.attrs["n_time_steps"]
            seq_class_ids = g["seq_class_ids"][:] if "seq_class_ids" in g else None
            seq_len = g.attrs["seq_len"] if "seq_len" in g.attrs else None
            transcription = g["transcription"][:] if "transcription" in g else None
            sentence_label = g.attrs["sentence_label"][:] if "sentence_label" in g.attrs else None
            session = g.attrs["session"]
            block_num = g.attrs["block_num"]
            trial_num = g.attrs["trial_num"]

            data["neural_features"].append(neural_features)
            data["n_time_steps"].append(n_time_steps)
            data["seq_class_ids"].append(seq_class_ids)
            data["seq_len"].append(seq_len)
            data["transcriptions"].append(transcription)
            data["sentence_label"].append(sentence_label)
            data["session"].append(session)
            data["block_num"].append(block_num)
            data["trial_num"].append(trial_num)
    return data

class BrainToTextDataset(Dataset):
    """Dataset wrapper for train/val/test splits."""

    def __init__(
        self,
        data_type: Literal["train", "test", "val"],
        data_config: dict = config,
        max_load: Optional[int] = MAX_LOAD,
        input_path: Path = NEURAL_DATA_DIR,
    ) -> None:
        self._type = data_type
        self._max_load = max_load
        self.input_path = input_path
        self.config = data_config

        self.sessions_labels: List[str] = self.config.get("dataset", {}).get("sessions", [])
        self.sessions = sorted(list(self.input_path.rglob(f"*{self._type}*")))
        self.sessions_to_day_idx = {label: idx for idx, label in enumerate(self.sessions_labels)}

        print(f"This Dataset Class will load {self._type} dataset up to {self._max_load}.")

    def __getitem__(self, idx: int) -> Dict:
        if self._max_load is not None and idx >= self._max_load:
            raise IndexError

        ss_file = self.sessions[idx]
        print(f"Loading session: {ss_file}")
        row = load_h5py_file(str(ss_file))

        n_time_steps = np.array(row["n_time_steps"])

        input_layer = self.sessions_to_day_idx[str(ss_file.parent.name)]
        neural_features = np.vstack(row["neural_features"])
        assert neural_features.shape[-1] == NEURAL_HIDDEN_DIM, f"Neural features expected shape (*, 512) but got {neural_features.shape}"

        neural_input = np.expand_dims(neural_features, axis=0).astype(np.float32)
        features = torch.from_numpy(neural_input).to(DEVICE)
        logits = runSingleDecodingStep(features, input_layer, model, self.config, DEVICE)
        print(f"Neural Shape: {features.shape} -> Logits shape: {logits.shape}")

        sentence_label = row.get("sentence_label", [])

        if self._type != "test":
            true_label, pred_label = postprocess(true_labels=sentence_label, pred_logits=logits)
        else:
            true_label, pred_label = [], postprocess_decoded_logits(logits)

        return {
            "n_time_steps": n_time_steps,
            "sentence_label": sentence_label,
            "logits": logits,
            "pred_label": pred_label,
            "true_label": true_label,
        }

    def __len__(self) -> int:
        if self._max_load is not None:
            return min(len(self.sessions), self._max_load)
        return len(self.sessions)

# ------------------------ Decoding helpers -------------------

def decode_single_item(logits: np.ndarray) -> List[str]:
    print(f"[decode_single_item]: {logits.shape}")
    if logits.ndim >= 2:
        pred_seq = logits.squeeze(0).argmax(axis=-1)
    else:
        pred_seq = logits.argmax(-1)
    pred_seq = [int(p) for p in pred_seq if p != 0]
    pred_seq = [
        pred_seq[i]
        for i in range(len(pred_seq))
        if i == 0 or pred_seq[i] != pred_seq[i - 1]
    ]
    pred_seq = [LOGIT_TO_PHONEME[p] for p in pred_seq]
    return pred_seq

def preprocess_sentence_labels(sentence_labels: List[str]) -> List[str]:
    SENTENCE_DELIM = "\n\n"
    return (
        SENTENCE_DELIM.join(sentence_labels)
        .translate(str.maketrans("", "", ",?'\""))
        .split("\n")
    )

def postprocess_decoded_logits(logits: np.ndarray) -> List[str]:
    sample = decode_single_item(logits)
    tok_str = "".join(sample)
    return tok_str.split(" | ")

def postprocess(true_labels: List[str], pred_logits: np.ndarray) -> Tuple[List[str], List[str]]:
    true_tokens = preprocess_sentence_labels(true_labels)
    pred_tokens = postprocess_decoded_logits(pred_logits)

    idx = 0
    true_tokens_out, pred_tokens_out = [], []

    for trial in true_tokens:
        true_seq = trial.split()
        seq_len = len(true_seq)
        if seq_len == 0:
            continue

        pred_seq = pred_tokens[idx : idx + seq_len]
        idx += seq_len

        if true_seq[-1].endswith(".") and pred_seq:
            pred_seq[-1] = pred_seq[-1] + "."

        true_seq += [EOS_TOKEN]
        true_tokens_out.append(" ".join([BOS_TOKEN] + true_seq))
        pred_tokens_out.append(" ".join([BOS_TOKEN] + pred_seq + [EOS_TOKEN]))

    assert len(pred_tokens_out) == len(true_labels) and len(true_tokens_out) == len(
        true_labels
    ), f"{len(pred_tokens_out)} != {len(true_tokens)} [pred : true]"

    return true_tokens_out, pred_tokens_out

# ------------------------ Train / Val / Submit ---------------

def run_trainer(
    smoothing: float = 0.85,
    kb_path: Path = KB_PATH,
    max_load: Optional[int] = MAX_LOAD,
    save: bool = False,
) -> Tuple[KnowledgeBase, List[Dict]]:
    data = BrainToTextDataset(data_type="train", max_load=max_load)
    kb = KnowledgeBase(smoothing=smoothing)

    input_data: List[Dict] = []
    for item in tqdm(data, desc="Loading training dataset", unit="trial", leave=True):
        true_label, pred_label = item["true_label"], item["pred_label"]
        kb.update(true_label, pred_label)
        input_data.append(item)

    if kb_path is not None and save:
        kb.save(kb_path)

    return kb, input_data

def run_validation(
    kb_path: Path = KB_PATH,
    kb: Optional[KnowledgeBase] = None,
    max_load: Optional[int] = None,
) -> List[Tuple[str, str]]:
    if kb is None:
        kb = KnowledgeBase.load(kb_path)

    data = BrainToTextDataset(data_type="val", max_load=max_load)
    pairs: List[Tuple[str, str]] = []

    for item in tqdm(data, desc="Validating", unit="session", leave=True):
        sentence_labels: List[str] = item["sentence_label"]
        pred_label: List[str] = item["pred_label"]

        translated_tokens = [
            max(kb.translate(j).items(), key=lambda x: x[1])[0] if kb.translate(j) else j
            for seq in pred_label
            for j in seq.split()
        ]

        pred_sentence_segments: List[str] = []
        for seq_text in " ".join(translated_tokens).split(BOS_TOKEN):
            seq_text = seq_text.strip().strip(EOS_TOKEN).strip()
            if seq_text:
                pred_sentence_segments.append(seq_text)

        pred_sentence_list = kb.proof_reader(translated_sequence=pred_sentence_segments)
        pred_sentence = " ".join(pred_sentence_list)

        true_sentence = " ".join(sentence_labels)
        pairs.append((true_sentence, pred_sentence))

    return pairs

def run_submission(
    kb_path: Path = KB_PATH,
    kb: Optional[KnowledgeBase] = None,
    output_csv: Path = OUTPUT_PATH,
    max_load: Optional[int] = None,
) -> None:
    """
    Decode test set and write submission.csv with id,text. [web:23]
    """
    if kb is None:
        kb = KnowledgeBase.load(kb_path)

    data = BrainToTextDataset(data_type="test", max_load=max_load)

    all_sentences: List[str] = []
    all_ids: List[int] = []
    idx_counter = 0

    for item in tqdm(data, desc="Decoding test", unit="session", leave=True):
        pred_label: List[str] = item["pred_label"]

        translated_tokens = [
            max(kb.translate(j).items(), key=lambda x: x[1])[0] if kb.translate(j) else j
            for seq in pred_label
            for j in seq.split()
        ]

        pred_sentence_segments: List[str] = []
        for seq_text in " ".join(translated_tokens).split(BOS_TOKEN):
            seq_text = seq_text.strip().strip(EOS_TOKEN).strip()
            if seq_text:
                pred_sentence_segments.append(seq_text)

        cleaned_list = kb.proof_reader(translated_sequence=pred_sentence_segments)
        cleaned_sentence = " ".join(cleaned_list)

        # competition ignores punctuation and expects plain words [web:23]
        cleaned_sentence = cleaned_sentence.replace(",", "").replace("?", "").replace(".", "")
        all_sentences.append(cleaned_sentence)
        all_ids.append(idx_counter)
        idx_counter += 1

    import pandas as pd
    df_out = pd.DataFrame({"id": all_ids, "text": all_sentences})
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False)

# ------------------------ Usage in Kaggle Notebook ----------

# 1) Train KB (once, offline or in a training notebook)
kb, train_data = run_trainer(save=True)

# 2) In submission notebook:
# kb = KnowledgeBase.load(KB_PATH)
# run_submission(kb=kb)
