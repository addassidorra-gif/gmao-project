window.addEventListener("DOMContentLoaded", () => {
    window.setTimeout(() => {
        document.querySelectorAll(".message").forEach((item) => {
            item.style.opacity = "0";
            item.style.transition = "opacity 0.4s ease";
            window.setTimeout(() => {
                item.remove();
            }, 400);
        });
    }, 3000);
});
