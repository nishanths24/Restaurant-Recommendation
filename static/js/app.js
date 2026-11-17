// DineMind Client-Side Interactivity Script

document.addEventListener("DOMContentLoaded", function () {
    const citySelect = document.getElementById("city-select");
    const localitySelect = document.getElementById("locality-select");
    const cuisineBadges = document.querySelectorAll(".cuisine-badge");
    const cuisineInput = document.getElementById("cuisines-input");
    const selectedCuisinesContainer = document.getElementById("selected-cuisines-container");

    // Dynamic Locality population when City changes
    if (citySelect && localitySelect && window.CITY_LOCALITIES) {
        citySelect.addEventListener("change", function () {
            const selectedCity = this.value;
            localitySelect.innerHTML = '<option value="">Any Locality in this city</option>';
            
            if (selectedCity && window.CITY_LOCALITIES[selectedCity]) {
                const localities = window.CITY_LOCALITIES[selectedCity];
                localities.forEach(function (loc) {
                    const opt = document.createElement("option");
                    opt.value = loc;
                    opt.textContent = loc;
                    localitySelect.appendChild(opt);
                });
                localitySelect.disabled = false;
            } else {
                localitySelect.disabled = true;
            }
        });
    }

    // Cuisine quick-select badges
    if (cuisineBadges.length > 0 && cuisineInput) {
        let activeCuisines = new Set();
        
        // Initialize from existing input value if any
        if (cuisineInput.value.trim()) {
            cuisineInput.value.split(",").forEach(function (c) {
                const trimmed = c.trim();
                if (trimmed) activeCuisines.add(trimmed);
            });
        }

        function updateCuisineState() {
            cuisineBadges.forEach(function (badge) {
                const val = badge.getAttribute("data-cuisine");
                if (activeCuisines.has(val)) {
                    badge.classList.add("active");
                } else {
                    badge.classList.remove("active");
                }
            });
            cuisineInput.value = Array.from(activeCuisines).join(", ");
        }

        cuisineBadges.forEach(function (badge) {
            badge.addEventListener("click", function () {
                const val = this.getAttribute("data-cuisine");
                if (activeCuisines.has(val)) {
                    activeCuisines.delete(val);
                } else {
                    activeCuisines.add(val);
                }
                updateCuisineState();
            });
        });

        // If user manually types into cuisineInput, synchronize badges
        cuisineInput.addEventListener("input", function () {
            activeCuisines.clear();
            this.value.split(",").forEach(function (c) {
                const trimmed = c.trim();
                if (trimmed) activeCuisines.add(trimmed);
            });
            cuisineBadges.forEach(function (badge) {
                const val = badge.getAttribute("data-cuisine");
                if (activeCuisines.has(val)) {
                    badge.classList.add("active");
                } else {
                    badge.classList.remove("active");
                }
            });
        });

        updateCuisineState();
    }

    // Reset button functionality
    const resetBtn = document.getElementById("btn-reset-filters");
    if (resetBtn) {
        resetBtn.addEventListener("click", function (e) {
            e.preventDefault();
            const form = document.getElementById("preference-form");
            if (form) {
                form.reset();
                if (cuisineInput) cuisineInput.value = "";
                cuisineBadges.forEach(b => b.classList.remove("active"));
                if (localitySelect) {
                    localitySelect.innerHTML = '<option value="">Any Locality</option>';
                    localitySelect.disabled = true;
                }
            }
        });
    }
});
