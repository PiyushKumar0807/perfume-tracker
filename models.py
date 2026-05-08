"""
Database models and recommendation engine for the Perfume Tracker
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import numpy as np
import pandas as pd
try:
    import torch
except ImportError:  # Optional dependency for NCF mode
    torch = None
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, Dict, List, Optional, cast

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profiles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    full_name = db.Column(db.String(120), default='')
    age = db.Column(db.Integer, default=25)
    gender = db.Column(db.String(20), default='')  # Male, Female, Non-binary, Prefer not to say
    skin_tone = db.Column(db.String(50), default='')
    location = db.Column(db.String(120), default='')
    perfume_knowledge = db.Column(db.String(50), default='Beginner')  # Beginner, Intermediate, Expert
    profile_complete = db.Column(db.Boolean, default=False)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    ratings = db.relationship('PerfumeRating', backref='user', cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def mark_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    @property
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        total_fields = 0
        completed_fields = 0
        
        # Basic profile fields
        profile_fields = [
            ('full_name', self.full_name),
            ('age', self.age),
            ('gender', self.gender),
            ('skin_tone', self.skin_tone),
            ('location', self.location),
            ('perfume_knowledge', self.perfume_knowledge)
        ]
        
        for field_name, value in profile_fields:
            total_fields += 1
            if value and str(value).strip():
                completed_fields += 1
        
        # Preferences fields (5 categories)
        if self.preferences:
            pref_fields = [
                self.preferences.preferred_families,
                self.preferences.preferred_occasions,
                self.preferences.preferred_seasons,
                self.preferences.notes_liked,
                self.preferences.notes_disliked
            ]
            
            for pref_field in pref_fields:
                total_fields += 1
                try:
                    parsed = json.loads(pref_field or '[]')
                    if parsed and len(parsed) > 0:
                        completed_fields += 1
                except Exception:
                    pass
        
        return int((completed_fields / total_fields * 100) if total_fields > 0 else 0)
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserPreference(db.Model):
    """User fragrance preferences"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Fragrance preferences (stored as JSON)
    preferred_families = db.Column(db.String(500), default='[]')
    preferred_occasions = db.Column(db.String(500), default='[]')
    preferred_seasons = db.Column(db.String(500), default='[]')
    intensity_pref = db.Column(db.String(50), default='Moderate')
    price_range = db.Column(db.String(50), default='Mid-range')
    notes_liked = db.Column(db.String(500), default='[]')
    notes_disliked = db.Column(db.String(500), default='[]')
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_families(self):
        return json.loads(self.preferred_families or '[]')
    
    def set_families(self, families):
        self.preferred_families = json.dumps(families) if isinstance(families, list) else families
    
    def get_occasions(self):
        return json.loads(self.preferred_occasions or '[]')
    
    def set_occasions(self, occasions):
        self.preferred_occasions = json.dumps(occasions) if isinstance(occasions, list) else occasions
    
    def get_seasons(self):
        return json.loads(self.preferred_seasons or '[]')
    
    def set_seasons(self, seasons):
        self.preferred_seasons = json.dumps(seasons) if isinstance(seasons, list) else seasons
    
    def get_liked_notes(self):
        return json.loads(self.notes_liked or '[]')
    
    def set_liked_notes(self, notes):
        self.notes_liked = json.dumps(notes) if isinstance(notes, list) else notes
    
    def get_disliked_notes(self):
        return json.loads(self.notes_disliked or '[]')
    
    def set_disliked_notes(self, notes):
        self.notes_disliked = json.dumps(notes) if isinstance(notes, list) else notes
    
    def __repr__(self):
        return f'<UserPreference user_id={self.user_id}>'


class Perfume(db.Model):
    """Perfume catalog"""
    __tablename__ = 'perfumes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    gender_target = db.Column(db.String(50), default='Unisex')  # Male, Female, Unisex
    fragrance_family = db.Column(db.String(100), nullable=False, index=True)
    
    # Notes - ingredients
    top_notes = db.Column(db.String(300), default='')
    middle_notes = db.Column(db.String(300), default='')
    base_notes = db.Column(db.String(300), default='')
    
    # Attributes
    season = db.Column(db.String(100), default='')
    occasion = db.Column(db.String(200), default='')
    intensity = db.Column(db.String(50), default='Moderate')
    longevity = db.Column(db.String(50), default='Good')
    price_range = db.Column(db.String(50), default='Mid-range')
    age_group = db.Column(db.String(100), default='')
    sillage = db.Column(db.String(50), default='Moderate')
    description = db.Column(db.Text, default='')
    
    # Relationships
    ratings = db.relationship('PerfumeRating', backref='perfume', cascade='all, delete-orphan')
    
    # Stats
    avg_rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def update_stats(self):
        """Update average rating and total count"""
        ratings_list = cast(List[PerfumeRating], self.ratings)
        if ratings_list:
            ratings = [r.rating for r in ratings_list]
            self.avg_rating = sum(ratings) / len(ratings)
            self.total_ratings = len(ratings)
        else:
            self.avg_rating = 0.0
            self.total_ratings = 0
    
    def __repr__(self):
        return f'<Perfume {self.name}>'


class PerfumeRating(db.Model):
    """User ratings for perfumes"""
    __tablename__ = 'perfume_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    perfume_id = db.Column(db.Integer, db.ForeignKey('perfumes.id'), nullable=False, index=True)
    rating = db.Column(db.Float, nullable=False)  # 0.5-5.0
    review = db.Column(db.Text, default='')
    used_before = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one rating per user per perfume
    __table_args__ = (db.UniqueConstraint('user_id', 'perfume_id', name='unique_user_perfume_rating'),)
    
    def __repr__(self):
        return f'<PerfumeRating user={self.user_id} perfume={self.perfume_id} rating={self.rating}>'


if torch is not None:
    class NCFModel(torch.nn.Module):
        """Neural Collaborative Filtering model."""

        def __init__(self, n_users: int, n_items: int, embed_dim: int = 64,
                     hidden_layers: Optional[List[int]] = None):
            super().__init__()
            if hidden_layers is None:
                hidden_layers = [128, 64, 32]

            self.user_embedding = torch.nn.Embedding(n_users, embed_dim)
            self.item_embedding = torch.nn.Embedding(n_items, embed_dim)

            layers = []
            in_dim = embed_dim * 2
            for h in hidden_layers:
                layers += [torch.nn.Linear(in_dim, h), torch.nn.ReLU(), torch.nn.Dropout(0.2)]
                in_dim = h
            layers.append(torch.nn.Linear(in_dim, 1))
            layers.append(torch.nn.Sigmoid())

            self.mlp = torch.nn.Sequential(*layers)

            torch.nn.init.normal_(self.user_embedding.weight, std=0.01)
            torch.nn.init.normal_(self.item_embedding.weight, std=0.01)

        def forward(self, user_ids, item_ids):
            u = self.user_embedding(user_ids)
            v = self.item_embedding(item_ids)
            x = torch.cat([u, v], dim=-1)
            return self.mlp(x).squeeze(-1)
else:
    class _NCFModelFallback:
        """Fallback placeholder when torch is unavailable."""

        def __init__(self, *args, **kwargs):
            raise RuntimeError("PyTorch is not installed; NCF model is unavailable.")
    NCFModel = _NCFModelFallback  # type: ignore[assignment]


class NCFRecommender:
    """Drop-in replacement for PerfumeRecommender that uses the trained NCF model."""

    FAMILIES = ["Floral", "Woody", "Oriental", "Fresh", "Citrus", "Gourmand",
                "Chypre", "Aquatic", "Aromatic", "Spicy", "Fougère", "Musk"]
    SEASONS = ["Spring", "Summer", "Fall", "Winter"]
    OCCASIONS = ["Casual", "Office", "Evening", "Night", "Sport", "Special", "Daytime"]
    INTENSITIES = ["Light", "Moderate", "Strong"]
    PRICE_RANGES = ["Budget", "Mid-range", "Luxury", "Ultra-luxury"]
    AGE_GROUPS = ["Young", "Middle", "Mature"]
    LONGEVITIES = ["Average", "Good", "Excellent"]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self._model: Optional[NCFModel] = None
        self._user_id_map: Dict[int, int] = {}
        self._item_id_map: Dict[int, int] = {}
        self._item_id_rev: Dict[int, int] = {}
        self.perfume_df = None
        self.feat_matrix = None

    def _resolve_model_path(self):
        if self.model_path:
            return self.model_path
        try:
            from flask import current_app
            return current_app.config.get('NCF_MODEL_PATH', 'ncf_model.pt')
        except RuntimeError:
            return 'ncf_model.pt'

    def _load_model(self):
        if torch is None:
            return False
        if self._model is not None:
            return True
        path = self._resolve_model_path()
        if not os.path.exists(path):
            return False
        try:
            checkpoint = torch.load(path, map_location='cpu', weights_only=False)
            n_users = checkpoint['n_users']
            n_items = checkpoint['n_items']
            embed_dim = checkpoint.get('embed_dim', 64)
            hidden_layers = checkpoint.get('hidden_layers', [128, 64, 32])

            model = NCFModel(n_users, n_items, embed_dim, hidden_layers)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()

            self._model = model
            self._user_id_map = checkpoint.get('user_id_map', {})
            self._item_id_map = checkpoint.get('item_id_map', {})
            self._item_id_rev = {v: k for k, v in self._item_id_map.items()}
            return True
        except Exception as e:
            print(f"NCF model load error: {e}")
            return False

    def _ncf_scores(self, user_id: int, candidate_perfume_ids: List[int]) -> Dict[int, float]:
        if not self._load_model():
            return {}

        u_idx = self._user_id_map.get(user_id)
        if u_idx is None:
            return {}

        item_indices = []
        valid_ids = []
        for pid in candidate_perfume_ids:
            i_idx = self._item_id_map.get(pid)
            if i_idx is not None:
                item_indices.append(i_idx)
                valid_ids.append(pid)

        if not item_indices:
            return {}

        model = self._model
        if model is None:
            return {}

        with torch.no_grad():
            u_tensor = torch.tensor([u_idx] * len(item_indices), dtype=torch.long)
            i_tensor = torch.tensor(item_indices, dtype=torch.long)
            scores = cast(Any, model)(u_tensor, i_tensor).cpu().numpy()

        return {pid: float(s) for pid, s in zip(valid_ids, scores)}

    def _build_feature_matrix(self):
        assert self.perfume_df is not None
        rows = []
        for _, row in self.perfume_df.iterrows():
            v = []
            for f in self.FAMILIES:
                v.append(1.0 if f.lower() in row.get("fragrance_family", "").lower() else 0.0)
            seasons = [x.strip() for x in str(row.get("season", "")).split(",")]
            for s in self.SEASONS:
                v.append(1.0 if s in seasons else 0.0)
            occasions = [x.strip() for x in str(row.get("occasion", "")).split(",")]
            for o in self.OCCASIONS:
                v.append(1.0 if o in occasions else 0.0)
            for i in self.INTENSITIES:
                v.append(1.0 if row.get("intensity", "") == i else 0.0)
            for p in self.PRICE_RANGES:
                v.append(1.0 if row.get("price_range", "") == p else 0.0)
            age_groups = [x.strip() for x in str(row.get("age_group", "")).split(",")]
            for a in self.AGE_GROUPS:
                v.append(1.0 if a in age_groups else 0.0)
            for lg in self.LONGEVITIES:
                v.append(1.0 if row.get("longevity", "") == lg else 0.0)
            notes_text = (str(row.get("top_notes", "")) + " " +
                          str(row.get("middle_notes", "")) + " " +
                          str(row.get("base_notes", ""))).lower()
            for note in ["rose", "jasmine", "vanilla", "sandalwood", "oud", "musk",
                         "bergamot", "patchouli", "cedar", "vetiver", "amber", "lavender"]:
                v.append(1.0 if note in notes_text else 0.0)
            rows.append(v)
        self.feat_matrix = np.array(rows, dtype=float)

    def _gender_mask(self, gender, perfume_genders):
        valid_targets = {
            "Male": ["Male", "Unisex"],
            "Female": ["Female", "Unisex"],
            "Non-binary": ["Male", "Female", "Unisex"],
            "Prefer not to say": ["Male", "Female", "Unisex"],
        }.get(gender, ["Male", "Female", "Unisex"])
        return np.array([any(g in valid_targets for g in str(pg).split(","))
                         for pg in perfume_genders])

    def build_user_vector(self, user_data, preferences):
        v = []
        fams = preferences.get_families() if hasattr(preferences, 'get_families') else []
        for f in self.FAMILIES:
            v.append(2.0 if f in fams else 0.0)
        seasons = preferences.get_seasons() if hasattr(preferences, 'get_seasons') else []
        for s in self.SEASONS:
            v.append(1.5 if s in seasons else 0.0)
        occasions = preferences.get_occasions() if hasattr(preferences, 'get_occasions') else []
        for o in self.OCCASIONS:
            v.append(1.5 if o in occasions else 0.0)
        intensity_pref = preferences.intensity_pref if hasattr(preferences, 'intensity_pref') else "Moderate"
        for i in self.INTENSITIES:
            v.append(2.0 if i == intensity_pref else 0.0)
        price_pref = preferences.price_range if hasattr(preferences, 'price_range') else "Mid-range"
        for p in self.PRICE_RANGES:
            v.append(2.0 if p == price_pref else 0.0)
        age = user_data.get("age", 25)
        user_age_group = "Young" if age < 25 else ("Middle" if age < 45 else "Mature")
        for a in self.AGE_GROUPS:
            v.append(2.0 if a == user_age_group else 0.0)
        v.extend([0.0, 1.0, 2.0])
        liked = preferences.get_liked_notes() if hasattr(preferences, 'get_liked_notes') else []
        disliked = preferences.get_disliked_notes() if hasattr(preferences, 'get_disliked_notes') else []
        for note in ["rose", "jasmine", "vanilla", "sandalwood", "oud", "musk",
                     "bergamot", "patchouli", "cedar", "vetiver", "amber", "lavender"]:
            if note.lower() in [n.lower() for n in liked]:
                v.append(3.0)
            elif note.lower() in [n.lower() for n in disliked]:
                v.append(-2.0)
            else:
                v.append(0.0)
        return np.array(v, dtype=float)

    def _content_based(self, user_data, preferences, n=15, exclude_ids=None):
        if self.perfume_df is None or self.feat_matrix is None:
            return pd.DataFrame()
        user_vec = self.build_user_vector(user_data, preferences)
        if np.sum(np.abs(user_vec)) == 0:
            return self.perfume_df.sample(min(n, len(self.perfume_df)), random_state=42)
        similarities = cosine_similarity(user_vec.reshape(1, -1), self.feat_matrix)[0]
        gender_mask = self._gender_mask(user_data.get("gender", ""),
                                        self.perfume_df["gender_target"].values)
        similarities = similarities * gender_mask.astype(float)
        if exclude_ids:
            for idx, pid in enumerate(self.perfume_df.id.values):
                if pid in exclude_ids:
                    similarities[idx] = -999
        valid_idx = np.where(similarities > 0.1)[0]
        if len(valid_idx) == 0:
            valid_idx = np.argsort(similarities)[::-1]
        else:
            valid_idx = valid_idx[np.argsort(similarities[valid_idx])[::-1]]
        top_indices = valid_idx[:n]
        result = self.perfume_df.iloc[top_indices].copy()
        # FIX: rename column to 'score' (no leading underscore).
        # pandas.itertuples() silently renames columns starting with '_' to
        # positional names like '_7', so getattr(row, "_score") raises AttributeError.
        result["score"] = similarities[top_indices]
        if result.empty:
            return self.perfume_df.sample(min(n, len(self.perfume_df)), random_state=42)
        return result

    def recommend(self, user_id: int, user_data: dict, preferences, n: int = 12):
        """Generate hybrid NCF + content-based recommendations."""
        rated_perfumes = PerfumeRating.query.filter_by(user_id=user_id).all()
        rated_ids = {r.perfume_id for r in rated_perfumes}

        all_perfumes = Perfume.query.all()
        perfume_df = pd.DataFrame([{
            'id': p.id,
            'name': p.name,
            'brand': p.brand,
            'gender_target': p.gender_target,
            'fragrance_family': p.fragrance_family,
            'top_notes': p.top_notes,
            'middle_notes': p.middle_notes,
            'base_notes': p.base_notes,
            'season': p.season,
            'occasion': p.occasion,
            'intensity': p.intensity,
            'longevity': p.longevity,
            'price_range': p.price_range,
            'age_group': p.age_group,
            'avg_rating': p.avg_rating,
        } for p in all_perfumes])

        if perfume_df.empty:
            return []

        self.perfume_df = perfume_df
        self._build_feature_matrix()

        candidate_ids = [pid for pid in perfume_df['id'].values if pid not in rated_ids]

        # --- NCF scoring ---
        ncf_scores = self._ncf_scores(user_id, candidate_ids)

        # --- Content-based scoring ---
        cb_df = self._content_based(user_data, preferences, n=len(perfume_df),
                                    exclude_ids=rated_ids)
        cb_score_map = {}
        # FIX: check for 'score' column (renamed from '_score') and use iterrows()
        # instead of itertuples() to safely access all column names.
        if not cb_df.empty and 'score' in cb_df.columns:
            for _, row in cb_df.iterrows():
                rid: Any = row["id"]
                scr: Any = row["score"]
                cb_score_map[int(rid)] = float(scr)

        # --- Blend scores ---
        if ncf_scores:
            def _normalise(d):
                if not d:
                    return d
                lo, hi = min(d.values()), max(d.values())
                if hi == lo:
                    return {k: 0.5 for k in d}
                return {k: (v - lo) / (hi - lo) for k, v in d.items()}

            ncf_norm = _normalise(ncf_scores)
            cb_norm = _normalise(cb_score_map)

            blended = {}
            for pid in candidate_ids:
                ncf_s = ncf_norm.get(pid, 0.0)
                cb_s = cb_norm.get(pid, 0.0)
                blended[pid] = 0.7 * ncf_s + 0.3 * cb_s

            top_ids = sorted(blended.keys(), key=lambda pid: blended[pid], reverse=True)[:n]
        else:
            # Pure content-based fallback
            # FIX: use iterrows() instead of itertuples() to avoid underscore-column renaming
            top_ids = []
            for _, row in cb_df.iterrows():
                row_id: Any = row["id"]
                pid = int(row_id)
                if pid not in rated_ids:
                    top_ids.append(pid)
                if len(top_ids) >= n:
                    break

        # Fetch ORM objects preserving rank order
        perfume_map = {p.id: p for p in Perfume.query.filter(Perfume.id.in_(top_ids)).all()}
        return [perfume_map[pid] for pid in top_ids if pid in perfume_map]