// 后端 API 地址
// ⚠️ 改成你电脑的实际 IP，例如 http://192.168.1.100:5000
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
            
            // ✅ 新增：前端密码规则验证
            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9\s]).{12,18}$/;
            if (!passwordRegex.test(password)) {
                document.getElementById('message').innerHTML = '<p style="color:red">❌ Password must be 12-18 characters, include uppercase, lowercase, number and symbol (no spaces)</p>';
                return;
            }
            
            try {
                // ✅ 修改：去掉 confirm 字段
                const response = await fetch(`${API_URL}/api/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    document.getElementById('message').innerHTML = '<p style="color:green">✅ Registration successful! Redirecting...</p>';
                    
                    // ✅ 修改：注册成功后跳转到 question.html（问卷页）
                    setTimeout(() => {
                        window.location.href = 'question.html';
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
                    document.getElementById('message').innerHTML = '<p style="color:green">✅ Login successful! Checking status...</p>';
                    
                    // ✅ 修改：登录后先检查问卷状态再决定跳转
                    try {
                        const statusRes = await fetch(`${API_URL}/api/user/status`, {
                            headers: { 'Authorization': `Bearer ${data.token}` }
                        });
                        const statusData = await statusRes.json();
                        
                        if (statusData.success && statusData.has_completed_questionnaire) {
                            // 已答过问卷 → 跳转 dashboard
                            document.getElementById('message').innerHTML = '<p style="color:green">✅ Login successful! Redirecting to dashboard...</p>';
                            setTimeout(() => {
                                window.location.href = 'dashboard.html';
                            }, 1500);
                        } else {
                            // 未答过问卷 → 跳转问卷页
                            document.getElementById('message').innerHTML = '<p style="color:green">✅ Login successful! Redirecting to questionnaire...</p>';
                            setTimeout(() => {
                                window.location.href = 'question.html';
                            }, 1500);
                        }
                    } catch (err) {
                        console.error('Status check failed:', err);
                        // 状态检查失败，默认去问卷页
                        setTimeout(() => {
                            window.location.href = 'question.html';
                        }, 1500);
                    }
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
                    loadProfile();
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
            // ✅ 修改：登出后跳转到 index.html（首页）
            window.location.href = 'index.html';
        });
    }

    // ========== ✅ 新增：index.html 的 Start 和 Login 按钮 ==========
    const startBtn = document.getElementById('startBtn');
    const loginPageBtn = document.getElementById('loginBtn');

    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                // 未登录 → 去登录页
                window.location.href = 'login.html';
            } else {
                // 已登录 → 检查问卷状态
                try {
                    const statusRes = await fetch(`${API_URL}/api/user/status`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const statusData = await statusRes.json();
                    
                    if (statusData.success && statusData.has_completed_questionnaire) {
                        window.location.href = 'dashboard.html';
                    } else {
                        window.location.href = 'question.html';
                    }
                } catch (err) {
                    console.error('Status check failed:', err);
                    window.location.href = 'question.html';
                }
            }
        });
    }

    if (loginPageBtn) {
        loginPageBtn.addEventListener('click', () => {
            window.location.href = 'login.html';
        });
    }

    // ========== ✅ 新增：question.html 页面加载时检查是否已答过问卷 ==========
    const isQuestionPage = window.location.pathname.includes('question.html');
    if (isQuestionPage) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
        } else {
            // 检查是否已经答过问卷
            (async () => {
                try {
                    const statusRes = await fetch(`${API_URL}/api/user/status`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const statusData = await statusRes.json();
                    
                    if (statusData.success && statusData.has_completed_questionnaire) {
                        // 已经答过问卷，不应该在这里，跳去 dashboard
                        window.location.href = 'dashboard.html';
                    }
                } catch (err) {
                    console.error('Status check failed:', err);
                }
            })();
        }
    }

    // ========== ✅ 新增：dashboard.html 页面加载时检查是否未答过问卷 ==========
    const isDashboardPage = window.location.pathname.includes('dashboard.html');
    if (isDashboardPage) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
        } else {
            // 检查是否未答过问卷
            (async () => {
                try {
                    const statusRes = await fetch(`${API_URL}/api/user/status`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const statusData = await statusRes.json();
                    
                    if (!statusData.success || !statusData.has_completed_questionnaire) {
                        // 未答过问卷，跳去问卷页
                        window.location.href = 'question.html';
                    }
                } catch (err) {
                    console.error('Status check failed:', err);
                }
            })();
        }
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
