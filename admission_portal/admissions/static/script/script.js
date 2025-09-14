// Countdown timer
let countdown = 10;
const timerElement = document.getElementById('timer');
const countdownContainer = document.getElementById('countdown');

const timer = setInterval(() => {
    countdown--;
    timerElement.textContent = countdown;
    
    if (countdown <= 3) {
        countdownContainer.style.background = 'rgba(255, 107, 107, 0.2)';
        countdownContainer.style.borderColor = 'rgba(255, 107, 107, 0.3)';
    }
    
    if (countdown <= 0) {
        clearInterval(timer);
        // Redirect to admission form page
        // Replace 'admission.html' with your actual form page URL
        window.location.href = 'admission.html';
    }
}, 1000);

// Create floating particles
function createParticle() {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    
    const size = Math.random() * 4 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
    particle.style.animationDelay = Math.random() * 2 + 's';
    
    document.getElementById('particles').appendChild(particle);
    
    setTimeout(() => {
        particle.remove();
    }, 8000);
}

// Create particles periodically
setInterval(createParticle, 300);

// Initial particles
for (let i = 0; i < 10; i++) {
    setTimeout(createParticle, i * 200);
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".login-form");
    const username = form.querySelector("input[name='username']");
    const password = form.querySelector("input[name='password']");
    const btn = form.querySelector(".login-btn");

    form.addEventListener("submit", (e) => {
        e.preventDefault(); // prevent real form submit

        const user = username.value.trim();
        const pass = password.value.trim();

        // Check for empty fields
        if (user === "" || pass === "") {
            showNotification("Please fill in both fields!", "error");
            return;
        }

        // Hardcoded login credentials
        if (user === "admin" && pass === "admin123") {
            // Add loading effect
            btn.disabled = true;
            btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i>`;

            setTimeout(() => {
                window.location.href = "admin.html"; // redirect
            }, 1500);
        } else {
            showNotification("Invalid username or password!", "error");
            password.value = ""; 
            password.focus();
        }
    });
});

// --- Notification function (same as admission form) ---
function showNotification(message, type) {
    // Remove existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="close-btn">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add notification styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;

    const closeBtn = notification.querySelector('.close-btn');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        margin-left: 10px;
        padding: 0;
        font-size: 16px;
    `;

    document.body.appendChild(notification);

    // Auto remove after 5s
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// --- Add keyframe animation if not already present ---
if (!document.getElementById("notif-anim")) {
    const style = document.createElement('style');
    style.id = "notif-anim";
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}
