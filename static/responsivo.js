document.addEventListener("DOMContentLoaded", function() {
    let save = document.getElementById("save-body");
    let scrollUp = document.getElementById("scroll-up");
    
    save.addEventListener("click", () => {
        document.getElementById("save-form").submit();
    })

    scrollUp.addEventListener("click", () => {
        window.scroll(document.documentElement.scrollHeight, 0);
    })
});