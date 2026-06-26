"""
Stress-test trace generator.

Designed to exercise every node and code path in the multi-agent system:
  Orchestrate → Retrieve (novel query, no vectordb hit)
  → Initialize (RunnableParallel: plan + library extraction)
  → Update (API validation)
  → [plan shown] → "N" feedback triggers Revise (RunnableParallel: plan + task)
  → [revised plan] → "Y"
  → Execute subgraph (multiple Generate→Execute→Generate loops due to complexity)
  → [result shown] → "Y"
  → Memorize → END

Run from the project root:
  .venv/bin/python stress_test_run.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# ── env ──────────────────────────────────────────────────────────────────────
load_dotenv(find_dotenv())

# Force a dedicated LangSmith project so the trace is isolated
os.environ["LANGCHAIN_PROJECT"] = f"stress-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ── path ─────────────────────────────────────────────────────────────────────
# Nodes use open('state/functions.json') — must run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from function import baseball_lambda

SESSION_ID = "stress_test_001"

# ── Step 1: novel, multi-function, analytically complex query ─────────────────
# Chosen to guarantee a vectordb miss (Initialize path, not Modify) and to
# require statcast, playerid_reverse_lookup, and heavy pandas work across
# multiple date ranges — maximising Generate→Execute loop iterations.
TASK_1 = (
    "For the 2022 MLB season, identify every pitcher who threw at least 300 sliders. "
    "For those pitchers, compute their average slider velocity, horizontal break (pfx_x), "
    "and vertical break (pfx_z) broken out by month (April through September). "
    "Then find the single pitcher whose slider movement (combined pfx_x + pfx_z vector) "
    "changed the most from April to September 2022. "
    "Finally, show that pitcher's game-by-game strikeout totals across the entire 2022 season."
)

# ── Step 2: reject the plan and add a non-trivial revision ───────────────────
# Forces a full Revise cycle (another RunnableParallel + plan rewrite).
# Adding ERA-per-month requires a separate statcast aggregation pass that
# wasn't in the original plan — the agent must restructure the code.
TASK_2 = (
    "The plan looks mostly right but is missing something important. "
    "Please also include that pitcher's monthly ERA for the 2022 season alongside "
    "the movement stats, so we can see whether their effectiveness tracked with "
    "their stuff changes. Make sure ERA is calculated from the statcast data, "
    "not just looked up from a summary table."
)

# ── Step 3 & 4: accept plan, then confirm result ─────────────────────────────
TASK_3 = "yes"
TASK_4 = "yes"

DIVIDER = "\n" + "=" * 72 + "\n"

def run():
    print(f"{DIVIDER}LangSmith project: {os.environ['LANGCHAIN_PROJECT']}")

    print(f"{DIVIDER}STEP 1 — initial complex task")
    print(f"Task: {TASK_1[:120]}...")
    result = baseball_lambda.execute_workflow(TASK_1, SESSION_ID)
    print(f"\nAgent response:\n{result}")

    print(f"{DIVIDER}STEP 2 — reject plan and request revision")
    print(f"Task: {TASK_2[:120]}...")
    result = baseball_lambda.execute_workflow(TASK_2, SESSION_ID)
    print(f"\nAgent response:\n{result}")

    print(f"{DIVIDER}STEP 3 — approve revised plan → triggers Execute subgraph")
    result = baseball_lambda.execute_workflow(TASK_3, SESSION_ID)
    print(f"\nAgent response:\n{result}")

    print(f"{DIVIDER}STEP 4 — confirm result → triggers Memorize")
    result = baseball_lambda.execute_workflow(TASK_4, SESSION_ID)
    print(f"\nAgent response:\n{result}")

    print(f"{DIVIDER}Done. Check traces at https://smith.langchain.com")

if __name__ == "__main__":
    run()
