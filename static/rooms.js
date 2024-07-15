document.addEventListener('DOMContentLoaded', function(){
    console.log('Document loaded');
    const whitelistTable = document.getElementById('overview');
    if (whitelistTable){
        fetchWhitelist();
    }
    const addForm = document.getElementById('addForm');
    if (addForm){
        addForm.addEventListener('submit', function(event){
            event.preventDefault();
            console.log("form submitted");
            const uid = document.getElementById('uid').value;
            const name = document.getElementById('name').value;
            const permissions = document.getElementById('permission').value;
            const door = document.getElementById('door').value;
            const host = document.getElementById('host').value;
            const time = document.getElementById('time').value;
            addEntry(uid, name, permissions, host);
        })
    } else{
        console.log('Add form not found');
    }
    const filterUser = document.getElementById('room_filter');
    if (filterUser){
        filterUser.addEventListener('change', function(){
            console.log('Room filter changed:', this.value);
            fetchWhitelist();
        });
    } else{
        console.log('Room filter not found');
    }
});

function fetchWhitelist(){
    const ufilter = document.getElementById('room_filter').value;
    console.log("Fetching whitelist");
    fetch('/get_overview')
    .then(response => response.json())
    .then(data => {
        console.log("whitelist received");
        data.sort((a, b) => {
                return a['Time'] < b['Time'] ? 1 : -1;
        });
        const filterDropdown = document.getElementById('room_filter');
        const doors = [...new Set(data.map(entry => entry.Door))];
        
        filterDropdown.innerHTML = '<option value = "all">All</option>';
        doors.forEach(door => {
            filterDropdown.innerHTML += `<option value="${door}">${door}</option>`;
        });
        const whitelist = document.getElementById('overview');
        whitelist.innerHTML = '';
        data.forEach(entry => {
            if (ufilter === 'all' || entry.Door === ufilter){
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${entry.UID}</td>
                    <td>${entry.User}</td>
                    <td>${entry.Permission}</td>
                    <td>${entry.Door}</td>
                    <td>${entry.Host}</td>
                    <td>${entry.Time}</td>
                    `;
                    whitelist.appendChild(row);
            }
        });
    }).catch(error => console.error('Error fetching whitelist: ', error));
}
