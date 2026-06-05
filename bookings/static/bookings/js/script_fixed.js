// Narrative Studio — Booking JS

(function () {
    let currentStep = 1;
    const totalSteps = 5;

    // ── Step Navigation ──────────────────────────────────────────
    function showStep(step) {
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        const el = document.getElementById(`step-${step}`);
        if (el) el.classList.add('active');

        const prev = document.getElementById('prev');
        const next = document.getElementById('next');
        if (prev) prev.style.display = step > 1 ? 'inline-flex' : 'none';
        if (next) next.style.display = step < totalSteps ? 'inline-flex' : 'none';

        // Update progress dots
        for (let i = 1; i <= totalSteps; i++) {
            const dot = document.getElementById(`prog-${i}`);
            if (!dot) continue;
            dot.classList.remove('active', 'completed');
            if (i < step) dot.classList.add('completed');
            else if (i === step) dot.classList.add('active');
        }
    }

    function checkTimeSlotStatus() {
        const timeSelect = document.getElementById('time');
        const timeWarning = document.getElementById('time-warning');
        const nextBtn = document.getElementById('next');
        const selectedTime = timeSelect?.value;
        
        if (!selectedTime) {
            if (timeWarning) timeWarning.style.display = 'none';
            if (nextBtn) nextBtn.disabled = false;
            return;
        }
        
        const timeOption = document.querySelector(`#time option[value="${selectedTime}"]`);
        
        if (timeOption?.disabled) {
            if (timeWarning) timeWarning.style.display = 'block';
            if (nextBtn) nextBtn.disabled = true;
        } else {
            if (timeWarning) timeWarning.style.display = 'none';
            if (nextBtn) nextBtn.disabled = false;
        }
    }

    function validateStep(step) {
        if (step === 1) {
            const date = document.getElementById('date')?.value;
            const time = document.getElementById('time')?.value;
            if (!date || !time) {
                alert('Please select both date and time');
                return false;
            }
        }
        if (step === 2) {
            const name = document.getElementById('name')?.value;
            const email = document.getElementById('email')?.value;
            const phone = document.getElementById('phone')?.value;
            const birthday = document.getElementById('birthday')?.value;
            
            if (!name?.trim()) {
                alert('Please enter your full name');
                return false;
            }
            if (!email?.trim() || !email.includes('@')) {
                alert('Please enter a valid email address');
                return false;
            }
            if (!phone?.trim()) {
                alert('Please enter your phone number');
                return false;
            }
            if (!birthday) {
                alert('Please select your birthday');
                return false;
            }
        }
        if (step === 3) {
            const selectedAddons = document.querySelectorAll('.addon-item.selected');
            const pets = document.getElementById('pets')?.value;
            
            if (selectedAddons.length === 0) {
                alert('Please select at least one add-on');
                return false;
            }
            if (pets === null || pets === undefined || pets === '') {
                alert('Please specify number of pets (0 if none)');
                return false;
            }
        }
        if (step === 4) {
            const payment = document.getElementById('payment-input')?.value;
            if (!payment) {
                alert('Please select a payment method');
                return false;
            }
        }
        if (step === 5) {
            const terms = document.getElementById('terms')?.checked;
            if (!terms) {
                alert('Please accept the policies and guidelines to proceed');
                return false;
            }
        }
        return true;
    }

    // ── Price Calculation ─────────────────────────────────────────
    function calculateTotal() {
        const packageSelect = document.getElementById('package');
        const petInput = document.getElementById('pets');
        const totalEl = document.getElementById('total');
        const summaryAddons = document.getElementById('summary-addons');
        const summaryPets = document.getElementById('summary-pets');
        const summaryPackage = document.getElementById('summary-package');

        let base = 0;
        if (packageSelect && packageSelect.selectedOptions[0]) {
            const opt = packageSelect.selectedOptions[0];
            base = parseFloat(opt.dataset.price) || 0;
            if (summaryPackage) summaryPackage.textContent = opt.text.split('—')[0].trim();
        }

        let addonsTotal = 0;
        document.querySelectorAll('.addon-item.selected').forEach(item => {
            addonsTotal += parseFloat(item.dataset.price) || 0;
        });

        const pets = Math.max(0, parseInt(petInput?.value) || 0);
        const petFee = pets * 100;

        const total = base + addonsTotal + petFee;

        if (totalEl) {
            totalEl.classList.add('price-pulse');
            totalEl.textContent = `₱${total.toLocaleString()}`;
            setTimeout(() => totalEl.classList.remove('price-pulse'), 400);
        }
        if (summaryAddons) summaryAddons.textContent = `₱${addonsTotal.toLocaleString()}`;
        if (summaryPets) summaryPets.textContent = `₱${petFee.toLocaleString()}`;
    }

    // ── Summary Date/Time ─────────────────────────────────────────
    function updateSummaryDateTime() {
        const dateEl = document.getElementById('summary-date');
        const timeEl = document.getElementById('summary-time');
        const dateInput = document.getElementById('date');
        const timeInput = document.getElementById('time');
        if (dateEl && dateInput?.value) dateEl.textContent = dateInput.value;
        if (timeEl && timeInput?.value) timeEl.textContent = timeInput.value;
    }

    // ── Time Slot Availability ────────────────────────────────────
    function updateTimeSlotAvailability() {
        const dateInput = document.getElementById('date');
        const packageSelect = document.getElementById('package');
        const timeSelect = document.getElementById('time');
        
        if (!dateInput?.value || !packageSelect?.value || !timeSelect) {
            return;
        }
        
        fetch(`/api/booked-times/?date=${dateInput.value}&package=${packageSelect.value}`)
            .then(res => res.json())
            .then(data => {
                const bookedTimes = data.booked_times || [];
                timeSelect.querySelectorAll('option').forEach(option => {
                    if (option.value === '') return;
                    const isBooked = bookedTimes.includes(option.value);
                    option.disabled = isBooked;
                    const baseText = option.textContent.split(' (')[0];
                    option.textContent = baseText + (isBooked ? ' (Booked)' : '');
                });
                checkTimeSlotStatus();
            })
            .catch(err => console.error('Error fetching booked times:', err));
    }

    // ── Init ──────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        // Hamburger menu functionality
        const hamburger = document.getElementById('hamburger');
        const navMenu = document.getElementById('nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                navMenu.classList.toggle('active');
            });
            
            navMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                });
            });
            
            document.addEventListener('click', (e) => {
                if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                }
            });
        }
        
        // Booking form functionality
        if (!document.getElementById('booking-form')) return;

        showStep(currentStep);
        calculateTotal();

        document.getElementById('next')?.addEventListener('click', () => {
            if (validateStep(currentStep) && currentStep < totalSteps) { 
                currentStep++; 
                showStep(currentStep); 
            }
        });

        document.getElementById('prev')?.addEventListener('click', () => {
            if (currentStep > 1) { currentStep--; showStep(currentStep); }
        });

        // Package change
        document.getElementById('package')?.addEventListener('change', () => {
            calculateTotal();
            updateTimeSlotAvailability();
        });

        // Pets
        document.getElementById('pets')?.addEventListener('input', calculateTotal);

        // Date / Time summary and availability
        document.getElementById('date')?.addEventListener('change', () => {
            updateSummaryDateTime();
            updateTimeSlotAvailability();
        });

        document.getElementById('time')?.addEventListener('change', () => {
            updateSummaryDateTime();
            checkTimeSlotStatus();
        });

        // Addon toggle
        document.querySelectorAll('.addon-item').forEach(item => {
            item.addEventListener('click', () => {
                item.classList.toggle('selected');
                const cb = item.querySelector('input[type="checkbox"]');
                if (cb) cb.checked = item.classList.contains('selected');
                calculateTotal();
            });
        });

        // Solid backdrop swatches
        document.querySelectorAll('.solid-backdrop-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.solid-backdrop-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                const input = document.getElementById('backdrop-input');
                if (input) input.value = item.dataset.id;
            });
        });

        // Creative backdrop swatches
        document.querySelectorAll('.creative-backdrop-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.creative-backdrop-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                const input = document.getElementById('creative-backdrop-input');
                if (input) input.value = item.dataset.id;
            });
        });

        // Payment options
        document.querySelectorAll('.payment-option').forEach(opt => {
            opt.addEventListener('click', () => {
                document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
                opt.classList.add('selected');
                const input = document.getElementById('payment-input');
                if (input) input.value = opt.dataset.value;
            });
        });

        // Terms & Conditions checkbox
        const termsCheckboxItem = document.querySelector('.terms-checkbox-item');
        const termsCheckbox = document.getElementById('terms');
        if (termsCheckboxItem && termsCheckbox) {
            termsCheckboxItem.addEventListener('click', (e) => {
                if (e.target === termsCheckbox) return;
                
                e.stopPropagation();
                termsCheckbox.checked = !termsCheckbox.checked;
                termsCheckboxItem.classList.toggle('selected', termsCheckbox.checked);
            });
            
            termsCheckbox.addEventListener('click', () => {
                termsCheckboxItem.classList.toggle('selected', termsCheckbox.checked);
            });
        }

    });
})();
