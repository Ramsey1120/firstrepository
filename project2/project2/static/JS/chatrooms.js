document.addEventListener("DOMContentLoaded", () => {

    const add_room = document.querySelector(".add-room");
    const cancel_room = document.querySelector(".cancel-room");
    const form = document.querySelector(".form");
    const channel_name = document.querySelector("#channel-name");
    const admin = localStorage.getItem("username");

    add_room.onclick = () => form.style.display = "block";
    cancel_room.onclick = () => form.style.display = "none";

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        form.onsubmit = e => {

            e.preventDefault();

            var id = Math.ceil(Math.random() * 10000);
            var title = channel_name.value;

            if (title.length === 0) {

                channel_name.style.borderColor = "red";
                channel_name.placeholder = "you must fill the field";
                channel_name.placeholder.color = "red";

                setTimeout(() => {

                    channel_name.style.borderColor = "";
                    channel_name.placeholder = "insert chatroom name";

                }, 5000);

                return;

            } else {

                socket.emit('create room', { 'id': id, 'admin': admin, 'chat_title': title, 'all_messages': [] });

            };

        };
    });


    socket.on('all chatrooms loaded', data => {

        data.data.forEach(item => {

            const room = Handlebars.compile(document.querySelector('#room').innerHTML);
            const content = room({ 'title': item.chat_title, 'id': item.id, 'admin': item.admin });

            if (item.admin === admin) {

                document.querySelector(".my-channels").insertAdjacentHTML('beforeend', content);

            } else {

                document.querySelector(".other-channels").insertAdjacentHTML('beforeend', content);
            };

        });

    });


    socket.on('room already exists', () => {

        channel_name.style.borderColor = "red";
        channel_name.value = "";
        channel_name.placeholder = "name already in use"

        setTimeout(() => {
            channel_name.style.borderColor = "";
            channel_name.placeholder = "insert chatroom name ";
        }, 5000);

    });


    socket.on('room created', data => {

        const room = Handlebars.compile(document.querySelector('#room').innerHTML);
        const content = room({ 'title': data.chat_title, 'id': data.id, 'admin': data.admin });

        if (data.admin === admin) {

            document.querySelector('.my-channels').insertAdjacentHTML('beforeend', content);

        } else {
            document.querySelector('.other-channels').insertAdjacentHTML('beforeend', content);

        };

        form.style.display = "none";

    });


});