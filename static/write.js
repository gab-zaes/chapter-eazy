

document.addEventListener("DOMContentLoaded", function(){
    let page = document.querySelector(".paper");

    document.getElementById("save-submit-value").value = document.querySelector(".paper").value;
    if (page.scrollHeight > 825) {
        page.setAttribute("rows", Math.round(page.scrollHeight / 27));
    }
    

    document.querySelector(".area-chapter").addEventListener("click", function(){
        document.querySelector(".windowed").classList.toggle("hidden");
    });
    let chapters = document.querySelectorAll(".chapter-name")
    for (let chapter of chapters) {
        if (chapter.innerHTML === document.querySelector("#chapter_title_h1").innerHTML) {
            chapter.parentNode.classList.add("ativo");
        };
    };
    
    page.addEventListener("keyup", function(){
        document.getElementById("save-submit-value").value = page.value;
    });

    document.getElementById("show-order").addEventListener("click", (event) => {
        document.querySelector(".order").classList.toggle("hidden");
    });

    document.getElementById("scroll").addEventListener("click", () => {
        window.scroll(0, document.documentElement.scrollHeight);
    });

    page.addEventListener("keydown", (keyDownEvent) => {
        page.setAttribute("rows", Math.round(page.scrollHeight / 27.5));
        console.log(page.rows);
        console.log(page.scrollHeight);
    });
});