const API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', function() {
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const messageDiv = document.getElementById('message');
            
            // 简单验证
            if (!username || !password) {
                messageDiv.innerHTML = '<p style="color:red">❌ Username and password are required</p>';
                return;
            }
            
            // 显示加载状态
            messageDiv.innerHTML = '<p style="color:blue">⏳ Registering...</p>';
            
            try {
                const response = await fetch(`${API_URL}/api/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        username: username, 
                        email: email, 
                        password: password 
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    messageDiv.innerHTML = '<p style="color:green">✅ Registration successful! Redirecting to login...</p>';
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 1500);
                } else {
                    messageDiv.innerHTML = `<p style="color:red">❌ ${data.message}</p>`;
                }
            } catch (error) {
                console.error('Error:', error);
                messageDiv.innerHTML = '<p style="color:red">❌ Cannot connect to backend. Make sure the server is running on port 5000.</p>';
            }
        });
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const messageDiv = document.getElementById('message');
            
            if (!username || !password) {
                messageDiv.innerHTML = '<p style="color:red">❌ Username and password are required</p>';
                return;
            }
            
            messageDiv.innerHTML = '<p style="color:blue">⏳ Logging in...</p>';
            
            try {
                const response = await fetch(`${API_URL}/api/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        username: username, 
                        password: password 
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    messageDiv.innerHTML = '<p style="color:green">✅ Login successful! Redirecting to dashboard...</p>';
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1500);
                } else {
                    messageDiv.innerHTML = `<p style="color:red">❌ ${data.message}</p>`;
                }
            } catch (error) {
                console.error('Error:', error);
                messageDiv.innerHTML = '<p style="color:red">❌ Cannot connect to backend. Make sure the server is running on port 5000.</p>';
            }
        });
    }
    
});

const user = JSON.parse(localStorage.getItem("user"));
const height = localStorage.getItem("height");
const weight = localStorage.getItem("weight");

if (user) {
    const usernameEl = document.getElementById("username");
    if (usernameEl) {
        usernameEl.innerText = user.username;
    }
}

if (height && weight) {
    const h = height / 100;
    const bmi = weight / (h * h);

    document.getElementById("height").innerText = height + " cm";
    document.getElementById("weight").innerText = weight + " kg";
    document.getElementById("bmi").innerText = bmi.toFixed(1);
}