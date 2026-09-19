# ============================================================
# AIMO3 FULL SUBMISSION — Unsloth + Qwen3-30B-A3B + QLoRA
# Strategy: QLoRA fine-tune → merge → vLLM inference
#           with Tool-Integrated Reasoning (TIR) + majority voting
#
# Notebook structure:
#   PART 1 — Fine-tuning  (run once, saves merged model)
#   PART 2 — Inference    (Kaggle submission entry point)
# ============================================================

# ── INSTALL (run in a Kaggle cell before this script) ───────
# !pip install unsloth vllm -q
# !pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 -q

# ==============================================================
# PART 1 — FINE-TUNING WITH UNSLOTH + QLORA
# ==============================================================

from unsloth import FastLanguageModel
from datasets import Dataset
from trl import SFTTrainer, SFTConfig
import torch
import json
import re
import os

# ── 1.1  Config ───────────────────────────────────────────────
MODEL_NAME        = "unsloth/Qwen3-30B-A3B-unsloth-bnb-4bit"  # Unsloth pre-quantised
FINETUNED_DIR     = "/kaggle/working/qwen3_aimo_merged"
MAX_SEQ_LENGTH    = 8192
LORA_R            = 16
LORA_ALPHA        = 16
TARGET_MODULES    = ["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"]

# ── 1.2  Load base model (4-bit QLoRA) ───────────────────────
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name      = MODEL_NAME,
    max_seq_length  = MAX_SEQ_LENGTH,
    dtype           = None,          # auto (bf16 on H100)
    load_in_4bit    = True,
)

# ── 1.3  Attach LoRA adapters ─────────────────────────────────
model = FastLanguageModel.get_peft_model(
    model,
    r                   = LORA_R,
    target_modules      = TARGET_MODULES,
    lora_alpha          = LORA_ALPHA,
    lora_dropout        = 0,         # 0 = optimised by Unsloth
    bias                = "none",
    use_gradient_checkpointing = "unsloth",
    random_state        = 42,
)

model.print_trainable_parameters()
# Expected: ~100M / 30B trainable (~0.3%)

# ── 1.4  Training data ────────────────────────────────────────
# Format: Tool-Integrated Reasoning (TIR)
# Model interleaves natural language + Python code blocks
# which get executed and fed back as observations.
#
# Source datasets to attach as Kaggle datasets:
#   • AI-MO/NuminaMath-CoT    (~860k problems, CoT format)
#   • AI-MO/NuminaMath-TIR    (~70k problems, TIR format)  ← primary
#   • lighteval/MATH           (AIME/AMC style)

SYSTEM_PROMPT = (
    "You are an expert mathematics olympiad solver. "
    "Solve problems step by step. When helpful, write Python code inside "
    "```python ... ``` blocks to compute intermediate results. "
    "Always put your final integer answer inside \\boxed{}."
)

def format_tir_example(problem: str, solution: str) -> str:
    """Format a problem/solution pair into chat template."""
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": problem},
        {"role": "assistant","content": solution},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,       # thinking OFF during SFT
    )

# ── Minimal synthetic example — replace with NuminaMath-TIR ──
raw_examples = [
    {
        "problem": (
            "Find all positive integers $n$ such that "
            "$n^2 - 19n + 99$ is a perfect square."
        ),
        "solution": (
            "Let $n^2 - 19n + 99 = k^2$ for some non-negative integer $k$.\n"
            "```python\nresults = []\n"
            "for n in range(1, 10000):\n"
            "    val = n*n - 19*n + 99\n"
            "    if val >= 0 and int(val**0.5)**2 == val:\n"
            "        results.append(n)\n"
            "print(results)\n```\n"
            "Execution output: [1, 9, 10, 18]\n"
            "The positive integers are $n \\in \\{1, 9, 10, 18\\}$, "
            "giving sum $= 1+9+10+18 = \\boxed{38}$."
        ),
    },
    # ── Add NuminaMath-TIR rows here in production ───────────
    # from datasets import load_dataset
    # ds = load_dataset("AI-MO/NuminaMath-TIR", split="train")
    # raw_examples += [{"problem": r["problem"], "solution": r["solution"]} for r in ds]
]

train_dataset = Dataset.from_list([
    {"text": format_tir_example(ex["problem"], ex["solution"])}
    for ex in raw_examples
])

# ── 1.5  SFT Trainer ──────────────────────────────────────────
trainer = SFTTrainer(
    model       = model,
    tokenizer   = tokenizer,
    train_dataset = train_dataset,
    args = SFTConfig(
        dataset_text_field      = "text",
        max_seq_length          = MAX_SEQ_LENGTH,
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,     # effective batch = 8
        warmup_steps            = 10,
        num_train_epochs        = 1,
        learning_rate           = 2e-4,
        fp16                    = not torch.cuda.is_bf16_supported(),
        bf16                    = torch.cuda.is_bf16_supported(),
        logging_steps           = 10,
        optim                   = "adamw_8bit",
        weight_decay            = 0.01,
        lr_scheduler_type       = "cosine",
        seed                    = 42,
        output_dir              = "/kaggle/working/checkpoints",
        report_to               = "none",
    ),
)

print("Starting fine-tuning...")
trainer_stats = trainer.train()
print(f"Training complete. Loss: {trainer_stats.training_loss:.4f}")

# ── 1.6  Merge LoRA → base and save ──────────────────────────
print("Merging LoRA adapters into base model...")
model = FastLanguageModel.for_inference(model)   # enables faster inference kernel

# Merge + save as full bf16 weights for vLLM
model.save_pretrained_merged(
    FINETUNED_DIR,
    tokenizer,
    save_method = "merged_16bit",   # full bf16; use "lora" to save adapter only
)
print(f"Merged model saved to {FINETUNED_DIR}")

# Optional: also export as GGUF (if you want llama.cpp inference)
# model.save_pretrained_gguf(FINETUNED_DIR + "_gguf", tokenizer,
#                            quantization_method="q4_k_m")


# ==============================================================
# PART 2 — INFERENCE / KAGGLE SUBMISSION
# ==============================================================
# AIMO3 uses a gateway API — your app.py receives one problem
# at a time via the kaggle_evaluation module and must return
# a 5-digit integer answer.
# ==============================================================

import subprocess
import sys
import threading
import time
import traceback
from collections import Counter

# ── 2.1  Start vLLM server (background process) ───────────────
VLLM_PORT   = 8000
VLLM_MODEL  = FINETUNED_DIR   # or swap with original HF model

def start_vllm_server():
    """Launch vLLM OpenAI-compatible server as a subprocess."""
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model",              VLLM_MODEL,
        "--port",               str(VLLM_PORT),
        "--tensor-parallel-size","2",       # 2× H100 for 30B model
        "--max-model-len",      "16384",
        "--dtype",              "bfloat16",
        "--enable-prefix-caching",          # speeds up repeated prompts
        "--trust-remote-code",
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Stream server logs to stdout so Kaggle captures them
    def _stream():
        for line in process.stdout:
            print("[vllm]", line.decode().rstrip())
    threading.Thread(target=_stream, daemon=True).start()
    return process

def wait_for_vllm(timeout: int = 120):
    """Poll until the vLLM server is ready."""
    import urllib.request
    url = f"http://localhost:{VLLM_PORT}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            print("vLLM server is ready.")
            return True
        except Exception:
            time.sleep(3)
    raise RuntimeError("vLLM server failed to start within timeout.")

vllm_proc = start_vllm_server()
wait_for_vllm()

# ── 2.2  vLLM client helper ───────────────────────────────────
import urllib.request as _req

def vllm_generate(prompt: str, temperature: float = 0.7,
                  max_tokens: int = 4096, n: int = 1) -> list[str]:
    """
    Call local vLLM server.  Returns a list of `n` completion strings.
    Using /completions (raw text) so we can pass pre-formatted prompt.
    """
    payload = json.dumps({
        "model":       VLLM_MODEL,
        "prompt":      prompt,
        "temperature": temperature,
        "max_tokens":  max_tokens,
        "n":           n,
        "stop":        ["<|im_end|>", "</s>"],
    }).encode()

    req = _req.Request(
        f"http://localhost:{VLLM_PORT}/v1/completions",
        data    = payload,
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    with _req.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())

    return [choice["text"] for choice in result["choices"]]

# ── 2.3  Prompt builder ───────────────────────────────────────
# We use the tokenizer's chat template to format consistently
# with fine-tuning.  enable_thinking=True lets Qwen3 reason
# in <think>...</think> before answering.

from transformers import AutoTokenizer as _AT
_tok = _AT.from_pretrained(VLLM_MODEL, trust_remote_code=True)

def build_prompt(problem: str, enable_thinking: bool = True) -> str:
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": problem},
    ]
    return _tok.apply_chat_template(
        messages,
        tokenize              = False,
        add_generation_prompt = True,
        enable_thinking       = enable_thinking,
    )

# ── 2.4  Code execution (TIR) ─────────────────────────────────
import signal
import contextlib
from io import StringIO

@contextlib.contextmanager
def _timeout(seconds: int):
    def _handler(sig, frame):
        raise TimeoutError()
    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)

def execute_code_blocks(text: str, timeout: int = 10) -> str | None:
    """
    Extract all ```python ... ``` blocks from model output,
    execute them sequentially (sharing state), and return
    the last printed value as a string, or None on failure.
    """
    blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL)
    if not blocks:
        return None

    namespace: dict = {}
    last_output: str | None = None

    for code in blocks:
        buf = StringIO()
        try:
            with _timeout(timeout):
                # Redirect stdout
                exec(compile(code, "<string>", "exec"),   # noqa: S102
                     {**namespace, "__builtins__": __builtins__,
                      "print": lambda *a, **k: buf.write(" ".join(map(str, a)) + "\n")},
                     namespace)
            out = buf.getvalue().strip()
            if out:
                last_output = out
        except TimeoutError:
            print("[TIR] code block timed out")
            return None
        except Exception as exc:
            print(f"[TIR] execution error: {exc}")
            return None

    return last_output

# ── 2.5  Answer extraction ────────────────────────────────────
def extract_answer(text: str, code_output: str | None = None) -> int | None:
    """
    Priority order:
      1. \\boxed{N}
      2. Last integer from code execution output
      3. 'final answer is N' / 'answer: N' patterns
      4. Last standalone integer in text
    Returns an integer or None.
    """
    # 1 — \boxed{}
    boxed = re.findall(r"\\boxed\{([^}]+)\}", text)
    if boxed:
        try:
            val = int(re.sub(r"[^\d\-]", "", boxed[-1]))
            return val
        except ValueError:
            pass

    # 2 — code execution output
    if code_output:
        nums = re.findall(r"-?\d+", code_output)
        if nums:
            return int(nums[-1])

    # 3 — explicit answer statements
    patterns = [
        r"(?:final answer|answer)\s*(?:is|=|:)\s*(-?\d+)",
        r"therefore[,\s]+(-?\d+)",
        r"=\s*\\boxed\{(-?\d+)\}",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))

    # 4 — last integer in response
    all_ints = re.findall(r"\b(-?\d{1,7})\b", text)
    if all_ints:
        return int(all_ints[-1])

    return None

# ── 2.6  Majority voting ──────────────────────────────────────
def weighted_majority_vote(candidates: list[dict]) -> int | None:
    """
    Each candidate is {"answer": int | None, "weight": float}.
    Returns the answer with the highest total weight, or None.
    """
    scores: dict[int, float] = {}
    for c in candidates:
        if c["answer"] is None:
            continue
        scores[c["answer"]] = scores.get(c["answer"], 0.0) + c["weight"]

    if not scores:
        return None
    return max(scores, key=scores.__getitem__)

# ── 2.7  Core solver ──────────────────────────────────────────
NUM_ATTEMPTS    = 8      # number of diverse samples per problem
GREEDY_ATTEMPTS = 1      # first N are greedy (temp=0)
MAX_TOKENS      = 4096

def solve(problem: str) -> int:
    """
    Solve a single AIMO3 problem.
    Returns a 5-digit-safe integer (0–99999).
    """
    prompt = build_prompt(problem, enable_thinking=True)
    candidates: list[dict] = []

    for i in range(NUM_ATTEMPTS):
        temperature = 0.0 if i < GREEDY_ATTEMPTS else 0.7
        try:
            outputs = vllm_generate(prompt, temperature=temperature,
                                    max_tokens=MAX_TOKENS, n=1)
            raw = outputs[0]
        except Exception as exc:
            print(f"[solver] vLLM call failed on attempt {i}: {exc}")
            continue

        # Parse <think>...</think> out of Qwen3 output
        think_end = raw.find("</think>")
        response  = raw[think_end + len("</think>"):].strip() if think_end != -1 else raw

        # TIR: run embedded code
        code_out  = execute_code_blocks(response)

        # Extract answer
        answer = extract_answer(response, code_out)

        # Weight factors
        weight = 1.0
        if i < GREEDY_ATTEMPTS:
            weight += 0.2          # greedy bonus
        if code_out is not None:
            weight += 0.5          # code execution succeeded
        if re.search(r"\\boxed\{", response):
            weight += 0.2          # explicit boxed answer

        candidates.append({"answer": answer, "weight": weight})
        print(f"  attempt {i+1}/{NUM_ATTEMPTS}: answer={answer}, weight={weight:.1f}")

    result = weighted_majority_vote(candidates)
    if result is None:
        print("[solver] No answer extracted — defaulting to 0")
        result = 0

    # AIMO3: answers are 5-digit integers (00000–99999)
    result = max(0, min(99999, abs(result)))
    print(f"  → Final answer: {result}")
    return result

# ── 2.8  Kaggle evaluation gateway ───────────────────────────
# AIMO3 uses a client/server pattern: the gateway sends problems
# one at a time and expects integer answers back via the API.
# The kaggle_evaluation package is provided as a competition dataset.

try:
    import kaggle_evaluation.aimo_3_inference_server as _server

    class AIMO3Solver(_server.AIMO3InferenceServer):
        def predict(self, problem_id: str, problem_text: str,
                    time_remaining_secs: int) -> int:
            print(f"\n{'='*60}")
            print(f"Problem ID : {problem_id}")
            print(f"Time left  : {time_remaining_secs}s")
            print(f"Problem    : {problem_text[:200]}...")
            answer = solve(problem_text)
            print(f"Submitted  : {answer}")
            return answer

    if __name__ == "__main__":
        solver = AIMO3Solver()
        solver.serve()

except ImportError:
    # ── Local testing fallback (no gateway) ──────────────────
    print("kaggle_evaluation not found — running local test mode\n")

    test_problems = [
        {
            "id": "local_001",
            "problem": (
                "Find the sum of all positive integers $n \\leq 1000$ "
                "such that $\\binom{n}{3}$ is divisible by $7$."
            ),
            "answer": None,   # unknown
        },
        {
            "id": "local_002",
            "problem": (
                "How many integers between $1$ and $10000$ inclusive "
                "have the property that their decimal representation "
                "contains the digit $7$ exactly twice?"
            ),
            "answer": None,
        },
    ]

    for ex in test_problems:
        print(f"\nSolving: {ex['id']}")
        ans = solve(ex["problem"])
        print(f"Answer : {ans}"
              + (f" (expected {ex['answer']})" if ex["answer"] else ""))
