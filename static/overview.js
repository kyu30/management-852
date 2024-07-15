document.addEventListener('DOMContentLoaded', function(){
    fetchWhitelist();
    document.getElementById('addForm').addEventListener('submit', function(event){
        event.preventDefault();
        console.log("form submitted");
        const uid = document.getElementById('uid').value;
        const name = document.getElementById('name').value;
        const permissions = document.getElementById('permission').value;
        const door = document.getElementById('door').value;
        const time = document.getElementById('time').value;
        addEntry(uid, name, permissions, host);
    });
});

function fetchWhitelist(){
    fetch('/get_overview')
    .then(response => response.json())
    .then(data => {
        console.log("whitelist received");
        data.sort((a, b) => {
            return a['Time'] < b['Time'] ? 1 : -1;
        });
        const whitelist = document.getElementById('overview');
        whitelist.innerHTML = '';
        data.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.UID}</td>
                <td>${entry.User}</td>
                <td>${entry.Permission}</td>
                <td>${entry.Door}</td>
                <td>${entry.Time}</td>
                `;
                whitelist.appendChild(row);
        });
    }).catch(error => console.error('Error fetching whitelist: ', error));
}
