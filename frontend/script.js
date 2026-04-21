const API_URL = 'http://10.131.53.162:5000';

const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_URL}/api/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                document.getElementById('message').innerHTML = '<p style="color:green">✅ Registration successful!</p>';
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                document.getElementById('message').innerHTML = `<p style="color:red">❌ ${data.message}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('message').innerHTML = '<p style="color:red">❌ Cannot connect to backend</p>';
        }
    });
} 
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_URL}/api/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                document.getElementById('message').innerHTML = '<p style="color:green">✅ Login successful!</p>';
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                document.getElementById('message').innerHTML = `<p style="color:red">❌ ${data.message}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('message').innerHTML = '<p style="color:red">❌ Cannot connect to backend</p>';
        }
    });
}