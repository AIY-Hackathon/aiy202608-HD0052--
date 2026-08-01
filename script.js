// 深色模式切换
const themeBtn = document.getElementById('themeBtn');
const body = document.body;

themeBtn.addEventListener('click', () => {
  body.classList.toggle('dark');
  themeBtn.textContent = body.classList.contains('dark')
    ? '切换浅色模式'
    : '切换深色模式';
});

// 打招呼按钮
const greetBtn = document.getElementById('greetBtn');
const greetMsg = document.getElementById('greetMsg');

greetBtn.addEventListener('click', () => {
  greetMsg.textContent = '你好！JavaScript 已经成功运行了 🎉';
});
