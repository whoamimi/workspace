# Refactored comp monitor to add to local workspace

import functools

import torch


def profile_memory(per_batch=False):
    """
    Decorator to profile GPU/CPU memory usage before, after, and optionally per batch.
    Tracks peak GPU memory usage across all batches.

    Args:
        per_batch (bool): If True, prints memory usage after every batch.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            peak_memory = 0.0  # Track peak memory

            def print_memory_usage(label=""):
                nonlocal peak_memory
                if torch.cuda.is_available():
                    allocated = torch.cuda.memory_allocated(0) / 1024**3
                    reserved = torch.cuda.memory_reserved(0) / 1024**3
                    max_alloc = torch.cuda.max_memory_allocated(0) / 1024**3
                    peak_memory = max(peak_memory, allocated, max_alloc)
                    print("=" * 60)
                    print(f"GPU MEMORY USAGE {label}")
                    print("=" * 60)
                    print("CUDA available: True")
                    print(f"Device: {torch.cuda.get_device_name(0)}")
                    print(f"Memory Allocated: {allocated:.3f} GB")
                    print(f"Memory Reserved: {reserved:.3f} GB")
                    print(f"Max Memory Allocated: {max_alloc:.3f} GB")
                else:
                    print("=" * 60)
                    print(f"CPU MEMORY USAGE {label}")
                    print("=" * 60)
                    print("Device: CPU")
                print("=" * 60)

            # Inject memory callback for per-batch monitoring
            if per_batch:
                kwargs["_memory_callback"] = print_memory_usage

            print("Before function execution:")
            print_memory_usage("BEFORE")

            result = func(*args, **kwargs)

            print("After function execution:")
            print_memory_usage("AFTER")

            print("=" * 60)
            print(f"PEAK GPU MEMORY DURING EXECUTION: {peak_memory:.3f} GB")
            print("=" * 60)

            return result

        return wrapper

    return decorator


@profile_memory(per_batch=True)
def get_embeddings_batched(
    sequences,
    tokenizer,
    model,
    device,
    batch_size=INFERENCE_BATCH_SIZE,
    max_length=20,
    _memory_callback=None,
):
    model.eval()
    all_embeddings = []

    for i in range(0, len(sequences), batch_size):
        batch_seqs = sequences[i : i + batch_size]

        inputs = tokenizer(
            batch_seqs,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            batch_embeddings = outputs.pooler_output.cpu()
            all_embeddings.append(batch_embeddings)

        del inputs, outputs
        if device.type == "cuda":
            torch.cuda.empty_cache()

        if (i // batch_size) % 10 == 0:
            print(
                f"Processed {min(i + batch_size, len(sequences))}/{len(sequences)} sequences"
            )

        if _memory_callback:
            _memory_callback(f"AFTER BATCH {i // batch_size + 1}")

    return torch.cat(all_embeddings, dim=0)
