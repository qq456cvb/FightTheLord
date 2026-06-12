# FightTheLord

A command-line **Dou Di Zhu** (斗地主, "Fight the Landlord") game in Python, with a rule-based AI, a human-play mode, and an early actor-critic (A3C-style) self-play experiment in TensorFlow.

This is the small precursor to [doudizhu-C](https://github.com/qq456cvb/doudizhu-C) (Combinatorial Q-Learning, AIIDE 2020): the card abstractions and the enumerated action space prototyped here later evolved into the C++ engine and CQL agents of that project.

## What's Inside

- `card.py` — card definitions and the core game knowledge:
  - `get_action_space()` enumerates every legal move type (singles, pairs, triples with kickers, straights, double/triple straights, bombs, rocket, ...) into a fixed discrete action space.
  - `CardGroup` validates moves, compares them (`bigger_than`), and greedily decomposes a hand into candidate groups (`analyze`).
- `player.py` — `Player` with three modes:
  - **rule-based AI** (default): plays from the greedy hand decomposition with simple heuristics (save bombs, hold big singles early, react to a teammate vs. the landlord, push when an opponent is down to one card);
  - **human** (`is_human`): type a comma-separated move in the terminal (e.g. `3,3,3,J`; `0` to pass);
  - **trainable** (`trainable`): turn control over to an external policy via `Game.step`.
- `game.py` — the game loop: dealing, the three landlord bonus cards, turn order, legal-move masking over the action space (`get_mask`), and an RL-style interface (`get_state` / `step`) exposing a 162-d state (one-hot of history, bonus cards, and the current hand). Run directly, it plays 100 games of you (player 2, as the landlord) against two rule-based AIs and reports the landlord win rate.
- `a3c.py` — self-play RL experiment: three small policy/value MLPs (one per seat) trained with advantage actor-critic on terminal win/lose rewards, with invalid actions masked out of the policy. Checkpoints go to `model/`, TensorBoard summaries to `train_global/`.

## Run

The code dates from the Python 2/3 transition era — `game.py` runs on Python 3 except for the human-input prompt which still uses `raw_input` (Python 2); `a3c.py` needs TensorFlow 1.x with `tf.contrib.slim`.

```bash
# play against two rule-based AIs in the terminal
python game.py

# train the actor-critic agents by self-play
python a3c.py
```

For a much stronger, properly trained agent (and a web UI to play against it), see [doudizhu-C](https://github.com/qq456cvb/doudizhu-C) and [doudizhu-tornado](https://github.com/qq456cvb/doudizhu-tornado).
