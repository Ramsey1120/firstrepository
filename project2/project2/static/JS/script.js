document.addEventListener("DOMContentLoaded", () => {

    Notification.requestPermission();

    const form = document.querySelector("form");
    const join_chat = document.querySelector(".join-chat");
    const current_user = localStorage.getItem("username");
    const last_room = localStorage.getItem("last chatroom");


    if (current_user) {

        if (last_room || last_room === undefined || last_room === null) {
            document.querySelector(".last-room").style.display = "block";
            document.querySelector(".last-room").href = last_room;
        }

        join_chat.style.visibility = "visible";
        form.style.display = "none";
        join_chat.innerHTML = "resume chatting";
        document.querySelector(".username").innerHTML = current_user;

    } else {


        form.onsubmit = e => {

            e.preventDefault();

            var username = document.querySelector("#username").value;
            var error = document.querySelector(".err-msg");

            if (username.length === 0) {

                document.querySelector("#username").style.borderColor = "red";
                let content = document.createTextNode("you must fill the field");
                error.appendChild(content);

                setTimeout(() => {
                    error.innerHTML = "";
                    document.querySelector("#username").style.borderColor = "";
                }, 5000);

                return;

            } else {

                join_chat.style.visibility = "visible";
                window.localStorage.setItem("username", username);

            };


        };

    };
});
