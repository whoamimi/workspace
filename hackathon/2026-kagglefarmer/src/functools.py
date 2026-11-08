# Decorator functions for loggings/reportings/traces or model visualisers


def trace_state(
    grid,
    *,
    step=None,
    action=None,
    reward=None,
    status=None,
    player=None,
    prefix="TRACE",
):
    """Pretty-print an environment state to stdout."""

    H = len(grid)
    W = len(grid[0]) if H else 0

    header = f"[{prefix}]"

    if step is not None:
        header += f" step={step}"

    if player is not None:
        header += f" player={player}"

    if action is not None:
        header += f" action={action}"

    if reward is not None:
        header += f" reward={reward}"

    if status is not None:
        header += f" status={status}"

    print(header)

    # Column coordinates
    print("     " + " ".join(f"{c:^7}" for c in range(W)))

    # Separator
    print("    " + "-" * (W * 8 - 1))

    for r, row in enumerate(grid):
        cells = []

        for cell in row:
            if cell is None:
                value = "."
            elif cell == "LOCKED":
                value = "#"
            else:
                value = str(cell)[:7]

            cells.append(f"{value:^7}")

        print(f"{r:>3} |" + "|".join(cells) + "|")


def agent_trace(
    step,
    state,
    *,
    action=None,
    reward=None,
    status=None,
    player=None,
):
    print(
        f"[AGENT]"
        f" step={step}"
        f" player={player}"
        f" action={action}"
        f" reward={reward}"
        f" status={status}"
    )

    trace_state(state, prefix="STATE")
