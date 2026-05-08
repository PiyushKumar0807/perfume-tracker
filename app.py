"""
Flask Perfume Recommendation System
Main application file with authentication, user profiles, and ML recommendations
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from functools import wraps  # FIX: needed for login_required decorator
from sqlalchemy import func, or_
from models import db, User, UserPreference, Perfume, PerfumeRating, NCFRecommender
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize recommender
recommender = NCFRecommender()

# Add custom Jinja2 filters
def from_json_filter(value):
    """Custom Jinja2 filter to parse JSON strings"""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []

app.jinja_env.filters['from_json'] = from_json_filter


def parse_notes_filter(value):
    """JSON array (seed data) or comma-separated text (CSV import) -> list of note strings."""
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    if s.startswith("["):
        try:
            out = json.loads(s)
            return out if isinstance(out, list) else [str(out)]
        except (ValueError, TypeError):
            pass
    return [x.strip() for x in s.split(",") if x.strip()]


app.jinja_env.filters["parse_notes"] = parse_notes_filter

# Create database tables
with app.app_context():
    db.create_all()

# Constants
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)  # FIX: use @wraps(f) to preserve function metadata correctly
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if not isinstance(password, str) or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                flash('Username already exists.', 'danger')
            else:
                flash('Email already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Create user preferences
            preferences = UserPreference(user_id=user.id)
            db.session.add(preferences)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Registration error: {e}")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username, password]):
            flash('Username and password are required.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            user.mark_login()
            db.session.commit()

            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with recommendations"""
    user_id = session['user_id']
    user = db.session.get(User, user_id)  # FIX: Query.get() is deprecated; use db.session.get()

    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Get user preferences
    preferences = UserPreference.query.filter_by(user_id=user_id).first()

    # Get recommendations
    user_data = {
        'age': user.age,
        'gender': user.gender
    }

    recommendations = recommender.recommend(user_id, user_data, preferences, n=12)

    # Get user's ratings for display
    user_ratings = PerfumeRating.query.filter_by(user_id=user_id).all()
    rated_perfumes = {rating.perfume_id: rating for rating in user_ratings}

    # Sort recent ratings by latest rating timestamp and limit to 6
    recent_ratings = sorted(
        user_ratings,
        key=lambda r: r.updated_at or r.created_at,
        reverse=True
    )[:6]

    return render_template('dashboard.html',
                         user=user,
                         recommendations=recommendations,
                         rated_perfumes=rated_perfumes,
                         preferences=preferences,
                         recent_ratings=recent_ratings)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user_id = session['user_id']
    user = db.session.get(User, user_id)  # FIX: use db.session.get()
    preferences = UserPreference.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        # Update basic profile
        user.full_name = request.form.get('full_name', '')
        # FIX: guard against empty/invalid age input before int() conversion
        age_str = request.form.get('age', '25')
        try:
            user.age = int(age_str) if age_str else 25
        except ValueError:
            user.age = 25
        user.gender = request.form.get('gender', '')
        user.skin_tone = request.form.get('skin_tone', '')
        user.location = request.form.get('location', '')
        user.perfume_knowledge = request.form.get('perfume_knowledge', 'Beginner')

        # Update preferences
        preferences.intensity_pref = request.form.get('intensity_pref', 'Moderate')
        preferences.price_range = request.form.get('price_range', 'Mid-range')

        # Handle multi-select fields
        families = request.form.getlist('preferred_families')
        preferences.set_families(families)

        occasions = request.form.getlist('preferred_occasions')
        preferences.set_occasions(occasions)

        seasons = request.form.getlist('preferred_seasons')
        preferences.set_seasons(seasons)

        liked_notes = request.form.getlist('notes_liked')
        preferences.set_liked_notes(liked_notes)

        disliked_notes = request.form.getlist('notes_disliked')
        preferences.set_disliked_notes(disliked_notes)

        user.profile_complete = True
        preferences.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
            print(f"Profile update error: {e}")

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user, preferences=preferences)


# Modal price buckets vs DB strings (CSV uses "Mid-range"; samples use "$50-$100", etc.)
_PRICE_FILTER_TERMS = {
    "$0-$50": ["Budget", "$0", "$50", "0-50"],
    "$50-$100": ["Mid-range", "$50", "$100", "50-100"],
    "$100-$200": ["Mid-range", "Luxury", "$100", "$200", "100-200"],
    "$200+": ["Luxury", "Ultra", "$200", "200+"],
}

_BROWSE_MIN_RESULTS = 4


def _apply_browse_sort(query, sort):
    if sort == "name":
        return query.order_by(Perfume.name.asc(), Perfume.id.asc())
    if sort == "brand":
        return query.order_by(Perfume.brand.asc(), Perfume.id.asc())
    if sort == "rating":
        return query.order_by(
            func.coalesce(Perfume.avg_rating, 0).desc(), Perfume.id.asc()
        )
    if sort == "newest":
        return query.order_by(Perfume.id.desc())
    return query.order_by(Perfume.id.asc())


def _browse_perfumes_query(
    search,
    family,
    brand,
    gender,
    price_range,
    min_rating,
    season,
    occasion,
    sort,
    *,
    use_search,
    use_family,
    use_brand,
    use_gender,
    use_price,
    use_min_rating,
    use_season,
    use_occasion,
):
    """Build filtered query; flags control which user-selected filters are applied."""
    q = Perfume.query

    if use_search and search:
        q = q.filter(
            (Perfume.name.contains(search))
            | (Perfume.brand.contains(search))
            | (Perfume.description.contains(search))
        )

    if use_family and family:
        q = q.filter(Perfume.fragrance_family.contains(family))

    if use_brand and brand:
        q = q.filter(Perfume.brand.contains(brand))

    if use_gender and gender:
        q = q.filter(Perfume.gender_target.contains(gender))

    if use_price and price_range:
        terms = _PRICE_FILTER_TERMS.get(price_range, [price_range])
        clauses = [Perfume.price_range.contains(t) for t in terms]
        q = q.filter(clauses[0] if len(clauses) == 1 else or_(*clauses))

    if use_min_rating and min_rating is not None:
        # CSV rows start unrated (0); still show them so filters are not empty
        q = q.filter(
            (Perfume.total_ratings == 0)
            | (func.coalesce(Perfume.avg_rating, 0) >= min_rating)
        )

    if use_season and season:
        sn = func.coalesce(func.trim(Perfume.season), "")
        q = q.filter((sn == "") | Perfume.season.contains(season))

    if use_occasion and occasion:
        oc = func.coalesce(func.trim(Perfume.occasion), "")
        q = q.filter((oc == "") | Perfume.occasion.contains(occasion))

    return _apply_browse_sort(q, sort)


@app.route("/perfumes")
@login_required
def perfumes():
    """Browse all perfumes; relax filters if needed so at least a few results appear."""
    page = request.args.get("page", 1, type=int)
    if page is None or page < 1:
        page = 1
    per_page = 20

    search = request.args.get("search", "")
    family = request.args.get("family", "")
    brand = request.args.get("brand", "")
    gender = request.args.get("gender", "")
    sort = request.args.get("sort", "") or ""
    price_range = request.args.get("price_range", "")
    min_rating = request.args.get("min_rating", type=float)
    season = request.args.get("season", "")
    occasion = request.args.get("occasion", "")

    use = {
        "min_rating": min_rating is not None,
        "season": bool(season),
        "occasion": bool(occasion),
        "price": bool(price_range),
        "gender": bool(gender),
        "family": bool(family),
        "brand": bool(brand),
        "search": bool(search),
    }
    initial_use = dict(use)
    relax_order = [
        "min_rating",
        "season",
        "occasion",
        "price",
        "gender",
        "family",
        "brand",
        "search",
    ]

    total_catalog = db.session.query(func.count(Perfume.id)).scalar() or 0
    target_floor = min(_BROWSE_MIN_RESULTS, total_catalog)

    def build():
        return _browse_perfumes_query(
            search,
            family,
            brand,
            gender,
            price_range,
            min_rating,
            season,
            occasion,
            sort,
            use_search=use["search"],
            use_family=use["family"],
            use_brand=use["brand"],
            use_gender=use["gender"],
            use_price=use["price"],
            use_min_rating=use["min_rating"],
            use_season=use["season"],
            use_occasion=use["occasion"],
        )

    count = build().count()
    for key in relax_order:
        if count >= target_floor:
            break
        if not use.get(key):
            continue
        use[key] = False
        count = build().count()

    query = build()
    perfumes_page = query.paginate(page=page, per_page=per_page, error_out=False)  # FIX: renamed to avoid shadowing the 'perfumes' function

    filters_relaxed = use != initial_use

    cp = perfumes_page.page
    tp = perfumes_page.pages or 1
    paginate_from = max(1, cp - 2)
    paginate_to_excl = min(tp + 1, cp + 3)
    pagination_pages = list(range(paginate_from, paginate_to_excl))

    perfumes_query_args = {
        k: request.args.get(k) for k in request.args if k != "page"
    }

    active_filters = []
    if search:
        active_filters.append(("search", "Search", search))
    if family:
        active_filters.append(("family", "Family", family))
    if brand:
        active_filters.append(("brand", "Brand", brand))
    if gender:
        active_filters.append(("gender", "Gender", gender))
    if price_range:
        active_filters.append(("price_range", "Price", price_range))
    if min_rating is not None:
        active_filters.append(("min_rating", "Min rating", str(min_rating)))
    if season:
        active_filters.append(("season", "Season", season))
    if occasion:
        active_filters.append(("occasion", "Occasion", occasion))
    if sort:
        active_filters.append(("sort", "Sort", sort))

    return render_template(
        "perfumes.html",
        perfumes=perfumes_page,
        perfumes_query_args=perfumes_query_args,
        search=search,
        selected_family=family,
        selected_brand=brand,
        selected_gender=gender,
        active_filters=active_filters,
        total_count=perfumes_page.total,
        total_pages=perfumes_page.pages,
        current_page=perfumes_page.page,
        pagination_pages=pagination_pages,
        filters_relaxed=filters_relaxed,
        browse_min_results=_BROWSE_MIN_RESULTS,
    )

@app.route('/perfume/<int:perfume_id>')
@login_required
def perfume_detail(perfume_id):
    """View perfume details and rate it"""
    perfume = db.session.get(Perfume, perfume_id)  # FIX: use db.session.get(); add 404 manually
    if perfume is None:
        from flask import abort
        abort(404)
    user_id = session['user_id']

    # Get user's rating if exists
    user_rating = PerfumeRating.query.filter_by(
        user_id=user_id, perfume_id=perfume_id
    ).first()

    # Get similar perfumes
    similar_perfumes = Perfume.query.filter(
        Perfume.fragrance_family == perfume.fragrance_family,
        Perfume.id != perfume_id
    ).limit(6).all()

    return render_template('perfume_detail.html',
                         perfume=perfume,
                         user_rating=user_rating,
                         similar_perfumes=similar_perfumes)

@app.route('/rate', methods=['POST'])
@login_required
def rate_perfume():
    """Rate a perfume (handles both AJAX and regular form submissions)"""
    user_id = session['user_id']
    perfume_id = int(request.form.get('perfume_id', 0))
    rating = float(request.form.get('rating', 0))
    review = request.form.get('comment', '')
    used_before = 'used_before' in request.form

    # Check if this is an AJAX request
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request - return JSON
        if not perfume_id or not (0.5 <= rating <= 5.0):
            return jsonify({'success': False, 'message': 'Invalid rating data'})

        # Check if rating already exists
        existing_rating = PerfumeRating.query.filter_by(
            user_id=user_id, perfume_id=perfume_id
        ).first()

        try:
            if existing_rating:
                existing_rating.rating = rating
                existing_rating.review = review
                existing_rating.updated_at = datetime.utcnow()
            else:
                new_rating = PerfumeRating(
                    user_id=user_id,
                    perfume_id=perfume_id,
                    rating=rating,
                    review=review
                )
                db.session.add(new_rating)

            # Update perfume stats
            perfume = db.session.get(Perfume, perfume_id)  # FIX: use db.session.get()
            if perfume:
                perfume.update_stats()

            db.session.commit()
            return jsonify({'success': True, 'message': 'Rating saved successfully!'})

        except Exception as e:
            db.session.rollback()
            print(f"Rating error: {e}")
            return jsonify({'success': False, 'message': 'An error occurred while saving your rating.'})

    else:
        # Regular form submission - redirect back
        if not (0.5 <= rating <= 5.0):
            flash('Rating must be between 0.5 and 5.0.', 'danger')
            return redirect(url_for('perfume_detail', perfume_id=perfume_id))

        # Check if rating already exists
        existing_rating = PerfumeRating.query.filter_by(
            user_id=user_id, perfume_id=perfume_id
        ).first()

        try:
            if existing_rating:
                existing_rating.rating = rating
                existing_rating.review = review
                existing_rating.used_before = used_before
                existing_rating.updated_at = datetime.utcnow()
            else:
                new_rating = PerfumeRating(
                    user_id=user_id,
                    perfume_id=perfume_id,
                    rating=rating,
                    review=review,
                    used_before=used_before
                )
                db.session.add(new_rating)

            # Update perfume stats
            perfume = db.session.get(Perfume, perfume_id)  # FIX: use db.session.get()
            if perfume:
                perfume.update_stats()

            db.session.commit()
            flash('Rating saved successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving your rating.', 'danger')
            print(f"Rating error: {e}")

        # Check if request came from dashboard (via referer)
        referer = request.headers.get('Referer', '')
        if 'dashboard' in referer:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('perfume_detail', perfume_id=perfume_id))

@app.route('/api/recommendations')
@login_required
def api_recommendations():
    """API endpoint for getting recommendations"""
    user_id = session['user_id']
    user = db.session.get(User, user_id)  # FIX: use db.session.get()
    preferences = UserPreference.query.filter_by(user_id=user_id).first()

    user_data = {
        'age': user.age,
        'gender': user.gender
    }

    recommendations = recommender.recommend(user_id, user_data, preferences, n=12)

    # Convert to JSON-serializable format
    recs_data = []
    for perf in recommendations:
        recs_data.append({
            'id': perf.id,
            'name': perf.name,
            'brand': perf.brand,
            'fragrance_family': perf.fragrance_family,
            'description': perf.description[:100] + '...' if len(perf.description) > 100 else perf.description,
            'avg_rating': round(perf.avg_rating, 1) if perf.avg_rating else 0,
            'total_ratings': perf.total_ratings
        })

    return jsonify({'recommendations': recs_data})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)