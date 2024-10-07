async function submitSettings(event){
    event.preventDefault();
    setting = {
        "lockdown_time": $('#lockdowntime').val(),
        "maindoorsecs": $('#maindoorsecs').val(),
    }
    await fetch('settings',{
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
        },
        body: JSON.stringify(setting)
        });
    location.replace('/');
}