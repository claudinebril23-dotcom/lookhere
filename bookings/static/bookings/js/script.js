// Narrative Studio — Booking JS

(function () {
    let currentStep = 1;
    const totalSteps = 3;
    let selectedDate = null;
    let selectedTime = null;
    let isTimeBooked = false;
    let currentDate = new Date();

    // All possible time slots — 9:00 AM to 6:00 PM (hourly)
    const allTimeSlots = [
        '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
        '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM'
    ];

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function formatDateDisplay(date) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];

        const currentMonthEl = document.getElementById('current-month');
        if (currentMonthEl) {
            currentMonthEl.textContent = `${monthNames[month]} ${year}`;
        }

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const daysContainer = document.getElementById('date-picker-days');
        if (!daysContainer) return;

        daysContainer.innerHTML = '';

        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'date-day empty';
            daysContainer.appendChild(emptyDay);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayEl = document.createElement('div');
            dayEl.className = 'date-day';
            dayEl.textContent = day;

            const cellDate = new Date(year, month, day);
            cellDate.setHours(0, 0, 0, 0);

            if (cellDate < today) {
                dayEl.classList.add('disabled');
            } else {
                dayEl.addEventListener('click', () => selectDate(cellDate));
            }

            if (cellDate.getTime() === today.getTime()) {
                dayEl.classList.add('today');
            }

            if (selectedDate && cellDate.getTime() === selectedDate.getTime()) {
                dayEl.classList.add('selected');
            }

            daysContainer.appendChild(dayEl);
        }
    }

    function selectDate(date) {
        selectedDate = date;
        selectedTime = null;
        isTimeBooked = false;

        const dateInput = document.getElementById('date');
        const timeInput = document.getElementById('time');
        const warningBox = document.getElementById('time-warning');
        const nextBtn = document.getElementById('next');
        const message = document.getElementById('time-slot-message');

        if (dateInput) dateInput.value = formatDate(date);
        if (timeInput) timeInput.value = '';
        if (warningBox) warningBox.style.display = 'none';
        if (message) message.style.display = 'none';
        if (nextBtn && currentStep === 1) {
            nextBtn.disabled = true;
            nextBtn.style.opacity = '0.5';
            nextBtn.style.cursor = 'not-allowed';
        }

        renderCalendar();
        updateSummaryDateTime();
        loadTimeSlots();
    }

    async function loadTimeSlots() {
        if (!selectedDate) return;

        const container = document.getElementById('time-slots-container');
        const message = document.getElementById('time-slot-message');
        const loading = document.getElementById('time-slot-loading');

        if (message) message.style.display = 'none';
        if (container) container.style.display = 'none';
        if (loading) loading.style.display = 'flex';

        try {
            const dateStr = formatDate(selectedDate);
            const response = await fetch(`/api/booked-times/?date=${dateStr}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            const bookedTimes = data.booked_times || [];

            console.log('Loaded booked times:', bookedTimes);

            renderTimeSlots(bookedTimes);

            if (loading) loading.style.display = 'none';
            if (container) container.style.display = 'grid';

        } catch (error) {
            console.error('Error loading time slots:', error);
            if (loading) loading.style.display = 'none';
            if (message) {
                message.textContent = 'Error loading time slots. Please try again.';
                message.style.display = 'block';
                message.style.background = 'rgba(255, 107, 107, 0.1)';
                message.style.borderColor = 'rgba(255, 107, 107, 0.3)';
            }
        }
    }

    function renderTimeSlots(bookedTimes) {
        const container = document.getElementById('time-slots-container');
        const timeInput = document.getElementById('time');
        const warningBox = document.getElementById('time-warning');
        const nextBtn = document.getElementById('next');

        if (!container) return;

        container.innerHTML = '';
        selectedTime = null;
        isTimeBooked = false;
        if (timeInput) timeInput.value = '';
        if (warningBox) warningBox.style.display = 'none';
        if (nextBtn && currentStep === 1) {
            nextBtn.disabled = true;
            nextBtn.style.opacity = '0.5';
            nextBtn.style.cursor = 'not-allowed';
        }

        // Normalise booked times to lowercase for reliable comparison
        const bookedNormalised = bookedTimes.map(t => t.trim().toLowerCase());

        // Check if selected date is today
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const isToday = selectedDate && selectedDate.getTime() === today.getTime();
        const currentHour = new Date().getHours();

        allTimeSlots.forEach(function (time) {
            const slot = document.createElement('button');
            slot.type = 'button';
            slot.className = 'time-slot-btn';
            slot.textContent = time;

            const booked = bookedNormalised.includes(time.trim().toLowerCase());

            // Check if time has passed (only for today)
            let isPastTime = false;
            if (isToday) {
                // Convert time slot to 24-hour format for comparison
                const timeMatch = time.match(/(\d+):(\d+)\s*(AM|PM)/i);
                if (timeMatch) {
                    let hour = parseInt(timeMatch[1]);
                    const period = timeMatch[3].toUpperCase();

                    // Convert to 24-hour format
                    if (period === 'PM' && hour !== 12) {
                        hour += 12;
                    } else if (period === 'AM' && hour === 12) {
                        hour = 0;
                    }

                    // Time has passed if the slot hour is less than or equal to current hour
                    isPastTime = hour <= currentHour;
                }
            }

            console.log('Time ' + time + ': ' + (booked ? 'BOOKED' : isPastTime ? 'PAST' : 'Available'));

            if (booked) {
                slot.classList.add('booked');
                slot.setAttribute('title', 'This slot is already booked');
                slot.setAttribute('aria-disabled', 'true');
            } else if (isPastTime) {
                slot.classList.add('booked'); // Use same styling as booked
                slot.setAttribute('title', 'This time has already passed');
                slot.setAttribute('aria-disabled', 'true');
            }

            slot.addEventListener('click', function () {
                handleTimeSlotClick(time, booked || isPastTime, slot);
            });

            container.appendChild(slot);
        });
    }

    function handleTimeSlotClick(time, booked, slotElement) {
        const timeInput = document.getElementById('time');
        const warningBox = document.getElementById('time-warning');
        const nextBtn = document.getElementById('next');

        console.log('Clicked: ' + time + ', Booked/Unavailable: ' + booked);

        if (booked) {
            // Check if it's a past time or already booked
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const isToday = selectedDate && selectedDate.getTime() === today.getTime();
            const currentHour = new Date().getHours();

            let isPastTime = false;
            if (isToday) {
                const timeMatch = time.match(/(\d+):(\d+)\s*(AM|PM)/i);
                if (timeMatch) {
                    let hour = parseInt(timeMatch[1]);
                    const period = timeMatch[3].toUpperCase();
                    if (period === 'PM' && hour !== 12) {
                        hour += 12;
                    } else if (period === 'AM' && hour === 12) {
                        hour = 0;
                    }
                    isPastTime = hour <= currentHour;
                }
            }

            if (warningBox) {
                if (isPastTime) {
                    warningBox.innerHTML = '<div style="display:flex;align-items:flex-start;gap:1rem;"><div style="font-size:1.5rem;">⏰</div><div><h3 style="margin:0 0 0.5rem 0;color:#EF4444;">Time Has Passed</h3><p style="margin:0;color:#991B1B;font-size:0.95rem;">This time slot has already passed today. Please select a future time slot.</p></div></div>';
                } else {
                    warningBox.innerHTML = '<div style="display:flex;align-items:flex-start;gap:1rem;"><div style="font-size:1.5rem;">⚠️</div><div><h3 style="margin:0 0 0.5rem 0;color:#EF4444;">Time Slot Already Booked</h3><p style="margin:0;color:#991B1B;font-size:0.95rem;">The time you selected is already booked. Please pick another time to proceed.</p></div></div>';
                }
                warningBox.style.display = 'block';
            }
            isTimeBooked = true;
            selectedTime = null;
            if (timeInput) timeInput.value = '';
            if (nextBtn && currentStep === 1) {
                nextBtn.disabled = true;
                nextBtn.style.opacity = '0.5';
                nextBtn.style.cursor = 'not-allowed';
            }
            return;
        }

        // Available slot — select it
        document.querySelectorAll('.time-slot-btn').forEach(function (btn) {
            btn.classList.remove('selected');
        });
        slotElement.classList.add('selected');

        selectedTime = time;
        isTimeBooked = false;
        if (timeInput) timeInput.value = time;
        if (warningBox) warningBox.style.display = 'none';

        // Enable Next button
        if (nextBtn && currentStep === 1) {
            nextBtn.disabled = false;
            nextBtn.style.opacity = '1';
            nextBtn.style.cursor = 'pointer';
        }

        updateSummaryDateTime();
    }

    function showStep(step) {
        document.querySelectorAll('.step').forEach(function (s) {
            s.classList.remove('active');
        });
        const el = document.getElementById('step-' + step);
        if (el) el.classList.add('active');

        const prev = document.getElementById('prev');
        const next = document.getElementById('next');
        if (prev) prev.style.display = step > 1 ? 'inline-flex' : 'none';
        if (next) next.style.display = step < totalSteps ? 'inline-flex' : 'none';

        for (let i = 1; i <= totalSteps; i++) {
            const dot = document.getElementById('prog-' + i);
            if (!dot) continue;
            dot.classList.remove('active', 'completed');
            if (i < step) dot.classList.add('completed');
            else if (i === step) dot.classList.add('active');
        }
    }

    function validateStep(step) {
        if (step === 1) {
            const date = document.getElementById('date') ? document.getElementById('date').value : '';
            const time = document.getElementById('time') ? document.getElementById('time').value : '';

            if (!date) {
                showValidationError('Please select a date to continue.');
                return false;
            }
            if (!time) {
                showValidationError('Please select a time slot to continue.');
                return false;
            }
            if (isTimeBooked) {
                showValidationError('The selected time slot is already booked. Please choose another.');
                return false;
            }
        }
        if (step === 2) {
            const nameEl = document.getElementById('name');
            const emailEl = document.getElementById('email');
            const phoneEl = document.getElementById('phone');
            const name = nameEl ? nameEl.value : '';
            const email = emailEl ? emailEl.value : '';
            const phone = phoneEl ? phoneEl.value : '';

            if (!name.trim()) {
                showValidationError('Please enter your full name');
                return false;
            }
            if (!email.trim() || !email.includes('@')) {
                showValidationError('Please enter a valid email address');
                return false;
            }
            if (!phone.trim()) {
                showValidationError('Please enter your phone number.');
                return false;
            }
        }
        if (step === 3) {
            const selectedAddons = document.querySelectorAll('.addon-item.selected');
            const backdropEl = document.getElementById('backdrop-input');
            const paymentEl = document.getElementById('payment-input');
            const recaptchaEl = document.getElementById('recaptcha-agree');
            const selectedBackdrop = backdropEl ? backdropEl.value : '';
            const payment = paymentEl ? paymentEl.value : '';
            const recaptchaAgree = recaptchaEl ? recaptchaEl.checked : false;

            if (!selectedBackdrop) {
                showValidationError('Please select a backdrop');
                return false;
            }
            if (selectedAddons.length === 0) {
                showValidationError('Please select at least one add-on');
                return false;
            }
            if (!recaptchaAgree) {
                showValidationError('Please agree to the terms to proceed');
                return false;
            }
        }
        return true;
    }

    function showValidationError(message) {
        const warningBox = document.getElementById('time-warning');
        if (warningBox) {
            warningBox.innerHTML = '<div style="display:flex;align-items:flex-start;gap:1rem;"><div style="font-size:1.5rem;">⚠️</div><div><h3 style="margin:0 0 0.5rem 0;color:#EF4444;">Validation Error</h3><p style="margin:0;color:#991B1B;font-size:0.95rem;">' + message + '</p></div></div>';
            warningBox.style.display = 'block';
            warningBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        console.warn('Validation Error:', message);
    }

    function calculateTotal() {
        const packageInput = document.getElementById('package-input');
        const totalEl = document.getElementById('total');
        const summaryAddons = document.getElementById('summary-addons');
        const summaryPackage = document.getElementById('summary-package');

        let base = 0;
        if (packageInput && packageInput.value) {
            const packageId = packageInput.value;
            const packageName = packageInput.dataset.packageName || '—';
            const packagePrice = parseFloat(packageInput.dataset.packagePrice) || 0;
            base = packagePrice;
            if (summaryPackage) summaryPackage.textContent = packageName;
        }

        let addonsTotal = 0;
        document.querySelectorAll('.addon-item.selected').forEach(function (item) {
            addonsTotal += parseFloat(item.dataset.price) || 0;
        });

        const total = base + addonsTotal;

        if (totalEl) {
            totalEl.classList.add('price-pulse');
            totalEl.textContent = '₱' + total.toLocaleString();
            setTimeout(function () { totalEl.classList.remove('price-pulse'); }, 400);
        }
        if (summaryAddons) summaryAddons.textContent = '₱' + addonsTotal.toLocaleString();
    }

    function updateSummaryDateTime() {
        const dateEl = document.getElementById('summary-date');
        const timeEl = document.getElementById('summary-time');
        const datetimeSummary = document.getElementById('datetime-summary');
        const summaryDatetimeText = document.getElementById('summary-datetime-text');

        if (dateEl && selectedDate) {
            dateEl.textContent = formatDate(selectedDate);
        }
        if (timeEl && selectedTime) {
            timeEl.textContent = selectedTime;
        }

        if (datetimeSummary && summaryDatetimeText) {
            if (selectedDate && selectedTime) {
                datetimeSummary.style.display = 'flex';
                summaryDatetimeText.textContent = formatDateDisplay(selectedDate) + ' at ' + selectedTime;
            } else if (selectedDate) {
                datetimeSummary.style.display = 'flex';
                summaryDatetimeText.textContent = formatDateDisplay(selectedDate) + ' — Please select a time';
            } else {
                datetimeSummary.style.display = 'none';
            }
        }
    }

    document.addEventListener('DOMContentLoaded', function () {

        // ── Transparent navbar scroll behaviour (home page hero) ──
        const nav = document.getElementById('main-nav');
        if (nav && nav.classList.contains('nav-hero-transparent')) {
            var SCROLL_THRESHOLD = 80;
            function updateNavOnScroll() {
                if (window.scrollY > SCROLL_THRESHOLD) {
                    nav.classList.add('nav-scrolled');
                } else {
                    nav.classList.remove('nav-scrolled');
                }
            }
            window.addEventListener('scroll', updateNavOnScroll, { passive: true });
            updateNavOnScroll();
        }

        // ── Hamburger menu ──
        const hamburger = document.getElementById('hamburger');
        const navMenu = document.getElementById('nav-menu');
        const mainNav = document.getElementById('main-nav');

        function positionMobileMenu() {
            if (mainNav && navMenu && window.innerWidth <= 768) {
                const navRect = mainNav.getBoundingClientRect();
                navMenu.style.top = navRect.bottom + 'px';
            }
        }

        if (hamburger && navMenu) {
            hamburger.addEventListener('click', function (e) {
                e.stopPropagation();
                hamburger.classList.toggle('active');
                navMenu.classList.toggle('active');
                positionMobileMenu();
            });

            navMenu.querySelectorAll('a').forEach(function (link) {
                link.addEventListener('click', function () {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                });
            });

            document.addEventListener('click', function (e) {
                if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                }
            });

            window.addEventListener('resize', function () {
                if (window.innerWidth > 768) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                    navMenu.style.top = '';
                } else {
                    positionMobileMenu();
                }
            });

            window.addEventListener('scroll', positionMobileMenu);
        }

        // ── Booking page only ──
        const bookingForm = document.getElementById('booking-form');
        if (!bookingForm) return;

        // Initialize calendar
        renderCalendar();

        // Calendar navigation
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');

        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', function () {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar();
            });
        }

        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', function () {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar();
            });
        }

        showStep(currentStep);
        calculateTotal();

        const nextBtn = document.getElementById('next');
        const prevBtn = document.getElementById('prev');

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                if (validateStep(currentStep) && currentStep < totalSteps) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                if (currentStep > 1) {
                    currentStep--;
                    showStep(currentStep);
                }
            });
        }

        // Package is pre-selected via hidden input, calculate total on load
        calculateTotal();

        // Add-ons
        document.querySelectorAll('.addon-item').forEach(function (item) {
            item.addEventListener('click', function () {
                item.classList.toggle('selected');
                const cb = item.querySelector('input[type="checkbox"]');
                if (cb) cb.checked = item.classList.contains('selected');
                calculateTotal();
            });
        });

        // ── Backdrop modal ──
        var currentBackdropData = null;

        document.querySelectorAll('.backdrop-card').forEach(function (item) {
            item.addEventListener('click', function () {
                var color = item.dataset.color;
                var backdropId = item.dataset.id;
                var backdropName = item.dataset.name;
                var backdropImage = item.dataset.image;

                currentBackdropData = { color: color, backdropId: backdropId, backdropName: backdropName, backdropImage: backdropImage };

                var modal = document.getElementById('backdrop-modal');
                if (!modal) return;

                var nameEl = document.getElementById('backdrop-modal-name');
                var nameOverlay = document.getElementById('backdrop-modal-name-overlay');
                var fallback = document.getElementById('backdrop-modal-fallback');
                var imageEl = document.getElementById('backdrop-modal-image');
                var wrapper = modal.querySelector('.modal-content-wrapper');

                if (nameEl) nameEl.textContent = backdropName;
                if (nameOverlay) nameOverlay.textContent = backdropName;

                if (backdropImage && imageEl) {
                    imageEl.src = backdropImage;
                    imageEl.style.display = 'block';
                    if (fallback) fallback.style.display = 'none';
                } else {
                    if (imageEl) imageEl.style.display = 'none';
                    if (fallback) {
                        fallback.style.display = 'flex';
                        fallback.style.background = color;
                    }
                }

                modal.style.display = 'flex';
                setTimeout(function () {
                    if (wrapper) wrapper.style.transform = 'scale(1)';
                }, 10);
            });
        });

        // Modal close
        const backdropModal = document.getElementById('backdrop-modal');
        if (backdropModal) {
            const closeBtn = backdropModal.querySelector('.modal-close-btn');
            const modalBackdropEl = backdropModal.querySelector('.modal-backdrop');

            function closeModal() {
                const wrapper = backdropModal.querySelector('.modal-content-wrapper');
                if (wrapper) wrapper.style.transform = 'scale(0.95)';
                setTimeout(function () {
                    backdropModal.style.display = 'none';
                    currentBackdropData = null;
                }, 200);
            }

            if (closeBtn) closeBtn.addEventListener('click', closeModal);
            if (modalBackdropEl) modalBackdropEl.addEventListener('click', closeModal);

            const selectBackdropBtn = document.getElementById('select-backdrop-btn');
            if (selectBackdropBtn) {
                selectBackdropBtn.addEventListener('click', function () {
                    if (currentBackdropData) {
                        var hiddenInput = document.getElementById('backdrop-input');

                        // Deselect all cards
                        document.querySelectorAll('.backdrop-card').forEach(function (i) {
                            i.classList.remove('selected');
                        });

                        // Select the chosen card
                        var selectedBox = document.querySelector('.backdrop-card[data-id="' + currentBackdropData.backdropId + '"]');
                        if (selectedBox) {
                            selectedBox.classList.add('selected');
                        }

                        if (hiddenInput) hiddenInput.value = currentBackdropData.backdropId;

                        closeModal();
                    }
                });
            }
        }

        // Payment options
        document.querySelectorAll('.payment-option').forEach(function (opt) {
            opt.addEventListener('click', function () {
                document.querySelectorAll('.payment-option').forEach(function (o) {
                    o.classList.remove('selected');
                });
                opt.classList.add('selected');
                const input = document.getElementById('payment-input');
                if (input) input.value = opt.dataset.value;
            });
        });

        // Terms checkbox
        const termsCheckboxItem = document.querySelector('.terms-checkbox-item');
        const termsCheckbox = document.getElementById('terms');
        if (termsCheckboxItem && termsCheckbox) {
            termsCheckboxItem.addEventListener('click', function (e) {
                if (e.target === termsCheckbox) return;
                e.stopPropagation();
                termsCheckbox.checked = !termsCheckbox.checked;
                termsCheckboxItem.classList.toggle('selected', termsCheckbox.checked);
            });
            termsCheckbox.addEventListener('click', function () {
                termsCheckboxItem.classList.toggle('selected', termsCheckbox.checked);
            });
        }

    });

})();
