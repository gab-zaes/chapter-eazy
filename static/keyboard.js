//first we create an object to keep track of the pressed keys
let isKeyPressed = {
    "Tab": false, // tab in ASCII
    "s": false,  //s
    "-": false
}

document.onkeydown = (keyDownEvent) => {   
    isKeyPressed[keyDownEvent.key] = true;
   
    if (keyDownEvent.ctrlKey && isKeyPressed["s"]) {
        keyDownEvent.preventDefault();
        document.getElementById("save-form").submit();
    } else if (isKeyPressed["Tab"]) {
        // replaces "Tab" for "      "
        keyDownEvent.preventDefault();
        let curPos = document.querySelector(".paper").selectionStart;
        let text = document.querySelector(".paper").value;

        // slice the string taking into account the cursor position
        document.querySelector(".paper").value = text.slice(0, curPos) + "      " + text.slice(curPos);

        // define cursor position at the end
        document.querySelector(".paper").selectionStart = curPos + 6;
        document.querySelector(".paper").selectionEnd = curPos + 6;

    } else if (isKeyPressed["-"]) {
        // replaces "-" for "‒"
        keyDownEvent.preventDefault();
        let curPos = document.querySelector(".paper").selectionStart;
        let text = document.querySelector(".paper").value;

        // slice the string taking into account the cursor position
        document.querySelector(".paper").value = text.slice(0, curPos) + "‒" + text.slice(curPos);

        // define cursor position at the end
        document.querySelector(".paper").selectionStart = curPos + 1;
        document.querySelector(".paper").selectionEnd = curPos + 1;
    }
};

document.onkeyup = (keyUpEvent) => {
    isKeyPressed[keyUpEvent.key] = false;
};
