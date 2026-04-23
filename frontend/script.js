// ================================================
// API Configuration
// ================================================
const API_BASE_URL = 'http://localhost:5000/api';

// ================================================
// Utility Functions
// ================================================

// Store token in localStorage
function setToken(token) {
    localStorage.setItem('auth_token', token);
}

// Get token from localStorage
function getToken() {
    return localStorage.getItem('auth_token');
}

// Remove token (logout)
function removeToken() {
    localStorage.removeItem('auth_token');
}

// Check if user is logged in
function isLoggedIn() {
    return getToken() !== null;
}

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (options.body && options.body instanceof FormData) {
        delete headers['Content-Type'];
        delete config.headers['Content-Type'];
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();
        return { response, data };
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// ================================================
// Authentication Functions
// ================================================

// Register user
async function register(username, password, confirm, email) {
    const { response, data } = await apiCall('/register', {
        method: 'POST',
        body: JSON.stringify({ username, password, confirm, email })
    });
    
    if (response.ok && data.success) {
        setToken(data.token);
        return { success: true, user: data.user };
    }
    
    return { success: false, message: data.message };
}

// Login user
async function login(username, password) {
    const { response, data } = await apiCall('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    
    if (response.ok && data.success) {
        setToken(data.token);
        return { success: true, user: data.user };
    }
    
    return { success: false, message: data.message };
}

// Logout user
function logout() {
    removeToken();
    window.location.href = 'login.html'; // Redirect to login page
}

// Get user profile
async function getProfile() {
    const { response, data } = await apiCall('/profile', {
        method: 'GET'
    });
    
    if (response.ok && data.success) {
        return { success: true, user: data.user };
    }
    
    return { success: false, message: data.message };
}

// Update user profile (with avatar upload)
async function updateProfile(profileData) {
    const formData = new FormData();
    
    if (profileData.gender) formData.append('gender', profileData.gender);
    if (profileData.height) formData.append('height', profileData.height);
    if (profileData.weight) formData.append('weight', profileData.weight);
    if (profileData.fitness_level) formData.append('fitness_level', profileData.fitness_level);
    if (profileData.country) formData.append('country', profileData.country);
    if (profileData.bio) formData.append('bio', profileData.bio);
    if (profileData.date_of_birth) formData.append('date_of_birth', profileData.date_of_birth);
    if (profileData.avatar) formData.append('avatar', profileData.avatar);
    
    const { response, data } = await apiCall('/profile', {
        method: 'PUT',
        body: formData
    });
    
    if (response.ok && data.success) {
        return { success: true, message: data.message };
    }
    
    return { success: false, message: data.message };
}

// ================================================
// DOM Elements and Event Handlers
// ================================================

// Registration Form Handler
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;
    const email = document.getElementById('email').value;
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Registering...';
    submitBtn.disabled = true;
    
    const result = await register(username, password, confirm, email);
    
    if (result.success) {
        // Show success message
        showMessage('Registration successful! Redirecting...', 'success');
        // Redirect to dashboard or home page
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    } else {
        showMessage(result.message, 'error');
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Login Form Handler
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Logging in...';
    submitBtn.disabled = true;
    
    const result = await login(username, password);
    
    if (result.success) {
        showMessage('Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    } else {
        showMessage(result.message, 'error');
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Profile Form Handler
async function handleUpdateProfile(event) {
    event.preventDefault();
    
    const profileData = {
        gender: document.getElementById('gender')?.value,
        height: document.getElementById('height')?.value,
        weight: document.getElementById('weight')?.value,
        fitness_level: document.getElementById('fitness_level')?.value,
        country: document.getElementById('country')?.value,
        bio: document.getElementById('bio')?.value,
        date_of_birth: document.getElementById('date_of_birth')?.value,
        avatar: document.getElementById('avatar')?.files[0]
    };
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Updating...';
    submitBtn.disabled = true;
    
    const result = await updateProfile(profileData);
    
    if (result.success) {
        showMessage('Profile updated successfully!', 'success');
        // Refresh profile display
        loadProfile();
    } else {
        showMessage(result.message, 'error');
    }
    
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
}

// Load and display profile data
async function loadProfile() {
    const result = await getProfile();
    
    if (result.success) {
        const user = result.user;
        
        // Populate form fields if they exist
        if (document.getElementById('display_username')) {
            document.getElementById('display_username').textContent = user.username;
        }
        if (document.getElementById('display_email')) {
            document.getElementById('display_email').textContent = user.email;
        }
        if (document.getElementById('gender')) {
            document.getElementById('gender').value = user.gender || '';
        }
        if (document.getElementById('height')) {
            document.getElementById('height').value = user.height || '';
        }
        if (document.getElementById('weight')) {
            document.getElementById('weight').value = user.weight || '';
        }
        if (document.getElementById('fitness_level')) {
            document.getElementById('fitness_level').value = user.fitness_level || '';
        }
        if (document.getElementById('country')) {
            document.getElementById('country').value = user.country || '';
        }
        if (document.getElementById('bio')) {
            document.getElementById('bio').value = user.bio || '';
        }
        if (document.getElementById('date_of_birth')) {
            document.getElementById('date_of_birth').value = user.date_of_birth || '';
        }
        if (document.getElementById('avatar_preview') && user.avatar) {
            document.getElementById('avatar_preview').src = `http://localhost:5000${user.avatar}`;
        }
    } else if (result.message === 'Token missing' || result.message === 'Invalid or expired token') {
        // Redirect to login if token is invalid
        window.location.href = 'login.html';
    } else {
        showMessage('Failed to load profile: ' + result.message, 'error');
    }
}

// ================================================
// UI Helper Functions
// ================================================

// Show message to user
function showMessage(message, type = 'info') {
    // Check if message container exists, if not create one
    let messageContainer = document.getElementById('message-container');
    
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.style.position = 'fixed';
        messageContainer.style.top = '20px';
        messageContainer.style.right = '20px';
        messageContainer.style.zIndex = '9999';
        document.body.appendChild(messageContainer);
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.style.cssText = `
        padding: 12px 20px;
        margin-bottom: 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        animation: slideIn 0.3s ease-out;
        cursor: pointer;
    `;
    
    // Set colors based on message type
    if (type === 'success') {
        messageDiv.style.backgroundColor = '#4CAF50';
    } else if (type === 'error') {
        messageDiv.style.backgroundColor = '#f44336';
    } else {
        messageDiv.style.backgroundColor = '#2196F3';
    }
    
    messageDiv.textContent = message;
    
    // Add click to dismiss
    messageDiv.onclick = function() {
        messageDiv.remove();
    };
    
    messageContainer.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// Add CSS animation for messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Check authentication on protected pages
function checkAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}

// ================================================
// Page Initialization
// ================================================

// Initialize based on current page
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    
    // Registration page
    if (currentPage === 'register.html' || currentPage === 'register') {
        const form = document.getElementById('register-form');
        if (form) {
            form.addEventListener('submit', handleRegister);
        }
    }
    
    // Login page
    if (currentPage === 'login.html' || currentPage === 'login') {
        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', handleLogin);
        }
        
        // Check if already logged in
        if (isLoggedIn()) {
            window.location.href = 'dashboard.html';
        }
    }
    
    // Profile/Dashboard page
    if (currentPage === 'dashboard.html' || currentPage === 'profile.html') {
        checkAuth();
        loadProfile();
        
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', handleUpdateProfile);
        }
        
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
        
        // Avatar preview
        const avatarInput = document.getElementById('avatar');
        if (avatarInput) {
            avatarInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const preview = document.getElementById('avatar_preview');
                        if (preview) {
                            preview.src = e.target.result;
                        }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }
});

// ================================================
// Export for use in other files (if using modules)
// ================================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        register,
        login,
        logout,
        getProfile,
        updateProfile,
        isLoggedIn
    };
}