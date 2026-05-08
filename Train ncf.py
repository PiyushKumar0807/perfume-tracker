#!/usr/bin/env python3
"""
NCF Training Script for PerfumeAI
===================================
Run once (or after significant new ratings accumulate) to train the Neural
Collaborative Filtering model and save it to disk.

Usage:
    python train_ncf.py

The script reads all ratings from the SQLite database, trains the NCF model,
and saves the checkpoint to the path configured in config.py
(default: ncf_model.pt in the project root).

If there are fewer than MIN_RATINGS ratings in the database, training is
skipped and a warning is printed — the app will fall back to content-based
filtering until enough data is collected.
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from app import app, db
from models import PerfumeRating, NCFModel
from config import Config

# ── Hyper-parameters ──────────────────────────────────────────────────────────
EMBED_DIM     = getattr(Config, 'NCF_EMBED_DIM', 64)
HIDDEN_LAYERS = [128, 64, 32]
EPOCHS        = getattr(Config, 'NCF_EPOCHS', 20)
BATCH_SIZE    = 1024
LR            = 1e-3
NEG_RATIO     = 4          # negative samples per positive interaction
MIN_RATINGS   = 10         # skip training if fewer ratings exist
MODEL_PATH    = getattr(Config, 'NCF_MODEL_PATH',
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ncf_model.pt'))


# ── Dataset ───────────────────────────────────────────────────────────────────

class RatingDataset(Dataset):
    """Implicit-feedback dataset.

    Positive samples  → ratings >= 3.0  (label = 1)
    Negative samples  → randomly sampled unrated items (label = 0)
    """

    def __init__(self, user_indices, item_indices, labels):
        self.users  = torch.tensor(user_indices, dtype=torch.long)
        self.items  = torch.tensor(item_indices, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_dataset(ratings, n_items: int, neg_ratio: int):
    """Convert DB rating rows into training triples with negative sampling."""
    # Positive interactions: rating >= 3.0
    user_item_pos = set()
    for r in ratings:
        if r.rating >= 3.0:
            user_item_pos.add((r.user_id, r.perfume_id))

    users, items, labels = [], [], []

    for u, i in user_item_pos:
        users.append(u)
        items.append(i)
        labels.append(1.0)

    # Negative sampling
    all_item_ids = list(range(n_items))
    rng = np.random.default_rng(42)
    n_neg = len(user_item_pos) * neg_ratio

    sampled = 0
    attempts = 0
    max_attempts = n_neg * 10
    unique_users = list({u for u, _ in user_item_pos})

    while sampled < n_neg and attempts < max_attempts:
        u = unique_users[rng.integers(len(unique_users))]
        i = int(rng.integers(n_items))
        if (u, i) not in user_item_pos:
            users.append(u)
            items.append(i)
            labels.append(0.0)
            sampled += 1
        attempts += 1

    return users, items, labels


# ── Main ──────────────────────────────────────────────────────────────────────

def train():
    with app.app_context():
        ratings = PerfumeRating.query.all()

    if len(ratings) < MIN_RATINGS:
        print(f"Only {len(ratings)} ratings found (need at least {MIN_RATINGS}). "
              "Skipping NCF training — app will use content-based fallback.")
        return

    print(f"Found {len(ratings)} ratings. Building ID maps ...")

    # Build contiguous integer maps for users and items
    raw_user_ids = sorted({r.user_id    for r in ratings})
    raw_item_ids = sorted({r.perfume_id for r in ratings})

    user_id_map = {uid: idx for idx, uid in enumerate(raw_user_ids)}
    item_id_map = {iid: idx for idx, iid in enumerate(raw_item_ids)}

    n_users = len(user_id_map)
    n_items = len(item_id_map)
    print(f"  Users: {n_users}  |  Items (rated): {n_items}")

    # Re-index ratings
    indexed_ratings = []
    for r in ratings:
        indexed_ratings.append(
            type('R', (), {
                'user_id':    user_id_map[r.user_id],
                'perfume_id': item_id_map[r.perfume_id],
                'rating':     r.rating,
            })()
        )

    print("Building training dataset with negative sampling ...")
    users, items, labels = build_dataset(indexed_ratings, n_items, NEG_RATIO)
    dataset = RatingDataset(users, items, labels)
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

    print(f"  Total samples: {len(dataset)} "
          f"({int(sum(labels))} positive, {int(len(labels) - sum(labels))} negative)")

    # Model, loss, optimizer
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on: {device}")

    model = NCFModel(n_users, n_items, EMBED_DIM, HIDDEN_LAYERS).to(device)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    print(f"\nTraining for {EPOCHS} epochs ...")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        for batch_users, batch_items, batch_labels in loader:
            batch_users  = batch_users.to(device)
            batch_items  = batch_items.to(device)
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad()
            preds = model(batch_users, batch_items)
            loss  = criterion(preds, batch_labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(batch_labels)

        scheduler.step()
        avg_loss = total_loss / len(dataset)
        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{EPOCHS}  loss={avg_loss:.4f}")

    # Save checkpoint
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'n_users':          n_users,
        'n_items':          n_items,
        'embed_dim':        EMBED_DIM,
        'hidden_layers':    HIDDEN_LAYERS,
        'user_id_map':      user_id_map,   # db user_id  -> model index
        'item_id_map':      item_id_map,   # db perfume_id -> model index
    }
    torch.save(checkpoint, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")
    print("Training complete!")


if __name__ == '__main__':
    train()