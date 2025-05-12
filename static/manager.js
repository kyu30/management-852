document.addEventListener('DOMContentLoaded', function(){
    fetchWhitelist();
    document.getElementById('addForm').addEventListener('submit', function(event){
        event.preventDefault();
        console.log("form submitted");
        const uid = document.getElementById('uid').value;
        const name = document.getElementById('name').value;
        const permissions = document.getElementById('permission').value;
        const host = document.getElementById('host').value;
        addEntry(uid, name, permissions, host);
    });
});

function fetchWhitelist(){
    fetch('/get_whitelist')
    .then(response => response.json())
    .then(data => {
        console.log("whitelist received");
        console.log(data)
        const whitelist = document.getElementById('whitelist');
        whitelist.innerHTML = '';
        data.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.uid}</td>
                <td>${entry.name}</td>
                <td>${entry.access}</td>
                <td>${entry.host}</td>
                <td>${entry.last_used}</td>
                <td><button onclick = "deleteEntry('${entry.UID}')">Delete</button></td>
                `;
                whitelist.appendChild(row);
        });
    }).catch(error => console.error('Error fetching whitelist: ', error));
}

function addEntry(uid, name, permissions, host){
    console.log('Adding entry:', { uid, name, permissions, host });
    fetch('/add_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ uid, name, permissions, host })
    })
    .then(response => {
        console.log('Add entry response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Add entry response:', data);
        if(data.status === 'success'){
            fetchWhitelist();
        } else{
            alert (`Failed to add entry: ${data.message}`);
        }
    })
    .catch(error => console.error('Error adding entry:', error));
}

function deleteEntry(uid){
    fetch('/delete_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({uid})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.status)
        if (data.status === 'success') {
            fetchWhitelist();
        } else {
            alert('Failed to delete entry')
        }
    });
}