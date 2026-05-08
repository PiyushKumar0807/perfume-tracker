// PerfumeAI JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Rating system
    initializeRatingSystem();

    // Search functionality
    initializeSearch();

    // Profile completion progress
    updateProfileProgress();

    // Enhanced card animations with stagger
    const cards = document.querySelectorAll(".perfume-card");
    cards.forEach((card, i) => {
        card.style.animationDelay = `${i * 0.1}s`;
        card.classList.add('fade-in-up');
    });

    // Scroll to top button with smooth animation
    const scrollTopBtn = document.getElementById("scrollTopBtn");
    if (scrollTopBtn) {
        window.addEventListener("scroll", () => {
            scrollTopBtn.style.display = window.scrollY > 220 ? "block" : "none";
        });
        scrollTopBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    }

    // Add floating animation to feature icons
    const featureIcons = document.querySelectorAll('.feature-icon');
    featureIcons.forEach((icon, index) => {
        icon.style.animationDelay = `${index * 0.5}s`;
        icon.classList.add('floating');
    });

    // Enhanced button hover effects
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const hero = document.querySelector('.hero-section');
        if (hero) {
            const scrolled = window.pageYOffset;
            hero.style.backgroundPositionY = -(scrolled * 0.5) + 'px';
        }
    });

    // Add loading animation for perfume cards
    addLoadingAnimation();

    // Initialize particle effect for hero section
    createParticles();
});

function addLoadingAnimation() {
    const cards = document.querySelectorAll('.perfume-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const img = this.querySelector('img');
            if (img) {
                img.style.transform = 'scale(1.1)';
                img.style.transition = 'transform 0.3s ease';
            }
        });
        card.addEventListener('mouseleave', function() {
            const img = this.querySelector('img');
            if (img) {
                img.style.transform = 'scale(1)';
            }
        });
    });
}

function createParticles() {
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;

    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        heroSection.appendChild(particle);
    }
}

function initializeRatingSystem() {
    // Handle star rating clicks
    document.querySelectorAll('.rating-stars input').forEach(function(input) {
        input.addEventListener('change', function() {
            var rating = this.value;
            var stars = this.parentElement.querySelectorAll('label');

            stars.forEach(function(star, index) {
                if (index < rating) {
                    star.classList.add('text-warning');
                    star.classList.remove('text-muted');
                } else {
                    star.classList.remove('text-warning');
                    star.classList.add('text-muted');
                }
            });
        });
    });
}

function initializeSearch() {
    // Debounced search for perfume browsing
    var searchTimeout;
    var searchInput = document.getElementById('search-input');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(searchInput.value);
            }, 300);
        });
    }
}

function performSearch(query) {
    // Update URL with search parameters
    var url = new URL(window.location);
    if (query) {
        url.searchParams.set('search', query);
    } else {
        url.searchParams.delete('search');
    }

    // Reload page with new search parameters
    window.location.href = url.toString();
}

function updateProfileProgress() {
    // Calculate profile completion percentage
    var profileFields = [
        'full_name', 'age', 'gender', 'skin_tone', 'location', 'perfume_knowledge'
    ];

    var preferencesFields = [
        'preferred_families', 'preferred_seasons', 'preferred_occasions',
        'intensity_pref', 'price_range', 'notes_liked', 'notes_disliked'
    ];

    var completedFields = 0;
    var totalFields = profileFields.length + preferencesFields.length;

    // Check profile fields
    profileFields.forEach(function(field) {
        var element = document.getElementById(field);
        if (element && element.value && element.value.trim() !== '') {
            completedFields++;
        }
    });

    // Check preferences (checkboxes)
    preferencesFields.forEach(function(field) {
        var checkboxes = document.querySelectorAll('input[name="' + field + '"]:checked');
        if (checkboxes.length > 0) {
            completedFields++;
        }
    });

    var progressPercentage = Math.round((completedFields / totalFields) * 100);

    // Update progress bar if it exists
    var progressBar = document.getElementById('profile-progress');
    if (progressBar) {
        progressBar.style.width = progressPercentage + '%';
        progressBar.setAttribute('aria-valuenow', progressPercentage);
        progressBar.textContent = progressPercentage + '%';
    }

    // Update progress text
    var progressText = document.getElementById('profile-progress-text');
    if (progressText) {
        progressText.textContent = 'Profile ' + progressPercentage + '% complete';
    }
}

// Quick rating function for dashboard
function quickRate(perfumeId, perfumeName) {
    // This function is defined in the dashboard template
    // It's here for reference and potential reuse
    console.log('Quick rating for:', perfumeId, perfumeName);
}

// AJAX function for refreshing recommendations
function refreshRecommendations() {
    var button = event.target.closest('button');
    var originalHtml = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;

    fetch('/api/recommendations')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            updateRecommendationsDisplay(data.recommendations);
        })
        .catch(function(error) {
            console.error('Error refreshing recommendations:', error);
            showAlert('Error refreshing recommendations. Please try again.', 'danger');
        })
        .finally(function() {
            button.innerHTML = originalHtml;
            button.disabled = false;
        });
}

function updateRecommendationsDisplay(recommendations) {
    var container = document.getElementById('recommendations-container');
    if (!container) return;

    if (recommendations && recommendations.length > 0) {
        var html = '<div class="row g-4">';
        recommendations.forEach(function(perfume) {
            html += `
                <div class="col-md-6 col-lg-4">
                    <div class="card h-100 perfume-card">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-1">${escapeHtml(perfume.name)}</h6>
                                ${perfume.avg_rating ? `<span class="badge bg-warning text-dark"><i class="fas fa-star"></i> ${perfume.avg_rating}</span>` : ''}
                            </div>
                            <p class="text-muted small mb-2">${escapeHtml(perfume.brand)}</p>
                            <p class="text-muted small mb-2">${escapeHtml(perfume.fragrance_family)}</p>
                            <p class="card-text small flex-grow-1">${escapeHtml(perfume.description)}</p>
                            <div class="mt-auto">
                                <a href="/perfume/${perfume.id}" class="btn btn-primary btn-sm flex-fill">
                                    <i class="fas fa-eye"></i> View
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    } else {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-magic fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No recommendations yet</h5>
                <p class="text-muted">Complete your profile and rate some perfumes to get personalized recommendations!</p>
                <a href="/profile" class="btn btn-primary">
                    <i class="fas fa-user-edit"></i> Complete Profile
                </a>
            </div>
        `;
    }
}

function showAlert(message, type) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    var container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return (text || '').replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Password confirmation validation
function validatePasswordConfirm() {
    var password = document.getElementById('password');
    var confirmPassword = document.getElementById('confirm_password');

    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity('Passwords do not match');
        } else {
            confirmPassword.setCustomValidity('');
        }
    }
}

// Attach password validation to form
document.addEventListener('DOMContentLoaded', function() {
    var confirmPasswordField = document.getElementById('confirm_password');
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', validatePasswordConfirm);
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Loading state for forms
function setFormLoading(form, loading) {
    var submitBtn = form.querySelector('button[type="submit"]');
    var inputs = form.querySelectorAll('input, select, textarea, button');

    if (loading) {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
        inputs.forEach(function(input) {
            input.disabled = true;
        });
    } else {
        if (submitBtn) {
            submitBtn.disabled = false;
            // Reset button text (this would need to be more sophisticated in a real app)
        }
        inputs.forEach(function(input) {
            input.disabled = false;
        });
    }
}

// Auto-save profile drafts (optional enhancement)
var profileAutoSaveTimeout;
function autoSaveProfile() {
    clearTimeout(profileAutoSaveTimeout);
    profileAutoSaveTimeout = setTimeout(function() {
        // In a real implementation, this would save to localStorage or send to server
        console.log('Auto-saving profile draft...');
    }, 2000);
}

// Attach auto-save to profile form
document.addEventListener('DOMContentLoaded', function() {
    var profileForm = document.querySelector('form[action*="profile"]');
    if (profileForm) {
        var inputs = profileForm.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('input', autoSaveProfile);
        });
    }
});