document.addEventListener('DOMContentLoaded', function(){
    fetchWhitelist();
    document.getElementById('addForm').addEventListener('submit', function(event){
        event.preventDefault();
        console.log("form submitted");
        const uid = document.getElementById('uid').value;
        const name = document.getElementById('name').value;
        const permissions = document.getElementById('permission').value;
        const door = document.getElementById('door').value;
        const host = document.getElementById('host').value;
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
                <td>${entry.uid}</td>
                <td>${entry.name}</td>
                <td>${entry.access}</td>
                <td>${entry.host}</td>
                <td>${entry.last_used}</td>
                <td>${entry.door}</td>
                `;
                whitelist.appendChild(row);
        });
    }).catch(error => console.error('Error fetching whitelist: ', error));
}
