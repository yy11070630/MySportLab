// 后端 API 地址
const API_URL = 'http://localhost:5000';

// 等待页面加载完成
document.addEventListener('DOMContentLoaded', function() {

    // ========== 注册 ==========
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;   
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm').value;
            
            // 密码确认验证
            if (password !== confirm) {
                document.getElementById('message').innerHTML = '<p style="color:red">❌ Passwords do not match!</p>';
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/api/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password, confirm })
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
                document.getElementById('message').innerHTML = `<p style="color:red">❌ Error: ${error.message}</p>`;
            }
        });
    }

    // ========== 登录 ==========
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch(`${API_URL}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
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
                document.getElementById('message').innerHTML = `<p style="color:red">❌ Error: ${error.message}</p>`;
            }
        });
    }

    // ========== 更新 Profile ==========
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = 'login.html';
                return;
            }
            
            const formData = new FormData();
            formData.append('gender', document.getElementById('gender').value);
            formData.append('height', document.getElementById('height').value);
            formData.append('weight', document.getElementById('weight').value);
            formData.append('fitness_level', document.getElementById('fitness_level').value);
            formData.append('country', document.getElementById('country').value);
            formData.append('bio', document.getElementById('bio').value);
            formData.append('date_of_birth', document.getElementById('date_of_birth').value);
            
            const avatarFile = document.getElementById('avatar').files[0];
            if (avatarFile) {
                formData.append('avatar', avatarFile);
            }
            
            try {
                const response = await fetch(`${API_URL}/api/profile`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('message').innerHTML = '<p style="color:green">✅ Profile updated!</p>';
                    loadProfile(); // 刷新显示
                } else {
                    document.getElementById('message').innerHTML = `<p style="color:red">❌ ${data.message}</p>`;
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('message').innerHTML = `<p style="color:red">❌ Error: ${error.message}</p>`;
            }
        });
    }

    // ========== 登出功能 ==========
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        });
    }

});

// ========== 获取并显示 Profile ==========
async function loadProfile() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 显示用户信息
            const profileInfo = document.getElementById('profileInfo');
            if (profileInfo) {
                profileInfo.innerHTML = `
                    <p><strong>Username:</strong> ${data.user.username}</p>
                    <p><strong>Email:</strong> ${data.user.email}</p>
                    ${data.profile.avatar ? `<img src="${API_URL}${data.profile.avatar}" width="100">` : ''}
                    <p><strong>Gender:</strong> ${data.profile.gender || 'Not set'}</p>
                    <p><strong>Height:</strong> ${data.profile.height || 'Not set'} cm</p>
                    <p><strong>Weight:</strong> ${data.profile.weight || 'Not set'} kg</p>
                    <p><strong>Fitness Level:</strong> ${data.profile.fitness_level || 'Not set'}</p>
                    <p><strong>Country:</strong> ${data.profile.country || 'Not set'}</p>
                    <p><strong>Bio:</strong> ${data.profile.bio || 'Not set'}</p>
                    <p><strong>Date of Birth:</strong> ${data.profile.date_of_birth || 'Not set'}</p>
                `;
            }
            
            // 填充表单（如果有）
            if (document.getElementById('gender')) {
                document.getElementById('gender').value = data.profile.gender || '';
                document.getElementById('height').value = data.profile.height || '';
                document.getElementById('weight').value = data.profile.weight || '';
                document.getElementById('fitness_level').value = data.profile.fitness_level || '';
                document.getElementById('country').value = data.profile.country || '';
                document.getElementById('bio').value = data.profile.bio || '';
                document.getElementById('date_of_birth').value = data.profile.date_of_birth || '';
            }
        } else {
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error:', error);
        window.location.href = 'login.html';
    }
}

// ========== 检查登录状态（用于需要登录的页面）==========
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
    }
}

// 如果在 profile 页面，加载数据
if (window.location.pathname.includes('profile.html')) {
    loadProfile();
}

// 如果在 dashboard 页面，检查登录
if (window.location.pathname.includes('dashboard.html')) {
    checkAuth();
}