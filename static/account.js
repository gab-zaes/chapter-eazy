function toggleForm() {
    document.getElementById("del-user-form").classList.toggle("hidden");
        document.getElementById("change-pass-form").classList.toggle("hidden");
        document.getElementById("del-chap-form").classList.toggle("hidden");

        //change style of the delete button to "take me back"
        btn = document.getElementById("delete-btn");
        btn.classList.toggle("red");
        btn.classList.toggle("discreto");
        if (btn.innerHTML != "Take me back") {
            btn.innerHTML = "Take me back";
        }
        else {
            btn.innerHTML = "Delete account";
        }
}

document.addEventListener("DOMContentLoaded", function(){
    document.getElementById("delete-btn").addEventListener("click", toggleForm);
    document.getElementById("take-back-btn").addEventListener("click", toggleForm);
})