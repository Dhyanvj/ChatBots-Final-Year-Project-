document.addEventListener('DOMContentLoaded', function () {
    const openAppBtn = document.getElementById('openAppBtn');

    openAppBtn.addEventListener('click', function () {
        openStreamlitApp();
    });

    function openStreamlitApp() {
        // Redirect the user to the Streamlit app
        window.open("http://localhost:8501/", "_blank");
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const openAppBtn1 = document.getElementById('openAppBtn1');

    openAppBtn1.addEventListener('click', function () {
        openStreamlitApp1();
    });

    function openStreamlitApp1() {
        // Redirect the user to the Streamlit app
        window.open("http://localhost:8502/", "_blank");
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const openAppBtn3 = document.getElementById('openAppBtn3');

    openAppBtn3.addEventListener('click', function () {
        openStreamlitApp3();
    });

    function openStreamlitApp3() {
        // Redirect the user to the Streamlit app
        window.open("http://localhost:8503/", "_blank");
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const openAppBtn2 = document.getElementById('openAppBtn2');

    openAppBtn2.addEventListener('click', function () {
        openStreamlitApp2();
    });

    function openStreamlitApp2() {
        // Redirect the user to the Streamlit app
        window.open("http://localhost:8504/", "_blank");
    }
});