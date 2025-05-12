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
            addEntry(uid, name, permissions);
        })
    } else{
        console.log('Add form not found');
    }
    const filterUser = document.getElementById('user_filter');
    if (filterUser){
        filterUser.addEventListener('change', function(){
            console.log('User filter changed:', this.value);
            fetchWhitelist();
        });
    } else{
        console.log('User filter not found');
    }
});

function fetchWhitelist(){
    const filterDropdown = document.getElementById('user_filter');
    const ufilter = filterDropdown.value;
    console.log("Fetching whitelist");
    fetch('/get_overview')
    .then(response => response.json())
    .then(data => {
        console.log("whitelist received");
        data.sort((a, b) => new Date(b.Time) - new Date(a.Time));

        const users = [...new Set(data.map(entry => entry.name))];
        
        filterDropdown.innerHTML = `<option value="all">All</option>` + users.map(user => `<option value="${user}">${user}</option>`).join('');
        const whitelist = document.getElementById('overview');
        whitelist.innerHTML = '';
        data.forEach(entry => {
            if (ufilter === 'all' || entry.name === ufilter){
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
            }
        });
    }).catch(error => console.error('Error fetching whitelist: ', error));
}
