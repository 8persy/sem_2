document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.navigation');
    console.log(navLinks)
    const currentPath = window.location.pathname; // Получаем текущий путь из URL

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            // Удаляем класс active у всех ссылок
            navLinks.forEach(nav => nav.classList.remove('active'));
            // Добавляем класс active к текущей вкладке
            link.classList.add('active');
        }
    });
});