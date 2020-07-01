document.addEventListener("DOMContentLoaded", () => {

    const send_chat = document.querySelector("#send-msg");
    const current_user = localStorage.getItem("username");


    if (current_user == null) {
        window.location.replace("http://127.0.0.1:5000/error")
    }

    var room_id = window.location.href;
    var id = room_id.slice(30);

    var channel_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


    // if (localStorage.length < 2) {

    //     channel_socket.emit('load latest 100 messages', { 'room_id': id })

    // } else {

    // }

    var message = document.querySelector("#msg-content").value;

    channel_socket.on('connect', () => {

        channel_socket.emit('user joined channel', { 'username': current_user, 'room_id': id });

        send_chat.onclick = () => {

            var message = document.querySelector("#msg-content").value;
            var msg_date = new Date(Date.now());

            var hours = msg_date.getHours();
            var minutes = msg_date.getMinutes();

            if (minutes <= 9) {
                var minutes = "0" + minutes;
            };

            if (hours <= 9) {
                var hours = "0" + hours;
            };

            var timestamp = hours + ":" + minutes;

            if (message.length === 0) {

                return;
            } else {
                channel_socket.emit('message sent', {
                    'room_id': id,
                    'user': current_user,
                    'message': message,
                    'date': timestamp
                });
                document.querySelector("#msg-content").value = "";
            };

        };

    });


    // handlebars has built in helpers that allow to define functions that I can use to interact with my template
    Handlebars.registerHelper('check_author', user => {

        if (user === "") {
            return false;
        } else {
            return true;
        }

    });


    channel_socket.on('message processed', data => {

        if (data.user === current_user) {
            data.user = "";

        } else if (data.user !== current_user) {

            showNotifications(data.user, data.message, data.date, data.id);
        }

        const chat = Handlebars.compile(document.querySelector('#chats').innerHTML);
        const content = chat({
            'user': data.user,
            'message': data.message,
            'date': data.date
        });

        console.log(showNotifications(data.user, data.message, data.date, data.id))
        document.querySelector(".chats").innerHTML += content;
        document.querySelector(".chats").scrollTop = document.querySelector(".chats").scrollHeight;
    });


    window.onbeforeunload = () => {
        channel_socket.emit('leave room', { 'username': current_user, 'room_id': id })
        localStorage.setItem('last chatroom', window.location.href)
    }
});
